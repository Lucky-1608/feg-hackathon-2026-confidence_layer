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
    MarketContext,
    SafetyContext,
    Session,
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
