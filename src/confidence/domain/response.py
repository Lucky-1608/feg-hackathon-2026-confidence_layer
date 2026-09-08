"""Response Generator.

Deterministically formats the final response using approved action templates.
"""

from __future__ import annotations

from confidence.domain.actions import ActionRegistry
from confidence.domain.enums import ActionId
from confidence.domain.models import DecisionContext


class ResponseGenerator:
    """Generates the safe response string."""

    def __init__(self, action_registry: ActionRegistry) -> None:
        self.action_registry = action_registry

    def generate(self, selected_action: ActionId, context: DecisionContext) -> str | None:
        """Generate response based on the selected action and available context."""

        if selected_action == ActionId.NO_INTERVENTION:
            return None

        action_def = self.action_registry.get(selected_action)
        if not action_def or not action_def.copy_template:
            return None

        # Build variables dict from context for template substitution
        variables: dict[str, str] = {}

        if context.slip and context.slip.selections:
            # We just take the first selection for simple templates
            selection = context.slip.selections[0]
            variables["market_name"] = selection.market_name or "this market"
            variables["event_name"] = selection.event_name or "this event"

            if selection.odds_history and len(selection.odds_history) > 0:
                variables["old_odds"] = str(selection.odds_history[0].odds)
            variables["new_odds"] = str(selection.odds)

            # Find market context if available
            market = next((m for m in context.markets if m.market_id == selection.market_id), None)
            if market and market.market_definition:
                variables["market_definition"] = market.market_definition
            else:
                variables["market_definition"] = ""

        if context.slip.stake is not None:
            variables["stake"] = str(context.slip.stake)
        if context.slip.potential_return is not None:
            variables["potential_return"] = str(context.slip.potential_return)

        # Add summary of selections
        if context.slip and context.slip.selections:
            variables["selection_count"] = str(len(context.slip.selections))
            variables["selections_summary"] = f"{len(context.slip.selections)} selections"

        try:
            return action_def.copy_template.format(**variables)
        except Exception:
            # If template substitution fails, fail closed (return None)
            return None
