"""Strongly typed domain models for the Confidence Layer.

All version-sensitive objects include their version.
All models use Pydantic v2 strict validation.
No arbitrary dictionaries — every structure is explicitly typed.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from confidence.domain.enums import (
    ActionId,
    NoInterventionReason,
    OutcomeType,
    SafetyBlockReason,
    SafetyStatus,
    UncertaintyState,
)

# --- Session & Slip Context ---


class Session(BaseModel):
    """A user's betslip confirmation session."""

    session_id: UUID
    anonymous_actor_id: str = Field(description="Opaque identifier. Never contains PII.")
    started_at: datetime
    client_version: str


class OddsSnapshot(BaseModel):
    """A point-in-time odds value from an authoritative source."""

    odds: Decimal
    timestamp: datetime
    source: str


class Selection(BaseModel):
    """A single selection within a betslip."""

    selection_id: str
    market_id: str
    event_id: str
    event_name: str = ""
    market_name: str = ""
    odds: Decimal
    odds_at_placement: Decimal | None = None
    odds_history: list[OddsSnapshot] = Field(default_factory=list)


class SlipContext(BaseModel):
    """State of the betslip at decision time."""

    slip_id: str
    selections: list[Selection]
    stake: Decimal | None = None
    potential_return: Decimal | None = None
    created_at: datetime


class MarketContext(BaseModel):
    """Authoritative market data for a selection."""

    market_id: str
    market_name: str
    event_name: str
    market_definition: str = ""
    odds_history: list[OddsSnapshot] = Field(default_factory=list)
    is_live: bool = False
    data_freshness: datetime | None = None


# --- Safety Context ---


class HarmIndicators(BaseModel):
    """Behavioral indicators of potential gambling harm.

    These are derived from authoritative server-side data,
    never trusted from the browser.
    """

    rapid_loss_chasing: bool = False
    escalating_stakes: bool = False
    session_duration_extreme: bool = False
    loss_recovery_pattern: bool = False

    def has_any(self) -> bool:
        """Return True if any harm indicator is present."""
        return self.rapid_loss_chasing or self.escalating_stakes or self.session_duration_extreme or self.loss_recovery_pattern


