"""Tests for Event Bus and DLQ."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from confidence.domain.enums import EventType
from confidence.domain.event_contracts import ConfidenceEvent
from confidence.infrastructure.event_bus import InMemoryEventPublisher


@pytest.mark.asyncio
async def test_in_memory_event_publisher() -> None:
    publisher = InMemoryEventPublisher()

    event = ConfidenceEvent(
        event_id=uuid4(),
        event_type=EventType.CONFIRM_ATTEMPT,
        session_id=uuid4(),
        anonymous_actor_id="actor-1",
        timestamp=datetime.now(UTC),
        sequence_number=1,
        client_version="1.0",
    )

    await publisher.publish(event)

    assert len(publisher.published_events) == 1
    assert publisher.published_events[0] == event
