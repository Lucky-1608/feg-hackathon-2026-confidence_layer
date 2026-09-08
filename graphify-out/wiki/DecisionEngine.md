# DecisionEngine

> God node · 38 connections · `src/confidence/application/engine.py`

**Community:** [Decision Engine & API Models](Decision_Engine_&_API_Models.md)

## Connections by Relation

### calls
- engine() `EXTRACTED`
- get_decision_engine() `EXTRACTED`

### contains
- engine.py `EXTRACTED`

### imports
- dependencies.py `EXTRACTED`
- routes.py `EXTRACTED`

### method
- .__init__() `EXTRACTED`
- ._build_failure_decision() `EXTRACTED`
- .decide() `EXTRACTED`
- ._execute_pipeline() `EXTRACTED`

### rationale_for
- Central orchestrator for the Confidence Layer. `EXTRACTED`

### references
- .test_blocked_safety_context_always_yields_no_intervention() `EXTRACTED`
- .test_required_data_must_be_present() `EXTRACTED`
- .test_selected_actions_are_registered() `EXTRACTED`
- .test_adversarial_policy_bypass_caught_by_final_check() `EXTRACTED`
- .test_timeout_enforcement() `EXTRACTED`
- .test_scenario_a_odds_uncertainty() `EXTRACTED`
- .test_scenario_b_market_uncertainty() `EXTRACTED`
- .test_scenario_c_legitimate_reconsideration() `EXTRACTED`
- .test_scenario_d_potential_harm() `EXTRACTED`
- .test_scenario_e_self_exclusion() `EXTRACTED`
- .test_scenario_f_missing_authoritative_odds() `EXTRACTED`
- .test_scenario_g_low_confidence() `EXTRACTED`
- .test_scenario_h_safety_dependency_failure() `EXTRACTED`

### uses
- [SafetyContract](SafetyContract.md) `INFERRED`
- [ActionRegistry](ActionRegistry.md) `INFERRED`
- [ActionId](ActionId.md) `INFERRED`
- [UncertaintyState](UncertaintyState.md) `INFERRED`
- [DecisionRequest](DecisionRequest.md) `INFERRED`
- [NoInterventionReason](NoInterventionReason.md) `INFERRED`
- SafetyStatus `INFERRED`
- PolicySelector `INFERRED`
- TestEndToEndScenarios `INFERRED`
- ResponseGenerator `INFERRED`
- StateEstimator `INFERRED`
- ContextBuilder `INFERRED`
- TestPropertyInvariants `INFERRED`
- TestAdversarialAndFailures `INFERRED`
- create_decision() `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*