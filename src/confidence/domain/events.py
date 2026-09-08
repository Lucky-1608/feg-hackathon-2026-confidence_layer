"""Versioned event schema for the Confidence Layer.

Events are the primary input from the client. Critical values
(odds, returns, self-exclusion, account limits, harm state, financial state)
must NOT be trusted from the browser — they must come from authoritative
server-side sources.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from confidence.domain.enums import EventType


class ConfidenceEvent(BaseModel):
    """A versioned event from the client.

    Schema follows the architecture spec's event format.
    Sequence numbers enable ordering and duplicate detection.
    """

    event_id: UUID
    event_type: EventType
    session_id: UUID
    anonymous_actor_id: str = Field(
        description="Opaque identifier. Never contains PII."
    )
    timestamp: datetime
    sequence_number: int = Field(ge=0)
    client_version: str
    schema_version: str = "1"
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Client-side context. Values here are NOT authoritative.",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific payload data.",
    )

    @field_validator("anonymous_actor_id")
    @classmethod
    def actor_id_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("anonymous_actor_id must not be empty")
        return v

    @field_validator("client_version")
    @classmethod
    def version_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("client_version must not be empty")
        return v

    @field_validator("sequence_number")
    @classmethod
    def sequence_must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("sequence_number must be non-negative")
        return v
