"""Record stable experiment assignment at the session randomization unit."""

import sqlalchemy as sa

from alembic import op

revision = "006_experiments_active"
down_revision = "005_shadow_mode"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "outbox",
        sa.Column("message_id", sa.Uuid, primary_key=True),
        sa.Column("topic", sa.String(100), primary_key=True),
        sa.Column("partition_key", sa.String(255), nullable=False),
        sa.Column("payload", sa.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("delivered", sa.Boolean, nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_outbox_delivery", "outbox", ["delivered", "created_at"])
    op.create_table(
        "experiment_assignments",
        sa.Column("experiment_id", sa.Uuid, sa.ForeignKey("experiments.experiment_id"), primary_key=True),
        sa.Column("session_id", sa.Uuid, sa.ForeignKey("sessions.session_id"), primary_key=True),
        sa.Column("assignment", sa.String(20), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_experiment_assignments_group", "experiment_assignments", ["experiment_id", "assignment"])


def downgrade() -> None:
    op.drop_table("outbox")
    op.drop_table("experiment_assignments")
