"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from confidence.api.routes import router
from confidence.config import load_config
from confidence.log import configure_logging, get_logger


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    config = load_config()

    # Configure logging based on env
    configure_logging(config.log_level)
    logger = get_logger("confidence.api")

    app = FastAPI(
        title="Confidence Layer API",
        description="Decision engine for betslip interventions.",
        version="0.1.0",
    )

    @app.on_event("startup")
    async def startup_event() -> None:
        logger.info("Application starting", env=config.env)

    @app.get("/health", tags=["Monitoring"])
    async def health_check() -> dict[str, str]:
        """Basic liveness check."""
        return {"status": "ok"}

    @app.get("/ready", tags=["Monitoring"])
    async def readiness_check() -> dict[str, str]:
        """Readiness check. In production, this would verify connections."""
        return {"status": "ready"}

    app.include_router(router)

    return app


app = create_app()
