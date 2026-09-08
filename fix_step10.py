import re

# 1. Add SafetyClass to enums.py
with open("src/confidence/domain/enums.py", "r") as f:
    enums = f.read()

if "class SafetyClass(StrEnum):" not in enums:
    enums_addition = """
class SafetyClass(StrEnum):
    \"\"\"Safety classification of an action.\"\"\"
    CONVERSION_ORIENTED = "CONVERSION_ORIENTED"
    NEUTRAL = "NEUTRAL"
    PROTECTIVE = "PROTECTIVE"
"""
    enums = enums + enums_addition
    with open("src/confidence/domain/enums.py", "w") as f:
        f.write(enums)

# 2. Update actions.py to import SafetyClass and use it in ActionDefinition
with open("src/confidence/domain/actions.py", "r") as f:
    actions = f.read()

actions = actions.replace(
    "from confidence.domain.enums import ActionCategory, ActionId, UncertaintyState",
    "from confidence.domain.enums import ActionCategory, ActionId, UncertaintyState, SafetyClass"
)

if "safety_class: SafetyClass =" not in actions:
    actions = actions.replace(
        "    category: ActionCategory",
        "    category: ActionCategory\n    safety_class: SafetyClass = SafetyClass.NEUTRAL"
    )
    
    # Update default actions to explicitly set safety_class where needed
    actions = actions.replace(
        "            category=ActionCategory.NO_ACTION,\n            allowed_states=_ALL_STATES,",
        "            category=ActionCategory.NO_ACTION,\n            safety_class=SafetyClass.PROTECTIVE,\n            allowed_states=_ALL_STATES,"
    )
    actions = actions.replace(
        "            category=ActionCategory.INFORMATIONAL,\n            allowed_states=[UncertaintyState.MARKET_MEANING],",
        "            category=ActionCategory.INFORMATIONAL,\n            safety_class=SafetyClass.CONVERSION_ORIENTED,\n            allowed_states=[UncertaintyState.MARKET_MEANING],"
    )
    actions = actions.replace(
        "            category=ActionCategory.INFORMATIONAL,\n            allowed_states=[UncertaintyState.ODDS_CHANGE],",
        "            category=ActionCategory.INFORMATIONAL,\n            safety_class=SafetyClass.CONVERSION_ORIENTED,\n            allowed_states=[UncertaintyState.ODDS_CHANGE],"
    )
    actions = actions.replace(
        "            category=ActionCategory.VERIFICATION,\n            allowed_states=[UncertaintyState.SLIP_CONFIGURATION],",
        "            category=ActionCategory.VERIFICATION,\n            safety_class=SafetyClass.CONVERSION_ORIENTED,\n            allowed_states=[UncertaintyState.SLIP_CONFIGURATION],"
    )
    actions = actions.replace(
        "            category=ActionCategory.INFORMATIONAL,\n            allowed_states=[UncertaintyState.STAKE_RETURN],",
        "            category=ActionCategory.INFORMATIONAL,\n            safety_class=SafetyClass.CONVERSION_ORIENTED,\n            allowed_states=[UncertaintyState.STAKE_RETURN],"
    )
    actions = actions.replace(
        "            category=ActionCategory.DEFERRAL,\n            allowed_states=[",
        "            category=ActionCategory.DEFERRAL,\n            safety_class=SafetyClass.NEUTRAL,\n            allowed_states=["
    )

    with open("src/confidence/domain/actions.py", "w") as f:
        f.write(actions)

print("Step 10 action updates applied.")
