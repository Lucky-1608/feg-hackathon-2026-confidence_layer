"""Tests for the Action Registry.

Verifies:
- All 6 initial actions are registered
- NO_INTERVENTION is always available
- Action eligibility filtering works correctly
- The registry rejects construction without NO_INTERVENTION
- State/data requirements are enforced
"""

from __future__ import annotations

import pytest

from confidence.domain.actions import ActionDefinition, ActionRegistry
from confidence.domain.enums import ActionCategory, ActionId, UncertaintyState


class TestActionRegistryConstruction:
    def test_default_registry_has_six_actions(
        self, action_registry: ActionRegistry
    ) -> None:
        actions = action_registry.all_action_ids()
        assert len(actions) == 6
        assert ActionId.NO_INTERVENTION in actions
        assert ActionId.EXPLAIN_MARKET in actions
        assert ActionId.EXPLAIN_ODDS_CHANGE in actions
        assert ActionId.VERIFY_SELECTIONS in actions
        assert ActionId.SHOW_STAKE_RETURN in actions
        assert ActionId.OFFER_DEFER in actions

    def test_rejects_registry_without_no_intervention(self) -> None:
        with pytest.raises(ValueError, match="NO_INTERVENTION"):
            ActionRegistry(
                actions={
                    ActionId.EXPLAIN_MARKET: ActionDefinition(
                        action_id=ActionId.EXPLAIN_MARKET,
                        category=ActionCategory.INFORMATIONAL,
                        allowed_states=[UncertaintyState.MARKET_MEANING],
                    ),
                }
            )

    def test_no_intervention_is_always_registered(
        self, action_registry: ActionRegistry
    ) -> None:
        assert action_registry.is_registered(ActionId.NO_INTERVENTION)


class TestActionRegistryLookup:
    def test_get_existing_action(self, action_registry: ActionRegistry) -> None:
        action = action_registry.get(ActionId.EXPLAIN_ODDS_CHANGE)
        assert action is not None
        assert action.action_id == ActionId.EXPLAIN_ODDS_CHANGE
        assert action.category == ActionCategory.INFORMATIONAL

    def test_get_nonexistent_action(self, action_registry: ActionRegistry) -> None:
        # Use a valid enum value that might not be registered in a custom registry.
        # In the default registry all are present, so we test with a custom one.
        custom_registry = ActionRegistry(
            actions={
                ActionId.NO_INTERVENTION: ActionDefinition(
                    action_id=ActionId.NO_INTERVENTION,
                    category=ActionCategory.NO_ACTION,
                    allowed_states=list(UncertaintyState),
                ),
            }
        )
        assert custom_registry.get(ActionId.EXPLAIN_MARKET) is None

    def test_is_registered(self, action_registry: ActionRegistry) -> None:
        assert action_registry.is_registered(ActionId.OFFER_DEFER)


