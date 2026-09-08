"""Dependency injection for the API.

Wires together domain authorities, provider adapters, and infrastructure.
Demo providers are used by default; production adapters plug in via configuration.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from confidence.application.context_builder import ContextBuilder
from confidence.application.engine import DecisionEngine, PersistenceProvider
from confidence.config import load_config
from confidence.domain.actions import ActionRegistry
from confidence.domain.models import (
    HarmIndicators,
    MarketContext,
    OddsSnapshot,
    SafetyContext,
    Selection,
    SlipContext,
)
from confidence.domain.policy import PolicySelector
from confidence.domain.response import ResponseGenerator
from confidence.domain.safety import SafetyContract
from confidence.domain.state import StateEstimator
from confidence.infrastructure.persistence import DatabasePersistenceProvider
from confidence.infrastructure.providers import MarketProvider, SafetyProvider, SlipProvider

# Engine cache — allows lifespan to dispose on shutdown
_engine_cache: dict[str, AsyncEngine] = {}


class DummySafetyProvider(SafetyProvider):
    """Synthetic safety provider for demo scenarios.

    Branches on actor_id — NEVER use in production.
    """

    async def get_safety_context(self, session_id: UUID, anonymous_actor_id: str) -> SafetyContext:
        if anonymous_actor_id == "actor-safety-down":
            raise RuntimeError("Simulated Safety Service Failure")

        harm = HarmIndicators(rapid_loss_chasing=(anonymous_actor_id == "actor-harm"))
        is_excluded = anonymous_actor_id == "actor-self-excluded"

        return SafetyContext(
            is_self_excluded=is_excluded,
            harm_indicators=harm,
            data_freshness=datetime.now(UTC),
        )


class DummySlipProvider(SlipProvider):
    """Synthetic slip provider for demo scenarios."""

    async def get_slip_context(self, slip_id: str) -> SlipContext:
        if slip_id == "slip-down":
            raise RuntimeError("Simulated Slip Service Failure")

        odds_hist = []
        if slip_id != "slip-missing-odds":
            odds_hist = [
                OddsSnapshot(
                    odds=Decimal("2.30"),
                    timestamp=datetime.now(UTC),
                    source="test",
                )
            ]

        return SlipContext(
            slip_id=slip_id,
            selections=[
                Selection(
                    selection_id="sel-1",
                    market_id="mkt-1",
                    event_id="evt-1",
                    event_name="Demo Match",
                    market_name="Match Winner",
                    odds=Decimal("2.5"),
                    odds_history=odds_hist,
                )
            ],
            stake=Decimal("10.0"),
            potential_return=Decimal("25.0"),
            created_at=datetime.now(UTC),
        )


class DummyMarketProvider(MarketProvider):
    """Synthetic market provider for demo scenarios."""

    async def get_market_context(self, market_id: str) -> MarketContext:
        return MarketContext(
            market_id=market_id,
            market_name="Match Winner",
            event_name="Demo Match",
            market_definition="Predict the winner.",
            data_freshness=datetime.now(UTC),
        )


def get_engine() -> AsyncEngine:
    """Get or create the async database engine."""
    if "engine" not in _engine_cache:
        config = load_config()
        _engine_cache["engine"] = create_async_engine(
            config.database.url,
            pool_size=config.database.pool_size,
            max_overflow=config.database.max_overflow,
            pool_pre_ping=True,
            echo=False,
        )
    return _engine_cache["engine"]


def get_persistence_provider() -> PersistenceProvider:
    return DatabasePersistenceProvider(get_engine())


def get_action_registry() -> ActionRegistry:
    return ActionRegistry()


def get_safety_contract() -> SafetyContract:
    return SafetyContract()


def get_state_estimator() -> StateEstimator:
    return StateEstimator()


def get_policy_selector() -> PolicySelector:
    return PolicySelector()


def get_response_generator(
    registry: ActionRegistry = Depends(get_action_registry),  # noqa: B008,
) -> ResponseGenerator:
    return ResponseGenerator(registry)


def get_context_builder() -> ContextBuilder:
    return ContextBuilder(
        safety_provider=DummySafetyProvider(),
        slip_provider=DummySlipProvider(),
        market_provider=DummyMarketProvider(),
    )


def get_decision_engine(
    context_builder: ContextBuilder = Depends(get_context_builder),  # noqa: B008
    safety_contract: SafetyContract = Depends(get_safety_contract),  # noqa: B008
    state_estimator: StateEstimator = Depends(get_state_estimator),  # noqa: B008
    action_registry: ActionRegistry = Depends(get_action_registry),  # noqa: B008
    policy_selector: PolicySelector = Depends(get_policy_selector),  # noqa: B008
    response_generator: ResponseGenerator = Depends(get_response_generator),  # noqa: B008
) -> DecisionEngine:
    config = load_config()
    return DecisionEngine(
        context_builder=context_builder,
        safety_contract=safety_contract,
        state_estimator=state_estimator,
        action_registry=action_registry,
        policy_selector=policy_selector,
        response_generator=response_generator,
        persistence=get_persistence_provider(),
        timeout_ms=config.decision.timeout_ms,
    )
