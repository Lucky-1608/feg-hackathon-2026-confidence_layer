"""Context Builder.

Constructs the DecisionContext from the incoming request and authoritative providers.
Ensures that safety data and market facts are never trusted from the client.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel

from confidence.domain.models import DecisionContext, InteractionContext, Session
from confidence.infrastructure.providers import MarketProvider, SafetyProvider, SlipProvider


class DecisionRequest(BaseModel):
    """The incoming API request for a decision."""

    session_id: UUID
    anonymous_actor_id: str
    client_version: str
    slip_id: str
    interaction: InteractionContext


class ContextBuilder:
    """Builds a complete, trustworthy DecisionContext."""

    def __init__(
        self,
        safety_provider: SafetyProvider,
        slip_provider: SlipProvider,
        market_provider: MarketProvider,
    ) -> None:
        self.safety_provider = safety_provider
        self.slip_provider = slip_provider
        self.market_provider = market_provider

    async def build(self, request: DecisionRequest) -> DecisionContext:
        """Construct the context safely."""

        # 1. Construct session
        session = Session(
            session_id=request.session_id,
            anonymous_actor_id=request.anonymous_actor_id,
            started_at=datetime.now(UTC),  # Or get from session store
            client_version=request.client_version,
        )

        # 2. Get authoritative safety context
        try:
            safety = await self.safety_provider.get_safety_context(
                request.session_id, request.anonymous_actor_id
            )
        except Exception:
            # If provider fails, fail closed by providing stale safety context
            # This triggers S5 safety block (SAFETY_DEPENDENCY_UNAVAILABLE -> SYSTEM_FAILURE)
            from datetime import timedelta

            from confidence.domain.models import SafetyContext

            safety = SafetyContext(data_freshness=datetime.now(UTC) - timedelta(days=1))

        # 3. Get authoritative slip context
        # If this fails, we can't provide factual actions, but NO_INTERVENTION might still be OK
        try:
            slip = await self.slip_provider.get_slip_context(request.slip_id)
        except Exception:
            # Fallback empty slip, will cause eligibility to drop factual actions

            from confidence.domain.models import SlipContext

            slip = SlipContext(
                slip_id=request.slip_id, selections=[], created_at=datetime.now(UTC)
            )

        # 4. Get authoritative market context
        markets = []
        for selection in slip.selections:
            try:
                market = await self.market_provider.get_market_context(selection.market_id)
                markets.append(market)
            except Exception:
                pass  # Missing market data will drop eligibility for market explanations

        return DecisionContext(
            session=session,
            slip=slip,
            markets=markets,
            safety=safety,
            interaction=request.interaction,
        )
