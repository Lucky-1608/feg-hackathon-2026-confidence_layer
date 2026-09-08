"""Domain Ports (Protocols).

The domain owns its interfaces (hexagonal architecture).
Infrastructure adapters must implement these protocols.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable
from uuid import UUID

from confidence.domain.models import (
    Decision,
    DecisionContext,
    InteractionContext,
    MarketContext,
    Outcome,
    SafetyContext,
    Session,
    SessionSummary,
    SlipContext,
)


@runtime_checkable
class SafetyProvider(Protocol):
    """Provides authoritative safety state for a session/user."""

    async def get_safety_context(self, session_id: UUID, anonymous_actor_id: str) -> SafetyContext:
        """Fetch safety context (self-exclusion, restrictions, harm indicators)."""
        ...


@runtime_checkable
class SlipProvider(Protocol):
    """Provides authoritative betslip state."""

    async def get_slip_context(self, slip_id: str) -> SlipContext:
        """Fetch authoritative slip details (selections, stake, returns)."""
        ...


@runtime_checkable
class MarketProvider(Protocol):
    """Provides authoritative market data."""

    async def get_market_context(self, market_id: str) -> MarketContext:
        """Fetch authoritative market definition and odds history."""
        ...


@runtime_checkable
class SessionProvider(Protocol):
    """Provides session metadata."""

    async def get_session(self, session_id: UUID) -> Session:
        """Fetch session metadata."""
        ...


@runtime_checkable
class PersistenceProvider(Protocol):
    """Interface for async audit logging."""

    async def persist_decision(self, decision: Decision, context: DecisionContext) -> None:
        """Persist a decision and its audit log to the database."""
        ...


@runtime_checkable
class SessionStateProvider(Protocol):
    """Accumulated interaction signals from the event stream."""

    async def get_interaction_state(self, session_id: UUID) -> InteractionContext | None: ...


class OutcomePersistenceProvider(PersistenceProvider, Protocol):
    async def get_decision(self, decision_id: UUID) -> Decision | None: ...
    async def get_context(self, decision_id: UUID) -> DecisionContext | None: ...
    async def persist_outcome(self, outcome: Outcome) -> None: ...
    async def record_reward_join(self, outcome_id: UUID, latency_ms: int, is_late: bool) -> None: ...


class SessionHistoryProvider(Protocol):
    async def get_recent_sessions(self, anonymous_actor_id: str, lookback_days: int = 30) -> list[SessionSummary]: ...
