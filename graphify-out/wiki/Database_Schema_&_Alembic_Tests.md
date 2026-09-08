# Database Schema & Alembic Tests

> 25 nodes · cohesion 0.08

## Key Concepts

- **TestSchemaCreation** (13 connections) — `tests/test_schema.py`
- **env.py** (4 connections) — `alembic/env.py`
- **schema.py** (4 connections) — `src/confidence/db/schema.py`
- **test_schema.py** (3 connections) — `tests/test_schema.py`
- **run_migrations_offline()** (2 connections) — `alembic/env.py`
- **run_migrations_online()** (2 connections) — `alembic/env.py`
- **.test_all_tables_created()** (2 connections) — `tests/test_schema.py`
- **.test_schema_is_idempotent()** (2 connections) — `tests/test_schema.py`
- **Alembic environment configuration.** (1 connections) — `alembic/env.py`
- **Run migrations in 'offline' mode.** (1 connections) — `alembic/env.py`
- **Run migrations in 'online' mode.** (1 connections) — `alembic/env.py`
- **Database schema for the Confidence Layer. Uses SQLAlchemy Core table…** (1 connections) — `src/confidence/db/schema.py`
- **Tests for the database schema. Verifies that the SQLAlchemy schema creates all…** (1 connections) — `tests/test_schema.py`
- **create_all should be safe to call multiple times.** (1 connections) — `tests/test_schema.py`
- **Verify all tables can be created and have correct structure.** (1 connections) — `tests/test_schema.py`
- **All 9 required tables must be created.** (1 connections) — `tests/test_schema.py`
- **.test_action_registry_columns()** (1 connections) — `tests/test_schema.py`
- **.test_audit_log_columns()** (1 connections) — `tests/test_schema.py`
- **.test_audit_log_foreign_key_to_decisions()** (1 connections) — `tests/test_schema.py`
- **.test_decisions_columns()** (1 connections) — `tests/test_schema.py`
- **.test_decisions_foreign_key_to_sessions()** (1 connections) — `tests/test_schema.py`
- **.test_events_columns()** (1 connections) — `tests/test_schema.py`
- **.test_events_foreign_key_to_sessions()** (1 connections) — `tests/test_schema.py`
- **.test_outcomes_foreign_keys()** (1 connections) — `tests/test_schema.py`
- **.test_sessions_columns()** (1 connections) — `tests/test_schema.py`

## Relationships

- [Application Engine & Domain Models](Application_Engine_&_Domain_Models.md) (1 shared connections)

## Source Files

- `alembic/env.py`
- `src/confidence/db/schema.py`
- `tests/test_schema.py`

## Audit Trail

- EXTRACTED: 25 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*