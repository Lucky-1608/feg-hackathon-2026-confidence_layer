"""FastAPI application entrypoint.

Uses the modern lifespan context manager for startup/shutdown lifecycle.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from confidence.api.routes import router
from confidence.config import load_config
from confidence.log import configure_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager — handles startup and shutdown."""
    config = load_config()
    configure_logging(config.log_level)
    log = get_logger("confidence.api")

    log.info("startup_begin", env=config.env)

    # Store config in app state for access by dependencies
    app.state.config = config

    # Initialize event publisher
    from confidence.api.dependencies import get_event_publisher

    publisher = get_event_publisher()
    await publisher.start()

    yield  # Application is running

    # Graceful shutdown
    log.info("shutdown_begin")

    await publisher.stop()

    # Dispose database engine if cached
    from confidence.api.dependencies import _engine_cache

    engine = _engine_cache.get("engine")
    if engine is not None:
        await engine.dispose()
        log.info("database_engine_disposed")

    log.info("shutdown_complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Confidence Layer API",
        description="Production real-time safety-constrained decision platform for betslip interventions.",
        version="0.4.0",
        lifespan=lifespan,
    )

    # CORS middleware for cross-origin requests from UI dev servers
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
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
        checks: dict[str, str] = {}

        # Check database connectivity
        try:
            from confidence.api.dependencies import _engine_cache

            engine = _engine_cache.get("engine")
            if engine is not None:
                from sqlalchemy import text

                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                checks["database"] = "ok"
            else:
                checks["database"] = "not_configured"
        except Exception as e:
            checks["database"] = f"error: {e}"

        # Overall status
        all_ok = all(v == "ok" or v == "not_configured" for v in checks.values())
        status_code = 200 if all_ok else 503

        from fastapi.responses import JSONResponse

        return JSONResponse(
            content={"status": "ready" if all_ok else "not_ready", "checks": checks},
            status_code=status_code,
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
