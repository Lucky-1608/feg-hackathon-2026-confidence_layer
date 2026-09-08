"""Join observed outcomes to immutable decision provenance for learning."""

from uuid import UUID

from pydantic import BaseModel, Field

from confidence.domain.enums import ActionId, OutcomeType, SafetyStatus
from confidence.domain.models import Decision, DecisionContext, Outcome
from confidence.domain.ports import OutcomePersistenceProvider
from confidence.infrastructure.event_bus import EventPublisher


class RewardSignal(BaseModel):
    outcome_id: UUID | None = None
    decision_id: UUID
    session_id: UUID
    action_taken: ActionId
    context_features: dict[str, float]
    reward: float = Field(ge=-1, le=1, allow_inf_nan=False)
    join_latency_ms: int = Field(ge=0)
    is_late_join: bool = False
    candidate_actions: list[ActionId] = Field(default_factory=list)
    selection_probability: float = Field(default=1.0, gt=0, le=1, allow_inf_nan=False)


class RewardJoinService:
    def __init__(
        self, persistence: OutcomePersistenceProvider, event_publisher: EventPublisher, join_window_seconds: float = 300.0
    ) -> None:
        self.persistence = persistence
        self.publisher = event_publisher
        self.join_window_seconds = join_window_seconds

    async def process_outcome(self, outcome: Outcome) -> RewardSignal | None:
        decision = await self.persistence.get_decision(outcome.decision_id)
        context = await self.persistence.get_context(outcome.decision_id)
        if decision is None or context is None or decision.session_id != outcome.session_id:
            return None
        latency = int((outcome.timestamp - decision.timestamp).total_seconds() * 1000)
        if latency < 0:
            return None
        late = latency > self.join_window_seconds * 1000
        await self.persistence.record_reward_join(outcome.outcome_id, latency, late)
        if late:
            return None
        if decision.shadow_mode or decision.safety_status != SafetyStatus.SAFE:
            return None
        signal = self.build_signal(decision, outcome, context, latency)
        await self.publisher.publish_message("confidence.rewards", str(signal.session_id), signal.model_dump(mode="json"))
        return signal

    @staticmethod
    def build_signal(decision: Decision, outcome: Outcome, context: DecisionContext, latency: int) -> RewardSignal:
        # Behavioral quality only; never use financial size or harm features in policy inputs.
        reward = {
            OutcomeType.CLARIFICATION_ACCEPTED: 0.6,
            OutcomeType.CLARIFICATION_DISMISSED: 0.2,
            OutcomeType.BET_COMPLETED: 0.5,
            OutcomeType.BET_ABANDONED: 0.5,
            OutcomeType.BET_DEFERRED: 0.9,
            OutcomeType.SELECTION_CORRECTED: 0.8,
        }[outcome.outcome_type]
        return RewardSignal(
            outcome_id=outcome.outcome_id,
            decision_id=decision.decision_id,
            session_id=decision.session_id,
            action_taken=decision.selected_action,
            candidate_actions=decision.candidate_actions,
            selection_probability=decision.policy_metadata.get("selection_probability", 1.0),
            context_features={
                "dwell_time_seconds": context.interaction.dwell_time_seconds,
                "recent_backtracks": float(context.interaction.recent_backtracks),
            },
            reward=reward,
            join_latency_ms=latency,
        )
