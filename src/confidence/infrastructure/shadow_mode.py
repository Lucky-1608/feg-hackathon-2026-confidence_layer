"""Stable session assignment across processes and restarts."""

import hashlib
from uuid import UUID

from confidence.config import ShadowConfig


def stable_bucket(value: str) -> float:
    return int.from_bytes(hashlib.sha256(value.encode()).digest()[:8], "big") / 2**64 * 100


class ShadowModeController:
    def __init__(self, config: ShadowConfig | None = None) -> None:
        self.config = config or ShadowConfig()

    def should_shadow(self, session_id: UUID, actor_id: str) -> bool:
        match self.config.shadow_mode:
            case "full":
                return True
            case "percentage":
                return stable_bucket(str(session_id)) < self.config.shadow_percentage
            case "actor_list":
                return actor_id in self.config.shadow_actors
            case _:
                return False
