# Conversion Safety Rules

> 8 nodes · cohesion 0.36

## Key Concepts

- **TestConversionOrientation** (8 connections) — `tests/test_safety_contract.py`
- **.is_conversion_oriented()** (7 connections) — `src/confidence/domain/safety.py`
- **.test_explain_market_is_conversion()** (2 connections) — `tests/test_safety_contract.py`
- **.test_explain_odds_is_conversion()** (2 connections) — `tests/test_safety_contract.py`
- **.test_no_intervention_not_conversion()** (2 connections) — `tests/test_safety_contract.py`
- **.test_offer_defer_not_conversion()** (2 connections) — `tests/test_safety_contract.py`
- **Return True if an action is conversion-oriented. NO_INTERVENTION and…** (1 connections) — `src/confidence/domain/safety.py`
- **Test which actions are classified as conversion-oriented.** (1 connections) — `tests/test_safety_contract.py`

## Relationships

- [Safety Authority & Invariants](Safety_Authority_&_Invariants.md) (3 shared connections)
- [Action Registry & Definitions](Action_Registry_&_Definitions.md) (2 shared connections)

## Source Files

- `src/confidence/domain/safety.py`
- `tests/test_safety_contract.py`

## Audit Trail

- EXTRACTED: 13 (87%)
- INFERRED: 2 (13%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*