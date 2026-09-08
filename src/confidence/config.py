"""Environment-based configuration for the Confidence Layer.

All configuration is loaded from environment variables with sensible defaults.
No secrets in source code.
"""

from __future__ import annotations

from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from confidence.domain.sqs import SQSConfig


class EnvironmentSettings(BaseSettings):
    """Resolve each settings group at load time, including the local dotenv file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", populate_by_name=True)


class SQSSettings(SQSConfig, EnvironmentSettings):
    model_config = SettingsConfigDict(env_prefix="SQS_", allow_inf_nan=False, frozen=True)


class DatabaseConfig(EnvironmentSettings):
    """PostgreSQL connection configuration."""

    url: str = "postgresql+asyncpg://confidence:confidence@localhost:5432/confidence"
    url_sync: str = "postgresql+psycopg://confidence:confidence@localhost:5432/confidence"
    pool_size: int = 5
    max_overflow: int = 10

    model_config = SettingsConfigDict(env_prefix="DATABASE_")


class SafetyConfig(EnvironmentSettings):
    """Safety Authority configuration."""

    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0, allow_inf_nan=False)
    data_max_age_seconds: float = Field(default=300.0, gt=0.0, allow_inf_nan=False)

    model_config = SettingsConfigDict(env_prefix="SAFETY_")


class DecisionConfig(EnvironmentSettings):
    """Decision Engine configuration."""

    timeout_ms: int = Field(default=100, gt=0)
    state_confidence_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        allow_inf_nan=False,
        validation_alias=AliasChoices("STATE_CONFIDENCE_THRESHOLD", "DECISION_STATE_CONFIDENCE_THRESHOLD"),
    )

    model_config = SettingsConfigDict(env_prefix="DECISION_")


class ServerConfig(EnvironmentSettings):
    """HTTP server configuration."""

    host: str = "0.0.0.0"
    port: int = 8000


class RedisConfig(EnvironmentSettings):
    url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_prefix="REDIS_")


class KafkaConfig(EnvironmentSettings):
    bootstrap_servers: str = "localhost:19092"

    model_config = SettingsConfigDict(env_prefix="KAFKA_")


class ModelConfig(EnvironmentSettings):
    state_estimator_type: Literal["rules", "lgbm"] = "rules"
    state_estimator_model_path: str | None = None
    state_estimator_confidence_threshold: float = Field(default=0.5, ge=0.5, le=1, allow_inf_nan=False)


class PolicyConfig(EnvironmentSettings):
    policy_type: Literal["deterministic", "bandit"] = "deterministic"
    bandit_model_path: str | None = None
    bandit_exploration_rate: float = Field(default=0.1, ge=0, le=1, allow_inf_nan=False)


class AuthConfig(EnvironmentSettings):
    auth_provider: Literal["development", "jwt"] = "development"
    jwks_url: str | None = None
    jwt_issuer: str | None = None
    jwt_audience: str | None = None


class RateLimitConfig(EnvironmentSettings):
    rate_limit_enabled: bool = True
    per_actor_rpm: int = Field(default=60, gt=0)
    per_ip_rpm: int = Field(default=120, gt=0)
    global_rpm: int = Field(default=10000, gt=0)


class ShadowConfig(EnvironmentSettings):
    shadow_mode: Literal["off", "full", "percentage", "actor_list"] = "off"
    shadow_percentage: float = Field(default=0, ge=0, le=100, allow_inf_nan=False)
    shadow_actors: list[str] = Field(default_factory=list)


class TracingConfig(EnvironmentSettings):
    tracing_enabled: bool = False
    otlp_endpoint: str | None = None


class AppConfig(EnvironmentSettings):
    """Top-level application configuration."""

    env: str = Field(default="development", validation_alias=AliasChoices("APP_ENV", "ENV", "env"))
    log_level: str = "INFO"
    demo_mode: bool = True
    auth_provider: str = "development"

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    decision: DecisionConfig = Field(default_factory=DecisionConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    kafka: KafkaConfig = Field(default_factory=KafkaConfig)
    tracing: TracingConfig = Field(default_factory=TracingConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    shadow: ShadowConfig = Field(default_factory=ShadowConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    policy: PolicyConfig = Field(default_factory=PolicyConfig)
    sqs: SQSSettings = Field(default_factory=SQSSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def require_runtime(self) -> None:
        if self.auth.auth_provider == "jwt" and not self.demo_mode:
            if not self.auth.jwks_url or not self.auth.jwt_issuer or not self.auth.jwt_audience:
                raise RuntimeError("Production authentication is not configured")
            return
        self.require_demo_runtime()

    def require_demo_runtime(self) -> None:
        """Refuse synthetic authority data outside the local demo.

        Replace with validated adapter/identity selection when operator contracts
        are available. Disabling DEMO_MODE cannot activate unimplemented providers.
        """
        if self.env not in {"development", "local", "test"} or not self.demo_mode or self.auth_provider != "development":
            raise RuntimeError(
                "Operator providers and production authentication are not configured. "
                "The demo requires APP_ENV=development/local/test, DEMO_MODE=true and AUTH_PROVIDER=development."
            )


def load_config() -> AppConfig:
    """Load configuration from environment variables."""
    return AppConfig()
