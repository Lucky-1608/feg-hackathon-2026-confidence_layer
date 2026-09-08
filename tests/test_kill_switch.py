import asyncio
from unittest.mock import AsyncMock
from uuid import uuid4

import fakeredis.aioredis

from confidence.application.context_builder import DecisionRequest
from confidence.application.engine import DecisionEngine
from confidence.config import ShadowConfig
from confidence.domain.enums import ActionId
from confidence.domain.models import InteractionContext
from confidence.domain.policy import PolicySelector
from confidence.domain.response import ResponseGenerator
from confidence.domain.state import StateEstimator
from confidence.infrastructure.kill_switch import KillSwitch
from confidence.infrastructure.shadow_mode import ShadowModeController


async def test_controls(sample_context, action_registry, safety_contract):
    redis = fakeredis.aioredis.FakeRedis()
    switch = KillSwitch(redis)
    assert not await switch.is_active()
    await switch.activate("test", "admin")
    assert await switch.is_active()
    builder = AsyncMock()
    builder.build.return_value = sample_context
    persistence = AsyncMock()
    engine = DecisionEngine(
        builder,
        safety_contract,
        StateEstimator(),
        action_registry,
        PolicySelector(),
        ResponseGenerator(action_registry),
        persistence,
        kill_switch=switch,
    )
    req = DecisionRequest(session_id=uuid4(), anonymous_actor_id="a", client_version="1", slip_id="slip", interaction=InteractionContext())
    result = await engine.decide(req)
    assert result.decision.reason == "KILL_SWITCH"
    builder.build.assert_not_called()
    await switch.deactivate()
    engine.shadow_controller = ShadowModeController(ShadowConfig(shadow_mode="full"))
    result = await engine.decide(req)
    await asyncio.sleep(0)
    assert result.decision.selected_action == ActionId.NO_INTERVENTION
    assert result.decision.reason == "shadow_mode"
    assert persistence.persist_decision.call_args[0][0].shadow_mode
    switch.redis = AsyncMock()
    switch.redis.exists.side_effect = RuntimeError()
    assert await switch.is_active()
    await redis.aclose()


def test_shadow_stability():
    session = uuid4()
    controller = ShadowModeController(ShadowConfig(shadow_mode="percentage", shadow_percentage=50))
    assert len({controller.should_shadow(session, "actor") for _ in range(20)}) == 1
    assert ShadowModeController(ShadowConfig(shadow_mode="actor_list", shadow_actors=["a"])).should_shadow(session, "a")


async def test_kill_switch_bypasses_saturated_limiter(sample_context, action_registry, safety_contract):
    from confidence.infrastructure.backpressure import ConcurrencyLimiter

    limiter = ConcurrencyLimiter(1)
    await limiter.semaphore.acquire()
    switch = AsyncMock()
    switch.is_active.return_value = True
    engine = DecisionEngine(
        AsyncMock(),
        safety_contract,
        StateEstimator(),
        action_registry,
        PolicySelector(),
        ResponseGenerator(action_registry),
        AsyncMock(),
        kill_switch=switch,
        concurrency_limiter=limiter,
        persist=False,
    )
    result = await engine.decide(
        DecisionRequest(session_id=uuid4(), anonymous_actor_id="a", client_version="1", slip_id="s", interaction=InteractionContext())
    )
    assert result.decision.reason == "KILL_SWITCH"
    limiter.semaphore.release()
