"""Policy Authority.

Selects the best action from a set of safe and eligible candidate actions.
Phase 2 implementation uses explicit deterministic prioritization.
"""

from __future__ import annotations

from confidence.domain.actions import ActionDefinition
from confidence.domain.enums import ActionCategory, ActionId, UncertaintyState
from confidence.domain.models import DecisionContext, StateEstimate


class PolicySelector:
    """Deterministic policy selector.

    Selects an action based on explicit prioritization:
    1. Exact informational action matching the state
    2. Any other informational action
    3. Verification action
    4. Deferral action (OFFER_DEFER)
    5. NO_INTERVENTION
    """

    VERSION = "policy-v1"

    def __init__(self) -> None:
        self.state_to_preferred_action = {
            UncertaintyState.MARKET_MEANING: ActionId.EXPLAIN_MARKET,
            UncertaintyState.ODDS_CHANGE: ActionId.EXPLAIN_ODDS_CHANGE,
            UncertaintyState.SLIP_CONFIGURATION: ActionId.VERIFY_SELECTIONS,
            UncertaintyState.STAKE_RETURN: ActionId.SHOW_STAKE_RETURN,
            UncertaintyState.GENERAL_UI_FRICTION: ActionId.OFFER_DEFER,
        }

    def select_action(
        self,
        context: DecisionContext,
        state_estimate: StateEstimate,
        eligible_actions: list[ActionDefinition],
    ) -> ActionId:
        """Select the best action from the eligible set."""

        if not eligible_actions:
            return ActionId.NO_INTERVENTION

        eligible_ids = {action.action_id for action in eligible_actions}

        # 1. NO_INTERVENTION if it's the only one
        if len(eligible_ids) == 1 and ActionId.NO_INTERVENTION in eligible_ids:
            return ActionId.NO_INTERVENTION

        # 2. Exact match for state
        preferred_action = self.state_to_preferred_action.get(state_estimate.state)
        if preferred_action and preferred_action in eligible_ids:
            return preferred_action

        # 3. Informational actions (less intrusive)
        informational = [a.action_id for a in eligible_actions if a.category == ActionCategory.INFORMATIONAL]
        if informational:
            # Pick first available to be deterministic
            return sorted(informational)[0]

        # 4. Deferral action
        if ActionId.OFFER_DEFER in eligible_ids:
            return ActionId.OFFER_DEFER

        # 5. Fallback
        return ActionId.NO_INTERVENTION
