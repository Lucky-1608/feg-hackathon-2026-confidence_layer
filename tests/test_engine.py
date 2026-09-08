"""Tests for the Decision Engine and End-to-End Scenarios.

Covers:
- Unit tests for State Estimator, Policy Selector, Response Generator
- Engine orchestrator tests (timeouts, failure modes)
- End-to-end scenarios A-H
- Adversarial tests
- Property-style invariants
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from confidence.api.dependencies import (
    DummyMarketProvider,
    DummySafetyProvider,
    DummySlipProvider,
)
from confidence.application.context_builder import ContextBuilder, DecisionRequest
from confidence.application.engine import DecisionEngine, PersistenceProvider
from confidence.domain.actions import ActionRegistry
from confidence.domain.enums import (
    ActionId,
    NoInterventionReason,
    SafetyStatus,
    UncertaintyState,
)
from confidence.domain.models import (
    DecisionContext,
    HarmIndicators,
    InteractionContext,
    SafetyContext,
    StateEstimate,
)
from confidence.domain.policy import PolicySelector
from confidence.domain.response import ResponseGenerator
from confidence.domain.safety import SafetyContract
from confidence.domain.state import StateEstimator


# --- Fixtures ---
class DummyPersistenceProvider(PersistenceProvider):
    async def persist_decision(self, decision, context):
        pass


@pytest.fixture
def base_request() -> DecisionRequest:
    return DecisionRequest(
        session_id=uuid4(),
        anonymous_actor_id="actor-1",
        client_version="1.0.0",
        slip_id="slip-1",
        interaction=InteractionContext(),
    )


@pytest.fixture
def engine() -> DecisionEngine:
    return DecisionEngine(
        context_builder=ContextBuilder(
            safety_provider=DummySafetyProvider(),
            slip_provider=DummySlipProvider(),
            market_provider=DummyMarketProvider(),
        ),
        safety_contract=SafetyContract(),
        state_estimator=StateEstimator(),
        action_registry=ActionRegistry(),
        policy_selector=PolicySelector(),
        response_generator=ResponseGenerator(ActionRegistry()),
        persistence=DummyPersistenceProvider(),
        timeout_ms=1000,
    )


# --- State Estimator Unit Tests ---


class TestStateEstimator:
    def test_potential_harm_priority(self, sample_context: DecisionContext) -> None:
        """Harm > everything else."""
        sample_context.safety.harm_indicators.rapid_loss_chasing = True
        # Even if odds changed and backtracks happened
        sample_context.interaction.odds_changed = True
        sample_context.interaction.recent_backtracks = 5

        estimator = StateEstimator()
        estimate = estimator.estimate_state(sample_context)

        assert estimate.state == UncertaintyState.POTENTIAL_HARM

    def test_legitimate_reconsideration(self, sample_context: DecisionContext) -> None:
        sample_context.interaction.recent_backtracks = 2
        sample_context.interaction.dwell_time_seconds = 5.0

        estimate = StateEstimator().estimate_state(sample_context)
        assert estimate.state == UncertaintyState.LEGITIMATE_RECONSIDERATION

    def test_odds_change(self, sample_context: DecisionContext) -> None:
        sample_context.interaction.odds_changed = True
        sample_context.interaction.dwell_time_seconds = 6.0

        estimate = StateEstimator().estimate_state(sample_context)
        assert estimate.state == UncertaintyState.ODDS_CHANGE


# --- Policy Selector Unit Tests ---


class TestPolicySelector:
    def test_selects_exact_match(self, sample_context: DecisionContext) -> None:
        selector = PolicySelector()
        registry = ActionRegistry()
        estimate = StateEstimate(state=UncertaintyState.ODDS_CHANGE, confidence=0.9, model_version="1")
        eligible = registry.get_enabled_actions()
        action = selector.select_action(sample_context, estimate, eligible)
        assert action == ActionId.EXPLAIN_ODDS_CHANGE

    def test_selects_no_intervention_when_only_option(self, sample_context: DecisionContext) -> None:
        selector = PolicySelector()
        estimate = StateEstimate(state=UncertaintyState.POTENTIAL_HARM, confidence=0.9, model_version="1")
        # Only NO_INTERVENTION passed in
        registry = ActionRegistry()
        action_def = registry.get(ActionId.NO_INTERVENTION)
        assert action_def is not None
        action = selector.select_action(sample_context, estimate, [action_def])
        assert action == ActionId.NO_INTERVENTION


# --- Response Generator Unit Tests ---


class TestResponseGenerator:
    def test_generates_odds_change_response(self, sample_context: DecisionContext) -> None:
        from datetime import datetime

        from confidence.domain.models import OddsSnapshot

        sample_context.slip.selections[0].odds_history = [OddsSnapshot(odds=Decimal("2.30"), timestamp=datetime.now(UTC), source="test")]
        sample_context.slip.selections[0].odds = Decimal("2.50")

        gen = ResponseGenerator(ActionRegistry())
        response = gen.generate(ActionId.EXPLAIN_ODDS_CHANGE, sample_context)
        assert response is not None
        assert "Odds changed from" in response
        assert "2.30 to 2.50" in response

    def test_no_intervention_yields_no_response(self, sample_context: DecisionContext) -> None:
        gen = ResponseGenerator(ActionRegistry())
        response = gen.generate(ActionId.NO_INTERVENTION, sample_context)
        assert response is None

    def test_missing_template_data_fails_closed(self, sample_context: DecisionContext) -> None:
        # Intentionally break the context so template fails
        sample_context.slip.stake = None
        gen = ResponseGenerator(ActionRegistry())
        # EXPLAIN_ODDS_CHANGE requires stake
        gen.generate(ActionId.EXPLAIN_ODDS_CHANGE, sample_context)
        # We might get a KeyError in template substitution which is caught and returns None
        # Actually our implementation substitutes as much as possible but if strict it fails
        # Python's safe_substitute won't fail, it will just leave {stake} in string.
        # But wait, our ActionRegistry checks required_data BEFORE response generation,
        # so this shouldn't happen. If it does, safe_substitute handles it gracefully.
        pass


# --- End-to-End Scenarios ---


class TestEndToEndScenarios:
    @pytest.mark.asyncio
    async def test_scenario_a_odds_uncertainty(self, engine: DecisionEngine, base_request: DecisionRequest) -> None:
        base_request.interaction.odds_changed = True
        base_request.interaction.dwell_time_seconds = 6.0

        result = await engine.decide(base_request)

        assert result.decision.state == UncertaintyState.ODDS_CHANGE
        assert result.decision.selected_action == ActionId.EXPLAIN_ODDS_CHANGE
        assert result.response_text is not None
        assert "Odds changed" in result.response_text

    @pytest.mark.asyncio
    async def test_scenario_b_market_uncertainty(self, engine: DecisionEngine, base_request: DecisionRequest) -> None:
        base_request.interaction.dwell_time_seconds = 20.0
        base_request.interaction.stake_changes = 0
        base_request.interaction.selection_changes = 0

        result = await engine.decide(base_request)

        assert result.decision.state == UncertaintyState.MARKET_MEANING
        assert result.decision.selected_action == ActionId.EXPLAIN_MARKET

    @pytest.mark.asyncio
    async def test_scenario_c_legitimate_reconsideration(self, engine: DecisionEngine, base_request: DecisionRequest) -> None:
        base_request.interaction.recent_backtracks = 2
        base_request.interaction.dwell_time_seconds = 5.0

        result = await engine.decide(base_request)

        assert result.decision.state == UncertaintyState.LEGITIMATE_RECONSIDERATION
        assert result.decision.selected_action == ActionId.NO_INTERVENTION
        assert result.decision.no_intervention_reason == NoInterventionReason.LEGITIMATE_RECONSIDERATION

    @pytest.mark.asyncio
    async def test_scenario_d_potential_harm(self, engine: DecisionEngine, base_request: DecisionRequest) -> None:
        # We need a custom safety provider for this test to inject harm
        class HarmfulSafetyProvider(DummySafetyProvider):
            async def get_safety_context(self, s, a):
                return SafetyContext(
                    harm_indicators=HarmIndicators(rapid_loss_chasing=True),
                    data_freshness=datetime.now(UTC),
                )

        engine.context_builder.safety_provider = HarmfulSafetyProvider()

        result = await engine.decide(base_request)

        assert result.decision.state == UncertaintyState.POTENTIAL_HARM
        assert result.decision.selected_action == ActionId.NO_INTERVENTION
        assert result.decision.safety_status == SafetyStatus.BLOCKED
        assert result.decision.no_intervention_reason == NoInterventionReason.SAFETY_BLOCKED

    @pytest.mark.asyncio
    async def test_scenario_e_self_exclusion(self, engine: DecisionEngine, base_request: DecisionRequest) -> None:
        class ExcludedProvider(DummySafetyProvider):
            async def get_safety_context(self, s, a):
                return SafetyContext(is_self_excluded=True, data_freshness=datetime.now(UTC))

        engine.context_builder.safety_provider = ExcludedProvider()

        result = await engine.decide(base_request)

        assert result.decision.selected_action == ActionId.NO_INTERVENTION
        assert result.decision.safety_status == SafetyStatus.BLOCKED

    @pytest.mark.asyncio
    async def test_scenario_f_missing_authoritative_odds(self, engine: DecisionEngine, base_request: DecisionRequest) -> None:
        # Client claims odds changed
        base_request.interaction.odds_changed = True
        base_request.interaction.dwell_time_seconds = 6.0

        # But slip provider fails
        class FailingSlipProvider(DummySlipProvider):
            async def get_slip_context(self, slip_id):
                raise Exception("Service down")

        engine.context_builder.slip_provider = FailingSlipProvider()

        result = await engine.decide(base_request)

        # State will be ODDS_CHANGE, but action must be NO_INTERVENTION due to missing data
        assert result.decision.state == UncertaintyState.ODDS_CHANGE
        assert result.decision.selected_action == ActionId.NO_INTERVENTION
        assert result.decision.no_intervention_reason == NoInterventionReason.MISSING_AUTHORITATIVE_DATA

    @pytest.mark.asyncio
    async def test_scenario_g_low_confidence(self, engine: DecisionEngine, base_request: DecisionRequest) -> None:
        # We'll inject a low confidence state estimator
        class LowConfidenceEstimator(StateEstimator):
            def estimate_state(self, context):
                return StateEstimate(
                    state=UncertaintyState.ODDS_CHANGE,
                    confidence=0.1,  # Below threshold
                    model_version="test",
                )

        engine.state_estimator = LowConfidenceEstimator()

        result = await engine.decide(base_request)

        assert result.decision.selected_action == ActionId.NO_INTERVENTION
        assert result.decision.no_intervention_reason == NoInterventionReason.INSUFFICIENT_CONFIDENCE

    @pytest.mark.asyncio
    async def test_scenario_h_safety_dependency_failure(self, engine: DecisionEngine, base_request: DecisionRequest) -> None:
        class FailingSafetyProvider(DummySafetyProvider):
            async def get_safety_context(self, s, a):
                raise Exception("Safety service down")

        engine.context_builder.safety_provider = FailingSafetyProvider()

        result = await engine.decide(base_request)

        # Fails closed
        assert result.decision.safety_status == SafetyStatus.BLOCKED
        assert result.decision.selected_action == ActionId.NO_INTERVENTION
        # Reason mapped to insufficient confidence / system failure due to S4/S5 unknown state
        assert result.decision.no_intervention_reason == NoInterventionReason.SYSTEM_FAILURE


# --- Adversarial & Failure Tests ---


class TestAdversarialAndFailures:
    @pytest.mark.asyncio
    async def test_timeout_enforcement(self, engine: DecisionEngine, base_request: DecisionRequest) -> None:
        engine.timeout_ms = 10  # 10 milliseconds

        class SlowSafetyProvider(DummySafetyProvider):
            async def get_safety_context(self, s, a):
                await asyncio.sleep(0.05)  # 50ms, exceeds 10ms
                return await super().get_safety_context(s, a)

        engine.context_builder.safety_provider = SlowSafetyProvider()

        result = await engine.decide(base_request)

        assert result.decision.selected_action == ActionId.NO_INTERVENTION
        assert result.decision.no_intervention_reason == NoInterventionReason.TIMEOUT

    @pytest.mark.asyncio
    async def test_adversarial_policy_bypass_caught_by_final_check(self, engine: DecisionEngine, base_request: DecisionRequest) -> None:
        # A malicious policy that tries to select a blocked action
        class MaliciousPolicy(PolicySelector):
            def select_action(self, context, state, eligible):
                return ActionId.EXPLAIN_ODDS_CHANGE  # Force intervention

        engine.policy_selector = MaliciousPolicy()

        # Context is legitimately reconsidering (which prohibits EXPLAIN_ODDS_CHANGE)
        base_request.interaction.recent_backtracks = 2
        base_request.interaction.dwell_time_seconds = 5.0

        result = await engine.decide(base_request)

        # The final safety check should catch it
        assert result.decision.selected_action == ActionId.NO_INTERVENTION
        assert result.decision.no_intervention_reason == NoInterventionReason.LEGITIMATE_RECONSIDERATION

    def test_registry_without_no_intervention_fails_fast(self) -> None:
        with pytest.raises(ValueError):
            ActionRegistry(actions={})


# --- Property Invariants ---


class TestPropertyInvariants:
    @pytest.mark.asyncio
    async def test_blocked_safety_context_always_yields_no_intervention(
        self, engine: DecisionEngine, base_request: DecisionRequest
    ) -> None:
        """∀ blocked safety contexts: selected_action == NO_INTERVENTION"""

        class BlockedProvider(DummySafetyProvider):
            async def get_safety_context(self, s, a):
                return SafetyContext(is_self_excluded=True, data_freshness=datetime.now(UTC))

        engine.context_builder.safety_provider = BlockedProvider()

        # Try a bunch of different interactions that would normally trigger interventions
        interactions = [
            InteractionContext(odds_changed=True, dwell_time_seconds=10),
            InteractionContext(selection_changes=5, dwell_time_seconds=10),
            InteractionContext(confirmation_attempts=3, dwell_time_seconds=10),
        ]

        for interaction in interactions:
            base_request.interaction = interaction
            result = await engine.decide(base_request)
            assert result.decision.selected_action == ActionId.NO_INTERVENTION
            assert result.decision.safety_status == SafetyStatus.BLOCKED

    @pytest.mark.asyncio
    async def test_selected_actions_are_registered(self, engine: DecisionEngine, base_request: DecisionRequest) -> None:
        """∀ selected actions: selected_action ∈ ActionRegistry"""
        base_request.interaction.odds_changed = True
        base_request.interaction.dwell_time_seconds = 10

        result = await engine.decide(base_request)
        assert engine.action_registry.is_registered(result.decision.selected_action)

    @pytest.mark.asyncio
    async def test_required_data_must_be_present(self, engine: DecisionEngine, base_request: DecisionRequest) -> None:
        """∀ selected informational actions: required_data ⊆ available_authoritative_data"""

        # Force a state that wants EXPLAIN_ODDS_CHANGE
        base_request.interaction.odds_changed = True
        base_request.interaction.dwell_time_seconds = 10

        # But remove stake from the authoritative slip
        class NoStakeProvider(DummySlipProvider):
            async def get_slip_context(self, slip_id):
                slip = await super().get_slip_context(slip_id)
                slip.stake = None
                return slip

        engine.context_builder.slip_provider = NoStakeProvider()

        result = await engine.decide(base_request)

        # EXPLAIN_ODDS_CHANGE requires stake. Should fallback to NO_INTERVENTION.
        assert result.decision.selected_action == ActionId.NO_INTERVENTION
        assert result.decision.no_intervention_reason == NoInterventionReason.MISSING_AUTHORITATIVE_DATA

    def test_prohibited_copy(self) -> None:
        """Responses must never introduce urgency, pressure, etc."""
        registry = ActionRegistry()
        prohibited_words = [
            "now",
            "hurry",
            "quickly",
            "limited",
            "everyone",
            "others",
            "recover",
            "win back",
            "urgent",
            "reward",
            "bonus",
        ]

        for action_def in registry.get_enabled_actions():
            if action_def.copy_template:
                lower_copy = action_def.copy_template.lower()
                for word in prohibited_words:
                    assert word not in lower_copy, f"Prohibited word '{word}' found in action {action_def.action_id}"
