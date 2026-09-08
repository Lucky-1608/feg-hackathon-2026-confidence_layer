"""Persistence for audit logs and decisions.

Architectural constraint: Persistence is downstream of the decision.
It must NEVER cause a decision failure. All persistence calls are
fire-and-forget from the engine's perspective.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from statistics import mean, median, quantiles
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import insert, select, true, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from confidence.db.schema import audit_log, decisions, events, experiment_assignments, outbox, outcomes, session_quality_scores, sessions
from confidence.domain.enums import ActionId
from confidence.domain.event_contracts import ConfidenceEvent
from confidence.domain.models import Decision, DecisionContext, Outcome
from confidence.domain.ports import PersistenceProvider
from confidence.domain.sqs import SessionQualityResult
from confidence.log import get_logger
from confidence.observability.metrics import AUDIT_ERRORS, SQS_SCORES

logger = get_logger("confidence.persistence")


class DatabasePersistenceProvider(PersistenceProvider):
    """Saves decisions and audit records asynchronously to the database.

    All column values must match db/schema.py exactly.
    This class is called via asyncio.create_task() — never on the critical path.
    """

    def __init__(self, engine: AsyncEngine) -> None:
        self.session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async def persist_decision(self, decision: Decision, context: DecisionContext) -> None:
        """Persist a decision and its audit log to the database.

        Called as a background task — errors are logged but never re-raised
        to affect the decision response.
        """
        now = datetime.now(UTC)

        try:
            async with self.session_factory() as session, session.begin():
                # 1. Upsert parent session record (required by FK constraint)
                try:
                    await session.execute(
                        pg_insert(sessions)
                        .values(
                            session_id=decision.session_id,
                            anonymous_actor_id=context.session.anonymous_actor_id,
                            started_at=context.session.started_at,
                            client_version=context.session.client_version,
                            created_at=now,
                        )
                        .on_conflict_do_nothing(index_elements=["session_id"])
                    )
                except Exception:
                    # Fallback for non-PostgreSQL (e.g., SQLite in tests)
                    await session.execute(
                        insert(sessions)
                        .values(
                            session_id=decision.session_id,
                            anonymous_actor_id=context.session.anonymous_actor_id,
                            started_at=context.session.started_at,
                            client_version=context.session.client_version,
                            created_at=now,
                        )
                        .prefix_with("OR IGNORE")
                    )

                if "experiment_id" in decision.policy_metadata:
                    await session.execute(
                        pg_insert(experiment_assignments)
                        .values(
                            experiment_id=UUID(decision.policy_metadata["experiment_id"]),
                            session_id=decision.session_id,
                            assignment=decision.policy_metadata["assignment"],
                            assigned_at=decision.timestamp,
                        )
                        .on_conflict_do_nothing(index_elements=["experiment_id", "session_id"])
                    )

                # 2. Insert decision record — all columns match schema.py
                await session.execute(
                    insert(decisions).values(
                        decision_id=decision.decision_id,
                        session_id=decision.session_id,
                        timestamp=decision.timestamp,
                        state=decision.state.value if decision.state else "UNKNOWN",
                        state_confidence=decision.state_confidence,
                        safety_status=decision.safety_status.value if decision.safety_status else "UNKNOWN",
                        safety_block_reasons=[r.value for r in decision.safety_block_reasons],
                        candidate_actions=[a.value for a in decision.candidate_actions],
                        selected_action=decision.selected_action.value,
                        no_intervention_reason=decision.no_intervention_reason.value if decision.no_intervention_reason else None,
                        policy_version=decision.policy_version,
                        model_version=decision.model_version,
                        action_registry_version=decision.action_registry_version,
                        facts_version=decision.facts_version,
                        reason=decision.reason or "Pipeline completed",
                        response_text=decision.response_text,
                        shadow_mode=decision.shadow_mode,
                        created_at=now,
                    )
                )

                # 3. Insert audit log — all columns match schema.py
                await session.execute(
                    insert(audit_log).values(
                        audit_id=uuid4(),
                        decision_id=decision.decision_id,
                        timestamp=decision.timestamp,
                        context_snapshot=context.model_dump(mode="json"),
                        safety_result={
                            "status": decision.safety_status.value if decision.safety_status else "UNKNOWN",
                            "block_reasons": [r.value for r in decision.safety_block_reasons],
                        },
                        state_estimate={
                            "state": decision.state.value if decision.state else "UNKNOWN",
                            "confidence": decision.state_confidence,
                            "model_version": decision.model_version,
                            "policy_metadata": decision.policy_metadata,
                        },
                        candidate_actions=[a.value for a in decision.candidate_actions],
                        selected_action=decision.selected_action.value,
                        no_intervention_reason=decision.no_intervention_reason.value if decision.no_intervention_reason else None,
                        policy_version=decision.policy_version,
                        model_version=decision.model_version,
                        action_registry_version=decision.action_registry_version,
                        facts_version=decision.facts_version,
                        reason=decision.reason or "Pipeline completed",
                        response_text=decision.response_text,
                        shadow_mode=decision.shadow_mode,
                        created_at=now,
                    )
                )

            logger.info("decision_persisted", decision_id=str(decision.decision_id))
        except Exception as e:
            AUDIT_ERRORS.inc()
            logger.error(
                "decision_persist_failed",
                error=str(e),
                decision_id=str(decision.decision_id),
            )
            # Do NOT re-raise — this is off the critical path

    async def get_decision(self, decision_id: UUID) -> Decision | None:
        async with self.session_factory() as session:
            row = (await session.execute(select(decisions).where(decisions.c.decision_id == decision_id))).mappings().first()
        if row is None:
            return None
        values = dict(row)
        if values["timestamp"].tzinfo is None:
            values["timestamp"] = values["timestamp"].replace(tzinfo=UTC)
        async with self.session_factory() as session:
            estimate = (await session.execute(select(audit_log.c.state_estimate).where(audit_log.c.decision_id == decision_id))).scalar()
        values["policy_metadata"] = (estimate or {}).get("policy_metadata", {})
        return Decision.model_validate(values)

    async def get_context(self, decision_id: UUID) -> DecisionContext | None:
        async with self.session_factory() as session:
            data = (await session.execute(select(audit_log.c.context_snapshot).where(audit_log.c.decision_id == decision_id))).scalar()
        return DecisionContext.model_validate(data) if data else None

    async def persist_outcome(self, outcome: Outcome) -> None:
        async with self.session_factory() as session, session.begin():
            await session.execute(
                insert(outcomes).values(
                    outcome_id=outcome.outcome_id,
                    decision_id=outcome.decision_id,
                    session_id=outcome.session_id,
                    timestamp=outcome.timestamp,
                    outcome_type=outcome.outcome_type.value,
                    metadata_={**outcome.metadata, "time_to_action_ms": outcome.time_to_action_ms},
                    schema_version=outcome.schema_version,
                    created_at=datetime.now(UTC),
                )
            )

    async def record_reward_join(self, outcome_id: UUID, latency_ms: int, is_late: bool) -> None:
        async with self.session_factory() as session, session.begin():
            data = (await session.execute(select(outcomes.c.metadata_).where(outcomes.c.outcome_id == outcome_id))).scalar_one()
            await session.execute(
                update(outcomes)
                .where(outcomes.c.outcome_id == outcome_id)
                .values(metadata_={**data, "join_latency_ms": latency_ms, "is_late_join": is_late})
            )

    async def get_events(self, session_id: UUID) -> list[ConfidenceEvent]:
        async with self.session_factory() as session:
            rows = (
                (await session.execute(select(events).where(events.c.session_id == session_id).order_by(events.c.sequence_number)))
                .mappings()
                .all()
            )
        return [ConfidenceEvent.model_validate({**dict(row), "timestamp": row["timestamp"].replace(tzinfo=UTC)}) for row in rows]

    async def persist_sqs(self, outcome: Outcome, result: SessionQualityResult, version: str) -> None:
        SQS_SCORES.observe(result.clamped_score)
        async with self.session_factory() as session, session.begin():
            await session.execute(
                insert(session_quality_scores).values(
                    score_id=uuid4(),
                    session_id=outcome.session_id,
                    decision_id=outcome.decision_id,
                    outcome_id=outcome.outcome_id,
                    **result.model_dump(),
                    sqs_config_version=version,
                    computed_at=datetime.now(UTC),
                )
            )

    async def sqs_metrics(self, hours: int = 24, actor_id: str | None = None) -> dict[str, Any]:
        async with self.session_factory() as session:
            rows = (
                (
                    await session.execute(
                        select(session_quality_scores, decisions.c.selected_action)
                        .join(decisions)
                        .join(sessions, sessions.c.session_id == decisions.c.session_id)
                        .where(sessions.c.anonymous_actor_id == actor_id if actor_id is not None else true())
                        .where(session_quality_scores.c.computed_at >= datetime.now(UTC) - timedelta(hours=hours))
                    )
                )
                .mappings()
                .all()
            )
        values = [float(row["clamped_score"]) for row in rows]
        quartiles = quantiles(values, n=4, method="inclusive") if len(values) > 1 else [values[0] if values else 0.0] * 3
        return dict(
            mean=mean(values) if values else 0.0,
            median=median(values) if values else 0.0,
            p25=quartiles[0],
            p75=quartiles[2],
            total_sessions=len({r["session_id"] for r in rows}),
            harm_sessions=len({r["session_id"] for r in rows if r["harm_indicator_load"] > 0}),
            intervention_rate=sum(r["selected_action"] != ActionId.NO_INTERVENTION.value for r in rows) / len(rows) if rows else 0.0,
        )

    async def persist_event(self, event: ConfidenceEvent) -> None:
        async with self.session_factory() as session, session.begin():
            await session.execute(
                pg_insert(sessions)
                .values(
                    session_id=event.session_id,
                    anonymous_actor_id=event.anonymous_actor_id,
                    started_at=event.timestamp,
                    client_version=event.client_version,
                    created_at=datetime.now(UTC),
                )
                .on_conflict_do_nothing(index_elements=["session_id"])
            )
            values = event.model_dump()
            values["event_type"] = event.event_type.value
            await session.execute(
                pg_insert(events).values(**values, created_at=datetime.now(UTC)).on_conflict_do_nothing(index_elements=["event_id"])
            )

    async def get_session_decisions(self, session_id: UUID) -> list[Decision]:
        async with self.session_factory() as session:
            ids = (
                (
                    await session.execute(
                        select(decisions.c.decision_id).where(decisions.c.session_id == session_id).order_by(decisions.c.timestamp)
                    )
                )
                .scalars()
                .all()
            )
        result = []
        for decision_id in ids:
            decision = await self.get_decision(decision_id)
            if decision is not None:
                result.append(decision)
        return result

    async def record_outcome_bundle(
        self, outcome: Outcome, score: SessionQualityResult, version: str, messages: list[tuple[str, dict[str, Any]]]
    ) -> bool:
        """Outcome, quality score, and broker delivery intent commit atomically."""
        async with self.session_factory() as session, session.begin():
            existing = (await session.execute(select(outcomes).where(outcomes.c.outcome_id == outcome.outcome_id))).mappings().first()
            if existing is not None:
                if (
                    existing["decision_id"] != outcome.decision_id
                    or existing["session_id"] != outcome.session_id
                    or existing["outcome_type"] != outcome.outcome_type.value
                    or existing["metadata_"].get("time_to_action_ms") != outcome.time_to_action_ms
                    or {k: v for k, v in existing["metadata_"].items() if k not in {"time_to_action_ms", "join_latency_ms", "is_late_join"}}
                    != {k: v for k, v in outcome.metadata.items() if k not in {"time_to_action_ms", "join_latency_ms", "is_late_join"}}
                ):
                    raise ValueError("Outcome ID reused with different content")
                return False
            await session.execute(
                insert(outcomes).values(
                    outcome_id=outcome.outcome_id,
                    decision_id=outcome.decision_id,
                    session_id=outcome.session_id,
                    timestamp=outcome.timestamp,
                    outcome_type=outcome.outcome_type.value,
                    metadata_={**outcome.metadata, "time_to_action_ms": outcome.time_to_action_ms},
                    schema_version=outcome.schema_version,
                    created_at=datetime.now(UTC),
                )
            )
            await session.execute(
                insert(session_quality_scores).values(
                    score_id=uuid4(),
                    session_id=outcome.session_id,
                    decision_id=outcome.decision_id,
                    outcome_id=outcome.outcome_id,
                    **score.model_dump(),
                    sqs_config_version=version,
                    computed_at=datetime.now(UTC),
                )
            )
            for topic, payload in messages:
                await session.execute(
                    insert(outbox).values(
                        message_id=outcome.outcome_id,
                        topic=topic,
                        partition_key=str(outcome.session_id),
                        payload=payload,
                        created_at=datetime.now(UTC),
                        delivered=False,
                    )
                )
        SQS_SCORES.observe(score.clamped_score)
        return True
