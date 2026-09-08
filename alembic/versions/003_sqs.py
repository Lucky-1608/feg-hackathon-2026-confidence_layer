"""Add versioned session quality scores."""

import sqlalchemy as sa

from alembic import op

revision = "003_sqs"
down_revision = "002_hardening"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "session_quality_scores",
        sa.Column("score_id", sa.Uuid, primary_key=True),
        sa.Column("session_id", sa.Uuid, sa.ForeignKey("sessions.session_id"), nullable=False),
        sa.Column("decision_id", sa.Uuid, sa.ForeignKey("decisions.decision_id"), nullable=False),
        sa.Column("outcome_id", sa.Uuid, sa.ForeignKey("outcomes.outcome_id"), nullable=False, unique=True),
        *[
            sa.Column(name, sa.Float, nullable=False)
            for name in ("raw_score", "clamped_score", "action_value", "discovery_efficiency", "harm_indicator_load")
        ],
        sa.Column("sqs_config_version", sa.String(20), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
    )
    for name, column in [("session", "session_id"), ("decision", "decision_id"), ("computed", "computed_at")]:
        op.create_index(f"ix_sqs_{name}", "session_quality_scores", [column])


def downgrade() -> None:
    op.drop_table("session_quality_scores")
