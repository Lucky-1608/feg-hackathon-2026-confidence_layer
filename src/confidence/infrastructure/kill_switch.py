"""Global protective control. Unavailable control storage means active."""

import asyncio
import json
from datetime import UTC, datetime

from redis.asyncio import Redis

from confidence.observability.metrics import KILL_SWITCH_STATE


class KillSwitch:
    KEY = "confidence:kill_switch"

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def is_active(self) -> bool:
        try:
            async with asyncio.timeout(0.01):
                active = bool(await self.redis.exists(self.KEY))
                KILL_SWITCH_STATE.set(int(active))
                return active
        except Exception:
            KILL_SWITCH_STATE.set(1)
            return True

    async def activate(self, reason: str, activated_by: str) -> None:
        await self.redis.set(
            self.KEY, json.dumps(dict(reason=reason, activated_by=activated_by, activated_at=datetime.now(UTC).isoformat()))
        )

    async def deactivate(self) -> None:
        await self.redis.delete(self.KEY)
