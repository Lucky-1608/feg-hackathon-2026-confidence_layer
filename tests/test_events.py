"""Tests for the event schema.

Verifies event validation, required fields, sequence number constraints,
and that the schema rejects invalid data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from pydantic import ValidationError

from confidence.domain.enums import EventType
from confidence.domain.events import ConfidenceEvent

if TYPE_CHECKING:
    from datetime import datetime


class TestConfidenceEvent:
    def test_valid_event(self, now: datetime) -> None:
        e = ConfidenceEvent(
            event_id=uuid4(),
            event_type=EventType.CONFIRM_ATTEMPT,
            session_id=uuid4(),
            anonymous_actor_id="actor-001",
            timestamp=now,
            sequence_number=1,
            client_version="1.0.0",
        )
        assert e.schema_version == "1"
        assert e.context == {}
        assert e.payload == {}

    def test_event_with_payload(self, now: datetime) -> None:
        e = ConfidenceEvent(
            event_id=uuid4(),
            event_type=EventType.ODDS_UPDATE,
            session_id=uuid4(),
            anonymous_actor_id="actor-001",
            timestamp=now,
            sequence_number=5,
            client_version="1.0.0",
            payload={"old_odds": "2.30", "new_odds": "2.50"},
        )
        assert e.payload["old_odds"] == "2.30"

    def test_rejects_empty_actor_id(self, now: datetime) -> None:
        with pytest.raises(ValidationError, match="anonymous_actor_id"):
            ConfidenceEvent(
                event_id=uuid4(),
                event_type=EventType.CONFIRM_ATTEMPT,
                session_id=uuid4(),
                anonymous_actor_id="  ",
                timestamp=now,
                sequence_number=0,
                client_version="1.0.0",
            )

    def test_rejects_empty_client_version(self, now: datetime) -> None:
        with pytest.raises(ValidationError, match="client_version"):
            ConfidenceEvent(
                event_id=uuid4(),
                event_type=EventType.CONFIRM_ATTEMPT,
                session_id=uuid4(),
                anonymous_actor_id="actor-001",
                timestamp=now,
                sequence_number=0,
                client_version="  ",
            )

    def test_rejects_negative_sequence(self, now: datetime) -> None:
        with pytest.raises(ValidationError):
            ConfidenceEvent(
                event_id=uuid4(),
                event_type=EventType.CONFIRM_ATTEMPT,
                session_id=uuid4(),
                anonymous_actor_id="actor-001",
                timestamp=now,
                sequence_number=-1,
                client_version="1.0.0",
            )

    def test_rejects_invalid_event_type(self, now: datetime) -> None:
        with pytest.raises(ValidationError):
            ConfidenceEvent(
                event_id=uuid4(),
                event_type="INVALID_TYPE",  # type: ignore[arg-type]
                session_id=uuid4(),
                anonymous_actor_id="actor-001",
                timestamp=now,
                sequence_number=0,
                client_version="1.0.0",
            )

    def test_event_serialization_roundtrip(self, now: datetime) -> None:
        original = ConfidenceEvent(
            event_id=uuid4(),
            event_type=EventType.STAKE_CHANGE,
            session_id=uuid4(),
            anonymous_actor_id="actor-001",
            timestamp=now,
            sequence_number=10,
            client_version="1.0.0",
            payload={"new_stake": "20.00"},
        )
        data = original.model_dump(mode="json")
        restored = ConfidenceEvent.model_validate(data)
        assert restored.event_id == original.event_id
        assert restored.event_type == original.event_type
        assert restored.payload == original.payload

    def test_all_event_types_valid(self, now: datetime) -> None:
        """Every EventType enum value should produce a valid event."""
        for event_type in EventType:
            e = ConfidenceEvent(
                event_id=uuid4(),
                event_type=event_type,
                session_id=uuid4(),
                anonymous_actor_id="actor-001",
                timestamp=now,
                sequence_number=0,
                client_version="1.0.0",
            )
            assert e.event_type == event_type
