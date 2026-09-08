"""Environment-based configuration for the Confidence Layer.

All configuration is loaded from environment variables with sensible defaults.
No secrets in source code.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """PostgreSQL connection configuration."""

    url: str = "postgresql+asyncpg://confidence:confidence@localhost:5432/confidence"
    url_sync: str = "postgresql+psycopg://confidence:confidence@localhost:5432/confidence"
    pool_size: int = 5
    max_overflow: int = 10

    model_config = SettingsConfigDict(env_prefix="DATABASE_")


class SafetyConfig(BaseSettings):
    """Safety Authority configuration."""

    confidence_threshold: float = 0.5
    data_max_age_seconds: float = 300.0

    model_config = SettingsConfigDict(env_prefix="SAFETY_")


class DecisionConfig(BaseSettings):
    """Decision Engine configuration."""

    timeout_ms: int = 100
    state_confidence_threshold: float = 0.5

    model_config = SettingsConfigDict(env_prefix="DECISION_")


class ServerConfig(BaseSettings):
    """HTTP server configuration."""

    host: str = "0.0.0.0"
    port: int = 8000


class RedisConfig(BaseSettings):
    url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_prefix="REDIS_")


class KafkaConfig(BaseSettings):
    bootstrap_servers: str = "localhost:19092"

    model_config = SettingsConfigDict(env_prefix="KAFKA_")


class AppConfig(BaseSettings):
    """Top-level application configuration."""

    env: str = "development"
    log_level: str = "INFO"

    # We will instantiate them directly
    database: DatabaseConfig = DatabaseConfig()
    safety: SafetyConfig = SafetyConfig()
    decision: DecisionConfig = DecisionConfig()
    server: ServerConfig = ServerConfig()
    redis: RedisConfig = RedisConfig()
    kafka: KafkaConfig = KafkaConfig()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def load_config() -> AppConfig:
    """Load configuration from environment variables."""
    return AppConfig()
