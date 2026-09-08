"""Session State & Idempotency in Redis.

Manages distributed state for sessions and API idempotency.
Uses optimistic locking (WATCH/MULTI/EXEC) for safe concurrent updates.
"""

from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from redis.asyncio import Redis

from confidence.domain.models import InteractionContext, Session
from confidence.log import get_logger

logger = get_logger("confidence.session_state")


class RedisSessionStore:
    """Stores active sessions and interaction context."""

    def __init__(self, redis: Redis, ttl_seconds: int = 86400) -> None:
        self.redis = redis
        self.ttl = ttl_seconds

    def _session_key(self, session_id: UUID) -> str:
        return f"session:{session_id}"

    def _interaction_key(self, session_id: UUID) -> str:
        return f"interaction:{session_id}"

    async def save_session(self, session: Session) -> None:
        """Save basic session metadata."""
        key = self._session_key(session.session_id)
        payload = session.model_dump(mode="json")
        await self.redis.set(key, json.dumps(payload), ex=self.ttl)

    async def get_session(self, session_id: UUID) -> Session | None:
        """Retrieve session metadata."""
        key = self._session_key(session_id)
        data = await self.redis.get(key)
        if not data:
            return None
        return Session.model_validate_json(data)

    async def update_interaction(self, session_id: UUID, updates: dict[str, Any]) -> InteractionContext:
        """Safely update interaction context using optimistic locking."""
        key = self._interaction_key(session_id)

        async with self.redis.pipeline(transaction=True) as pipe:
            while True:
                try:
                    await pipe.watch(key)
                    data = await pipe.get(key)

                    from typing import cast

                    current = cast(dict[str, Any], json.loads(data)) if data else InteractionContext().model_dump(mode="json")

                    # Apply updates
                    for k, v in updates.items():
                        # Numeric additions vs replacements
                        if k in ("recent_backtracks", "selection_changes", "stake_changes", "confirmation_attempts"):
                            current[k] = current.get(k, 0) + v
                        else:
                            current[k] = v

                    updated_json = json.dumps(current)

                    cast(Any, pipe).multi()
                    pipe.set(key, updated_json, ex=self.ttl)
                    await pipe.execute()

                    return InteractionContext.model_validate(current)

                except Exception as e:
                    # WatchError means another client modified the key
                    import redis.exceptions

                    if isinstance(e, redis.exceptions.WatchError):
                        continue
                    raise

    async def get_interaction(self, session_id: UUID) -> InteractionContext | None:
        """Retrieve current interaction context."""
        key = self._interaction_key(session_id)
        data = await self.redis.get(key)
        if not data:
            return None
        return InteractionContext.model_validate_json(data)


class RedisIdempotencyStore:
    """Idempotency store using Redis SET NX."""

    def __init__(self, redis: Redis, ttl_seconds: int = 3600) -> None:
        self.redis = redis
        self.ttl = ttl_seconds

    def _key(self, idempotency_key: str) -> str:
        return f"idemp:{idempotency_key}"

    async def acquire(self, idempotency_key: str) -> bool:
        """Attempt to acquire idempotency lock. Returns True if acquired (first attempt)."""
        key = self._key(idempotency_key)
        # SET NX EX
        result = await self.redis.set(key, "1", ex=self.ttl, nx=True)
        return bool(result)

    async def save_response(self, idempotency_key: str, response: dict[str, Any]) -> None:
        """Save the successful response for a given idempotency key."""
        key = self._key(idempotency_key)
        payload = json.dumps(response)
        await self.redis.set(key, payload, ex=self.ttl)

    async def get_response(self, idempotency_key: str) -> dict[str, Any] | None:
        """Retrieve a saved response."""
        key = self._key(idempotency_key)
        data = await self.redis.get(key)
        if not data or data == b"1":
            return None
        from typing import cast

        return cast(dict[str, Any], json.loads(data))
