"""Permanent assignment uses a stable digest, never Python's salted hash()."""

from uuid import UUID

from confidence.infrastructure.shadow_mode import stable_bucket


class HoldoutManager:
    HOLDOUT_PERCENTAGE = 5

    def is_holdout(self, session_id: UUID) -> bool:
        return stable_bucket("holdout:" + str(session_id)) < self.HOLDOUT_PERCENTAGE
