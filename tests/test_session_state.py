"""Tests for session state and event ordering."""

from datetime import UTC, datetime
from uuid import uuid4

import fakeredis.aioredis
import pytest

from confidence.domain.models import Session
from confidence.infrastructure.event_ordering import SequenceValidator
from confidence.infrastructure.session_state import RedisIdempotencyStore, RedisSessionStore


@pytest.fixture
async def redis():
    """Provide a FakeRedis connection."""
    client = fakeredis.aioredis.FakeRedis()
    yield client
    await client.close()


@pytest.mark.asyncio
async def test_session_store_save_get(redis) -> None:
    store = RedisSessionStore(redis)
    session_id = uuid4()

    session = Session(session_id=session_id, anonymous_actor_id="actor-1", started_at=datetime.now(UTC), client_version="1.0")

    await store.save_session(session)
    retrieved = await store.get_session(session_id)

    assert retrieved is not None
    assert retrieved.session_id == session.session_id


@pytest.mark.asyncio
async def test_session_store_update_interaction(redis) -> None:
    store = RedisSessionStore(redis)
    session_id = uuid4()

    # First update
    ctx = await store.update_interaction(session_id, {"recent_backtracks": 1, "odds_changed": True})
    assert ctx.recent_backtracks == 1
    assert ctx.odds_changed is True

    # Second update
    ctx = await store.update_interaction(session_id, {"recent_backtracks": 2, "dwell_time_seconds": 5.0})
    # recent_backtracks is additive
    assert ctx.recent_backtracks == 3
    assert ctx.dwell_time_seconds == 5.0
    assert ctx.odds_changed is True


@pytest.mark.asyncio
async def test_idempotency_store(redis) -> None:
    store = RedisIdempotencyStore(redis)
    key = "req-123"

    # First acquire succeeds
    assert await store.acquire(key) is True

    # Second acquire fails
    assert await store.acquire(key) is False

    # Save response
    await store.save_response(key, {"status": "ok"})

    # Get response
    resp = await store.get_response(key)
    assert resp == {"status": "ok"}


@pytest.mark.asyncio
async def test_sequence_validator(redis) -> None:
    validator = SequenceValidator(redis)
    session_id = uuid4()

    # First event must be 0
    assert await validator.validate_and_increment(session_id, 0) is True

    # Duplicate 0 fails
    assert await validator.validate_and_increment(session_id, 0) is False

    # Gap 2 fails (expected 1)
    assert await validator.validate_and_increment(session_id, 2) is False

    # Correct 1 succeeds
    assert await validator.validate_and_increment(session_id, 1) is True
