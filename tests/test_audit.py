"""Tests for Audit Trail."""

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from confidence.domain.enums import ActionId, SafetyStatus, UncertaintyState
from confidence.domain.models import (
    AuditRecord,
    DecisionContext,
    InteractionContext,
    SafetyContext,
    SafetyResult,
    Session,
    SlipContext,
    StateEstimate,
)
from confidence.infrastructure.audit import AuditStore, BackgroundAuditLogger


class InMemoryAuditStore(AuditStore):
    def __init__(self) -> None:
        self.records: list[AuditRecord] = []

    async def save(self, record: AuditRecord) -> None:
        self.records.append(record)


@pytest.mark.asyncio
async def test_background_audit_logger() -> None:
    store = InMemoryAuditStore()
    logger = BackgroundAuditLogger(store)

    record = AuditRecord(
        audit_id=uuid4(),
        decision_id=uuid4(),
        timestamp=datetime.now(UTC),
        context_snapshot=DecisionContext(
            session=Session(session_id=uuid4(), anonymous_actor_id="a", started_at=datetime.now(UTC), client_version="1"),
            slip=SlipContext(slip_id="s", selections=[], created_at=datetime.now(UTC)),
            safety=SafetyContext(),
            interaction=InteractionContext(),
        ),
        safety_result=SafetyResult(status=SafetyStatus.SAFE, timestamp=datetime.now(UTC)),
        state_estimate=StateEstimate(state=UncertaintyState.ODDS_CHANGE, confidence=0.9, model_version="1"),
        candidate_actions=[],
        selected_action=ActionId.NO_INTERVENTION,
        policy_version="1",
        model_version="1",
        action_registry_version="1",
        reason="test",
    )

    # Fire and forget
    logger.log_decision(record)

    # Allow background task to run
    await asyncio.sleep(0.01)

    assert len(store.records) == 1
    assert store.records[0].audit_id == record.audit_id
