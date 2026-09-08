"""Versioned session quality measurement; harm cannot be offset by conversion."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from confidence.domain.enums import ActionId, EventType, OutcomeType, UncertaintyState
from confidence.domain.event_contracts import ConfidenceEvent
from confidence.domain.models import Decision, Outcome, SafetyContext


class SQSConfig(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False, frozen=True)
    w1_action_value: float = Field(default=0.4, ge=0, le=1)
    w2_discovery_efficiency: float = Field(default=0.3, ge=0, le=1)
    w3_harm_indicator_load: float = Field(default=0.7, ge=0, le=1)
    version: str = "sqs-v1"

    @model_validator(mode="after")
    def harm_weight_dominates(self) -> "SQSConfig":
        if self.w3_harm_indicator_load < self.w1_action_value + self.w2_discovery_efficiency:
            raise ValueError("w3 must be >= w1 + w2")
        return self


class SessionQualityResult(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    raw_score: float
    clamped_score: float = Field(ge=-1, le=1)
    action_value: float = Field(ge=0, le=1)
    discovery_efficiency: float = Field(ge=0, le=1)
    harm_indicator_load: float = Field(ge=0, le=1)


class SQSCalculator:
    def __init__(self, config: SQSConfig | None = None) -> None:
        self.config = config or SQSConfig()

    def compute_action_value(self, outcome: Outcome, decision: Decision) -> float:
        if outcome.outcome_type == OutcomeType.BET_COMPLETED:
            return 0.5 if decision.selected_action == ActionId.NO_INTERVENTION else 0.8
        if outcome.outcome_type == OutcomeType.BET_ABANDONED:
            return 0.9 if decision.state == UncertaintyState.LEGITIMATE_RECONSIDERATION else 0.5
        return {
            OutcomeType.CLARIFICATION_ACCEPTED: 0.6,
            OutcomeType.CLARIFICATION_DISMISSED: 0.2,
            OutcomeType.BET_DEFERRED: 0.9,
            OutcomeType.SELECTION_CORRECTED: 0.8,
        }[outcome.outcome_type]

    def compute_discovery_efficiency(self, session_events: list[ConfidenceEvent], outcome: Outcome) -> float:
        if outcome.outcome_type == OutcomeType.BET_DEFERRED:
            return 1.0
        if not session_events and outcome.time_to_action_ms is None:
            return 0.0  # Missing telemetry is not evidence of an efficient session.
        backtracks = sum(event.event_type == EventType.NAVIGATION_BACK for event in session_events)
        elapsed = outcome.time_to_action_ms or 0
        return 1.0 / (1.0 + backtracks + elapsed / 60000)

    def compute_harm_indicator_load(self, safety_context: SafetyContext, outcome: Outcome) -> float:
        indicators = safety_context.harm_indicators
        if not indicators.has_any():
            return 0.0
        if outcome.outcome_type == OutcomeType.BET_COMPLETED:
            return 1.0
        return min(1.0, 0.3 + 0.2 * bool(indicators.escalating_stakes) + 0.4 * bool(indicators.rapid_loss_chasing))

    def compute_sqs(
        self, decision: Decision, outcome: Outcome, safety_context: SafetyContext, session_events: list[ConfidenceEvent]
    ) -> SessionQualityResult:
        action = self.compute_action_value(outcome, decision)
        efficiency = self.compute_discovery_efficiency(session_events, outcome)
        harm = self.compute_harm_indicator_load(safety_context, outcome)
        # Weight dominance alone only proves dominance at load=1. Suppress positive
        # terms for ANY observed harm so partial loads cannot yield a positive score.
        if harm:
            action = efficiency = 0.0
        raw = self.config.w1_action_value * action + self.config.w2_discovery_efficiency * efficiency
        raw -= self.config.w3_harm_indicator_load * harm
        return SessionQualityResult(
            raw_score=raw,
            clamped_score=max(-1.0, min(1.0, raw)),
            action_value=action,
            discovery_efficiency=efficiency,
            harm_indicator_load=harm,
        )
