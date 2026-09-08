"""Versioned Action Registry for the Confidence Layer.

The Action Registry is the single source of truth for what actions
the Policy Authority can select. The policy can ONLY select registered
actions (invariant S9).

The registry is loaded into memory at startup. It does NOT depend on
the database for the critical decision path.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from confidence.domain.enums import ActionCategory, ActionId, UncertaintyState

# Registry version — increment when actions change.
ACTION_REGISTRY_VERSION = "1"


class ActionDefinition(BaseModel):
    """Definition of a single registered action.

    Each action declares:
    - which uncertainty states it is allowed in
    - what data it requires to execute
    - which states prohibit it
    - a copy template for response generation
    """

    action_id: ActionId
    category: ActionCategory
    allowed_states: list[UncertaintyState]
    required_data: list[str] = Field(default_factory=list)
    prohibited_states: list[UncertaintyState] = Field(default_factory=list)
    copy_template: str | None = None
    enabled: bool = True
    version: str = "1"


# All possible uncertainty states, for actions that are universally allowed.
_ALL_STATES = list(UncertaintyState)


class ActionRegistry:
    """In-memory registry of all valid actions.

    Invariants enforced:
    - S9: Policy can select only registered actions.
    - NO_INTERVENTION is always registered and always eligible.
    """

    def __init__(self, actions: dict[ActionId, ActionDefinition] | None = None) -> None:
        self._actions: dict[ActionId, ActionDefinition] = actions or dict(
            _DEFAULT_ACTIONS
        )
        # NO_INTERVENTION must always be present.
        if ActionId.NO_INTERVENTION not in self._actions:
            raise ValueError("NO_INTERVENTION must be registered in the action registry")
        self._version = ACTION_REGISTRY_VERSION

    @property
    def version(self) -> str:
        return self._version

    def get(self, action_id: ActionId) -> ActionDefinition | None:
        """Get an action definition by ID."""
        return self._actions.get(action_id)

    def is_registered(self, action_id: ActionId) -> bool:
        """Check if an action is registered (invariant S9)."""
        return action_id in self._actions

    def get_enabled_actions(self) -> list[ActionDefinition]:
        """Return all currently enabled actions."""
        return [a for a in self._actions.values() if a.enabled]

    def get_eligible_for_state(
        self,
        state: UncertaintyState,
        available_data: set[str],
    ) -> list[ActionDefinition]:
        """Return actions eligible for a given state and available data.

        An action is eligible if:
        1. It is enabled.
        2. The state is in its allowed_states.
        3. The state is NOT in its prohibited_states.
        4. All required_data is available.
        """
        eligible: list[ActionDefinition] = []
        for action in self._actions.values():
            if not action.enabled:
                continue
            if state in action.prohibited_states:
                continue
            if state not in action.allowed_states:
                continue
            if not set(action.required_data).issubset(available_data):
                continue
            eligible.append(action)
        return eligible

    def all_action_ids(self) -> list[ActionId]:
        """Return all registered action IDs."""
        return list(self._actions.keys())


# --- Default Action Definitions ---

_DEFAULT_ACTIONS: list[tuple[ActionId, ActionDefinition]] = [
    (
        ActionId.NO_INTERVENTION,
        ActionDefinition(
            action_id=ActionId.NO_INTERVENTION,
            category=ActionCategory.NO_ACTION,
            allowed_states=_ALL_STATES,
            required_data=[],
            prohibited_states=[],
            copy_template=None,
            enabled=True,
        ),
    ),
    (
        ActionId.EXPLAIN_MARKET,
        ActionDefinition(
            action_id=ActionId.EXPLAIN_MARKET,
            category=ActionCategory.INFORMATIONAL,
            allowed_states=[UncertaintyState.MARKET_MEANING],
            required_data=["market_name", "event_name", "market_definition"],
            prohibited_states=[
                UncertaintyState.POTENTIAL_HARM,
                UncertaintyState.LEGITIMATE_RECONSIDERATION,
            ],
            copy_template=(
                "This is a {market_name} market for {event_name}. "
                "{market_definition}"
            ),
            enabled=True,
        ),
    ),
    (
        ActionId.EXPLAIN_ODDS_CHANGE,
        ActionDefinition(
            action_id=ActionId.EXPLAIN_ODDS_CHANGE,
            category=ActionCategory.INFORMATIONAL,
            allowed_states=[UncertaintyState.ODDS_CHANGE],
            required_data=["old_odds", "new_odds", "stake", "potential_return"],
            prohibited_states=[
                UncertaintyState.POTENTIAL_HARM,
                UncertaintyState.LEGITIMATE_RECONSIDERATION,
            ],
            copy_template=(
                "Odds changed from {old_odds} to {new_odds} "
                "since you added this. "
                "At a {stake} stake, the current return is {potential_return}."
            ),
            enabled=True,
        ),
    ),
    (
        ActionId.VERIFY_SELECTIONS,
        ActionDefinition(
            action_id=ActionId.VERIFY_SELECTIONS,
            category=ActionCategory.VERIFICATION,
            allowed_states=[UncertaintyState.SLIP_CONFIGURATION],
            required_data=["selections_summary"],
            prohibited_states=[
                UncertaintyState.POTENTIAL_HARM,
                UncertaintyState.LEGITIMATE_RECONSIDERATION,
            ],
            copy_template="You have {selection_count} selections. {selections_summary}",
            enabled=True,
        ),
    ),
    (
        ActionId.SHOW_STAKE_RETURN,
        ActionDefinition(
            action_id=ActionId.SHOW_STAKE_RETURN,
            category=ActionCategory.INFORMATIONAL,
            allowed_states=[UncertaintyState.STAKE_RETURN],
            required_data=["stake", "potential_return"],
            prohibited_states=[
                UncertaintyState.POTENTIAL_HARM,
                UncertaintyState.LEGITIMATE_RECONSIDERATION,
            ],
            copy_template=(
                "At a {stake} stake, your potential return is {potential_return}."
            ),
            enabled=True,
        ),
    ),
    (
        ActionId.OFFER_DEFER,
        ActionDefinition(
            action_id=ActionId.OFFER_DEFER,
            category=ActionCategory.DEFERRAL,
            allowed_states=[
                UncertaintyState.MARKET_MEANING,
                UncertaintyState.ODDS_CHANGE,
                UncertaintyState.SLIP_CONFIGURATION,
                UncertaintyState.STAKE_RETURN,
                UncertaintyState.GENERAL_UI_FRICTION,
                UncertaintyState.DISTRACTION,
            ],
            required_data=[],
            prohibited_states=[
                UncertaintyState.POTENTIAL_HARM,
                UncertaintyState.LEGITIMATE_RECONSIDERATION,
            ],
            copy_template="You can save this bet slip and come back to it later.",
            enabled=True,
        ),
    ),
]
