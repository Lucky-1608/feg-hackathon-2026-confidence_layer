# Domain Events & Schema Validation

> 24 nodes · cohesion 0.16

## Key Concepts

- **ConfidenceEvent** (17 connections) — `src/confidence/domain/events.py`
- **TestConfidenceEvent** (11 connections) — `tests/test_events.py`
- **datetime** (9 connections)
- **EventType** (7 connections) — `src/confidence/domain/enums.py`
- **events.py** (6 connections) — `src/confidence/domain/events.py`
- **test_events.py** (5 connections) — `tests/test_events.py`
- **.test_all_event_types_valid()** (4 connections) — `tests/test_events.py`
- **field_validator** (3 connections)
- **.test_event_serialization_roundtrip()** (3 connections) — `tests/test_events.py`
- **.test_event_with_payload()** (3 connections) — `tests/test_events.py`
- **.test_rejects_empty_actor_id()** (3 connections) — `tests/test_events.py`
- **.test_rejects_empty_client_version()** (3 connections) — `tests/test_events.py`
- **.test_rejects_invalid_event_type()** (3 connections) — `tests/test_events.py`
- **.test_rejects_negative_sequence()** (3 connections) — `tests/test_events.py`
- **.test_valid_event()** (3 connections) — `tests/test_events.py`
- **.actor_id_must_not_be_empty()** (2 connections) — `src/confidence/domain/events.py`
- **.sequence_must_be_non_negative()** (2 connections) — `src/confidence/domain/events.py`
- **.version_must_not_be_empty()** (2 connections) — `src/confidence/domain/events.py`
- **Types of client events the system processes.** (1 connections) — `src/confidence/domain/enums.py`
- **BaseModel** (1 connections)
- **Versioned event schema for the Confidence Layer. Events are the primary input…** (1 connections) — `src/confidence/domain/events.py`
- **A versioned event from the client. Schema follows the architecture spec's event…** (1 connections) — `src/confidence/domain/events.py`
- **Tests for the event schema. Verifies event validation, required fields,…** (1 connections) — `tests/test_events.py`
- **Every EventType enum value should produce a valid event.** (1 connections) — `tests/test_events.py`

## Relationships

- [Application Engine & Domain Models](Application_Engine_&_Domain_Models.md) (7 shared connections)

## Source Files

- `src/confidence/domain/enums.py`
- `src/confidence/domain/events.py`
- `tests/test_events.py`

## Audit Trail

- EXTRACTED: 48 (94%)
- INFERRED: 3 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*