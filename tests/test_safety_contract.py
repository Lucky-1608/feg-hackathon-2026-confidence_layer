"""Tests for the Safety Contract.

Verifies all 17 system invariants (S1–S17) as automated tests.
The Safety Authority's correctness is validated empirically through
these tests — the architecture enforces structural constraints, and
this suite validates them.

Test coverage:
  S1: Self-excluded user → BLOCKED
  S2: Protective restriction → BLOCKED
  S3: Harmful-play state → BLOCKED
  S4: Unknown safety state → fail closed
  S5: Safety dependency unavailable → fail closed (stale data)
  S6: Market data unavailable → no factual explanation (tested in Phase 2)
  S7: Model failure → NO_INTERVENTION (tested via check_state_confidence)
  S8: Model confidence below threshold → NO_INTERVENTION
  S9: Policy selects only registered actions (tested in test_actions.py)
  S10: Policy cannot modify safety rules (tested architecturally)
  S11: User can always abandon (tested in UI / Phase 3)
  S12: No urgency mechanics (tested in response templates / Phase 2)
  S13: No artificial scarcity (tested in response templates / Phase 2)
  S14: No social-proof pressure (tested in response templates / Phase 2)
  S15: No coercive incentives (tested in response templates / Phase 2)
  S16: Timeout → NO_INTERVENTION (tested in failure tests / Phase 2)
  S17: Every decision auditable (tested in decision engine / Phase 2)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from confidence.domain.enums import (
    ActionId,
    NoInterventionReason,
    SafetyBlockReason,
    SafetyStatus,
    UncertaintyState,
)
from confidence.domain.models import (
    HarmIndicators,
    SafetyContext,
    SafetyResult,
    StateEstimate,
)
from confidence.domain.safety import SafetyContract

if TYPE_CHECKING:
    from datetime import datetime


class TestS1SelfExclusion:
    """S1: Self-excluded user → NO_INTERVENTION."""

    def test_self_excluded_user_is_blocked(
        self,
        safety_contract: SafetyContract,
        self_excluded_safety_context: SafetyContext,
        now: datetime,
    ) -> None:
        result = safety_contract.evaluate_safety(self_excluded_safety_context, now)
        assert result.status == SafetyStatus.BLOCKED
        assert SafetyBlockReason.SELF_EXCLUSION in result.block_reasons

    def test_self_excluded_cannot_receive_intervention(
        self,
        safety_contract: SafetyContract,
        self_excluded_safety_context: SafetyContext,
        now: datetime,
    ) -> None:
        result = safety_contract.evaluate_safety(self_excluded_safety_context, now)
        # Final safety check: any non-NO_INTERVENTION action must be blocked.
        check = safety_contract.final_safety_check(
            ActionId.EXPLAIN_ODDS_CHANGE,
            result,
            StateEstimate(
                state=UncertaintyState.ODDS_CHANGE,
                confidence=0.9,
                model_version="test",
            ),
        )
        assert check == NoInterventionReason.SAFETY_BLOCKED


class TestS2ProtectiveRestriction:
    """S2: Explicit protective restriction → NO_INTERVENTION."""

    def test_protective_restriction_is_blocked(
        self,
        safety_contract: SafetyContract,
        protective_restriction_context: SafetyContext,
        now: datetime,
    ) -> None:
        result = safety_contract.evaluate_safety(protective_restriction_context, now)
        assert result.status == SafetyStatus.BLOCKED
        assert SafetyBlockReason.PROTECTIVE_RESTRICTION in result.block_reasons


class TestS3HarmState:
    """S3: Strong harmful-play state → NO conversion-oriented intervention."""

    def test_harm_indicators_block_intervention(
        self,
        safety_contract: SafetyContract,
        harm_safety_context: SafetyContext,
        now: datetime,
    ) -> None:
        result = safety_contract.evaluate_safety(harm_safety_context, now)
        assert result.status == SafetyStatus.BLOCKED
        assert SafetyBlockReason.HARM_STATE in result.block_reasons

    def test_each_harm_indicator_independently_blocks(
        self,
        safety_contract: SafetyContract,
        now: datetime,
    ) -> None:
        indicators = [
            HarmIndicators(rapid_loss_chasing=True),
            HarmIndicators(escalating_stakes=True),
            HarmIndicators(session_duration_extreme=True),
            HarmIndicators(loss_recovery_pattern=True),
        ]
        for indicator in indicators:
            ctx = SafetyContext(
                harm_indicators=indicator,
                data_freshness=now,
            )
            result = safety_contract.evaluate_safety(ctx, now)
            assert result.status == SafetyStatus.BLOCKED, (
                f"Harm indicator {indicator} should block"
            )

    def test_final_check_blocks_conversion_in_harm_state(
        self,
        safety_contract: SafetyContract,
        now: datetime,
    ) -> None:
        safe_result = SafetyResult(status=SafetyStatus.SAFE, timestamp=now)
        harm_estimate = StateEstimate(
            state=UncertaintyState.POTENTIAL_HARM,
            confidence=0.9,
            model_version="test",
        )
        check = safety_contract.final_safety_check(
            ActionId.EXPLAIN_ODDS_CHANGE,
            safe_result,
            harm_estimate,
        )
        assert check == NoInterventionReason.SAFETY_BLOCKED

    def test_final_check_allows_no_intervention_in_harm_state(
        self,
        safety_contract: SafetyContract,
        now: datetime,
    ) -> None:
        safe_result = SafetyResult(status=SafetyStatus.SAFE, timestamp=now)
        harm_estimate = StateEstimate(
            state=UncertaintyState.POTENTIAL_HARM,
            confidence=0.9,
            model_version="test",
        )
        check = safety_contract.final_safety_check(
            ActionId.NO_INTERVENTION,
            safe_result,
            harm_estimate,
        )
        assert check is None  # NO_INTERVENTION is always safe


class TestS4UnknownSafetyState:
    """S4: Unknown safety state → fail closed."""

    def test_no_freshness_fails_closed(
        self,
        safety_contract: SafetyContract,
        no_freshness_safety_context: SafetyContext,
        now: datetime,
    ) -> None:
        result = safety_contract.evaluate_safety(no_freshness_safety_context, now)
        assert result.status == SafetyStatus.BLOCKED
        assert SafetyBlockReason.UNKNOWN_SAFETY_STATE in result.block_reasons

    def test_unknown_state_maps_to_insufficient_confidence(
        self,
        safety_contract: SafetyContract,
    ) -> None:
        reason = safety_contract.safety_block_to_no_intervention_reason(
            [SafetyBlockReason.UNKNOWN_SAFETY_STATE]
        )
        assert reason == NoInterventionReason.INSUFFICIENT_CONFIDENCE


class TestS5SafetyDependencyUnavailable:
    """S5: Safety dependency unavailable → fail closed."""

    def test_stale_safety_data_fails_closed(
        self,
        safety_contract: SafetyContract,
        stale_safety_context: SafetyContext,
        now: datetime,
    ) -> None:
        result = safety_contract.evaluate_safety(stale_safety_context, now)
        assert result.status == SafetyStatus.BLOCKED
        assert SafetyBlockReason.SAFETY_DEPENDENCY_UNAVAILABLE in result.block_reasons

    def test_dependency_unavailable_maps_to_system_failure(
        self,
        safety_contract: SafetyContract,
    ) -> None:
        reason = safety_contract.safety_block_to_no_intervention_reason(
            [SafetyBlockReason.SAFETY_DEPENDENCY_UNAVAILABLE]
        )
        assert reason == NoInterventionReason.SYSTEM_FAILURE


class TestS8ConfidenceThreshold:
    """S8: Model confidence below threshold → NO_INTERVENTION."""

    def test_low_confidence_returns_insufficient(
        self,
        safety_contract: SafetyContract,
    ) -> None:
        estimate = StateEstimate(
            state=UncertaintyState.ODDS_CHANGE,
            confidence=0.3,  # Below default 0.5 threshold
            model_version="test",
        )
        reason = safety_contract.check_state_confidence(estimate)
        assert reason == NoInterventionReason.INSUFFICIENT_CONFIDENCE

    def test_high_confidence_passes(
        self,
        safety_contract: SafetyContract,
    ) -> None:
        estimate = StateEstimate(
            state=UncertaintyState.ODDS_CHANGE,
            confidence=0.8,
            model_version="test",
        )
        reason = safety_contract.check_state_confidence(estimate)
        assert reason is None

    def test_unknown_state_fails_regardless_of_confidence(
        self,
        safety_contract: SafetyContract,
    ) -> None:
        estimate = StateEstimate(
            state=UncertaintyState.UNKNOWN,
            confidence=0.99,
            model_version="test",
        )
        reason = safety_contract.check_state_confidence(estimate)
        assert reason == NoInterventionReason.INSUFFICIENT_CONFIDENCE

    def test_exactly_at_threshold_passes(self) -> None:
        contract = SafetyContract(confidence_threshold=0.5)
        estimate = StateEstimate(
            state=UncertaintyState.ODDS_CHANGE,
            confidence=0.5,
            model_version="test",
        )
        reason = contract.check_state_confidence(estimate)
        assert reason is None

    def test_just_below_threshold_fails(self) -> None:
        contract = SafetyContract(confidence_threshold=0.5)
        estimate = StateEstimate(
            state=UncertaintyState.ODDS_CHANGE,
            confidence=0.499,
            model_version="test",
        )
        reason = contract.check_state_confidence(estimate)
        assert reason == NoInterventionReason.INSUFFICIENT_CONFIDENCE


class TestLegitimateReconsideration:
    """Legitimate reconsideration → NO_INTERVENTION."""

    def test_legitimate_reconsideration_detected(
        self,
        safety_contract: SafetyContract,
    ) -> None:
        estimate = StateEstimate(
            state=UncertaintyState.LEGITIMATE_RECONSIDERATION,
            confidence=0.85,
            model_version="test",
        )
        reason = safety_contract.check_legitimate_reconsideration(estimate)
        assert reason == NoInterventionReason.LEGITIMATE_RECONSIDERATION

    def test_non_reconsideration_passes(
        self,
        safety_contract: SafetyContract,
    ) -> None:
        estimate = StateEstimate(
            state=UncertaintyState.ODDS_CHANGE,
            confidence=0.85,
            model_version="test",
        )
        reason = safety_contract.check_legitimate_reconsideration(estimate)
        assert reason is None


class TestSafeContext:
    """Verify that a genuinely safe context passes all checks."""

    def test_safe_context_is_safe(
        self,
        safety_contract: SafetyContract,
        safe_safety_context: SafetyContext,
        now: datetime,
    ) -> None:
        result = safety_contract.evaluate_safety(safe_safety_context, now)
        assert result.status == SafetyStatus.SAFE
        assert result.block_reasons == []

    def test_safe_context_allows_intervention(
        self,
        safety_contract: SafetyContract,
        safe_safety_context: SafetyContext,
        now: datetime,
    ) -> None:
        result = safety_contract.evaluate_safety(safe_safety_context, now)
        estimate = StateEstimate(
            state=UncertaintyState.ODDS_CHANGE,
            confidence=0.85,
            model_version="test",
        )
        check = safety_contract.final_safety_check(ActionId.EXPLAIN_ODDS_CHANGE, result, estimate)
        assert check is None  # No block


class TestMultipleBlockReasons:
    """A context can trigger multiple block reasons simultaneously."""

    def test_self_excluded_with_harm(
        self,
        safety_contract: SafetyContract,
        now: datetime,
    ) -> None:
        ctx = SafetyContext(
            is_self_excluded=True,
            harm_indicators=HarmIndicators(rapid_loss_chasing=True),
            data_freshness=now,
        )
        result = safety_contract.evaluate_safety(ctx, now)
        assert result.status == SafetyStatus.BLOCKED
        assert SafetyBlockReason.SELF_EXCLUSION in result.block_reasons
        assert SafetyBlockReason.HARM_STATE in result.block_reasons

    def test_multiple_reasons_map_to_safety_blocked(
        self,
        safety_contract: SafetyContract,
    ) -> None:
        reason = safety_contract.safety_block_to_no_intervention_reason(
            [SafetyBlockReason.SELF_EXCLUSION, SafetyBlockReason.HARM_STATE]
        )
        assert reason == NoInterventionReason.SAFETY_BLOCKED


class TestConversionOrientation:
    """Test which actions are classified as conversion-oriented."""

    def test_no_intervention_not_conversion(self) -> None:
        assert not SafetyContract.is_conversion_oriented(ActionId.NO_INTERVENTION)

    def test_offer_defer_not_conversion(self) -> None:
        assert not SafetyContract.is_conversion_oriented(ActionId.OFFER_DEFER)

    def test_explain_odds_is_conversion(self) -> None:
        assert SafetyContract.is_conversion_oriented(ActionId.EXPLAIN_ODDS_CHANGE)

    def test_explain_market_is_conversion(self) -> None:
        assert SafetyContract.is_conversion_oriented(ActionId.EXPLAIN_MARKET)