class TestActionEligibility:
    def test_no_intervention_eligible_for_all_states(
        self, action_registry: ActionRegistry
    ) -> None:
        """NO_INTERVENTION must be eligible for every possible state."""
        for state in UncertaintyState:
            eligible = action_registry.get_eligible_for_state(state, set())
            eligible_ids = [a.action_id for a in eligible]
            assert ActionId.NO_INTERVENTION in eligible_ids, (
                f"NO_INTERVENTION should be eligible for state {state}"
            )

    def test_explain_odds_eligible_when_odds_change(
        self, action_registry: ActionRegistry
    ) -> None:
        eligible = action_registry.get_eligible_for_state(
            UncertaintyState.ODDS_CHANGE,
            {"old_odds", "new_odds", "stake", "potential_return"},
        )
        eligible_ids = [a.action_id for a in eligible]
        assert ActionId.EXPLAIN_ODDS_CHANGE in eligible_ids

    def test_explain_odds_not_eligible_without_data(
        self, action_registry: ActionRegistry
    ) -> None:
        eligible = action_registry.get_eligible_for_state(
            UncertaintyState.ODDS_CHANGE,
            set(),  # No data available
        )
        eligible_ids = [a.action_id for a in eligible]
        assert ActionId.EXPLAIN_ODDS_CHANGE not in eligible_ids

    def test_no_conversion_actions_for_potential_harm(
        self, action_registry: ActionRegistry
    ) -> None:
        """When state is POTENTIAL_HARM, only NO_INTERVENTION should be eligible."""
        eligible = action_registry.get_eligible_for_state(
            UncertaintyState.POTENTIAL_HARM,
            {"old_odds", "new_odds", "stake", "potential_return",
             "market_name", "event_name", "market_definition",
             "selections_summary"},
        )
        eligible_ids = [a.action_id for a in eligible]
        # Only NO_INTERVENTION should be eligible
        assert eligible_ids == [ActionId.NO_INTERVENTION]

    def test_no_conversion_actions_for_legitimate_reconsideration(
        self, action_registry: ActionRegistry
    ) -> None:
        """When state is LEGITIMATE_RECONSIDERATION, only NO_INTERVENTION should be eligible."""
        eligible = action_registry.get_eligible_for_state(
            UncertaintyState.LEGITIMATE_RECONSIDERATION,
            {"old_odds", "new_odds", "stake", "potential_return",
             "market_name", "event_name", "market_definition",
             "selections_summary"},
        )
        eligible_ids = [a.action_id for a in eligible]
        assert eligible_ids == [ActionId.NO_INTERVENTION]

    def test_explain_market_eligible_for_market_meaning(
        self, action_registry: ActionRegistry
    ) -> None:
        eligible = action_registry.get_eligible_for_state(
            UncertaintyState.MARKET_MEANING,
            {"market_name", "event_name", "market_definition"},
        )
        eligible_ids = [a.action_id for a in eligible]
        assert ActionId.EXPLAIN_MARKET in eligible_ids

    def test_offer_defer_eligible_for_general_friction(
        self, action_registry: ActionRegistry
    ) -> None:
        eligible = action_registry.get_eligible_for_state(
            UncertaintyState.GENERAL_UI_FRICTION,
            set(),
        )
        eligible_ids = [a.action_id for a in eligible]
        assert ActionId.OFFER_DEFER in eligible_ids

    def test_disabled_action_not_eligible(self) -> None:
        """Disabled actions should not appear in eligible lists."""
        registry = ActionRegistry(
            actions={
                ActionId.NO_INTERVENTION: ActionDefinition(
                    action_id=ActionId.NO_INTERVENTION,
                    category=ActionCategory.NO_ACTION,
                    allowed_states=list(UncertaintyState),
                    enabled=True,
                ),
                ActionId.EXPLAIN_MARKET: ActionDefinition(
                    action_id=ActionId.EXPLAIN_MARKET,
                    category=ActionCategory.INFORMATIONAL,
                    allowed_states=[UncertaintyState.MARKET_MEANING],
                    enabled=False,  # Disabled
                ),
            }
        )
        eligible = registry.get_eligible_for_state(
            UncertaintyState.MARKET_MEANING,
            {"market_name", "event_name", "market_definition"},
        )
        eligible_ids = [a.action_id for a in eligible]
        assert ActionId.EXPLAIN_MARKET not in eligible_ids


class TestActionDefinitions:
    def test_all_actions_have_versions(
        self, action_registry: ActionRegistry
    ) -> None:
        for action_id in action_registry.all_action_ids():
            action = action_registry.get(action_id)
            assert action is not None
            assert action.version, f"Action {action_id} missing version"

    def test_no_intervention_has_no_requirements(
        self, action_registry: ActionRegistry
    ) -> None:
        action = action_registry.get(ActionId.NO_INTERVENTION)
        assert action is not None
        assert action.required_data == []
        assert action.prohibited_states == []

    def test_informational_actions_have_templates(
        self, action_registry: ActionRegistry
    ) -> None:
        for action_id in [
            ActionId.EXPLAIN_MARKET,
            ActionId.EXPLAIN_ODDS_CHANGE,
            ActionId.SHOW_STAKE_RETURN,
        ]:
            action = action_registry.get(action_id)
            assert action is not None
            assert action.copy_template is not None, (
                f"Action {action_id} missing copy_template"
            )
