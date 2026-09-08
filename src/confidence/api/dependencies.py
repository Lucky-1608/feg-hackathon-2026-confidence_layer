"""Dependency injection for the API.

Wires together domain authorities, provider adapters, and infrastructure.
Demo providers are restricted to the local demo. Production adapters are not yet configured.
"""

from __future__ import annotations

from functools import lru_cache

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from confidence.application.context_builder import ContextBuilder
from confidence.application.engine import DecisionEngine
from confidence.config import load_config
from confidence.demo.providers import DummyMarketProvider, DummySafetyProvider, DummySlipProvider
from confidence.domain.actions import ActionRegistry
from confidence.domain.ml.contextual_bandit import BanditPolicySelector
from confidence.domain.ml.hesitation_classifier import LightGBMStateEstimator
from confidence.domain.policy import PolicySelector
from confidence.domain.response import ResponseGenerator
from confidence.domain.safety import SafetyContract
from confidence.domain.state import StateEstimator
from confidence.evaluation.holdout import HoldoutManager
from confidence.infrastructure.event_bus import EventPublisher, KafkaEventPublisher
from confidence.infrastructure.kill_switch import KillSwitch
from confidence.infrastructure.persistence import DatabasePersistenceProvider
from confidence.infrastructure.session_history import DatabaseSessionHistoryProvider
from confidence.infrastructure.session_state import RedisSessionStateProvider, RedisSessionStore
from confidence.infrastructure.shadow_mode import ShadowModeController
from confidence.infrastructure.unavailable import UnavailableAuthorities

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


def get_persistence_provider() -> DatabasePersistenceProvider:
    return DatabasePersistenceProvider(get_engine())


def get_action_registry() -> ActionRegistry:
    return ActionRegistry()


def get_safety_contract() -> SafetyContract:
    config = load_config()
    return SafetyContract(
        confidence_threshold=max(config.safety.confidence_threshold, config.decision.state_confidence_threshold),
        safety_data_max_age_seconds=config.safety.data_max_age_seconds,
    )


def get_state_estimator() -> StateEstimator:
    config = load_config().model
    return _state_estimator(config.state_estimator_type, config.state_estimator_model_path, config.state_estimator_confidence_threshold)


@lru_cache(maxsize=8)
def _state_estimator(kind: str, path: str | None, threshold: float) -> StateEstimator:
    return LightGBMStateEstimator(path, threshold) if kind == "lgbm" else StateEstimator()


def get_policy_selector() -> PolicySelector:
    config = load_config().policy
    return _policy_selector(config.policy_type, config.bandit_model_path, config.bandit_exploration_rate)


@lru_cache(maxsize=8)
def _policy_selector(kind: str, path: str | None, exploration: float) -> PolicySelector:
    return BanditPolicySelector(path, exploration_rate=exploration) if kind == "bandit" else PolicySelector()


def get_response_generator(
    registry: ActionRegistry = Depends(get_action_registry),  # noqa: B008,
) -> ResponseGenerator:
    return ResponseGenerator(registry)


def get_context_builder(
    request: Request = None,  # type: ignore[assignment]
) -> ContextBuilder:
    config = load_config()
    config.require_runtime()
    if not config.demo_mode:
        authorities = getattr(request.app.state, "authorities", None) if request is not None else None
        safety, slip, market = authorities or (UnavailableAuthorities(),) * 3
        return ContextBuilder(
            safety,
            slip,
            market,
            session_state_provider=RedisSessionStateProvider(RedisSessionStore(request.app.state.redis)) if request else None,
            session_history_provider=DatabaseSessionHistoryProvider(get_engine()),
        )
    return ContextBuilder(
        safety_provider=DummySafetyProvider(),
        slip_provider=DummySlipProvider(),
        market_provider=DummyMarketProvider(),
        session_history_provider=DatabaseSessionHistoryProvider(get_engine()) if not load_config().demo_mode else None,
        session_state_provider=RedisSessionStateProvider(RedisSessionStore(request.app.state.redis))
        if request is not None and hasattr(request.app.state, "redis")
        else None,
    )


def get_decision_engine(
    request: Request,
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
        kill_switch=KillSwitch(request.app.state.redis) if hasattr(request.app.state, "redis") else None,
        shadow_controller=ShadowModeController(config.shadow),
        experiment_manager=getattr(request.app.state, "experiments", None),
        concurrency_limiter=getattr(request.app.state, "concurrency_limiter", None),
        holdout_manager=HoldoutManager() if not config.demo_mode else None,
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
