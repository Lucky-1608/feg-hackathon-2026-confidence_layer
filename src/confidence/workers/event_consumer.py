"""Event Consumer Worker.

Long-running process that consumes events from Redpanda/Kafka
and processes them via EventProcessor.
"""

from __future__ import annotations

import asyncio
import json

from aiokafka import AIOKafkaConsumer
from pydantic import ValidationError

from confidence.application.event_processor import EventProcessor
from confidence.config import load_config
from confidence.domain.event_contracts import ConfidenceEvent
from confidence.infrastructure.dlq import KafkaDeadLetterQueue
from confidence.infrastructure.session_state import RedisSessionStore
from confidence.log import configure_logging, get_logger

logger = get_logger("confidence.event_consumer")


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
    processor = EventProcessor(session_store)

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
        async for msg in consumer:
            try:
                # 1. Parse and validate
                data = json.loads(msg.value)
                event = ConfidenceEvent.model_validate(data)

                # 2. Process
                await processor.process_event(event)

                # 3. Commit offset
                await consumer.commit()

            except (json.JSONDecodeError, ValidationError) as e:
                logger.error("invalid_event", error=str(e))
                await dlq.push(msg.value, f"Validation Error: {e}")
                await consumer.commit()
            except Exception as e:
                logger.error("processing_error", error=str(e))
                await dlq.push(msg.value, f"Processing Error: {e}")
                # Do not commit on system errors, rely on retry/DLQ policy
    except asyncio.CancelledError:
        logger.info("consumer_cancelled")
    finally:
        await consumer.stop()
        await dlq.stop()
        await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(run_consumer())
