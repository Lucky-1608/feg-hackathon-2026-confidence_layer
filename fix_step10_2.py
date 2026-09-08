import re

with open("src/confidence/domain/safety.py", "r") as f:
    safety = f.read()

# Update final_safety_check
safety = safety.replace(
    "    def final_safety_check(\n        self,\n        selected_action: ActionId,\n        safety_result: SafetyResult,\n        state_estimate: StateEstimate,\n    ) -> NoInterventionReason | None:",
    "    def final_safety_check(\n        self,\n        selected_action: ActionId,\n        safety_result: SafetyResult,\n        state_estimate: StateEstimate,\n        action_definition: 'ActionDefinition | None' = None,\n    ) -> NoInterventionReason | None:"
)

# And update the logic inside final_safety_check to use safety_class if available
safety = safety.replace(
    "        # S3: Harmful state → no conversion-oriented intervention\n        if state_estimate.state == UncertaintyState.POTENTIAL_HARM and selected_action != ActionId.NO_INTERVENTION:\n            return NoInterventionReason.SAFETY_BLOCKED",
    "        # S3: Harmful state → no conversion-oriented intervention\n        from confidence.domain.enums import SafetyClass\n        is_conversion = action_definition.safety_class == SafetyClass.CONVERSION_ORIENTED if action_definition else selected_action not in (ActionId.NO_INTERVENTION, ActionId.OFFER_DEFER)\n        if state_estimate.state == UncertaintyState.POTENTIAL_HARM and is_conversion:\n            return NoInterventionReason.SAFETY_BLOCKED"
)

with open("src/confidence/domain/safety.py", "w") as f:
    f.write(safety)

with open("src/confidence/application/engine.py", "r") as f:
    engine = f.read()

# update engine.py to pass action_definition to final_safety_check
engine = engine.replace(
    "        final_block = self.safety_contract.final_safety_check(\n            selected_action_id, safety_result, state_estimate\n        )",
    "        final_block = self.safety_contract.final_safety_check(\n            selected_action_id, safety_result, state_estimate, action_def\n        )"
)

with open("src/confidence/application/engine.py", "w") as f:
    f.write(engine)

print("Step 10 part 2 applied.")
