from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine

from confidence.api.app import create_app
from confidence.api.dependencies import get_event_publisher, get_persistence_provider
from confidence.application.reward_join import RewardJoinService
from confidence.db.schema import metadata, outcomes
from confidence.domain.enums import ActionId, OutcomeType, SafetyStatus, UncertaintyState
from confidence.domain.models import Decision, Outcome
from confidence.infrastructure.auth import AuthenticatedUser, verify_token
from confidence.infrastructure.event_bus import InMemoryEventPublisher
from confidence.infrastructure.persistence import DatabasePersistenceProvider


@pytest.fixture
async def outcome_setup(sample_context):
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    persistence = DatabasePersistenceProvider(engine)
    decision = Decision(
        decision_id=uuid4(),
        session_id=sample_context.session.session_id,
        timestamp=datetime.now(UTC),
        state=UncertaintyState.ODDS_CHANGE,
        state_confidence=0.9,
        safety_status=SafetyStatus.SAFE,
        candidate_actions=[ActionId.NO_INTERVENTION],
        selected_action=ActionId.NO_INTERVENTION,
        policy_version="policy-v1",
        model_version="rules-v1",
        action_registry_version="1",
        reason="test",
    )
    await persistence.persist_decision(decision, sample_context)
    publisher = InMemoryEventPublisher()
    yield persistence, decision, publisher
    await engine.dispose()


async def test_outcome_api(outcome_setup):
    persistence, decision, publisher = outcome_setup
    app = create_app()
    app.dependency_overrides.update(
        {
            get_persistence_provider: lambda: persistence,
            get_event_publisher: lambda: publisher,
            verify_token: lambda: AuthenticatedUser(subject="actor", operator_id="demo", scopes=["outcomes:write"], is_demo=True),
        }
    )
    payload = dict(decision_id=str(decision.decision_id), session_id=str(decision.session_id), outcome_type="BET_DEFERRED")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/v1/outcomes", json=payload)
        assert response.status_code == 201, response.text
        assert [m[0] for m in publisher.messages] == ["confidence.outcomes", "confidence.rewards"]
        async with persistence.session_factory() as session:
            assert len((await session.execute(select(outcomes))).all()) == 1
        assert (await client.post("/v1/outcomes", json={**payload, "outcome_type": "bad"})).status_code == 422
        assert (await client.post("/v1/outcomes", json={**payload, "session_id": str(uuid4())})).status_code == 404


async def test_late_reward(outcome_setup):
    persistence, decision, publisher = outcome_setup
    outcome = Outcome(
        outcome_id=uuid4(),
        decision_id=decision.decision_id,
        session_id=decision.session_id,
        timestamp=decision.timestamp + timedelta(minutes=10),
        outcome_type=OutcomeType.BET_DEFERRED,
    )
    await persistence.persist_outcome(outcome)
    assert await RewardJoinService(persistence, publisher).process_outcome(outcome) is None
    assert not publisher.messages


async def test_missing_reward_decision():
    persistence = AsyncMock()
    persistence.get_decision.return_value = None
    outcome = Outcome(
        outcome_id=uuid4(), decision_id=uuid4(), session_id=uuid4(), timestamp=datetime.now(UTC), outcome_type=OutcomeType.BET_DEFERRED
    )
    assert await RewardJoinService(persistence, InMemoryEventPublisher()).process_outcome(outcome) is None


async def test_broker_failure_is_durable_and_retry_is_idempotent(outcome_setup):
    from confidence.db.schema import outbox
    from confidence.infrastructure.outbox import OutboxDispatcher

    persistence, decision, publisher = outcome_setup
    broken = AsyncMock()
    broken.publish_message.side_effect = RuntimeError("broker down")
    app = create_app()
    app.dependency_overrides.update(
        {
            get_persistence_provider: lambda: persistence,
            get_event_publisher: lambda: broken,
            verify_token: lambda: AuthenticatedUser(subject="actor", operator_id="demo", scopes=["outcomes:write"], is_demo=True),
        }
    )
    payload = dict(
        outcome_id=str(uuid4()), decision_id=str(decision.decision_id), session_id=str(decision.session_id), outcome_type="BET_DEFERRED"
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        assert (await client.post("/v1/outcomes", json=payload)).status_code == 201
        assert (await client.post("/v1/outcomes", json=payload)).status_code == 201
        assert (await client.post("/v1/outcomes", json={**payload, "outcome_type": "BET_COMPLETED"})).status_code == 409
    async with persistence.session_factory() as session:
        assert len((await session.execute(select(outbox).where(outbox.c.delivered.is_(False)))).all()) == 2
        assert len((await session.execute(select(outcomes))).all()) == 1
    assert await OutboxDispatcher(persistence, publisher).flush() == 2
    assert await OutboxDispatcher(persistence, publisher).flush() == 0
