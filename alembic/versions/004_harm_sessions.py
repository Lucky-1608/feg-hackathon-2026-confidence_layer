"""Index actor history lookups."""

from alembic import op

revision = "004_harm_sessions"
down_revision = "003_sqs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_sessions_actor", "sessions", ["anonymous_actor_id"])


def downgrade() -> None:
    op.drop_index("ix_sessions_actor", table_name="sessions")
