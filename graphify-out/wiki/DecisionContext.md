# DecisionContext

> God node · 28 connections · `src/confidence/domain/models.py`

**Community:** [Application Engine & Domain Models](Application_Engine_&_Domain_Models.md)

## Connections by Relation

### calls
- sample_context() `EXTRACTED`
- .build() `EXTRACTED`

### contains
- domain/models.py `EXTRACTED`

### imports
- domain/__init__.py `EXTRACTED`
- engine.py `EXTRACTED`
- policy.py `EXTRACTED`
- context_builder.py `EXTRACTED`
- response.py `EXTRACTED`
- state.py `EXTRACTED`
- persistence.py `EXTRACTED`

### inherits
- BaseModel `EXTRACTED`

### rationale_for
- Complete context assembled by the Context Builder for a decision. This is the… `EXTRACTED`

### references
- .select_action() `EXTRACTED`
- .test_audit_contains_full_provenance() `EXTRACTED`
- .test_selects_exact_match() `EXTRACTED`
- .test_selects_no_intervention_when_only_option() `EXTRACTED`
- .test_generates_odds_change_response() `EXTRACTED`
- .generate() `EXTRACTED`
- .estimate_state() `EXTRACTED`
- .persist_decision() `EXTRACTED`
- .test_missing_template_data_fails_closed() `EXTRACTED`
- .test_no_intervention_yields_no_response() `EXTRACTED`
- .test_potential_harm_priority() `EXTRACTED`
- .persist_decision() `EXTRACTED`
- .test_legitimate_reconsideration() `EXTRACTED`
- .test_odds_change() `EXTRACTED`
- .test_context_serialization_roundtrip() `EXTRACTED`
- .test_full_context() `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*