# UncertaintyState

> God node · 35 connections · `src/confidence/domain/enums.py`

**Community:** [Application Engine & Domain Models](Application_Engine_&_Domain_Models.md)

## Connections by Relation

### contains
- enums.py `EXTRACTED`

### imports
- domain/models.py `EXTRACTED`
- domain/__init__.py `EXTRACTED`
- engine.py `EXTRACTED`
- safety.py `EXTRACTED`
- actions.py `EXTRACTED`
- policy.py `EXTRACTED`
- state.py `EXTRACTED`
- api/models.py `EXTRACTED`

### inherits
- StrEnum `EXTRACTED`

### rationale_for
- Possible states of user uncertainty during betslip confirmation. The State… `EXTRACTED`

### references
- .get_eligible_for_state() `EXTRACTED`

### uses
- [ActionRegistry](ActionRegistry.md) `INFERRED`
- [SafetyContract](SafetyContract.md) `INFERRED`
- [DecisionEngine](DecisionEngine.md) `INFERRED`
- [StateEstimate](StateEstimate.md) `INFERRED`
- ActionDefinition `INFERRED`
- PolicySelector `INFERRED`
- Decision `INFERRED`
- TestEndToEndScenarios `INFERRED`
- StateEstimator `INFERRED`
- TestActionEligibility `INFERRED`
- TestS3HarmState `INFERRED`
- TestS1SelfExclusion `INFERRED`
- TestS8ConfidenceThreshold `INFERRED`
- TestActionRegistryConstruction `INFERRED`
- TestActionRegistryLookup `INFERRED`
- DecisionResponse `INFERRED`
- TestSafeContext `INFERRED`
- TestDecision `INFERRED`
- TestPolicySelector `INFERRED`
- TestLegitimateReconsideration `INFERRED`
- *…and 3 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*