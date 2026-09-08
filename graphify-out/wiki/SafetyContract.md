# SafetyContract

> God node · 56 connections · `src/confidence/domain/safety.py`

**Community:** [Safety Authority & Invariants](Safety_Authority_&_Invariants.md)

## Connections by Relation

### calls
- safety_contract() `EXTRACTED`
- .test_exactly_at_threshold_passes() `EXTRACTED`
- .test_just_below_threshold_fails() `EXTRACTED`
- get_safety_contract() `EXTRACTED`

### contains
- safety.py `EXTRACTED`

### imports
- dependencies.py `EXTRACTED`
- domain/__init__.py `EXTRACTED`
- engine.py `EXTRACTED`

### method
- .is_conversion_oriented() `EXTRACTED`
- .final_safety_check() `EXTRACTED`
- .evaluate_safety() `EXTRACTED`
- .check_state_confidence() `EXTRACTED`
- .check_legitimate_reconsideration() `EXTRACTED`
- .safety_block_to_no_intervention_reason() `EXTRACTED`
- .__init__() `EXTRACTED`
- .confidence_threshold() `EXTRACTED`

### rationale_for
- Executable safety contract encoding invariants S1–S17. This contract is the… `EXTRACTED`

### references
- .__init__() `EXTRACTED`
- .test_self_excluded_with_harm() `EXTRACTED`
- .test_self_excluded_cannot_receive_intervention() `EXTRACTED`
- .test_each_harm_indicator_independently_blocks() `EXTRACTED`
- .test_final_check_allows_no_intervention_in_harm_state() `EXTRACTED`
- .test_final_check_blocks_conversion_in_harm_state() `EXTRACTED`
- .test_safe_context_allows_intervention() `EXTRACTED`
- .test_self_excluded_user_is_blocked() `EXTRACTED`
- .test_protective_restriction_is_blocked() `EXTRACTED`
- .test_harm_indicators_block_intervention() `EXTRACTED`
- .test_no_freshness_fails_closed() `EXTRACTED`
- .test_stale_safety_data_fails_closed() `EXTRACTED`
- .test_safe_context_is_safe() `EXTRACTED`
- .test_legitimate_reconsideration_detected() `EXTRACTED`
- .test_non_reconsideration_passes() `EXTRACTED`
- .test_high_confidence_passes() `EXTRACTED`
- .test_low_confidence_returns_insufficient() `EXTRACTED`
- .test_unknown_state_fails_regardless_of_confidence() `EXTRACTED`
- .test_multiple_reasons_map_to_safety_blocked() `EXTRACTED`
- .test_unknown_state_maps_to_insufficient_confidence() `EXTRACTED`
- *…and 1 more `references` connection(s) not listed (lowest-degree first to go)*

### uses
- [ActionId](ActionId.md) `INFERRED`
- [DecisionEngine](DecisionEngine.md) `INFERRED`
- [UncertaintyState](UncertaintyState.md) `INFERRED`
- [NoInterventionReason](NoInterventionReason.md) `INFERRED`
- SafetyStatus `INFERRED`
- SafetyBlockReason `INFERRED`
- engine() `INFERRED`
- TestS3HarmState `INFERRED`
- get_decision_engine() `INFERRED`
- TestS1SelfExclusion `INFERRED`
- TestS8ConfidenceThreshold `INFERRED`
- TestConversionOrientation `INFERRED`
- TestMultipleBlockReasons `INFERRED`
- TestS4UnknownSafetyState `INFERRED`
- TestS5SafetyDependencyUnavailable `INFERRED`
- TestSafeContext `INFERRED`
- TestLegitimateReconsideration `INFERRED`
- TestS2ProtectiveRestriction `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*