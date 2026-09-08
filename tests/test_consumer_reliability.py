from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import fakeredis.aioredis
import pytest

from confidence.application.event_processor import EventProcessor
from confidence.domain.enums import EventType
from confidence.domain.event_contracts import ConfidenceEvent
from confidence.infrastructure.event_ordering import SequenceValidator
from confidence.infrastructure.session_state import RedisSessionStore
from confidence.workers.event_consumer import ReliableEventConsumer


def record(sequence=0):
    event = ConfidenceEvent(
        event_id=uuid4(),
        session_id=uuid4(),
        anonymous_actor_id="actor",
        event_type=EventType.NAVIGATION_BACK,
        timestamp=datetime.now(UTC),
        sequence_number=sequence,
        client_version="1",
    )
    return SimpleNamespace(value=event.model_dump_json().encode(), topic="events", partition=2, offset=7), event


@pytest.mark.parametrize("sequence,dlq_count", [(0, 0), (2, 1)])
async def test_process_and_order(sequence, dlq_count):
    redis = fakeredis.aioredis.FakeRedis()
    consumer, dlq = AsyncMock(), AsyncMock()
    store = RedisSessionStore(redis)
    worker = ReliableEventConsumer(consumer, EventProcessor(store), SequenceValidator(redis), dlq, base_delay=0)
    msg, event = record(sequence)
    await worker.process_record(msg)
    assert dlq.push.await_count == dlq_count
    consumer.commit.assert_awaited_once()
    if not sequence:
        await worker.process_record(msg)
        assert (await store.get_interaction(event.session_id)).recent_backtracks == 1
    await redis.aclose()


async def test_retry_and_dlq_failure():
    consumer, processor, validator, dlq = (AsyncMock() for _ in range(4))
    validator.validate_and_increment.return_value = True
    processor.process_event.side_effect = [RuntimeError(), None]
    worker = ReliableEventConsumer(consumer, processor, validator, dlq, base_delay=0)
    await worker.process_record(record()[0])
    assert processor.process_event.await_count == 2
    consumer.commit.reset_mock()
    processor.process_event.side_effect = RuntimeError()
    dlq.push.side_effect = RuntimeError("broker down")
    with pytest.raises(RuntimeError):
        await worker.process_record(record()[0])
    consumer.commit.assert_not_called()
