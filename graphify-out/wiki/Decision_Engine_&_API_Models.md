# Decision Engine & API Models

> 52 nodes · cohesion 0.08

## Key Concepts

- **DecisionEngine** (38 connections) — `src/confidence/application/engine.py`
- **DecisionRequest** (28 connections) — `src/confidence/application/context_builder.py`
- **TestEndToEndScenarios** (18 connections) — `tests/test_engine.py`
- **asyncio** (15 connections)
- **TestPropertyInvariants** (13 connections) — `tests/test_engine.py`
- **InteractionContext** (11 connections) — `src/confidence/domain/models.py`
- **TestAdversarialAndFailures** (11 connections) — `tests/test_engine.py`
- **routes.py** (9 connections) — `src/confidence/api/routes.py`
- **DummySafetyProvider** (8 connections) — `src/confidence/api/dependencies.py`
- **api/models.py** (8 connections) — `src/confidence/api/models.py`
- **DecisionResponse** (8 connections) — `src/confidence/api/models.py`
- **create_decision()** (8 connections) — `src/confidence/api/routes.py`
- **._build_failure_decision()** (7 connections) — `src/confidence/application/engine.py`
- **.decide()** (6 connections) — `src/confidence/application/engine.py`
- **._execute_pipeline()** (6 connections) — `src/confidence/application/engine.py`
- **DecisionResult** (6 connections) — `src/confidence/application/engine.py`
- **.test_blocked_safety_context_always_yields_no_intervention()** (6 connections) — `tests/test_engine.py`
- **CreateDecisionRequest** (5 connections) — `src/confidence/api/models.py`
- **.test_required_data_must_be_present()** (5 connections) — `tests/test_engine.py`
- **.test_selected_actions_are_registered()** (5 connections) — `tests/test_engine.py`
- **base_request()** (4 connections) — `tests/test_engine.py`
- **.test_adversarial_policy_bypass_caught_by_final_check()** (4 connections) — `tests/test_engine.py`
- **.test_timeout_enforcement()** (4 connections) — `tests/test_engine.py`
- **.test_scenario_a_odds_uncertainty()** (4 connections) — `tests/test_engine.py`
- **.test_scenario_b_market_uncertainty()** (4 connections) — `tests/test_engine.py`
- *... and 27 more nodes in this community*

## Relationships

- [Application Engine & Domain Models](Application_Engine_&_Domain_Models.md) (21 shared connections)
- [API Dependencies & Context Providers](API_Dependencies_&_Context_Providers.md) (19 shared connections)
- [Action Registry & Definitions](Action_Registry_&_Definitions.md) (12 shared connections)
- [Safety Authority & Invariants](Safety_Authority_&_Invariants.md) (11 shared connections)
- [Market Context & Harm Indicators](Market_Context_&_Harm_Indicators.md) (3 shared connections)
- [FastAPI App & Database Session](FastAPI_App_&_Database_Session.md) (1 shared connections)

## Source Files

- `src/confidence/api/dependencies.py`
- `src/confidence/api/models.py`
- `src/confidence/api/routes.py`
- `src/confidence/application/context_builder.py`
- `src/confidence/application/engine.py`
- `src/confidence/domain/models.py`
- `tests/test_engine.py`

## Audit Trail

- EXTRACTED: 137 (77%)
- INFERRED: 42 (23%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*