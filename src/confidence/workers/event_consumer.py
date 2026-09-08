"""Event Consumer Worker.

Long-running process that consumes events from Redpanda/Kafka
and processes them via EventProcessor.
"""

from __future__ import annotations

import asyncio
from typing import Any

from aiokafka import AIOKafkaConsumer
from aiokafka.structs import OffsetAndMetadata, TopicPartition
from pydantic import ValidationError

from confidence.application.event_processor import EventProcessor
from confidence.config import load_config
from confidence.domain.event_contracts import ConfidenceEvent
from confidence.infrastructure.dlq import DeadLetterQueue, KafkaDeadLetterQueue
from confidence.infrastructure.event_ordering import SequenceValidator
from confidence.infrastructure.session_state import RedisSessionStore
from confidence.log import configure_logging, get_logger
from confidence.observability.metrics import EVENT_ERRORS

logger = get_logger("confidence.event_consumer")


class ReliableEventConsumer:
    """Stop on an unacknowledged record; never commit a later offset over it."""

    def __init__(
        self,
        consumer: Any,
        processor: EventProcessor,
        validator: SequenceValidator,
        dlq: DeadLetterQueue,
        retries: int = 3,
        base_delay: float = 0.1,
    ) -> None:
        self.consumer = consumer
        self.processor = processor
        self.validator = validator
        self.dlq = dlq
        self.retries = retries
        self.base_delay = base_delay

    async def process_record(self, msg: Any) -> None:
        try:
            event = ConfidenceEvent.model_validate_json(msg.value)
        except (ValueError, ValidationError):
            await self.dlq.push(msg.value, "validation_error")
        else:
            for attempt in range(self.retries + 1):
                try:
                    valid = await self.validator.validate_and_increment(event.session_id, event.sequence_number, event.event_id)
                    if valid:
                        await self.processor.process_event(event)
                    else:
                        await self.dlq.push(msg.value, "sequence_gap", event.session_id)
                    break
                except Exception:
                    EVENT_ERRORS.labels(event_type=event.event_type.value).inc()
                    if attempt == self.retries:
                        await self.dlq.push(msg.value, "processing_error", event.session_id)
                    else:
                        await asyncio.sleep(self.base_delay * 2**attempt)
        await self.consumer.commit({TopicPartition(msg.topic, msg.partition): OffsetAndMetadata(msg.offset + 1, "")})

    async def run(self) -> None:
        async for msg in self.consumer:
            await self.process_record(msg)


async def run_consumer() -> None:
    """Run the event consumer loop."""
    config = load_config()
    configure_logging(config.log_level)

    logger.info("starting_event_consumer", servers=config.kafka.bootstrap_servers)

    # Initialize dependencies
    # wait, session store needs redis.
    from redis.asyncio import Redis

    redis_client = Redis.from_url(config.redis.url, decode_responses=False)
    session_store = RedisSessionStore(redis_client)
    from sqlalchemy.ext.asyncio import create_async_engine

    from confidence.infrastructure.persistence import DatabasePersistenceProvider

    database = create_async_engine(config.database.url)
    processor = EventProcessor(session_store, DatabasePersistenceProvider(database))

    dlq = KafkaDeadLetterQueue(config.kafka.bootstrap_servers)
    await dlq.start()

    consumer = AIOKafkaConsumer(
        "confidence.events",
        bootstrap_servers=config.kafka.bootstrap_servers,
        group_id="confidence-event-processor",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )

    await consumer.start()
    logger.info("event_consumer_ready")

    try:
        await ReliableEventConsumer(consumer, processor, SequenceValidator(redis_client), dlq).run()
    except asyncio.CancelledError:
        logger.info("consumer_cancelled")
    finally:
        await consumer.stop()
        await dlq.stop()
        await redis_client.aclose()
        await database.dispose()


if __name__ == "__main__":
    asyncio.run(run_consumer())
