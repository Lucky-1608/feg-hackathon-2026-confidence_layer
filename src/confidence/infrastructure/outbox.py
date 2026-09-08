"""At-least-once broker delivery of committed outcomes and rewards."""

from sqlalchemy import select, update

from confidence.db.schema import outbox
from confidence.infrastructure.event_bus import EventPublisher
from confidence.infrastructure.persistence import DatabasePersistenceProvider


class OutboxDispatcher:
    def __init__(self, persistence: DatabasePersistenceProvider, publisher: EventPublisher) -> None:
        self.persistence = persistence
        self.publisher = publisher

    async def flush(self, limit: int = 100) -> int:
        delivered = 0
        async with self.persistence.session_factory() as session, session.begin():
            rows = (
                (
                    await session.execute(
                        select(outbox)
                        .where(outbox.c.delivered.is_(False))
                        .order_by(outbox.c.created_at, outbox.c.topic)
                        .limit(limit)
                        .with_for_update(skip_locked=True)
                    )
                )
                .mappings()
                .all()
            )
            for row in rows:
                await self.publisher.publish_message(row["topic"], row["partition_key"], row["payload"])
                await session.execute(
                    update(outbox).where(outbox.c.message_id == row["message_id"], outbox.c.topic == row["topic"]).values(delivered=True)
                )
                delivered += 1
        return delivered
