import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

from httpx import ASGITransport, AsyncClient

from confidence.api.app import create_app
from confidence.application.engine import DecisionEngine
from confidence.application.replay import ReplayManager
from confidence.domain.enums import EventType
from confidence.domain.event_contracts import ConfidenceEvent
from confidence.domain.policy import PolicySelector
from confidence.domain.response import ResponseGenerator
from confidence.domain.state import StateEstimator
from confidence.infrastructure.background import drain, pending_tasks, schedule
from tests.test_outcomes import outcome_setup  # noqa: F401


async def test_metrics_and_correlation():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as client:
        response = await client.get("/metrics", headers={"X-Request-ID": "test-123", "Authorization": "Bearer demo-token"})
        assert response.status_code == 200
        assert "confidence_decision_requests_total" in response.text
        assert response.headers["x-request-id"] == "test-123"
        assert (await client.get("/health")).headers["x-request-id"]


async def test_audit_drain():
    schedule(asyncio.sleep(0))
    assert await drain() == (1, 0)
    schedule(asyncio.sleep(60))
    assert await drain(timeout=0.001) == (0, 1)
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    assert not pending_tasks


async def test_replay(outcome_setup, sample_context, action_registry, safety_contract):  # noqa: F811
    persistence, decision, _ = outcome_setup
    event = ConfidenceEvent(
        event_id=uuid4(),
        session_id=decision.session_id,
        anonymous_actor_id=sample_context.session.anonymous_actor_id,
        timestamp=decision.timestamp + timedelta(seconds=1),
        sequence_number=0,
        event_type=EventType.NAVIGATION_BACK,
        client_version="1",
    )
    await persistence.persist_event(event)
    engine = DecisionEngine(
        AsyncMock(), safety_contract, StateEstimator(), action_registry, PolicySelector(), ResponseGenerator(action_registry), persistence
    )
    replay = ReplayManager(persistence, engine)
    report = await replay.replay_batch([decision.session_id])
    assert report.replayed_decisions == report.comparisons == 1
    assert len(await persistence.get_session_decisions(decision.session_id)) == 1


async def test_full_lifespan_shared_clients(monkeypatch):
    import fakeredis.aioredis
    from sqlalchemy.ext.asyncio import create_async_engine

    from confidence.api.app import lifespan
    from confidence.db.schema import metadata
    from confidence.infrastructure.event_bus import InMemoryEventPublisher

    redis = fakeredis.aioredis.FakeRedis()
    database = create_async_engine("sqlite+aiosqlite://")
    async with database.begin() as conn:
        await conn.run_sync(metadata.create_all)
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("AUTH_PROVIDER", "development")
    monkeypatch.setattr("confidence.api.app.Redis.from_url", lambda *a, **kw: redis)
    monkeypatch.setattr("confidence.api.dependencies.get_engine", lambda: database)
    publisher = InMemoryEventPublisher()
    monkeypatch.setattr("confidence.api.dependencies.get_event_publisher", lambda: publisher)
    app = create_app()
    async with lifespan(app):
        assert app.state.redis is redis
        assert app.state.experiments.available
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            assert (await client.get("/ready")).status_code == 200
    await database.dispose()


async def test_metrics_requires_auth():
    async with AsyncClient(transport=ASGITransport(app=create_app()), base_url="http://test", follow_redirects=True) as client:
        assert (await client.get("/metrics")).status_code == 401
