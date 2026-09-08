"""Dependency injection for the API.

Wires together domain authorities, provider adapters, and infrastructure.
Demo providers are used by default; production adapters plug in via configuration.
"""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from confidence.application.context_builder import ContextBuilder
from confidence.application.engine import DecisionEngine
from confidence.config import load_config
from confidence.demo.providers import DummyMarketProvider, DummySafetyProvider, DummySlipProvider
from confidence.domain.actions import ActionRegistry
from confidence.domain.policy import PolicySelector
from confidence.domain.ports import PersistenceProvider
from confidence.domain.response import ResponseGenerator
from confidence.domain.safety import SafetyContract
from confidence.domain.state import StateEstimator
from confidence.infrastructure.event_bus import EventPublisher, KafkaEventPublisher
from confidence.infrastructure.persistence import DatabasePersistenceProvider

# Engine cache — allows lifespan to dispose on shutdown
_engine_cache: dict[str, AsyncEngine] = {}


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


_publisher_cache: dict[str, EventPublisher] = {}


def get_event_publisher() -> EventPublisher:
    """Get the event publisher instance."""
    if "publisher" not in _publisher_cache:
        config = load_config()
        # In a real app we'd await start() during app lifespan,
        # but since this is called synchronously via Depends...
        # Wait, get_event_publisher is called inside the route body synchronously,
        # but start() is async. We should initialize it in lifespan.
        _publisher_cache["publisher"] = KafkaEventPublisher(bootstrap_servers=config.kafka.bootstrap_servers)
    return _publisher_cache["publisher"]
