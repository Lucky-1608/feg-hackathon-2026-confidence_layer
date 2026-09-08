# ActionRegistry

> God node · 56 connections · `src/confidence/domain/actions.py`

**Community:** [Action Registry & Definitions](Action_Registry_&_Definitions.md)

## Connections by Relation

### calls
- .test_selects_exact_match() `EXTRACTED`
- .test_selects_no_intervention_when_only_option() `EXTRACTED`
- .test_generates_odds_change_response() `EXTRACTED`
- action_registry() `EXTRACTED`
- .test_disabled_action_not_eligible() `EXTRACTED`
- .test_missing_template_data_fails_closed() `EXTRACTED`
- .test_no_intervention_yields_no_response() `EXTRACTED`
- .test_rejects_registry_without_no_intervention() `EXTRACTED`
- .test_get_nonexistent_action() `EXTRACTED`
- .test_prohibited_copy() `EXTRACTED`
- get_action_registry() `EXTRACTED`
- .test_registry_without_no_intervention_fails_fast() `EXTRACTED`

### contains
- actions.py `EXTRACTED`

### imports
- dependencies.py `EXTRACTED`
- domain/__init__.py `EXTRACTED`
- engine.py `EXTRACTED`
- response.py `EXTRACTED`

### method
- .get() `EXTRACTED`
- .get_eligible_for_state() `EXTRACTED`
- .all_action_ids() `EXTRACTED`
- .__init__() `EXTRACTED`
- .is_registered() `EXTRACTED`
- .get_enabled_actions() `EXTRACTED`
- .version() `EXTRACTED`

### rationale_for
- In-memory registry of all valid actions. Invariants enforced: - S9: Policy can… `EXTRACTED`

### references
- .__init__() `EXTRACTED`
- .test_no_conversion_actions_for_legitimate_reconsideration() `EXTRACTED`
- .test_no_conversion_actions_for_potential_harm() `EXTRACTED`
- .test_no_intervention_eligible_for_all_states() `EXTRACTED`
- .__init__() `EXTRACTED`
- .test_all_actions_have_versions() `EXTRACTED`
- .test_informational_actions_have_templates() `EXTRACTED`
- .test_no_intervention_has_no_requirements() `EXTRACTED`
- .test_explain_market_eligible_for_market_meaning() `EXTRACTED`
- .test_explain_odds_eligible_when_odds_change() `EXTRACTED`
- .test_explain_odds_not_eligible_without_data() `EXTRACTED`
- .test_offer_defer_eligible_for_general_friction() `EXTRACTED`
- .test_default_registry_has_six_actions() `EXTRACTED`
- .test_no_intervention_is_always_registered() `EXTRACTED`
- .test_get_existing_action() `EXTRACTED`
- .test_is_registered() `EXTRACTED`

### uses
- [ActionId](ActionId.md) `INFERRED`
- [DecisionEngine](DecisionEngine.md) `INFERRED`
- [UncertaintyState](UncertaintyState.md) `INFERRED`
- ResponseGenerator `INFERRED`
- TestActionEligibility `INFERRED`
- engine() `INFERRED`
- TestPropertyInvariants `INFERRED`
- get_decision_engine() `INFERRED`
- TestAdversarialAndFailures `INFERRED`
- TestActionRegistryConstruction `INFERRED`
- TestActionRegistryLookup `INFERRED`
- TestPolicySelector `INFERRED`
- TestResponseGenerator `INFERRED`
- TestActionDefinitions `INFERRED`
- get_response_generator() `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*