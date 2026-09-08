"""Database schema for the Confidence Layer.

Uses SQLAlchemy Core table definitions. These are engine-agnostic:
they work with PostgreSQL in production and SQLite in tests.

Architectural constraint: The database is for persistence and audit.
It is NOT in the critical synchronous decision path. The decision engine
operates on in-memory data and request context. Audit writes are downstream
and must not turn a safe decision into a failure.

Tables:
    sessions: User betslip sessions
    events: Versioned client events
    decision_contexts: Serialized context snapshots
    decisions: Decision records with full provenance
    outcomes: Observed outcomes for evaluation
    policies: Policy version tracking
    action_registry: Action definition snapshots
    experiments: Experiment/scenario definitions
    audit_log: Complete audit trail
"""

from __future__ import annotations

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    Uuid,
)

# Use a naming convention for constraints to make migrations deterministic.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


sessions = Table(
    "sessions",
    metadata,
    Column("session_id", Uuid, primary_key=True),
    Column("anonymous_actor_id", String(255), nullable=False),
    Column("started_at", DateTime(timezone=True), nullable=False),
    Column("client_version", String(50), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)


events = Table(
    "events",
    metadata,
    Column("event_id", Uuid, primary_key=True),
    Column(
        "session_id",
        Uuid,
        ForeignKey("sessions.session_id"),
        nullable=False,
    ),
    Column("event_type", String(50), nullable=False),
    Column("anonymous_actor_id", String(255), nullable=False),
    Column("timestamp", DateTime(timezone=True), nullable=False),
    Column("sequence_number", Integer, nullable=False),
    Column("client_version", String(50), nullable=False),
    Column("schema_version", String(10), nullable=False, server_default="1"),
    Column("context", JSON, nullable=False, server_default="{}"),
    Column("payload", JSON, nullable=False, server_default="{}"),
    Column("created_at", DateTime(timezone=True), nullable=False),
    # Idempotency: reject duplicate event_id (handled by PK).
    # Ordering: session + sequence for event ordering.
    UniqueConstraint("session_id", "sequence_number", name="uq_events_session_seq"),
    Index("ix_events_session_timestamp", "session_id", "timestamp"),
    Index("ix_events_session_sequence", "session_id", "sequence_number"),
    Index("ix_events_type_timestamp", "event_type", "timestamp"),
)


decision_contexts = Table(
    "decision_contexts",
    metadata,
    Column("context_id", Uuid, primary_key=True),
    Column(
        "session_id",
        Uuid,
        ForeignKey("sessions.session_id"),
        nullable=False,
    ),
    Column("context_version", String(10), nullable=False, server_default="1"),
    Column("context_data", JSON, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Index("ix_decision_contexts_session", "session_id"),
)


decisions = Table(
    "decisions",
    metadata,
    Column("decision_id", Uuid, primary_key=True),
    Column(
        "session_id",
        Uuid,
        ForeignKey("sessions.session_id"),
        nullable=False,
    ),
    Column("timestamp", DateTime(timezone=True), nullable=False),
    Column("state", String(50), nullable=False),
    Column("state_confidence", Float, nullable=False),
    Column("safety_status", String(20), nullable=False),
    Column("safety_block_reasons", JSON, nullable=False, server_default="[]"),
    Column("candidate_actions", JSON, nullable=False),
    Column("selected_action", String(50), nullable=False),
    Column("no_intervention_reason", String(50), nullable=True),
    Column("policy_version", String(20), nullable=False),
    Column("model_version", String(50), nullable=False),
    Column("action_registry_version", String(20), nullable=False),
    Column("facts_version", String(20), nullable=True),
    Column("reason", Text, nullable=False),
    Column("response_text", Text, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Index("ix_decisions_session", "session_id"),
    Index("ix_decisions_timestamp", "timestamp"),
)


outcomes = Table(
    "outcomes",
    metadata,
    Column("outcome_id", Uuid, primary_key=True),
    Column(
        "decision_id",
        Uuid,
        ForeignKey("decisions.decision_id"),
        nullable=False,
    ),
    Column(
        "session_id",
        Uuid,
        ForeignKey("sessions.session_id"),
        nullable=False,
    ),
    Column("timestamp", DateTime(timezone=True), nullable=False),
    Column("outcome_type", String(50), nullable=False),
    Column("metadata_", JSON, nullable=False, server_default="{}"),
    Column("schema_version", String(10), nullable=False, server_default="1"),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Index("ix_outcomes_decision", "decision_id"),
    Index("ix_outcomes_session", "session_id"),
)


policies = Table(
    "policies",
    metadata,
    Column("policy_id", Uuid, primary_key=True),
    Column("policy_version", String(20), nullable=False, unique=True),
    Column("policy_type", String(50), nullable=False),
    Column("policy_config", JSON, nullable=False),
    Column("is_active", Boolean, nullable=False, server_default="true"),
    Column("created_at", DateTime(timezone=True), nullable=False),
)


action_registry = Table(
    "action_registry",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("action_id", String(50), nullable=False),
    Column("category", String(50), nullable=False),
    Column("allowed_states", JSON, nullable=False),
    Column("required_data", JSON, nullable=False, server_default="[]"),
    Column("prohibited_states", JSON, nullable=False, server_default="[]"),
    Column("copy_template", Text, nullable=True),
    Column("enabled", Boolean, nullable=False, server_default="true"),
    Column("version", String(20), nullable=False),
    Column("registry_version", String(20), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Index("ix_action_registry_action_version", "action_id", "version"),
)


experiments = Table(
    "experiments",
    metadata,
    Column("experiment_id", Uuid, primary_key=True),
    Column("name", String(255), nullable=False),
    Column("description", Text, nullable=True),
    Column("experiment_type", String(50), nullable=False),
    Column("config", JSON, nullable=False),
    Column("is_active", Boolean, nullable=False, server_default="false"),
    Column("created_at", DateTime(timezone=True), nullable=False),
)


audit_log = Table(
    "audit_log",
    metadata,
    Column("audit_id", Uuid, primary_key=True),
    Column(
        "decision_id",
        Uuid,
        ForeignKey("decisions.decision_id"),
        nullable=False,
    ),
    Column("timestamp", DateTime(timezone=True), nullable=False),
    Column("context_snapshot", JSON, nullable=False),
    Column("safety_result", JSON, nullable=False),
    Column("state_estimate", JSON, nullable=False),
    Column("candidate_actions", JSON, nullable=False),
    Column("selected_action", String(50), nullable=False),
    Column("no_intervention_reason", String(50), nullable=True),
    Column("policy_version", String(20), nullable=False),
    Column("model_version", String(50), nullable=False),
    Column("action_registry_version", String(20), nullable=False),
    Column("facts_version", String(20), nullable=True),
    Column("reason", Text, nullable=False),
    Column("response_text", Text, nullable=True),
    Column("outcome", JSON, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Index("ix_audit_log_decision", "decision_id"),
    Index("ix_audit_log_timestamp", "timestamp"),
)
