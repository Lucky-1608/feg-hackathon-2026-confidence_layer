"""Fail-closed placeholders until an operator supplies authoritative adapters."""

from uuid import UUID

from confidence.domain.models import MarketContext, SafetyContext, SlipContext


class UnavailableAuthorities:
    async def get_safety_context(self, session_id: UUID, anonymous_actor_id: str) -> SafetyContext:
        return SafetyContext()

    async def get_slip_context(self, slip_id: str) -> SlipContext:
        raise RuntimeError("Authoritative slip adapter unavailable")

    async def get_market_context(self, market_id: str) -> MarketContext:
        raise RuntimeError("Authoritative market adapter unavailable")
