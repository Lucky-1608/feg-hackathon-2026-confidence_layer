# Application Engine & Domain Models

> 52 nodes · cohesion 0.08

## Key Concepts

- **domain/models.py** (36 connections) — `src/confidence/domain/models.py`
- **UncertaintyState** (35 connections) — `src/confidence/domain/enums.py`
- **domain/__init__.py** (32 connections) — `src/confidence/domain/__init__.py`
- **DecisionContext** (28 connections) — `src/confidence/domain/models.py`
- **engine.py** (25 connections) — `src/confidence/application/engine.py`
- **enums.py** (24 connections) — `src/confidence/domain/enums.py`
- **Decision** (18 connections) — `src/confidence/domain/models.py`
- **test_engine.py** (18 connections) — `tests/test_engine.py`
- **StateEstimator** (16 connections) — `src/confidence/domain/state.py`
- **actions.py** (15 connections) — `src/confidence/domain/actions.py`
- **policy.py** (14 connections) — `src/confidence/domain/policy.py`
- **ActionCategory** (11 connections) — `src/confidence/domain/enums.py`
- **response.py** (11 connections) — `src/confidence/domain/response.py`
- **state.py** (10 connections) — `src/confidence/domain/state.py`
- **StrEnum** (8 connections)
- **AuditRecord** (7 connections) — `src/confidence/domain/models.py`
- **persistence.py** (7 connections) — `src/confidence/infrastructure/persistence.py`
- **test_actions.py** (7 connections) — `tests/test_actions.py`
- **OutcomeType** (6 connections) — `src/confidence/domain/enums.py`
- **Outcome** (6 connections) — `src/confidence/domain/models.py`
- **TestStateEstimator** (6 connections) — `tests/test_engine.py`
- **.estimate_state()** (4 connections) — `src/confidence/domain/state.py`
- **.persist_decision()** (4 connections) — `src/confidence/infrastructure/persistence.py`
- **.test_potential_harm_priority()** (4 connections) — `tests/test_engine.py`
- **.persist_decision()** (3 connections) — `src/confidence/application/engine.py`
- *... and 27 more nodes in this community*

## Relationships

- [Safety Authority & Invariants](Safety_Authority_&_Invariants.md) (47 shared connections)
- [Action Registry & Definitions](Action_Registry_&_Definitions.md) (39 shared connections)
- [API Dependencies & Context Providers](API_Dependencies_&_Context_Providers.md) (32 shared connections)
- [Decision Engine & API Models](Decision_Engine_&_API_Models.md) (21 shared connections)
- [Market Context & Harm Indicators](Market_Context_&_Harm_Indicators.md) (15 shared connections)
- [Domain Model & Safety Tests](Domain_Model_&_Safety_Tests.md) (10 shared connections)
- [Domain Events & Schema Validation](Domain_Events_&_Schema_Validation.md) (7 shared connections)
- [Database Schema & Alembic Tests](Database_Schema_&_Alembic_Tests.md) (1 shared connections)

## Source Files

- `src/confidence/application/engine.py`
- `src/confidence/domain/__init__.py`
- `src/confidence/domain/actions.py`
- `src/confidence/domain/enums.py`
- `src/confidence/domain/models.py`
- `src/confidence/domain/policy.py`
- `src/confidence/domain/response.py`
- `src/confidence/domain/state.py`
- `src/confidence/infrastructure/persistence.py`
- `tests/test_actions.py`
- `tests/test_domain.py`
- `tests/test_engine.py`

## Audit Trail

- EXTRACTED: 241 (86%)
- INFERRED: 40 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*