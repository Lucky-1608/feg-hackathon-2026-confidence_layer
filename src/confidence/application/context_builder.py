"""Context Builder.

Constructs the DecisionContext from the incoming request and authoritative providers.
Ensures that safety data and market facts are never trusted from the client.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel

from confidence.domain.harm.detector import HarmClassifier
from confidence.domain.models import DecisionContext, InteractionContext, Session
from confidence.domain.ports import MarketProvider, SafetyProvider, SessionHistoryProvider, SessionStateProvider, SlipProvider
from confidence.infrastructure.resilience import CircuitBreakerRegistry, ResilienceConfig, execute_with_resilience


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
        session_state_provider: SessionStateProvider | None = None,
        session_history_provider: SessionHistoryProvider | None = None,
        harm_detector: HarmClassifier | None = None,
    ) -> None:
        self.safety_provider = safety_provider
        self.slip_provider = slip_provider
        self.market_provider = market_provider
        self.session_state_provider = session_state_provider
        self.session_history_provider = session_history_provider
        self.harm_detector = harm_detector or HarmClassifier()

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
            safety = await execute_with_resilience(
                self.safety_provider.get_safety_context,
                ResilienceConfig(timeout_seconds=0.5, retries=1, circuit_breaker=CircuitBreakerRegistry.get("safety_provider")),
                request.session_id,
                request.anonymous_actor_id,
            )
        except Exception:
            # If provider fails, fail closed by providing stale safety context
            # This triggers S5 safety block (SAFETY_DEPENDENCY_UNAVAILABLE -> SYSTEM_FAILURE)
            from datetime import timedelta

            from confidence.domain.models import SafetyContext

            safety = SafetyContext(data_freshness=datetime.now(UTC) - timedelta(days=1))

        if self.session_history_provider is not None:
            try:
                history = await execute_with_resilience(
                    self.session_history_provider.get_recent_sessions,
                    ResilienceConfig(timeout_seconds=0.02, retries=0, circuit_breaker=CircuitBreakerRegistry.get("history_provider")),
                    request.anonymous_actor_id,
                )
                detected = self.harm_detector.classify(history)
                if not safety.harm_indicators.has_any():
                    safety.harm_indicators = detected
            except Exception:
                safety.data_freshness = None

        # 3. Get authoritative slip context
        # If this fails, we can't provide factual actions, but NO_INTERVENTION might still be OK
        try:
            slip = await execute_with_resilience(
                self.slip_provider.get_slip_context,
                ResilienceConfig(timeout_seconds=0.5, retries=1, circuit_breaker=CircuitBreakerRegistry.get("slip_provider")),
                request.slip_id,
            )
        except Exception:
            # Fallback empty slip, will cause eligibility to drop factual actions

            from confidence.domain.models import SlipContext

            slip = SlipContext(slip_id=request.slip_id, selections=[], created_at=datetime.now(UTC))

        # 4. Get authoritative market context
        markets = []
        for selection in slip.selections:
            try:
                market = await execute_with_resilience(
                    self.market_provider.get_market_context,
                    ResilienceConfig(timeout_seconds=0.5, retries=1, circuit_breaker=CircuitBreakerRegistry.get("market_provider")),
                    selection.market_id,
                )
                markets.append(market)
            except Exception:
                pass  # Missing market data will drop eligibility for market explanations

        interaction = request.interaction
        if self.session_state_provider is not None:
            try:
                accumulated = await execute_with_resilience(
                    self.session_state_provider.get_interaction_state,
                    ResilienceConfig(timeout_seconds=0.02, retries=0, circuit_breaker=CircuitBreakerRegistry.get("session_provider")),
                    request.session_id,
                )
                if accumulated is not None:
                    merged = accumulated.model_dump()
                    merged.update(request.interaction.model_dump(exclude_unset=True))
                    interaction = InteractionContext.model_validate(merged)
            except Exception:
                pass  # Explicit request-only degradation for interaction telemetry.

        return DecisionContext(
            session=session,
            slip=slip,
            markets=markets,
            safety=safety,
            interaction=interaction,
        )
