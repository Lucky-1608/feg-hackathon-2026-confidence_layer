"""Event Ordering.

Validates sequence numbers to enforce strict ordering of events per session.
"""

from __future__ import annotations

from uuid import UUID

from redis.asyncio import Redis

from confidence.log import get_logger

logger = get_logger("confidence.event_ordering")


class SequenceValidator:
    """Validates and tracks event sequence numbers using Redis."""

    def __init__(self, redis: Redis, ttl_seconds: int = 86400) -> None:
        self.redis = redis
        self.ttl = ttl_seconds

    def _seq_key(self, session_id: UUID) -> str:
        return f"seq:{session_id}"

    async def validate_and_increment(self, session_id: UUID, sequence_number: int, event_id: UUID | None = None) -> bool:
        """Validate that the sequence number is exactly the next expected one.

        If valid, increments the counter and returns True.
        If invalid (duplicate or gap), returns False.
        """
        key = self._seq_key(session_id)

        # Uses Lua script for atomic validation and increment
        script = """
        if ARGV[3] ~= '' and redis.call('GET', KEYS[2]) == ARGV[3] then
            return 1
        end
        local current = redis.call('GET', KEYS[1])
        local expected = 0
        if current then
            expected = tonumber(current)
        end

        local received = tonumber(ARGV[1])

        if received == expected then
            redis.call('SET', KEYS[1], expected + 1, 'EX', ARGV[2])
            if ARGV[3] ~= '' then redis.call('SET', KEYS[2], ARGV[3], 'EX', ARGV[2]) end
            return 1
        else
            return 0
        end
        """

        result = await self.redis.eval(script, 2, key, f"{key}:last", sequence_number, self.ttl, str(event_id) if event_id else "")
        return bool(result)
