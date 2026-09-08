"""Persistence for audit logs and decisions.

Architectural constraint: Persistence is downstream of the decision.
It must NEVER cause a decision failure. All persistence calls are
fire-and-forget from the engine's perspective.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from confidence.db.schema import audit_log, decisions, sessions
from confidence.domain.models import Decision, DecisionContext
from confidence.domain.ports import PersistenceProvider
from confidence.log import get_logger

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
                        created_at=now,
                    )
                )

            logger.info("decision_persisted", decision_id=str(decision.decision_id))
        except Exception as e:
            logger.error(
                "decision_persist_failed",
                error=str(e),
                decision_id=str(decision.decision_id),
            )
            # Do NOT re-raise — this is off the critical path
