# DecisionRequest

> God node · 28 connections · `src/confidence/application/context_builder.py`

**Community:** [Decision Engine & API Models](Decision_Engine_&_API_Models.md)

## Connections by Relation

### calls
- base_request() `EXTRACTED`

### contains
- context_builder.py `EXTRACTED`

### imports
- engine.py `EXTRACTED`
- routes.py `EXTRACTED`

### inherits
- BaseModel `EXTRACTED`

### rationale_for
- The incoming API request for a decision. `EXTRACTED`

### references
- .build() `EXTRACTED`
- ._build_failure_decision() `EXTRACTED`
- .decide() `EXTRACTED`
- ._execute_pipeline() `EXTRACTED`
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
- [DecisionEngine](DecisionEngine.md) `INFERRED`
- TestEndToEndScenarios `INFERRED`
- TestPropertyInvariants `INFERRED`
- TestAdversarialAndFailures `INFERRED`
- create_decision() `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*