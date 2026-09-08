"""FastAPI application entrypoint.

Uses the modern lifespan context manager for startup/shutdown lifecycle.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from redis.asyncio import Redis

from confidence.api.routes import router
from confidence.config import load_config
from confidence.log import configure_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager — handles startup and shutdown."""
    config = load_config()
    config.require_runtime()
    configure_logging(config.log_level)
    log = get_logger("confidence.api")

    log.info("startup_begin", env=config.env)

    # Store config in app state for access by dependencies
    app.state.config = config
    from confidence.infrastructure.backpressure import ConcurrencyLimiter

    app.state.concurrency_limiter = ConcurrencyLimiter(200)

    # Initialize event publisher
    from confidence.api.dependencies import get_event_publisher

    app.state.redis = Redis.from_url(config.redis.url, decode_responses=False)
    publisher = get_event_publisher()
    app.state.publisher = publisher
    if config.tracing.tracing_enabled:
        from confidence.observability.tracing import setup_tracing

        app.state.tracer_provider = setup_tracing(otlp_endpoint=config.tracing.otlp_endpoint)
    try:
        await publisher.start()
        from confidence.api.dependencies import get_engine, get_policy_selector, get_state_estimator
        from confidence.evaluation.ab_test import ExperimentManager

        app.state.experiments = ExperimentManager(
            get_engine(),
            policies={config.policy.policy_type: get_policy_selector()},
            estimators={config.model.state_estimator_type: get_state_estimator()},
        )
        await app.state.experiments.refresh()

        from confidence.infrastructure.outbox import OutboxDispatcher
        from confidence.infrastructure.persistence import DatabasePersistenceProvider

        dispatcher = OutboxDispatcher(DatabasePersistenceProvider(get_engine()), publisher)

        async def deliver_outbox() -> None:
            while True:
                try:
                    async with asyncio.timeout(5):
                        await dispatcher.flush()
                except Exception:
                    log.warning("outbox_delivery_deferred")
                await asyncio.sleep(1)

        outbox_task = asyncio.create_task(deliver_outbox())

        async def refresh_experiments() -> None:
            while True:
                await asyncio.sleep(30)
                try:
                    await app.state.experiments.refresh()
                except Exception:
                    log.error("experiment_refresh_failed")

        refresh_task = asyncio.create_task(refresh_experiments())
        try:
            yield
        finally:
            outbox_task.cancel()
            refresh_task.cancel()
            import contextlib

            with contextlib.suppress(asyncio.CancelledError):
                await refresh_task
            with contextlib.suppress(asyncio.CancelledError):
                await outbox_task
    finally:
        log.info("shutdown_begin")
        from confidence.infrastructure.background import drain

        await drain()
        if hasattr(app.state, "tracer_provider"):
            await asyncio.to_thread(app.state.tracer_provider.force_flush, timeout_millis=1000)
        try:
            await publisher.stop()
        finally:
            await app.state.redis.aclose()
            from confidence.api.dependencies import _engine_cache, _publisher_cache

            engine = _engine_cache.pop("engine", None)
            _publisher_cache.clear()
            if engine is not None:
                await engine.dispose()
        log.info("shutdown_complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Confidence Layer API",
        description="Production real-time safety-constrained decision platform for betslip interventions.",
        version="0.4.0",
        lifespan=lifespan,
    )

    from confidence.infrastructure.rate_limiter import RateLimitMiddleware

    app.add_middleware(RateLimitMiddleware)

    from confidence.observability.correlation import CorrelationIdMiddleware

    app.add_middleware(CorrelationIdMiddleware)
    if load_config().tracing.tracing_enabled:
        from confidence.api.dependencies import get_engine
        from confidence.observability.tracing import instrument_app

        instrument_app(app, get_engine())
    from prometheus_client import make_asgi_app

    from confidence.observability.metrics_auth import AuthenticatedMetrics

    app.mount("/metrics", AuthenticatedMetrics(make_asgi_app()))

    # CORS middleware for cross-origin requests from UI dev servers
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health and readiness probes
    @app.get("/health", tags=["Monitoring"])
    async def health_check() -> dict[str, str]:
        """Basic liveness check. Returns OK if the process is alive."""
        return {"status": "ok"}

    from fastapi.responses import JSONResponse

    @app.get("/ready", tags=["Monitoring"], response_model=None)
    async def readiness_check() -> JSONResponse:
        """Readiness check. Verifies required dependencies are available."""
        from sqlalchemy import text

        from confidence.api.dependencies import get_engine

        async def database_check() -> None:
            async with get_engine().connect() as conn:
                await conn.execute(text("SELECT 1"))

        async def redis_check() -> None:
            await app.state.redis.ping()

        async def kafka_check() -> None:
            if not await app.state.publisher.is_ready():
                raise RuntimeError("unavailable")

        async def check(name: str) -> tuple[str, str]:
            try:
                async with asyncio.timeout(2.0):
                    await {"database": database_check, "redis": redis_check, "kafka": kafka_check}[name]()
                return name, "ok"
            except Exception:
                return name, "unavailable"

        checks = dict(await asyncio.gather(*(check(name) for name in ("database", "redis", "kafka"))))
        all_ok = all(value == "ok" for value in checks.values())
        return JSONResponse(
            content={"status": "ready" if all_ok else "not_ready", "checks": checks},
            status_code=200 if all_ok else 503,
        )

    # API routes
    app.include_router(router)

    # Serve UI static files
    ui_dir = Path(__file__).parent.parent / "ui"
    if ui_dir.exists():
        app.mount("/ui", StaticFiles(directory=str(ui_dir), html=True), name="ui")

    @app.get("/", include_in_schema=False)
    async def root_redirect() -> RedirectResponse:
        return RedirectResponse(url="/ui/")

    return app


app = create_app()
