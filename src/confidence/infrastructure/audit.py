"""Audit Trail.

Persists full audit records for every decision.
Audit persistence must NOT block the critical decision path.
"""

from __future__ import annotations

import asyncio
import json
from typing import Protocol

from confidence.domain.models import AuditRecord
from confidence.log import get_logger

logger = get_logger("confidence.audit")


class AuditStore(Protocol):
    """Interface for audit persistence."""

    async def save(self, record: AuditRecord) -> None:
        """Save an audit record."""
        ...


class KafkaAuditStore(AuditStore):
    """Publishes audit records to Kafka for downstream data warehousing."""

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
    """Manages non-blocking audit persistence."""

    def __init__(self, store: AuditStore) -> None:
        self.store = store

    def log_decision(self, record: AuditRecord) -> None:
        """Fire and forget audit logging."""
        asyncio.create_task(self._safe_log(record))

    async def _safe_log(self, record: AuditRecord) -> None:
        try:
            await self.store.save(record)
        except Exception as e:
            logger.error("background_audit_failed", error=str(e))
