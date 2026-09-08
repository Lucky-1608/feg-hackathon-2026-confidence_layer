# NoInterventionReason

> God node · 27 connections · `src/confidence/domain/enums.py`

**Community:** [Safety Authority & Invariants](Safety_Authority_&_Invariants.md)

## Connections by Relation

### contains
- enums.py `EXTRACTED`

### imports
- domain/models.py `EXTRACTED`
- domain/__init__.py `EXTRACTED`
- engine.py `EXTRACTED`
- safety.py `EXTRACTED`

### inherits
- StrEnum `EXTRACTED`

### rationale_for
- Explicit reason codes for NO_INTERVENTION decisions. These distinguish why no… `EXTRACTED`

### references
- ._build_failure_decision() `EXTRACTED`
- .final_safety_check() `EXTRACTED`
- .check_legitimate_reconsideration() `EXTRACTED`
- .check_state_confidence() `EXTRACTED`
- .safety_block_to_no_intervention_reason() `EXTRACTED`

### uses
- [SafetyContract](SafetyContract.md) `INFERRED`
- [DecisionEngine](DecisionEngine.md) `INFERRED`
- Decision `INFERRED`
- TestEndToEndScenarios `INFERRED`
- TestPropertyInvariants `INFERRED`
- TestS3HarmState `INFERRED`
- TestAdversarialAndFailures `INFERRED`
- TestS1SelfExclusion `INFERRED`
- TestS8ConfidenceThreshold `INFERRED`
- TestMultipleBlockReasons `INFERRED`
- TestS4UnknownSafetyState `INFERRED`
- TestS5SafetyDependencyUnavailable `INFERRED`
- AuditRecord `INFERRED`
- TestDecision `INFERRED`
- TestLegitimateReconsideration `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*