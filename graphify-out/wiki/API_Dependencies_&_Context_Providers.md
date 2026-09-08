# API Dependencies & Context Providers

> 58 nodes · cohesion 0.06

## Key Concepts

- **dependencies.py** (41 connections) — `src/confidence/api/dependencies.py`
- **PolicySelector** (19 connections) — `src/confidence/domain/policy.py`
- **ContextBuilder** (14 connections) — `src/confidence/application/context_builder.py`
- **SlipContext** (13 connections) — `src/confidence/domain/models.py`
- **engine()** (13 connections) — `tests/test_engine.py`
- **context_builder.py** (12 connections) — `src/confidence/application/context_builder.py`
- **get_decision_engine()** (11 connections) — `src/confidence/api/dependencies.py`
- **PersistenceProvider** (10 connections) — `src/confidence/application/engine.py`
- **providers.py** (9 connections) — `src/confidence/infrastructure/providers.py`
- **MarketProvider** (9 connections) — `src/confidence/infrastructure/providers.py`
- **SafetyProvider** (9 connections) — `src/confidence/infrastructure/providers.py`
- **SlipProvider** (9 connections) — `src/confidence/infrastructure/providers.py`
- **.__init__()** (8 connections) — `src/confidence/application/engine.py`
- **DummySlipProvider** (7 connections) — `src/confidence/api/dependencies.py`
- **.build()** (7 connections) — `src/confidence/application/context_builder.py`
- **DatabasePersistenceProvider** (7 connections) — `src/confidence/infrastructure/persistence.py`
- **TestPolicySelector** (7 connections) — `tests/test_engine.py`
- **DummyMarketProvider** (5 connections) — `src/confidence/api/dependencies.py`
- **get_context_builder()** (5 connections) — `src/confidence/api/dependencies.py`
- **get_persistence_provider()** (5 connections) — `src/confidence/api/dependencies.py`
- **.test_selects_exact_match()** (5 connections) — `tests/test_engine.py`
- **.test_selects_no_intervention_when_only_option()** (5 connections) — `tests/test_engine.py`
- **.get_safety_context()** (4 connections) — `src/confidence/api/dependencies.py`
- **.get_slip_context()** (4 connections) — `src/confidence/api/dependencies.py`
- **get_engine()** (4 connections) — `src/confidence/api/dependencies.py`
- *... and 33 more nodes in this community*

## Relationships

- [Application Engine & Domain Models](Application_Engine_&_Domain_Models.md) (32 shared connections)
- [Decision Engine & API Models](Decision_Engine_&_API_Models.md) (19 shared connections)
- [Action Registry & Definitions](Action_Registry_&_Definitions.md) (17 shared connections)
- [Safety Authority & Invariants](Safety_Authority_&_Invariants.md) (14 shared connections)
- [Market Context & Harm Indicators](Market_Context_&_Harm_Indicators.md) (13 shared connections)
- [FastAPI App & Database Session](FastAPI_App_&_Database_Session.md) (6 shared connections)
- [Domain Model & Safety Tests](Domain_Model_&_Safety_Tests.md) (3 shared connections)

## Source Files

- `src/confidence/api/dependencies.py`
- `src/confidence/application/context_builder.py`
- `src/confidence/application/engine.py`
- `src/confidence/domain/models.py`
- `src/confidence/domain/policy.py`
- `src/confidence/infrastructure/persistence.py`
- `src/confidence/infrastructure/providers.py`
- `tests/test_engine.py`

## Audit Trail

- EXTRACTED: 169 (84%)
- INFERRED: 32 (16%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*