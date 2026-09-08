"""API Data Models.

Defines the external API request and response schemas.
These are decoupled from the internal domain models to allow the API
to evolve independently of the core decision engine.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from confidence.domain.enums import ActionId, OutcomeType, SafetyStatus, UncertaintyState


class InteractionDataPayload(BaseModel):
    """Interaction payload from the client."""

    session_age_seconds: float = 0.0
    recent_backtracks: int = 0
    dwell_time_seconds: float = 0.0
    selection_changes: int = 0
    stake_changes: int = 0
    odds_changed: bool = False
    time_since_slip_creation_seconds: float = 0.0
    confirmation_attempts: int = 0
    interaction_velocity: float = 0.0


class CreateDecisionRequest(BaseModel):
    """External request payload for a new decision."""

    session_id: UUID
    anonymous_actor_id: str
    client_version: str
    slip_id: str
    interaction: InteractionDataPayload


class DecisionResponse(BaseModel):
    """External response payload."""

    decision_id: UUID
    action: ActionId
    state: UncertaintyState
    confidence: float
    reason: str
    response_text: str | None = None
    policy_version: str
    model_version: str
    action_registry_version: str
    safety_status: SafetyStatus


class CreateOutcomeRequest(BaseModel):
    outcome_id: UUID | None = None
    decision_id: UUID
    session_id: UUID
    outcome_type: OutcomeType
    time_to_action_ms: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class OutcomeResponse(BaseModel):
    outcome_id: UUID
    decision_id: UUID
    status: str = "recorded"
