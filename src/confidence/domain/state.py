"""State Authority.

Classifies user uncertainty during betslip confirmation into a defined taxonomy.
Phase 2 implementation uses explicit, deterministic, testable rules rather than
machine learning.
"""

from __future__ import annotations

from confidence.domain.enums import UncertaintyState
from confidence.domain.models import DecisionContext, StateEstimate


class StateEstimator:
    """Deterministic rule-based state estimator.

    Evaluates the decision context and classifies the user's uncertainty.
    Enforces a strict priority to ensure informational signals do not
    override safety-relevant signals.

    Priority:
    1. POTENTIAL_HARM
    2. LEGITIMATE_RECONSIDERATION
    3. Specific Informational (ODDS_CHANGE, MARKET_MEANING, SLIP_CONFIGURATION, STAKE_RETURN)
    4. GENERAL_UI_FRICTION
    5. DISTRACTION
    6. NO_UNCERTAINTY
    7. UNKNOWN
    """

    VERSION = "rules-v1"

    def estimate_state(self, context: DecisionContext) -> StateEstimate:
        """Evaluate context and return the highest priority state estimate."""

        # 1. POTENTIAL_HARM
        if context.safety.harm_indicators.has_any():
            return StateEstimate(
                state=UncertaintyState.POTENTIAL_HARM,
                confidence=1.0,
                model_version=self.VERSION,
                features_used=["harm_indicators"],
            )

        # 2. LEGITIMATE_RECONSIDERATION
        # Defined as abandoning after viewing odds or making multiple selection changes
        # without placing the bet, perhaps changing stake significantly back and forth
        if context.interaction.recent_backtracks > 1 and context.interaction.dwell_time_seconds < 10.0:
            return StateEstimate(
                state=UncertaintyState.LEGITIMATE_RECONSIDERATION,
                confidence=0.8,
                model_version=self.VERSION,
                features_used=["recent_backtracks", "dwell_time_seconds"],
            )

        # 3. Specific Informational
        # ODDS_CHANGE
        if context.interaction.odds_changed and context.interaction.dwell_time_seconds >= 5.0:
            return StateEstimate(
                state=UncertaintyState.ODDS_CHANGE,
                confidence=0.9,
                model_version=self.VERSION,
                features_used=["odds_changed", "dwell_time_seconds"],
            )

        # MARKET_MEANING
        # Deduced if they dwell on the market selection a long time without stake changes
        if (
            context.interaction.dwell_time_seconds >= 15.0
            and context.interaction.stake_changes == 0
            and context.interaction.selection_changes == 0
        ):
            return StateEstimate(
                state=UncertaintyState.MARKET_MEANING,
                confidence=0.7,
                model_version=self.VERSION,
                features_used=["dwell_time_seconds", "stake_changes", "selection_changes"],
            )

        # SLIP_CONFIGURATION
        if context.interaction.selection_changes > 2:
            return StateEstimate(
                state=UncertaintyState.SLIP_CONFIGURATION,
                confidence=0.85,
                model_version=self.VERSION,
                features_used=["selection_changes"],
            )

        # STAKE_RETURN
        if context.interaction.stake_changes > 2:
            return StateEstimate(
                state=UncertaintyState.STAKE_RETURN,
                confidence=0.85,
                model_version=self.VERSION,
                features_used=["stake_changes"],
            )

        # 4. GENERAL_UI_FRICTION
        if context.interaction.confirmation_attempts > 1:
            return StateEstimate(
                state=UncertaintyState.GENERAL_UI_FRICTION,
                confidence=0.9,
                model_version=self.VERSION,
                features_used=["confirmation_attempts"],
            )

        # 5. DISTRACTION
        if context.interaction.session_age_seconds > 300.0 and context.interaction.dwell_time_seconds == 0.0:
            return StateEstimate(
                state=UncertaintyState.DISTRACTION,
                confidence=0.7,
                model_version=self.VERSION,
                features_used=["session_age_seconds", "dwell_time_seconds"],
            )

        # 6. NO_UNCERTAINTY
        if context.interaction.dwell_time_seconds < 2.0 and context.interaction.confirmation_attempts <= 1:
            return StateEstimate(
                state=UncertaintyState.NO_UNCERTAINTY,
                confidence=0.95,
                model_version=self.VERSION,
                features_used=["dwell_time_seconds", "confirmation_attempts"],
            )

        # 7. UNKNOWN
        return StateEstimate(
            state=UncertaintyState.UNKNOWN,
            confidence=1.0,
            model_version=self.VERSION,
            features_used=[],
        )
