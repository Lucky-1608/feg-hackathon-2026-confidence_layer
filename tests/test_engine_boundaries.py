"""Regression evidence for safety ordering, policy eligibility and audit facts."""

import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from confidence.application.context_builder import ContextBuilder, DecisionRequest
from confidence.application.engine import DecisionEngine
from confidence.demo.providers import DummyMarketProvider, DummySafetyProvider, DummySlipProvider
from confidence.domain.actions import ActionRegistry
from confidence.domain.enums import ActionId, NoInterventionReason, SafetyStatus, UncertaintyState
from confidence.domain.models import InteractionContext, SafetyContext, StateEstimate
from confidence.domain.policy import PolicySelector
from confidence.domain.response import ResponseGenerator
from confidence.domain.safety import SafetyContract
from confidence.domain.state import StateEstimator


@pytest.fixture
def request_data() -> DecisionRequest:
    return DecisionRequest(
        session_id=uuid4(),
        anonymous_actor_id="actor-1",
        client_version="boundary-test",
        slip_id="slip-1",
        interaction=InteractionContext(odds_changed=True, dwell_time_seconds=6),
    )


@pytest.fixture
def engine() -> DecisionEngine:
    registry = ActionRegistry()
    return DecisionEngine(
        context_builder=ContextBuilder(DummySafetyProvider(), DummySlipProvider(), DummyMarketProvider()),
        safety_contract=SafetyContract(),
        state_estimator=StateEstimator(),
        action_registry=registry,
        policy_selector=PolicySelector(),
        response_generator=ResponseGenerator(registry),
        persistence=Mock(persist_decision=AsyncMock()),
    )


@pytest.mark.parametrize("safety_case", ["excluded", "restricted", "harm", "unknown", "stale"])
async def test_unsafe_context_never_reaches_policy(engine, request_data, monkeypatch, safety_case):
    safety = SafetyContext(data_freshness=datetime.now(UTC))
    if safety_case == "excluded":
        safety.is_self_excluded = True
    elif safety_case == "restricted":
        safety.has_protective_restrictions = True
    elif safety_case == "harm":
        safety.harm_indicators.rapid_loss_chasing = True
    elif safety_case == "unknown":
        safety.data_freshness = None
    else:
        safety.data_freshness = datetime.now(UTC) - timedelta(days=1)
    monkeypatch.setattr(engine.context_builder.safety_provider, "get_safety_context", AsyncMock(return_value=safety))
    policy = Mock(side_effect=AssertionError("Unsafe context reached policy"))
    monkeypatch.setattr(engine.policy_selector, "select_action", policy)

    result = await engine.decide(request_data)

    policy.assert_not_called()
    assert result.decision.safety_status != SafetyStatus.SAFE
    assert result.decision.selected_action == ActionId.NO_INTERVENTION
    assert result.decision.candidate_actions == [ActionId.NO_INTERVENTION]
    assert result.response_text is None


@pytest.mark.parametrize(
    ("state", "confidence", "reason"),
    [
        (UncertaintyState.ODDS_CHANGE, 0.1, NoInterventionReason.INSUFFICIENT_CONFIDENCE),
        (UncertaintyState.UNKNOWN, 1, NoInterventionReason.INSUFFICIENT_CONFIDENCE),
        (UncertaintyState.LEGITIMATE_RECONSIDERATION, 0.9, NoInterventionReason.LEGITIMATE_RECONSIDERATION),
        (UncertaintyState.NO_UNCERTAINTY, 0.9, NoInterventionReason.NO_UNCERTAINTY_DETECTED),
    ],
)
async def test_abstention_gate_never_reaches_policy(engine, request_data, monkeypatch, state, confidence, reason):
    monkeypatch.setattr(
        engine.state_estimator,
        "estimate_state",
        Mock(return_value=StateEstimate(state=state, confidence=confidence, model_version="test")),
    )
    policy = Mock(return_value=ActionId.EXPLAIN_ODDS_CHANGE)
    monkeypatch.setattr(engine.policy_selector, "select_action", policy)

    result = await engine.decide(request_data)

    policy.assert_not_called()
    assert result.decision.selected_action == ActionId.NO_INTERVENTION
    assert result.decision.no_intervention_reason == reason
    assert result.decision.candidate_actions == [ActionId.NO_INTERVENTION]


