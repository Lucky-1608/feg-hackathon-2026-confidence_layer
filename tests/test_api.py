"""API Integration Tests."""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from confidence.api.app import app, create_app
from confidence.api.routes import get_idempotency_store


@pytest.mark.asyncio
async def test_health_check() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.parametrize(
    ("actor", "slip", "interaction", "action", "safety"),
    [
        ("actor-1", "slip-1", {}, "NO_INTERVENTION", "SAFE"),
        ("actor-1", "slip-1", {"odds_changed": True, "dwell_time_seconds": 6}, "EXPLAIN_ODDS_CHANGE", "SAFE"),
        ("actor-1", "slip-1", {"dwell_time_seconds": 20}, "EXPLAIN_MARKET", "SAFE"),
        ("actor-1", "slip-1", {"recent_backtracks": 2, "dwell_time_seconds": 5}, "NO_INTERVENTION", "SAFE"),
        ("actor-harm", "slip-1", {"odds_changed": True, "dwell_time_seconds": 6}, "NO_INTERVENTION", "BLOCKED"),
        ("actor-self-excluded", "slip-1", {"odds_changed": True, "dwell_time_seconds": 6}, "NO_INTERVENTION", "BLOCKED"),
        ("actor-safety-down", "slip-1", {}, "NO_INTERVENTION", "STALE"),
        ("actor-1", "slip-missing-odds", {"odds_changed": True, "dwell_time_seconds": 6}, "NO_INTERVENTION", "SAFE"),
        ("actor-1", "slip-down", {"odds_changed": True, "dwell_time_seconds": 6}, "NO_INTERVENTION", "SAFE"),
    ],
)
async def test_demo_decisions_through_api(monkeypatch, tmp_path, actor, slip, interaction, action, safety):
    """Exercise auth, request parsing, dependency wiring and engine; storage is stubbed.

    ASGITransport intentionally does not start lifespan/Kafka here. This is API
    scenario coverage, not evidence of live dependency integration or durability.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("AUTH_PROVIDER", "development")
    monkeypatch.setattr("confidence.api.dependencies.get_persistence_provider", lambda: Mock(persist_decision=AsyncMock()))
    test_app = create_app()
    test_app.dependency_overrides[get_idempotency_store] = lambda: Mock()
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        response = await client.post(
            "/v1/decisions",
            headers={"Authorization": "Bearer demo-token"},
            json={
                "session_id": str(uuid4()),
                "anonymous_actor_id": actor,
                "client_version": "demo-test",
                "slip_id": slip,
                "interaction": interaction,
            },
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["action"] == action
        assert data["safety_status"] == safety
        if action == "NO_INTERVENTION":
            assert data["response_text"] is None
            assert data["reason"] != "Pipeline completed"
        else:
            assert data["response_text"]

        ui = await client.get("/ui/")
        assert ui.status_code == 200
        assert "intervention-overlay" in ui.text


async def test_readiness_checks_all_dependencies(monkeypatch):
    test_app = create_app()
    test_app.state.redis = AsyncMock()
    test_app.state.publisher = AsyncMock()
    test_app.state.publisher.is_ready.return_value = True
    engine = Mock()
    connection = AsyncMock()
    engine.connect.return_value.__aenter__ = AsyncMock(return_value=connection)
    engine.connect.return_value.__aexit__ = AsyncMock()
    monkeypatch.setattr("confidence.api.dependencies.get_engine", lambda: engine)
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        assert (await client.get("/ready")).status_code == 200
        test_app.state.redis.ping.side_effect = RuntimeError("secret")
        result = await client.get("/ready")
        assert result.status_code == 503
        assert "secret" not in result.text
        assert result.json()["checks"]["redis"] == "unavailable"
    assert len([r for r in test_app.routes if getattr(r, "path", "") == "/ready"]) == 1