class EnhancedHarmIndicators(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    rapid_loss_chasing: float = Field(default=0, ge=0, le=1)
    escalating_stakes: float = Field(default=0, ge=0, le=1)
    session_duration_extreme: float = Field(default=0, ge=0, le=1)
    loss_recovery_pattern: float = Field(default=0, ge=0, le=1)
    composite_harm_score: float = Field(default=0, ge=0, le=1)
    evidence: list[str] = Field(default_factory=list)

    def has_any(self, threshold: float = 0.3) -> bool:
        return (
            max(
                self.rapid_loss_chasing,
                self.escalating_stakes,
                self.session_duration_extreme,
                self.loss_recovery_pattern,
                self.composite_harm_score,
            )
            >= threshold
        )


class SessionSummary(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    session_id: UUID
    started_at: datetime
    ended_at: datetime | None = None
    total_stake: float = Field(default=0, ge=0)
    total_return: float | None = Field(default=None, ge=0)
    net_result: float | None = None
    bet_count: int = Field(default=0, ge=0)
    market_types: list[str] = Field(default_factory=list)
    deposit_count: int | None = Field(default=None, ge=0)
    mean_bet_interval_seconds: float | None = Field(default=None, ge=0)
    mean_selection_complexity: float | None = Field(default=None, ge=0)
    financial_data_complete: bool = False


class SafetyContext(BaseModel):
    """Safety-relevant state, sourced from authoritative server-side systems.

    These values must NEVER be trusted from the browser. They represent
    self-exclusion status, protective restrictions, and harm indicators.
    """

    is_self_excluded: bool = False
    has_protective_restrictions: bool = False
    harm_indicators: HarmIndicators | EnhancedHarmIndicators = Field(default_factory=HarmIndicators)
    data_freshness: datetime | None = None


# --- Interaction Context ---


class InteractionContext(BaseModel):
    """Behavioral signals from the user's interaction with the betslip.

    Every feature has a documented purpose:
    - session_age_seconds: time since session start (staleness indicator)
    - recent_backtracks: navigation reversals (uncertainty signal)
    - dwell_time_seconds: time on confirmation screen (hesitation signal)
    - selection_changes: number of selection modifications (configuration uncertainty)
    - stake_changes: number of stake modifications (stake uncertainty)
    - odds_changed: whether odds changed since slip creation (information gap)
    - time_since_slip_creation_seconds: slip age (context for hesitation)
    - confirmation_attempts: number of confirm button interactions (friction signal)
    - interaction_velocity: actions per minute (behavioral tempo)
    """

    session_age_seconds: float = 0.0
    recent_backtracks: int = 0
    dwell_time_seconds: float = 0.0
    selection_changes: int = 0
    stake_changes: int = 0
    odds_changed: bool = False
    time_since_slip_creation_seconds: float = 0.0
    confirmation_attempts: int = 0
    interaction_velocity: float = 0.0


# --- Composite Context ---


class DecisionContext(BaseModel):
    """Complete context assembled by the Context Builder for a decision.

    This is the input to the Decision Engine pipeline.
    """

    session: Session
    slip: SlipContext
    markets: list[MarketContext] = Field(default_factory=list)
    safety: SafetyContext = Field(default_factory=SafetyContext)
    interaction: InteractionContext = Field(default_factory=InteractionContext)
    context_version: str = "1"


# --- Authority Outputs ---


class SafetyResult(BaseModel):
    """Output of the Safety Authority.

    The Safety Authority answers: 'Can we intervene?'
    It does NOT optimize conversion.
    """

    status: SafetyStatus
    block_reasons: list[SafetyBlockReason] = Field(default_factory=list)
    timestamp: datetime
    authority_version: str = "1"


class StateEstimate(BaseModel):
    """Output of the State Authority.

    The State Authority answers: 'What is happening?'
    It remains separate from the safety decision.
    """

    state: UncertaintyState
    confidence: float = Field(ge=0.0, le=1.0)
    model_version: str
    features_used: list[str] = Field(default_factory=list)


# --- Decision ---


class Decision(BaseModel):
    """A complete decision record with full provenance.

    Must be reproducible from its recorded provenance.
    """

    decision_id: UUID
    session_id: UUID
    timestamp: datetime
    state: UncertaintyState
    state_confidence: float = Field(ge=0.0, le=1.0)
    safety_status: SafetyStatus
    safety_block_reasons: list[SafetyBlockReason] = Field(default_factory=list)
    candidate_actions: list[ActionId]
    selected_action: ActionId
    no_intervention_reason: NoInterventionReason | None = None
    policy_version: str
    model_version: str
    action_registry_version: str
    facts_version: str | None = None
    reason: str
    shadow_mode: bool = False
    policy_metadata: dict[str, Any] = Field(default_factory=dict)
    response_text: str | None = None


# --- Outcome ---


class Outcome(BaseModel):
    """Recorded outcome following a decision.

    Outcomes are submitted via POST /v1/outcomes for evaluation.
    """

    outcome_id: UUID
    decision_id: UUID
    session_id: UUID
    timestamp: datetime
    outcome_type: OutcomeType
    time_to_action_ms: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    schema_version: str = "1"


# --- Audit ---


class AuditRecord(BaseModel):
    """Complete audit trail entry for a decision.

    Stores everything needed to reconstruct why a decision was made.
    Audit persistence is downstream of the decision and must not
    cause decision failure.
    """

    audit_id: UUID
    decision_id: UUID
    timestamp: datetime
    context_snapshot: DecisionContext
    safety_result: SafetyResult
    state_estimate: StateEstimate
    candidate_actions: list[ActionId]
    selected_action: ActionId
    no_intervention_reason: NoInterventionReason | None = None
    policy_version: str
    model_version: str
    action_registry_version: str
    facts_version: str | None = None
    reason: str
    response_text: str | None = None
    outcome: Outcome | None = None
