# Domain Model & Safety Tests

> 24 nodes · cohesion 0.11

## Key Concepts

- **test_domain.py** (15 connections) — `tests/test_domain.py`
- **Session** (10 connections) — `src/confidence/domain/models.py`
- **datetime** (9 connections)
- **TestDecision** (7 connections) — `tests/test_domain.py`
- **TestSafetyResult** (5 connections) — `tests/test_domain.py`
- **TestStateEstimate** (4 connections) — `tests/test_domain.py`
- **.test_no_intervention_decision()** (3 connections) — `tests/test_domain.py`
- **.test_valid_decision()** (3 connections) — `tests/test_domain.py`
- **.test_valid_outcome()** (3 connections) — `tests/test_domain.py`
- **TestSafetyContext** (3 connections) — `tests/test_domain.py`
- **.test_blocked_result()** (3 connections) — `tests/test_domain.py`
- **.test_safe_result()** (3 connections) — `tests/test_domain.py`
- **TestSession** (3 connections) — `tests/test_domain.py`
- **.test_valid_session()** (3 connections) — `tests/test_domain.py`
- **TestOutcome** (2 connections) — `tests/test_domain.py`
- **.test_default_safe()** (2 connections) — `tests/test_domain.py`
- **.test_self_excluded()** (2 connections) — `tests/test_domain.py`
- **.test_session_serialization_roundtrip()** (2 connections) — `tests/test_domain.py`
- **TestSlipContext** (2 connections) — `tests/test_domain.py`
- **.test_valid_slip()** (2 connections) — `tests/test_domain.py`
- **.test_confidence_bounds()** (2 connections) — `tests/test_domain.py`
- **.test_valid_estimate()** (2 connections) — `tests/test_domain.py`
- **A user's betslip confirmation session.** (1 connections) — `src/confidence/domain/models.py`
- **Tests for domain model validation. Verifies that all Pydantic domain models…** (1 connections) — `tests/test_domain.py`

## Relationships

- [Safety Authority & Invariants](Safety_Authority_&_Invariants.md) (12 shared connections)
- [Application Engine & Domain Models](Application_Engine_&_Domain_Models.md) (10 shared connections)
- [Market Context & Harm Indicators](Market_Context_&_Harm_Indicators.md) (5 shared connections)
- [API Dependencies & Context Providers](API_Dependencies_&_Context_Providers.md) (3 shared connections)
- [FastAPI App & Database Session](FastAPI_App_&_Database_Session.md) (1 shared connections)
- [Action Registry & Definitions](Action_Registry_&_Definitions.md) (1 shared connections)

## Source Files

- `src/confidence/domain/models.py`
- `tests/test_domain.py`

## Audit Trail

- EXTRACTED: 55 (89%)
- INFERRED: 7 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*