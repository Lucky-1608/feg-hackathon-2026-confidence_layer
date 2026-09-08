"""Tests for the database schema.

Verifies that the SQLAlchemy schema creates all required tables
with correct columns, foreign keys, and indexes.
Uses SQLite in-memory for isolation — these tests do not require PostgreSQL.

Note: JSONB columns are tested as Text in SQLite since SQLite lacks JSONB.
The schema is authoritative; these tests verify structural completeness.
"""

from __future__ import annotations

from sqlalchemy import create_engine, inspect

from confidence.db.schema import metadata


class TestSchemaCreation:
    """Verify all tables can be created and have correct structure."""

    def test_all_tables_created(self) -> None:
        """All 9 required tables must be created."""
        engine = create_engine("sqlite:///:memory:")
        metadata.create_all(engine)
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())

        expected_tables = {
            "sessions",
            "events",
            "decision_contexts",
            "decisions",
            "outcomes",
            "policies",
            "action_registry",
            "experiments",
            "audit_log",
        }
        assert expected_tables.issubset(tables), (
            f"Missing tables: {expected_tables - tables}"
        )

    def test_sessions_columns(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        metadata.create_all(engine)
        inspector = inspect(engine)
        columns = {c["name"] for c in inspector.get_columns("sessions")}
        assert "session_id" in columns
        assert "anonymous_actor_id" in columns
        assert "started_at" in columns
        assert "client_version" in columns
        assert "created_at" in columns

    def test_events_columns(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        metadata.create_all(engine)
        inspector = inspect(engine)
        columns = {c["name"] for c in inspector.get_columns("events")}
        expected = {
            "event_id", "session_id", "event_type", "anonymous_actor_id",
            "timestamp", "sequence_number", "client_version", "schema_version",
            "context", "payload", "created_at",
        }
        assert expected.issubset(columns)

    def test_events_foreign_key_to_sessions(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        metadata.create_all(engine)
        inspector = inspect(engine)
        fks = inspector.get_foreign_keys("events")
        referred_tables = {fk["referred_table"] for fk in fks}
        assert "sessions" in referred_tables

    def test_decisions_columns(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        metadata.create_all(engine)
        inspector = inspect(engine)
        columns = {c["name"] for c in inspector.get_columns("decisions")}
        expected = {
            "decision_id", "session_id", "timestamp", "state",
            "state_confidence", "safety_status", "safety_block_reasons",
            "candidate_actions", "selected_action", "no_intervention_reason",
            "policy_version", "model_version", "action_registry_version",
            "facts_version", "reason", "response_text", "created_at",
        }
        assert expected.issubset(columns)

    def test_decisions_foreign_key_to_sessions(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        metadata.create_all(engine)
        inspector = inspect(engine)
        fks = inspector.get_foreign_keys("decisions")
        referred_tables = {fk["referred_table"] for fk in fks}
        assert "sessions" in referred_tables

    def test_outcomes_foreign_keys(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        metadata.create_all(engine)
        inspector = inspect(engine)
        fks = inspector.get_foreign_keys("outcomes")
        referred_tables = {fk["referred_table"] for fk in fks}
        assert "decisions" in referred_tables
        assert "sessions" in referred_tables

    def test_audit_log_foreign_key_to_decisions(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        metadata.create_all(engine)
        inspector = inspect(engine)
        fks = inspector.get_foreign_keys("audit_log")
        referred_tables = {fk["referred_table"] for fk in fks}
        assert "decisions" in referred_tables

    def test_audit_log_columns(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        metadata.create_all(engine)
        inspector = inspect(engine)
        columns = {c["name"] for c in inspector.get_columns("audit_log")}
        expected = {
            "audit_id", "decision_id", "timestamp", "context_snapshot",
            "safety_result", "state_estimate", "candidate_actions",
            "selected_action", "no_intervention_reason", "policy_version",
            "model_version", "action_registry_version", "facts_version",
            "reason", "response_text", "outcome", "created_at",
        }
        assert expected.issubset(columns)

    def test_action_registry_columns(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        metadata.create_all(engine)
        inspector = inspect(engine)
        columns = {c["name"] for c in inspector.get_columns("action_registry")}
        expected = {
            "id", "action_id", "category", "allowed_states",
            "required_data", "prohibited_states", "copy_template",
            "enabled", "version", "registry_version", "created_at",
        }
        assert expected.issubset(columns)

    def test_schema_is_idempotent(self) -> None:
        """create_all should be safe to call multiple times."""
        engine = create_engine("sqlite:///:memory:")
        metadata.create_all(engine)
        metadata.create_all(engine)  # Should not raise
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        assert len(tables) >= 9
