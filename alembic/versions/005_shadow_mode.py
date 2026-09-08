"""Preserve hypothetical decisions in shadow audit records."""

import sqlalchemy as sa

from alembic import op

revision = "005_shadow_mode"
down_revision = "004_harm_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in ("decisions", "audit_log"):
        op.add_column(table, sa.Column("shadow_mode", sa.Boolean, nullable=False, server_default=sa.false()))


def downgrade() -> None:
    for table in ("audit_log", "decisions"):
        op.drop_column(table, "shadow_mode")
