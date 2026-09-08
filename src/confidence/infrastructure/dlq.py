"""Dead Letter Queue (DLQ).

Handles events that fail processing or validation.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from confidence.log import get_logger
from confidence.observability.metrics import DLQ_MESSAGES

logger = get_logger("confidence.dlq")


class DeadLetterQueue(Protocol):
    """Interface for dead-lettering failed events."""

    async def push(self, raw_message: str | bytes, error_reason: str, session_id: UUID | None = None) -> None:
        """Push a failed message to the DLQ."""
        ...


class KafkaDeadLetterQueue(DeadLetterQueue):
    """Kafka/Redpanda implementation of DLQ."""

    def __init__(self, bootstrap_servers: str, topic: str = "confidence.dlq") -> None:
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        # Uses the same AIOKafkaProducer logic as EventPublisher
        from aiokafka import AIOKafkaProducer

        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else b"",
        )

    async def start(self) -> None:
        """Start the DLQ producer."""
        await self.producer.start()

    async def stop(self) -> None:
        """Stop the DLQ producer."""
        await self.producer.stop()

    async def push(self, raw_message: str | bytes, error_reason: str, session_id: UUID | None = None) -> None:
        """Push a failed message to DLQ."""
        if isinstance(raw_message, bytes):
            try:
                msg_str = raw_message.decode("utf-8")
            except UnicodeDecodeError:
                msg_str = raw_message.hex()
        else:
            msg_str = raw_message

        payload = {
            "failed_at": datetime.now(UTC).isoformat(),
            "error_reason": error_reason,
            "raw_message": msg_str,
        }

        key = str(session_id) if session_id else "unknown"

        await self.producer.send_and_wait(
            topic=self.topic,
            key=key,
            value=payload,
        )
        DLQ_MESSAGES.labels(
            reason=error_reason if error_reason in {"sequence_gap", "validation_error", "processing_error"} else "other"
        ).inc()
        logger.info("dlq_pushed", error_reason=error_reason)
