# Create infrastructure/audit.py and tests/test_audit.py

audit_code = """
\"\"\"Audit Trail.

Persists full audit records for every decision.
Audit persistence must NOT block the critical decision path.
\"\"\"

from __future__ import annotations

import asyncio
import json
from typing import Protocol

from confidence.domain.models import AuditRecord
from confidence.log import get_logger

logger = get_logger("confidence.audit")


class AuditStore(Protocol):
    \"\"\"Interface for audit persistence.\"\"\"

    async def save(self, record: AuditRecord) -> None:
        \"\"\"Save an audit record.\"\"\"
        ...


class KafkaAuditStore(AuditStore):
    \"\"\"Publishes audit records to Kafka for downstream data warehousing.\"\"\"

    def __init__(self, bootstrap_servers: str, topic: str = "confidence.audit") -> None:
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        from aiokafka import AIOKafkaProducer
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else b"",
        )

    async def start(self) -> None:
        await self.producer.start()

    async def stop(self) -> None:
        await self.producer.stop()

    async def save(self, record: AuditRecord) -> None:
        try:
            key = str(record.decision_id)
            # Use json loading/dumping for Pydantic V2
            value = json.loads(record.model_dump_json())
            await self.producer.send_and_wait(
                topic=self.topic,
                key=key,
                value=value,
            )
            logger.info("audit_saved", decision_id=str(record.decision_id))
        except Exception as e:
            logger.error("audit_save_failed", error=str(e), decision_id=str(record.decision_id))
            # In production, this might fall back to a local file or DLQ
            raise


class BackgroundAuditLogger:
    \"\"\"Manages non-blocking audit persistence.\"\"\"

    def __init__(self, store: AuditStore) -> None:
        self.store = store

    def log_decision(self, record: AuditRecord) -> None:
        \"\"\"Fire and forget audit logging.\"\"\"
        asyncio.create_task(self._safe_log(record))

    async def _safe_log(self, record: AuditRecord) -> None:
        try:
            await self.store.save(record)
        except Exception as e:
            logger.error("background_audit_failed", error=str(e))
"""

with open("src/confidence/infrastructure/audit.py", "w") as f:
    f.write(audit_code.strip() + "\n")

test_audit_code = """
\"\"\"Tests for Audit Trail.\"\"\"

import asyncio
import pytest
from datetime import datetime, UTC
from uuid import uuid4

from confidence.domain.models import AuditRecord, DecisionContext, Session, SlipContext, SafetyContext, InteractionContext, SafetyResult, StateEstimate
from confidence.domain.enums import ActionId, SafetyStatus, UncertaintyState
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
            interaction=InteractionContext()
        ),
        safety_result=SafetyResult(status=SafetyStatus.SAFE, timestamp=datetime.now(UTC)),
        state_estimate=StateEstimate(state=UncertaintyState.ODDS_CHANGE, confidence=0.9, model_version="1"),
        candidate_actions=[],
        selected_action=ActionId.NO_INTERVENTION,
        policy_version="1",
        model_version="1",
        action_registry_version="1",
        reason="test"
    )
    
    # Fire and forget
    logger.log_decision(record)
    
    # Allow background task to run
    await asyncio.sleep(0.01)
    
    assert len(store.records) == 1
    assert store.records[0].audit_id == record.audit_id
"""

with open("tests/test_audit.py", "w") as f:
    f.write(test_audit_code.strip() + "\n")

