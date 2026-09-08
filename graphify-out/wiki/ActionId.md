# ActionId

> God node · 43 connections · `src/confidence/domain/enums.py`

**Community:** [Action Registry & Definitions](Action_Registry_&_Definitions.md)

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
- response.py `EXTRACTED`
- api/models.py `EXTRACTED`

### inherits
- StrEnum `EXTRACTED`

### rationale_for
- Registered action identifiers. The policy can only select from these registered… `EXTRACTED`

### references
- .is_conversion_oriented() `EXTRACTED`
- .final_safety_check() `EXTRACTED`
- .select_action() `EXTRACTED`
- .get() `EXTRACTED`
- .generate() `EXTRACTED`
- .all_action_ids() `EXTRACTED`
- .__init__() `EXTRACTED`
- .is_registered() `EXTRACTED`

### uses
- [ActionRegistry](ActionRegistry.md) `INFERRED`
- [SafetyContract](SafetyContract.md) `INFERRED`
- [DecisionEngine](DecisionEngine.md) `INFERRED`
- ActionDefinition `INFERRED`
- PolicySelector `INFERRED`
- Decision `INFERRED`
- TestEndToEndScenarios `INFERRED`
- ResponseGenerator `INFERRED`
- TestActionEligibility `INFERRED`
- TestPropertyInvariants `INFERRED`
- TestS3HarmState `INFERRED`
- TestAdversarialAndFailures `INFERRED`
- TestS1SelfExclusion `INFERRED`
- TestActionRegistryConstruction `INFERRED`
- TestActionRegistryLookup `INFERRED`
- DecisionResponse `INFERRED`
- TestConversionOrientation `INFERRED`
- TestSafeContext `INFERRED`
- AuditRecord `INFERRED`
- TestDecision `INFERRED`
- *…and 4 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*