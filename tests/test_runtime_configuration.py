"""Demo isolation and effective configuration, without external dependencies."""

from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import ValidationError

from confidence.api.app import create_app, lifespan
from confidence.api.dependencies import get_context_builder, get_safety_contract
from confidence.config import load_config
from confidence.domain.enums import SafetyStatus
from confidence.domain.models import SafetyContext
from confidence.infrastructure.auth import verify_token


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("AUTH_PROVIDER", "development")
    monkeypatch.setenv("SAFETY_CONFIDENCE_THRESHOLD", "0.5")
    monkeypatch.setenv("STATE_CONFIDENCE_THRESHOLD", "0.5")


@pytest.mark.parametrize(
    ("setting", "value"),
    [("APP_ENV", "production"), ("APP_ENV", "staging"), ("APP_ENV", "typo"), ("DEMO_MODE", "false"), ("AUTH_PROVIDER", "jwt")],
)
async def test_unconfigured_runtime_refuses_startup_providers_and_demo_token(monkeypatch, setting, value):
    monkeypatch.setenv(setting, value)
    with pytest.raises(RuntimeError, match="not configured"):
        get_context_builder()

    with pytest.raises(HTTPException) as exc:
        verify_token(HTTPAuthorizationCredentials(scheme="Bearer", credentials="demo-token"))
    assert exc.value.status_code == 503

    publisher = Mock()
    monkeypatch.setattr("confidence.api.dependencies.get_event_publisher", publisher)
    with pytest.raises(RuntimeError, match="not configured"):
        async with lifespan(create_app()):
            pytest.fail("Unconfigured runtime started")
    publisher.assert_not_called()


@pytest.mark.parametrize("env", ["development", "local", "test"])
def test_local_demo_remains_available(monkeypatch, env):
    monkeypatch.setenv("APP_ENV", env)
    get_context_builder()
    assert verify_token(HTTPAuthorizationCredentials(scheme="Bearer", credentials="demo-token")).subject == "user-123"
    with pytest.raises(HTTPException) as exc:
        verify_token(HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid"))
    assert exc.value.status_code == 401


def test_nested_configuration_is_loaded_again_after_environment_changes(monkeypatch):
    before = load_config()
    monkeypatch.setenv("DECISION_TIMEOUT_MS", "27")
    monkeypatch.setenv("SAFETY_DATA_MAX_AGE_SECONDS", "2")
    monkeypatch.setenv("STATE_CONFIDENCE_THRESHOLD", "0.91")
    after = load_config()
    assert after.decision.timeout_ms == 27
    assert before.decision.timeout_ms != after.decision.timeout_ms
    contract = get_safety_contract()
    assert contract.confidence_threshold == 0.91
    now = datetime.now(UTC)
    safety = SafetyContext(data_freshness=now - timedelta(seconds=3))
    assert contract.evaluate_safety(safety, now).status == SafetyStatus.STALE


def test_lower_state_threshold_does_not_weaken_safety_threshold(monkeypatch):
    monkeypatch.setenv("SAFETY_CONFIDENCE_THRESHOLD", "0.9")
    monkeypatch.setenv("STATE_CONFIDENCE_THRESHOLD", "0.1")
    assert get_safety_contract().confidence_threshold == 0.9


def test_dotenv_reaches_nested_settings(monkeypatch, tmp_path):
    monkeypatch.delenv("STATE_CONFIDENCE_THRESHOLD")
    monkeypatch.delenv("SAFETY_CONFIDENCE_THRESHOLD")
    (tmp_path / ".env").write_text(
        "DECISION_TIMEOUT_MS=23\nSTATE_CONFIDENCE_THRESHOLD=0.82\nREDIS_URL=redis://example.invalid:6380/3\n",
        encoding="utf-8",
    )
    config = load_config()
    assert config.decision.timeout_ms == 23
    assert config.decision.state_confidence_threshold == 0.82
    assert config.redis.url == "redis://example.invalid:6380/3"


@pytest.mark.parametrize(
    ("setting", "value"),
    [
        ("DECISION_TIMEOUT_MS", "0"),
        ("STATE_CONFIDENCE_THRESHOLD", "nan"),
        ("SAFETY_CONFIDENCE_THRESHOLD", "1.1"),
        ("SAFETY_DATA_MAX_AGE_SECONDS", "-1"),
    ],
)
def test_invalid_safety_configuration_rejected(monkeypatch, setting, value):
    monkeypatch.setenv(setting, value)
    with pytest.raises(ValidationError):
        load_config()


def test_sqs_weights_checked_from_environment(monkeypatch):
    monkeypatch.setenv("SQS_W3_HARM_INDICATOR_LOAD", "0.5")
    with pytest.raises(ValidationError):
        load_config()
