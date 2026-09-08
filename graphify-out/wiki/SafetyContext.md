# SafetyContext

> God node · 31 connections · `src/confidence/domain/models.py`

**Community:** [Safety Authority & Invariants](Safety_Authority_&_Invariants.md)

## Connections by Relation

### calls
- .build() `EXTRACTED`
- harm_safety_context() `EXTRACTED`
- protective_restriction_context() `EXTRACTED`
- safe_safety_context() `EXTRACTED`
- self_excluded_safety_context() `EXTRACTED`
- stale_safety_context() `EXTRACTED`
- no_freshness_safety_context() `EXTRACTED`
- .test_self_excluded_with_harm() `EXTRACTED`
- .test_each_harm_indicator_independently_blocks() `EXTRACTED`
- .get_safety_context() `EXTRACTED`
- .test_default_safe() `EXTRACTED`
- .test_self_excluded() `EXTRACTED`

### contains
- domain/models.py `EXTRACTED`

### imports
- dependencies.py `EXTRACTED`
- domain/__init__.py `EXTRACTED`
- safety.py `EXTRACTED`
- context_builder.py `EXTRACTED`
- providers.py `EXTRACTED`

### inherits
- BaseModel `EXTRACTED`

### rationale_for
- Safety-relevant state, sourced from authoritative server-side systems. These… `EXTRACTED`

### references
- sample_context() `EXTRACTED`
- .evaluate_safety() `EXTRACTED`
- .test_self_excluded_cannot_receive_intervention() `EXTRACTED`
- .test_safe_context_allows_intervention() `EXTRACTED`
- .test_self_excluded_user_is_blocked() `EXTRACTED`
- .test_protective_restriction_is_blocked() `EXTRACTED`
- .test_harm_indicators_block_intervention() `EXTRACTED`
- .test_no_freshness_fails_closed() `EXTRACTED`
- .test_stale_safety_data_fails_closed() `EXTRACTED`
- .test_safe_context_is_safe() `EXTRACTED`
- .get_safety_context() `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*