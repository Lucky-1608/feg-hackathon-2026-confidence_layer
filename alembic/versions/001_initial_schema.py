"""Initial schema for Confidence Layer.

Revision ID: 001
Revises: None
Create Date: 2026-09-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import JSON, Uuid

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Sessions
    op.create_table(
        "sessions",
        sa.Column("session_id", Uuid, primary_key=True),
        sa.Column("anonymous_actor_id", sa.String(255), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("client_version", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Events
    op.create_table(
        "events",
        sa.Column("event_id", Uuid, primary_key=True),
        sa.Column(
            "session_id",
            Uuid,
            sa.ForeignKey("sessions.session_id"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("anonymous_actor_id", sa.String(255), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sequence_number", sa.Integer, nullable=False),
        sa.Column("client_version", sa.String(50), nullable=False),
        sa.Column("schema_version", sa.String(10), nullable=False, server_default="1"),
        sa.Column("context", JSON, nullable=False, server_default="{}"),
        sa.Column("payload", JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("session_id", "sequence_number", name="uq_events_session_seq"),
    )
    op.create_index("ix_events_session_timestamp", "events", ["session_id", "timestamp"])
    op.create_index("ix_events_session_sequence", "events", ["session_id", "sequence_number"])
    op.create_index("ix_events_type_timestamp", "events", ["event_type", "timestamp"])

    # Decision Contexts
    op.create_table(
        "decision_contexts",
        sa.Column("context_id", Uuid, primary_key=True),
        sa.Column(
            "session_id",
            Uuid,
            sa.ForeignKey("sessions.session_id"),
            nullable=False,
        ),
        sa.Column("context_version", sa.String(10), nullable=False, server_default="1"),
        sa.Column("context_data", JSON, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_decision_contexts_session", "decision_contexts", ["session_id"])

    # Decisions
    op.create_table(
        "decisions",
        sa.Column("decision_id", Uuid, primary_key=True),
        sa.Column(
            "session_id",
            Uuid,
            sa.ForeignKey("sessions.session_id"),
            nullable=False,
        ),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("state", sa.String(50), nullable=False),
        sa.Column("state_confidence", sa.Float, nullable=False),
        sa.Column("safety_status", sa.String(20), nullable=False),
        sa.Column("safety_block_reasons", JSON, nullable=False, server_default="[]"),
        sa.Column("candidate_actions", JSON, nullable=False),
        sa.Column("selected_action", sa.String(50), nullable=False),
        sa.Column("no_intervention_reason", sa.String(50), nullable=True),
        sa.Column("policy_version", sa.String(20), nullable=False),
        sa.Column("model_version", sa.String(50), nullable=False),
        sa.Column("action_registry_version", sa.String(20), nullable=False),
        sa.Column("facts_version", sa.String(20), nullable=True),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("response_text", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_decisions_session", "decisions", ["session_id"])
    op.create_index("ix_decisions_timestamp", "decisions", ["timestamp"])

    # Outcomes
    op.create_table(
        "outcomes",
        sa.Column("outcome_id", Uuid, primary_key=True),
        sa.Column(
            "decision_id",
            Uuid,
            sa.ForeignKey("decisions.decision_id"),
            nullable=False,
        ),
        sa.Column(
            "session_id",
            Uuid,
            sa.ForeignKey("sessions.session_id"),
            nullable=False,
        ),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("outcome_type", sa.String(50), nullable=False),
        sa.Column("metadata_", JSON, nullable=False, server_default="{}"),
        sa.Column("schema_version", sa.String(10), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_outcomes_decision", "outcomes", ["decision_id"])
    op.create_index("ix_outcomes_session", "outcomes", ["session_id"])

    # Policies
    op.create_table(
        "policies",
        sa.Column("policy_id", Uuid, primary_key=True),
        sa.Column("policy_version", sa.String(20), nullable=False, unique=True),
        sa.Column("policy_type", sa.String(50), nullable=False),
        sa.Column("policy_config", JSON, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Action Registry
    op.create_table(
        "action_registry",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("action_id", sa.String(50), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("allowed_states", JSON, nullable=False),
        sa.Column("required_data", JSON, nullable=False, server_default="[]"),
        sa.Column("prohibited_states", JSON, nullable=False, server_default="[]"),
        sa.Column("copy_template", sa.Text, nullable=True),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("registry_version", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_action_registry_action_version",
        "action_registry",
        ["action_id", "version"],
    )

    # Experiments
    op.create_table(
        "experiments",
        sa.Column("experiment_id", Uuid, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("experiment_type", sa.String(50), nullable=False),
        sa.Column("config", JSON, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Audit Log
    op.create_table(
        "audit_log",
        sa.Column("audit_id", Uuid, primary_key=True),
        sa.Column(
            "decision_id",
            Uuid,
            sa.ForeignKey("decisions.decision_id"),
            nullable=False,
        ),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("context_snapshot", JSON, nullable=False),
        sa.Column("safety_result", JSON, nullable=False),
        sa.Column("state_estimate", JSON, nullable=False),
        sa.Column("candidate_actions", JSON, nullable=False),
        sa.Column("selected_action", sa.String(50), nullable=False),
        sa.Column("no_intervention_reason", sa.String(50), nullable=True),
        sa.Column("policy_version", sa.String(20), nullable=False),
        sa.Column("model_version", sa.String(50), nullable=False),
        sa.Column("action_registry_version", sa.String(20), nullable=False),
        sa.Column("facts_version", sa.String(20), nullable=True),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("response_text", sa.Text, nullable=True),
        sa.Column("outcome", JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_log_decision", "audit_log", ["decision_id"])
    op.create_index("ix_audit_log_timestamp", "audit_log", ["timestamp"])


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("experiments")
    op.drop_table("action_registry")
    op.drop_table("policies")
    op.drop_table("outcomes")
    op.drop_table("decisions")
    op.drop_table("decision_contexts")
    op.drop_table("events")
    op.drop_table("sessions")
