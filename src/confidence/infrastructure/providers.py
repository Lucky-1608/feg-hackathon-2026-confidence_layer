"""Infrastructure adapters and interfaces.

Provides authoritative data that cannot be trusted from the client.
"""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from confidence.domain.models import MarketContext, SafetyContext, SlipContext


class SafetyProvider(Protocol):
    """Provides authoritative safety state for a session/user."""

    async def get_safety_context(self, session_id: UUID, anonymous_actor_id: str) -> SafetyContext:
        """Fetch safety context (self-exclusion, restrictions, harm indicators)."""
        ...


class SlipProvider(Protocol):
    """Provides authoritative betslip state."""

    async def get_slip_context(self, slip_id: str) -> SlipContext:
        """Fetch authoritative slip details (selections, stake, returns)."""
        ...


class MarketProvider(Protocol):
    """Provides authoritative market data."""

    async def get_market_context(self, market_id: str) -> MarketContext:
        """Fetch authoritative market definition and odds history."""
        ...
