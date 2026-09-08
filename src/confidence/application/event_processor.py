"""Event Processor.

Processes incoming events from the message broker to update session state.
"""

from __future__ import annotations

from confidence.domain.enums import EventType
from confidence.domain.event_contracts import ConfidenceEvent
from confidence.infrastructure.persistence import DatabasePersistenceProvider
from confidence.infrastructure.session_state import RedisSessionStore
from confidence.log import get_logger

logger = get_logger("confidence.event_processor")


class EventProcessor:
    """Processes domain events to update interaction context."""

    def __init__(self, session_store: RedisSessionStore, persistence: DatabasePersistenceProvider | None = None) -> None:
        self.session_store = session_store
        self.persistence = persistence

    async def process_event(self, event: ConfidenceEvent) -> None:
        """Process a single event and update the session."""
        if self.persistence is not None:
            await self.persistence.persist_event(event)
        updates = self.interaction_updates(event)
        if updates:
            await self.session_store.update_interaction(event.session_id, updates, event_id=event.event_id)

    @staticmethod
    def interaction_updates(event: ConfidenceEvent) -> dict[str, int | float | bool]:
        updates: dict[str, int | float | bool] = {}

        if event.event_type == EventType.SESSION_START:
            # We would create the session, but it might be handled upstream.
            # We just note the session age might start.
            pass
        elif event.event_type == EventType.NAVIGATION_BACK:
            updates["recent_backtracks"] = 1
        elif event.event_type == EventType.SELECTION_CHANGE:
            updates["selection_changes"] = 1
        elif event.event_type == EventType.STAKE_CHANGE:
            updates["stake_changes"] = 1
        elif event.event_type == EventType.ODDS_UPDATE:
            updates["odds_changed"] = True
        elif event.event_type == EventType.CONFIRM_ATTEMPT:
            updates["confirmation_attempts"] = 1
        elif event.event_type == EventType.HESITATION_DETECTED and "dwell_time_seconds" in event.payload:
            updates["dwell_time_seconds"] = float(event.payload["dwell_time_seconds"])

        return updates
