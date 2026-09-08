"""Safety Contract for the Confidence Layer.

Encodes system invariants S1–S17 as executable rules.
The Safety Authority answers: 'Can we intervene?'

Architectural constraint: Safety is structurally enforced by this contract.
Safety-model correctness must be validated empirically through the test suite
and scenario registry. The architecture does NOT claim mathematical guarantees;
it enforces structural constraints that are validated through testing.
"""

from __future__ import annotations

from datetime import UTC, datetime

from confidence.domain.actions import ActionDefinition
from confidence.domain.enums import (
    ActionId,
    NoInterventionReason,
    SafetyBlockReason,
    SafetyStatus,
    UncertaintyState,
)
from confidence.domain.models import SafetyContext, SafetyResult, StateEstimate

# --- Configuration ---

# Maximum age in seconds for safety data before it is considered stale.
SAFETY_DATA_MAX_AGE_SECONDS = 300.0  # 5 minutes

# Confidence threshold below which the system fails closed.
DEFAULT_CONFIDENCE_THRESHOLD = 0.5


class SafetyContract:
    """Executable safety contract encoding invariants S1–S17.

    This contract is the Safety Authority. It determines whether
    intervention is permitted, and why it is not.

    The contract does NOT optimize conversion. It only gates it.

    Invariants encoded:
        S1: Self-excluded user → NO_INTERVENTION
        S2: Explicit protective restriction → NO_INTERVENTION
        S3: Strong harmful-play state → NO conversion-oriented intervention
        S4: Unknown safety state → fail closed
        S5: Safety dependency unavailable → fail closed
        S6: Authoritative market data unavailable → no factual market explanation
        S7: Model failure → NO_INTERVENTION
        S8: Model confidence below threshold → NO_INTERVENTION
        S9: Policy can select only registered actions (enforced by ActionRegistry)
        S10: Policy cannot modify safety rules (enforced by architecture)
        S11: User can always abandon or defer (enforced by UI)
        S12: No urgency mechanics (enforced by response templates)
        S13: No artificial scarcity (enforced by response templates)
        S14: No social-proof pressure (enforced by response templates)
        S15: No coercive incentives (enforced by response templates)
        S16: Timeout → NO_INTERVENTION
        S17: Every decision must be auditable (enforced by Decision Engine)
    """

    def __init__(
        self,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
        safety_data_max_age_seconds: float = SAFETY_DATA_MAX_AGE_SECONDS,
    ) -> None:
        self._confidence_threshold = confidence_threshold
        self._safety_data_max_age_seconds = safety_data_max_age_seconds

    @property
    def confidence_threshold(self) -> float:
        return self._confidence_threshold

    def evaluate_safety(
        self,
        safety_context: SafetyContext,
        now: datetime | None = None,
    ) -> SafetyResult:
        """Evaluate whether intervention is permitted.

        Returns a SafetyResult with status and block reasons.
        Any block reason → BLOCKED. Unknown state → UNKNOWN (fail closed).
        """
        if now is None:
            now = datetime.now(UTC)

        block_reasons: list[SafetyBlockReason] = []

        # S1: Self-excluded user → NO_INTERVENTION
        if safety_context.is_self_excluded:
            block_reasons.append(SafetyBlockReason.SELF_EXCLUSION)

        # S2: Explicit protective restriction → NO_INTERVENTION
        if safety_context.has_protective_restrictions:
            block_reasons.append(SafetyBlockReason.PROTECTIVE_RESTRICTION)

        # S3: Strong harmful-play state → NO conversion-oriented intervention
        if safety_context.harm_indicators.has_any():
            block_reasons.append(SafetyBlockReason.HARM_STATE)

        # S5: Safety dependency unavailable → fail closed
        # Check data freshness. If safety data is stale, fail closed.
        if safety_context.data_freshness is not None:
            age = (now - safety_context.data_freshness).total_seconds()
            if age > self._safety_data_max_age_seconds:
                block_reasons.append(SafetyBlockReason.SAFETY_DEPENDENCY_UNAVAILABLE)
        else:
            # No freshness timestamp → we cannot verify data currency → fail closed (S4)
            block_reasons.append(SafetyBlockReason.UNKNOWN_SAFETY_STATE)

        status = SafetyStatus.SAFE
        if block_reasons:
            if SafetyBlockReason.UNKNOWN_SAFETY_STATE in block_reasons:
                status = SafetyStatus.UNKNOWN
            elif SafetyBlockReason.SAFETY_DEPENDENCY_UNAVAILABLE in block_reasons:
                status = SafetyStatus.STALE
            else:
                status = SafetyStatus.BLOCKED

        return SafetyResult(
            status=status,
            block_reasons=block_reasons,
            timestamp=now,
        )

    def check_state_confidence(
        self,
        state_estimate: StateEstimate,
    ) -> NoInterventionReason | None:
        """Check if state estimation confidence is sufficient.

        S4: Unknown safety state → fail closed
        S8: Model confidence below threshold → NO_INTERVENTION

        Returns a NoInterventionReason if confidence is insufficient,
        or None if confidence is acceptable.
        """
        # S4: Unknown state → fail closed
        if state_estimate.state == UncertaintyState.UNKNOWN:
            return NoInterventionReason.INSUFFICIENT_CONFIDENCE

        # S8: Confidence below threshold → NO_INTERVENTION
        if state_estimate.confidence < self._confidence_threshold:
            return NoInterventionReason.INSUFFICIENT_CONFIDENCE

        return None

    def check_legitimate_reconsideration(
        self,
        state_estimate: StateEstimate,
    ) -> NoInterventionReason | None:
        """Check if user is legitimately reconsidering.

        The system must never assume hesitation = intervention needed.
        If the user appears to be thoughtfully reconsidering, do not intervene.

        Returns NoInterventionReason.LEGITIMATE_RECONSIDERATION if applicable.
        """
        if state_estimate.state == UncertaintyState.LEGITIMATE_RECONSIDERATION:
            return NoInterventionReason.LEGITIMATE_RECONSIDERATION
        return None

    def final_safety_check(
        self,
        selected_action: ActionId,
        safety_result: SafetyResult,
        state_estimate: StateEstimate,
        action_definition: ActionDefinition | None = None,
    ) -> NoInterventionReason | None:
        """Final safety check before response generation.

        This is the last gate in the pipeline. It catches any
        action that should not have reached this point.

        Returns a NoInterventionReason if the action must be blocked,
        or None if it passes.
        """
        # If safety blocked or requires fail closed, must be NO_INTERVENTION
        is_safe = safety_result.status == SafetyStatus.SAFE
        if not is_safe and selected_action != ActionId.NO_INTERVENTION:
            return NoInterventionReason.SAFETY_BLOCKED

        # S3: Harmful state → no conversion-oriented intervention
        from confidence.domain.enums import SafetyClass

        is_conversion = (
            action_definition.safety_class == SafetyClass.CONVERSION_ORIENTED
            if action_definition
            else selected_action not in (ActionId.NO_INTERVENTION, ActionId.OFFER_DEFER)
        )
        if state_estimate.state == UncertaintyState.POTENTIAL_HARM and is_conversion:
            return NoInterventionReason.SAFETY_BLOCKED

        return None

    @staticmethod
    def safety_block_to_no_intervention_reason(
        block_reasons: list[SafetyBlockReason],
    ) -> NoInterventionReason:
        """Map safety block reasons to a NoInterventionReason.

        Multiple block reasons → SAFETY_BLOCKED (the primary code).
        Specific single reasons get more specific codes.
        """
        if not block_reasons:
            return NoInterventionReason.SAFETY_BLOCKED

        # If the only reason is unknown state, it's a different category
        if block_reasons == [SafetyBlockReason.UNKNOWN_SAFETY_STATE]:
            return NoInterventionReason.INSUFFICIENT_CONFIDENCE

        if block_reasons == [SafetyBlockReason.SAFETY_DEPENDENCY_UNAVAILABLE]:
            return NoInterventionReason.SYSTEM_FAILURE

        return NoInterventionReason.SAFETY_BLOCKED

    @staticmethod
    def is_conversion_oriented(action_id: ActionId) -> bool:
        """Return True if an action is conversion-oriented.

        NO_INTERVENTION and OFFER_DEFER are NOT conversion-oriented.
        All other actions potentially encourage bet completion.
        """
        return action_id not in (ActionId.NO_INTERVENTION, ActionId.OFFER_DEFER)
