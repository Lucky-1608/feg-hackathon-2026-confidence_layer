"""Persistence for audit logs and decisions."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from confidence.application.engine import PersistenceProvider
from confidence.db.schema import audit_log, decisions
from confidence.domain.models import Decision, DecisionContext


class DatabasePersistenceProvider(PersistenceProvider):
    """Saves decisions and audit records asynchronously to the database."""

    def __init__(self, engine: AsyncEngine) -> None:
        self.session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async def persist_decision(self, decision: Decision, context: DecisionContext) -> None:
        """Persist a decision and its audit log to the database.

        This should fail gracefully or run in the background.
        """
        async with self.session_factory() as session, session.begin():
            # Note: This assumes the session (session_id) already exists in the `sessions` table.
            # In a real app, if the session is missing, this might violate a foreign key.
            # We assume the session is pre-created by the interaction events stream.

            # 1. Insert Decision
            await session.execute(
                decisions.insert().values(
                    decision_id=decision.decision_id,
                    session_id=decision.session_id,
                    timestamp=decision.timestamp,
                    state=decision.state.value if decision.state else None,
                    state_confidence=decision.state_confidence,
                    safety_status=decision.safety_status.value if decision.safety_status else None,
                    selected_action=decision.selected_action.value if decision.selected_action else None,
                    no_intervention_reason=decision.no_intervention_reason.value if decision.no_intervention_reason else None,
                    policy_version=decision.policy_version,
                    model_version=decision.model_version,
                    action_registry_version=decision.action_registry_version,
                    facts_version=decision.facts_version,
                )
            )

            # 2. Insert Audit Log
            # We serialize the context and decision for immutability
            await session.execute(
                audit_log.insert().values(
                    decision_id=decision.decision_id,
                    context_snapshot=context.model_dump_json(),
                    decision_snapshot=decision.model_dump_json(),
                    reason=decision.reason,
                )
            )