async def test_registered_but_ineligible_policy_action_is_rejected(engine, request_data, monkeypatch):
    policy = Mock(return_value=ActionId.EXPLAIN_MARKET)
    monkeypatch.setattr(engine.policy_selector, "select_action", policy)

    result = await engine.decide(request_data)

    policy.assert_called_once()
    assert result.decision.state == UncertaintyState.ODDS_CHANGE
    assert ActionId.EXPLAIN_MARKET not in result.decision.candidate_actions
    assert result.decision.selected_action == ActionId.NO_INTERVENTION
    assert result.decision.no_intervention_reason == NoInterventionReason.SYSTEM_FAILURE
    assert result.response_text is None


async def test_safety_reason_precedes_missing_facts(engine, request_data):
    request_data.anonymous_actor_id = "actor-self-excluded"
    request_data.slip_id = "slip-missing-odds"
    result = await engine.decide(request_data)
    assert result.decision.no_intervention_reason == NoInterventionReason.SAFETY_BLOCKED
    assert result.decision.reason == NoInterventionReason.SAFETY_BLOCKED.value


@pytest.mark.parametrize("actor", ["actor-1", "actor-self-excluded"])
async def test_audit_keeps_actual_facts_and_isolates_later_mutation(engine, request_data, actor):
    request_data.anonymous_actor_id = actor
    result = await engine.decide(request_data)
    assert result.context is not None
    expected_context = result.context.model_copy(deep=True)
    expected_decision = result.decision.model_copy(deep=True)

    request_data.interaction.dwell_time_seconds = 999
    result.context.slip.stake = Decimal("999")
    result.decision.reason = "modified after response"
    await asyncio.sleep(0)

    engine.persistence.persist_decision.assert_awaited_once()
    saved_decision, saved_context = engine.persistence.persist_decision.await_args.args
    assert saved_decision == expected_decision
    assert saved_context == expected_context
    assert saved_context.slip.stake == Decimal("10")
    assert saved_context.slip.selections[0].odds == Decimal("2.5")
    assert saved_context.markets[0].market_definition == "Predict the winner."
    assert saved_context.safety.data_freshness is not None
    assert saved_context.safety.is_self_excluded == (actor == "actor-self-excluded")


async def test_timeout_audit_labels_unavailable_context(engine, request_data, monkeypatch):
    async def blocked_build(request):
        await asyncio.Event().wait()

    monkeypatch.setattr(engine.context_builder, "build", blocked_build)
    engine.timeout_ms = 5
    result = await engine.decide(request_data)
    await asyncio.sleep(0)
    assert result.decision.no_intervention_reason == NoInterventionReason.TIMEOUT
    _, context = engine.persistence.persist_decision.await_args.args
    assert context.context_version == "unavailable"
    assert context.safety.data_freshness is None


async def test_slow_audit_does_not_block_decision(engine, request_data, monkeypatch):
    release = asyncio.Event()
    finished = asyncio.Event()

    async def persist(decision, context):
        await release.wait()
        finished.set()

    monkeypatch.setattr(engine.persistence, "persist_decision", persist)
    try:
        result = await asyncio.wait_for(engine.decide(request_data), timeout=1)
        assert result.decision.selected_action == ActionId.EXPLAIN_ODDS_CHANGE
        assert not finished.is_set()
    finally:
        release.set()
        await asyncio.wait_for(finished.wait(), timeout=1)


async def test_internal_exception_detail_is_not_returned(engine, request_data, monkeypatch):
    monkeypatch.setattr(engine.state_estimator, "estimate_state", Mock(side_effect=RuntimeError("private upstream detail")))
    result = await engine.decide(request_data)
    assert result.decision.selected_action == ActionId.NO_INTERVENTION
    assert "private upstream detail" not in result.decision.reason
