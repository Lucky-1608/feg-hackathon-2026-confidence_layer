"""Daily aggregate report from persisted audit records, using UTC day boundaries."""

from collections import Counter
from datetime import UTC, date, datetime, time, timedelta

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine

from confidence.db.schema import audit_log, decisions, session_quality_scores
from confidence.domain.enums import ActionId
from confidence.domain.models import DecisionContext
from confidence.domain.sqs import SessionQualityResult
from confidence.evaluation.sqs_analysis import SQSAnalyzer, SQSReport


class DailyReport(BaseModel):
    date: date
    total_decisions: int
    intervention_rate: float
    safety_block_rate: float
    harm_indicator_rate: float
    top_actions: dict[str, int]
    sqs: SQSReport
    previous_day_decisions: int
    decision_count_change: int


class ReportGenerator:
    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine

    async def generate_daily_report(self, day: date) -> DailyReport:
        start = datetime.combine(day, time.min, tzinfo=UTC)
        end = start + timedelta(days=1)
        async with self.engine.connect() as conn:
            rows = (
                (
                    await conn.execute(
                        select(decisions, audit_log.c.context_snapshot)
                        .join(audit_log)
                        .where(decisions.c.timestamp >= start - timedelta(days=1), decisions.c.timestamp < end)
                    )
                )
                .mappings()
                .all()
            )
            score_rows = (
                (
                    await conn.execute(
                        select(session_quality_scores).where(
                            session_quality_scores.c.computed_at >= start, session_quality_scores.c.computed_at < end
                        )
                    )
                )
                .mappings()
                .all()
            )
        current = [r for r in rows if r["timestamp"].replace(tzinfo=UTC) >= start]
        previous = len(rows) - len(current)
        count = len(current)
        return DailyReport(
            date=day,
            total_decisions=count,
            intervention_rate=sum(r["selected_action"] != ActionId.NO_INTERVENTION and not r["shadow_mode"] for r in current) / count
            if count
            else 0,
            safety_block_rate=sum(r["safety_status"] != "SAFE" for r in current) / count if count else 0,
            harm_indicator_rate=sum(DecisionContext.model_validate(r["context_snapshot"]).safety.harm_indicators.has_any() for r in current)
            / count
            if count
            else 0,
            top_actions=dict(Counter(r["selected_action"] for r in current)),
            sqs=SQSAnalyzer().analyze([SessionQualityResult.model_validate(dict(r)) for r in score_rows]),
            previous_day_decisions=previous,
            decision_count_change=count - previous,
        )
