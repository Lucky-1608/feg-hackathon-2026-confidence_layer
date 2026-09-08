# Safety Authority & Invariants

> 74 nodes · cohesion 0.07

## Key Concepts

- **SafetyContract** (56 connections) — `src/confidence/domain/safety.py`
- **SafetyContext** (31 connections) — `src/confidence/domain/models.py`
- **StateEstimate** (29 connections) — `src/confidence/domain/models.py`
- **NoInterventionReason** (27 connections) — `src/confidence/domain/enums.py`
- **SafetyStatus** (25 connections) — `src/confidence/domain/enums.py`
- **safety.py** (19 connections) — `src/confidence/domain/safety.py`
- **SafetyBlockReason** (17 connections) — `src/confidence/domain/enums.py`
- **test_safety_contract.py** (15 connections) — `tests/test_safety_contract.py`
- **SafetyResult** (14 connections) — `src/confidence/domain/models.py`
- **datetime** (13 connections)
- **TestS3HarmState** (12 connections) — `tests/test_safety_contract.py`
- **TestS1SelfExclusion** (10 connections) — `tests/test_safety_contract.py`
- **TestS8ConfidenceThreshold** (10 connections) — `tests/test_safety_contract.py`
- **TestMultipleBlockReasons** (8 connections) — `tests/test_safety_contract.py`
- **TestS4UnknownSafetyState** (8 connections) — `tests/test_safety_contract.py`
- **TestS5SafetyDependencyUnavailable** (8 connections) — `tests/test_safety_contract.py`
- **TestSafeContext** (8 connections) — `tests/test_safety_contract.py`
- **TestLegitimateReconsideration** (7 connections) — `tests/test_safety_contract.py`
- **.final_safety_check()** (6 connections) — `src/confidence/domain/safety.py`
- **.test_audit_contains_full_provenance()** (6 connections) — `tests/test_domain.py`
- **TestS2ProtectiveRestriction** (6 connections) — `tests/test_safety_contract.py`
- **.evaluate_safety()** (5 connections) — `src/confidence/domain/safety.py`
- **TestAuditRecord** (5 connections) — `tests/test_domain.py`
- **.test_self_excluded_with_harm()** (5 connections) — `tests/test_safety_contract.py`
- **.test_self_excluded_cannot_receive_intervention()** (5 connections) — `tests/test_safety_contract.py`
- *... and 49 more nodes in this community*

## Relationships

- [Application Engine & Domain Models](Application_Engine_&_Domain_Models.md) (47 shared connections)
- [API Dependencies & Context Providers](API_Dependencies_&_Context_Providers.md) (14 shared connections)
- [Market Context & Harm Indicators](Market_Context_&_Harm_Indicators.md) (14 shared connections)
- [Domain Model & Safety Tests](Domain_Model_&_Safety_Tests.md) (12 shared connections)
- [Decision Engine & API Models](Decision_Engine_&_API_Models.md) (11 shared connections)
- [Action Registry & Definitions](Action_Registry_&_Definitions.md) (8 shared connections)
- [Conversion Safety Rules](Conversion_Safety_Rules.md) (3 shared connections)

## Source Files

- `src/confidence/domain/enums.py`
- `src/confidence/domain/models.py`
- `src/confidence/domain/safety.py`
- `tests/test_domain.py`
- `tests/test_safety_contract.py`

## Audit Trail

- EXTRACTED: 219 (76%)
- INFERRED: 68 (24%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*