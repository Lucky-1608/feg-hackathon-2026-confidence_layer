"""Event Bus Abstraction.

Provides a unified interface for publishing events to the message broker.
Includes an in-memory implementation for testing and a Kafka/Redpanda
implementation for production.
"""

from __future__ import annotations

import json
from typing import Protocol

from aiokafka import AIOKafkaProducer

from confidence.domain.event_contracts import ConfidenceEvent
from confidence.log import get_logger

logger = get_logger("confidence.event_bus")


class EventPublisher(Protocol):
    """Interface for publishing events."""

    async def start(self) -> None:
        """Start the publisher."""
        ...

    async def stop(self) -> None:
        """Stop the publisher."""
        ...

    async def publish(self, event: ConfidenceEvent) -> None:
        """Publish a domain event to the message broker."""
        ...


class KafkaEventPublisher(EventPublisher):
    """Kafka/Redpanda implementation of the event publisher."""

    def __init__(self, bootstrap_servers: str, topic: str = "confidence.events") -> None:
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        """Initialize and start the Kafka producer."""
        if self.producer is None:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8"),
            )
            await self.producer.start()
            logger.info("kafka_producer_started", servers=self.bootstrap_servers)

    async def stop(self) -> None:
        """Stop the Kafka producer."""
        if self.producer is not None:
            await self.producer.stop()
            self.producer = None
            logger.info("kafka_producer_stopped")

    async def publish(self, event: ConfidenceEvent) -> None:
        """Publish an event."""
        if self.producer is None:
            raise RuntimeError("Producer is not started")

        try:
            # Use session_id as the partition key to guarantee ordering per session
            key = str(event.session_id)
            value = event.model_dump(mode="json")

            await self.producer.send_and_wait(
                topic=self.topic,
                key=key,
                value=value,
            )
            logger.debug("event_published", event_id=str(event.event_id), event_type=event.event_type.value)
        except Exception as e:
            logger.error(
                "event_publish_failed",
                error=str(e),
                event_id=str(event.event_id),
            )
            raise


class InMemoryEventPublisher(EventPublisher):
    """In-memory publisher for testing."""

    def __init__(self) -> None:
        self.published_events: list[ConfidenceEvent] = []

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass

    async def publish(self, event: ConfidenceEvent) -> None:
        self.published_events.append(event)
