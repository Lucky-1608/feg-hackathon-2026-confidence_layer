"""Environment-based configuration for the Confidence Layer.

All configuration is loaded from environment variables with sensible defaults.
No secrets in source code.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


def _load_env() -> None:
    """Load .env file if present."""
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        load_dotenv(env_path)


@dataclass(frozen=True)
class DatabaseConfig:
    """PostgreSQL connection configuration."""

    url: str = "postgresql+asyncpg://confidence:confidence@localhost:5432/confidence"
    url_sync: str = "postgresql://confidence:confidence@localhost:5432/confidence"
    pool_size: int = 5
    max_overflow: int = 10


@dataclass(frozen=True)
class SafetyConfig:
    """Safety Authority configuration."""

    confidence_threshold: float = 0.5
    safety_data_max_age_seconds: float = 300.0


@dataclass(frozen=True)
class DecisionConfig:
    """Decision Engine configuration."""

    timeout_ms: int = 100
    state_confidence_threshold: float = 0.5


@dataclass(frozen=True)
class ServerConfig:
    """HTTP server configuration."""

    host: str = "0.0.0.0"
    port: int = 8000


@dataclass(frozen=True)
class RedisConfig:
    url: str = "redis://localhost:6379/0"


@dataclass(frozen=True)
class KafkaConfig:
    bootstrap_servers: str = "localhost:19092"


@dataclass(frozen=True)
class AppConfig:
    """Top-level application configuration."""

    env: str = "development"
    log_level: str = "INFO"
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    decision: DecisionConfig = field(default_factory=DecisionConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    kafka: KafkaConfig = field(default_factory=KafkaConfig)


def load_config() -> AppConfig:
    """Load configuration from environment variables.

    Call this once at application startup.
    """
    _load_env()

    return AppConfig(
        env=os.getenv("APP_ENV", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        database=DatabaseConfig(
            url=os.getenv(
                "DATABASE_URL",
                "postgresql+asyncpg://confidence:confidence@localhost:5432/confidence",
            ),
            url_sync=os.getenv(
                "DATABASE_URL_SYNC",
                "postgresql://confidence:confidence@localhost:5432/confidence",
            ),
            pool_size=int(os.getenv("DATABASE_POOL_SIZE", "5")),
            max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", "10")),
        ),
        safety=SafetyConfig(
            confidence_threshold=float(os.getenv("SAFETY_CONFIDENCE_THRESHOLD", "0.5")),
            safety_data_max_age_seconds=float(os.getenv("SAFETY_DATA_MAX_AGE_SECONDS", "300.0")),
        ),
        decision=DecisionConfig(
            timeout_ms=int(os.getenv("DECISION_TIMEOUT_MS", "100")),
            state_confidence_threshold=float(os.getenv("STATE_CONFIDENCE_THRESHOLD", "0.5")),
        ),
        server=ServerConfig(
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
        ),
        redis=RedisConfig(url=os.getenv("REDIS_URL", "redis://localhost:6379/0")),
        kafka=KafkaConfig(bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:19092")),
    )
