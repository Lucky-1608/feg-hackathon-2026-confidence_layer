"""Read only history adapter. Potential returns are never treated as settlements."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine

from confidence.db.schema import decisions, outcomes, sessions
from confidence.domain.models import SessionSummary


class DatabaseSessionHistoryProvider:
    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine

    async def get_recent_sessions(self, anonymous_actor_id: str, lookback_days: int = 30) -> list[SessionSummary]:
        async with self.engine.connect() as conn:
            rows = (
                (
                    await conn.execute(
                        select(sessions.c.session_id, sessions.c.started_at)
                        .outerjoin(decisions)
                        .outerjoin(outcomes, outcomes.c.decision_id == decisions.c.decision_id)
                        .where(
                            sessions.c.anonymous_actor_id == anonymous_actor_id,
                            sessions.c.started_at >= datetime.now(UTC) - timedelta(days=lookback_days),
                        )
                        .distinct()
                        .order_by(sessions.c.started_at)
                    )
                )
                .mappings()
                .all()
            )
        # Settlement/deposit feeds must enrich these summaries through the history port.
        # The detector fails closed on incomplete financial history.
        return [
            SessionSummary(session_id=row["session_id"], started_at=row["started_at"].replace(tzinfo=UTC), financial_data_complete=False)
            for row in rows
        ]
