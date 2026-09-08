# StateEstimate

> God node · 29 connections · `src/confidence/domain/models.py`

**Community:** [Safety Authority & Invariants](Safety_Authority_&_Invariants.md)

## Connections by Relation

### calls
- .test_audit_contains_full_provenance() `EXTRACTED`
- .test_selects_exact_match() `EXTRACTED`
- .test_selects_no_intervention_when_only_option() `EXTRACTED`
- .test_self_excluded_cannot_receive_intervention() `EXTRACTED`
- .test_final_check_allows_no_intervention_in_harm_state() `EXTRACTED`
- .test_final_check_blocks_conversion_in_harm_state() `EXTRACTED`
- .test_safe_context_allows_intervention() `EXTRACTED`
- .estimate_state() `EXTRACTED`
- .test_legitimate_reconsideration_detected() `EXTRACTED`
- .test_non_reconsideration_passes() `EXTRACTED`
- .test_exactly_at_threshold_passes() `EXTRACTED`
- .test_high_confidence_passes() `EXTRACTED`
- .test_just_below_threshold_fails() `EXTRACTED`
- .test_low_confidence_returns_insufficient() `EXTRACTED`
- .test_unknown_state_fails_regardless_of_confidence() `EXTRACTED`
- .test_confidence_bounds() `EXTRACTED`
- .test_valid_estimate() `EXTRACTED`

### contains
- domain/models.py `EXTRACTED`

### imports
- domain/__init__.py `EXTRACTED`
- safety.py `EXTRACTED`
- policy.py `EXTRACTED`
- state.py `EXTRACTED`

### inherits
- BaseModel `EXTRACTED`

### rationale_for
- Output of the State Authority. The State Authority answers: 'What is… `EXTRACTED`

### references
- .select_action() `EXTRACTED`
- .final_safety_check() `EXTRACTED`
- .check_legitimate_reconsideration() `EXTRACTED`
- .check_state_confidence() `EXTRACTED`

### uses
- [UncertaintyState](UncertaintyState.md) `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*