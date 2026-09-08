# Action Registry & Definitions

> 59 nodes · cohesion 0.06

## Key Concepts

- **ActionRegistry** (56 connections) — `src/confidence/domain/actions.py`
- **ActionId** (43 connections) — `src/confidence/domain/enums.py`
- **ActionDefinition** (20 connections) — `src/confidence/domain/actions.py`
- **ResponseGenerator** (17 connections) — `src/confidence/domain/response.py`
- **TestActionEligibility** (14 connections) — `tests/test_actions.py`
- **TestActionRegistryConstruction** (9 connections) — `tests/test_actions.py`
- **TestActionRegistryLookup** (9 connections) — `tests/test_actions.py`
- **TestResponseGenerator** (7 connections) — `tests/test_engine.py`
- **.select_action()** (6 connections) — `src/confidence/domain/policy.py`
- **TestActionDefinitions** (6 connections) — `tests/test_actions.py`
- **.test_generates_odds_change_response()** (5 connections) — `tests/test_engine.py`
- **.get()** (4 connections) — `src/confidence/domain/actions.py`
- **.get_eligible_for_state()** (4 connections) — `src/confidence/domain/actions.py`
- **.generate()** (4 connections) — `src/confidence/domain/response.py`
- **.test_disabled_action_not_eligible()** (4 connections) — `tests/test_actions.py`
- **.test_missing_template_data_fails_closed()** (4 connections) — `tests/test_engine.py`
- **.test_no_intervention_yields_no_response()** (4 connections) — `tests/test_engine.py`
- **get_response_generator()** (3 connections) — `src/confidence/api/dependencies.py`
- **.all_action_ids()** (3 connections) — `src/confidence/domain/actions.py`
- **.get_enabled_actions()** (3 connections) — `src/confidence/domain/actions.py`
- **.__init__()** (3 connections) — `src/confidence/domain/actions.py`
- **.is_registered()** (3 connections) — `src/confidence/domain/actions.py`
- **.test_no_conversion_actions_for_legitimate_reconsideration()** (3 connections) — `tests/test_actions.py`
- **.test_no_conversion_actions_for_potential_harm()** (3 connections) — `tests/test_actions.py`
- **.test_no_intervention_eligible_for_all_states()** (3 connections) — `tests/test_actions.py`
- *... and 34 more nodes in this community*

## Relationships

- [Application Engine & Domain Models](Application_Engine_&_Domain_Models.md) (39 shared connections)
- [API Dependencies & Context Providers](API_Dependencies_&_Context_Providers.md) (17 shared connections)
- [Decision Engine & API Models](Decision_Engine_&_API_Models.md) (12 shared connections)
- [Safety Authority & Invariants](Safety_Authority_&_Invariants.md) (8 shared connections)
- [Market Context & Harm Indicators](Market_Context_&_Harm_Indicators.md) (2 shared connections)
- [Conversion Safety Rules](Conversion_Safety_Rules.md) (2 shared connections)
- [Domain Model & Safety Tests](Domain_Model_&_Safety_Tests.md) (1 shared connections)

## Source Files

- `src/confidence/api/dependencies.py`
- `src/confidence/domain/actions.py`
- `src/confidence/domain/enums.py`
- `src/confidence/domain/policy.py`
- `src/confidence/domain/response.py`
- `tests/test_actions.py`
- `tests/test_engine.py`

## Audit Trail

- EXTRACTED: 133 (71%)
- INFERRED: 54 (29%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*