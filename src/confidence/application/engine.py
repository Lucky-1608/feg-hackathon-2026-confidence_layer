"""Decision Engine Orchestrator.

Coordinates the complete end-to-end pipeline:
1. Build context
2. Evaluate safety
3. Estimate state
4. Check confidence
5. Determine eligible actions
6. Select policy action
7. Perform final safety check
8. Generate response
9. Construct decision record
10. Fire-and-forget audit persistence
11. Return result

Architectural constraint: Persistence NEVER blocks the decision response.
Safety is a hard constraint — the pipeline fails closed on any safety ambiguity.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import UTC, datetime
from uuid import uuid4

from opentelemetry import trace

from confidence.application.context_builder import ContextBuilder, DecisionRequest
from confidence.domain.actions import ActionRegistry
from confidence.domain.enums import ActionId, NoInterventionReason, SafetyStatus, UncertaintyState
from confidence.domain.ml.contextual_bandit import selection_metadata
from confidence.domain.models import Decision, DecisionContext
from confidence.domain.policy import PolicySelector
from confidence.domain.ports import PersistenceProvider
from confidence.domain.response import ResponseGenerator
from confidence.domain.safety import SafetyContract
from confidence.domain.state import StateEstimator
from confidence.evaluation.ab_test import ExperimentManager
from confidence.evaluation.holdout import HoldoutManager
from confidence.infrastructure.background import schedule
from confidence.infrastructure.backpressure import ConcurrencyLimiter
from confidence.infrastructure.kill_switch import KillSwitch
from confidence.infrastructure.shadow_mode import ShadowModeController
from confidence.log import get_logger
from confidence.observability.correlation import request_id
from confidence.observability.metrics import AUDIT_ERRORS, DECISIONS, HARM_INDICATORS, NO_INTERVENTION, SAFETY_BLOCKS, SHADOW_DECISIONS
from confidence.observability.tracing import get_tracer

tracer = get_tracer("confidence.engine")
logger = get_logger("confidence.engine")


class DecisionResult:
    """The result of the decision pipeline."""

    def __init__(self, decision: Decision, response_text: str | None = None, context: DecisionContext | None = None) -> None:
        self.decision = decision
        self.response_text = response_text
        self.context = context


class DecisionEngine:
    """Central orchestrator for the Confidence Layer.

    Executes the decision pipeline under a strict timeout budget.
    All failures on the critical path produce NO_INTERVENTION.
    Audit persistence is fire-and-forget — it never blocks the response.
    """

    def __init__(
        self,
        context_builder: ContextBuilder,
        safety_contract: SafetyContract,
        state_estimator: StateEstimator,
        action_registry: ActionRegistry,
        policy_selector: PolicySelector,
        response_generator: ResponseGenerator,
        persistence: PersistenceProvider,
        timeout_ms: int = 100,
        kill_switch: KillSwitch | None = None,
        shadow_controller: ShadowModeController | None = None,
        clock: Callable[[], datetime] | None = None,
        persist: bool = True,
        experiment_manager: ExperimentManager | None = None,
        holdout_manager: HoldoutManager | None = None,
        concurrency_limiter: ConcurrencyLimiter | None = None,
    ) -> None:
        self.context_builder = context_builder
        self.safety_contract = safety_contract
        self.state_estimator = state_estimator
        self.action_registry = action_registry
        self.policy_selector = policy_selector
        self.response_generator = response_generator
        self.persistence = persistence
        self.timeout_ms = timeout_ms
        self.clock = clock or (lambda: datetime.now(UTC))
        self.persist = persist
        self.experiment_manager = experiment_manager
        self.holdout_manager = holdout_manager
        self.concurrency_limiter = concurrency_limiter
        self.kill_switch = kill_switch
        self.shadow_controller = shadow_controller or ShadowModeController()

    @tracer.start_as_current_span("decision_pipeline")
    async def decide(self, request: DecisionRequest) -> DecisionResult:
        """Execute the decision pipeline with a strict timeout."""
        try:
            result = await asyncio.wait_for(
                self._limited_pipeline(request),
                timeout=self.timeout_ms / 1000.0,
            )
        except TimeoutError:
            result = self._build_failure_decision(request, NoInterventionReason.TIMEOUT, "Execution exceeded timeout")
        except Exception as e:
            logger.error("pipeline_failure", error=str(e), session_id=str(request.session_id))
            result = self._build_failure_decision(request, NoInterventionReason.SYSTEM_FAILURE, "Decision pipeline unavailable")

        try:
            shadowed = self.shadow_controller.should_shadow(request.session_id, request.anonymous_actor_id)
        except Exception:
            result = self._build_failure_decision(request, NoInterventionReason.SYSTEM_FAILURE, "Shadow control unavailable")
            shadowed = False
        result.decision.policy_metadata["request_id"] = request_id.get()
        result.decision.shadow_mode = shadowed
        d = result.decision
        span = trace.get_current_span()
        for key, value in {
            "session_id": str(d.session_id),
            "safety_status": d.safety_status.value,
            "state": d.state.value,
            "selected_action": d.selected_action.value,
        }.items():
            span.set_attribute(key, value)
        if self.persist:
            DECISIONS.labels(status=d.safety_status.value, action=d.selected_action.value, state=d.state.value).inc()
            if d.no_intervention_reason:
                NO_INTERVENTION.labels(reason=d.no_intervention_reason.value).inc()
            for reason in d.safety_block_reasons:
                SAFETY_BLOCKS.labels(reason=reason.value).inc()
            if result.context:
                for name, value in result.context.safety.harm_indicators.model_dump().items():
                    if name in {"rapid_loss_chasing", "escalating_stakes", "session_duration_extreme", "loss_recovery_pattern"} and value:
                        HARM_INDICATORS.labels(indicator=name).inc()
            if shadowed:
                SHADOW_DECISIONS.inc()
        # Fire-and-forget audit persistence — NEVER blocks the response
        if self.persist:
            self._schedule_persistence(result.decision, request, result.context)

        if shadowed:
            shown = result.decision.model_copy(
                update=dict(
                    selected_action=ActionId.NO_INTERVENTION,
                    no_intervention_reason=NoInterventionReason.SHADOW_MODE,
                    reason="shadow_mode",
                    response_text=None,
                )
            )
            return DecisionResult(shown, context=result.context)
        return result

    async def _limited_pipeline(self, request: DecisionRequest) -> DecisionResult:
        if self.kill_switch is not None and await self.kill_switch.is_active():
            return self._build_failure_decision(request, NoInterventionReason.KILL_SWITCH, "KILL_SWITCH")
        if self.concurrency_limiter is None:
            return await self._controlled_pipeline(request)
        async with self.concurrency_limiter:
            return await self._controlled_pipeline(request)

    async def _controlled_pipeline(self, request: DecisionRequest) -> DecisionResult:
        if self.holdout_manager is not None and self.holdout_manager.is_holdout(request.session_id):
            return self._build_failure_decision(request, NoInterventionReason.HOLDOUT, "holdout")
        manager = self.experiment_manager
        if manager is not None and not manager.available:
            raise RuntimeError("Experiment configuration unavailable")
        if manager is not None and manager.active is not None:
            definition = manager.active
            assignment = await manager.get_assignment(request.session_id, definition.experiment_id)
            policy = manager.policies[definition.treatment_policy] if assignment == "treatment" else self.policy_selector
            estimator = manager.estimators[definition.treatment_estimator] if assignment == "treatment" else self.state_estimator
            result = await self._execute_pipeline(request, policy, estimator)
            result.decision.policy_metadata.update(experiment_id=str(definition.experiment_id), assignment=assignment)
            return result
        return await self._execute_pipeline(request)

    def _schedule_persistence(self, decision: Decision, request: DecisionRequest, context: DecisionContext | None) -> None:
        """Schedule audit persistence as a background task.

        This is intentionally fire-and-forget. If persistence fails,
        we log the error but never let it affect the decision response.
        """

        # Copy before scheduling so later request/result mutations cannot alter the receipt.
        decision_snapshot = decision.model_copy(deep=True)
        if context is None:
            # A timeout/provider failure may prevent a complete context being assembled.
            # Label this explicitly; do not represent reconstructed data as executed facts.
            from confidence.domain.models import SafetyContext, Session, SlipContext

            context = DecisionContext(
                session=Session(
                    session_id=request.session_id,
                    anonymous_actor_id=request.anonymous_actor_id,
                    started_at=decision.timestamp,
                    client_version=request.client_version,
                ),
                slip=SlipContext(slip_id=request.slip_id, selections=[], created_at=decision.timestamp),
                safety=SafetyContext(),
                interaction=request.interaction,
                context_version="unavailable",
            )
        context_snapshot = context.model_copy(deep=True)

        async def _persist() -> None:
            try:
                await self.persistence.persist_decision(decision_snapshot, context_snapshot)
            except Exception as e:
                AUDIT_ERRORS.inc()
                logger.error(
                    "audit_persist_failed",
                    error=str(e),
                    decision_id=str(decision.decision_id),
                )

        schedule(_persist())

    async def _execute_pipeline(
        self, request: DecisionRequest, policy_selector: PolicySelector | None = None, state_estimator: StateEstimator | None = None
    ) -> DecisionResult:
        """The core orchestration logic."""
        policy = policy_selector or self.policy_selector
        estimator = state_estimator or self.state_estimator
        selection_metadata.set({})
        # 1. Build Context
        with tracer.start_as_current_span("build_context"):
            context = await self.context_builder.build(request)
        now = self.clock()

        # 2. Evaluate Safety (Can we intervene?)
        with tracer.start_as_current_span("evaluate_safety"):
            safety_result = self.safety_contract.evaluate_safety(context.safety, now)

        # 3. Estimate State (What is happening?)
        with tracer.start_as_current_span("estimate_state"):
            state_estimate = estimator.estimate_state(context)

        # 4. Check Confidence
        confidence_reason = self.safety_contract.check_state_confidence(state_estimate)

        # Also check legitimate reconsideration which forces NO_INTERVENTION
        recon_reason = self.safety_contract.check_legitimate_reconsideration(state_estimate)

        # 5. Apply hard gates BEFORE exposing any candidates to Policy Authority.
        available_data_keys = self._compute_available_data_keys(context)
        no_intervention_reason: NoInterventionReason | None = None
        if safety_result.status != SafetyStatus.SAFE:
            no_intervention_reason = self.safety_contract.safety_block_to_no_intervention_reason(safety_result.block_reasons)
        elif confidence_reason:
            no_intervention_reason = confidence_reason
        elif recon_reason:
            no_intervention_reason = recon_reason
        elif state_estimate.state == UncertaintyState.NO_UNCERTAINTY:
            no_intervention_reason = NoInterventionReason.NO_UNCERTAINTY_DETECTED

        no_action = self.action_registry.get(ActionId.NO_INTERVENTION)
        assert no_action is not None  # ActionRegistry enforces this invariant at construction.
        eligible_actions = [no_action]
        selected_action = ActionId.NO_INTERVENTION
        if no_intervention_reason is None:
            with tracer.start_as_current_span("filter_eligible"):
                eligible_actions = self.action_registry.get_eligible_for_state(state_estimate.state, available_data_keys)
            preferred_action_id = policy.state_to_preferred_action.get(state_estimate.state)
            preferred_def = self.action_registry.get(preferred_action_id) if preferred_action_id else None
            if preferred_def and not set(preferred_def.required_data).issubset(available_data_keys):
                no_intervention_reason = NoInterventionReason.MISSING_AUTHORITATIVE_DATA
                eligible_actions = [no_action]
            else:
                # 6. Policy can choose ONLY from the gated, registered candidate set.
                with tracer.start_as_current_span("select_policy"):
                    selected_action = policy.select_action(context, state_estimate, eligible_actions)
                if selected_action not in {action.action_id for action in eligible_actions}:
                    selected_action = ActionId.NO_INTERVENTION
                    no_intervention_reason = NoInterventionReason.SYSTEM_FAILURE

        # 7. Final Safety Check
        with tracer.start_as_current_span("final_safety_check"):
            final_block_reason = self.safety_contract.final_safety_check(
                selected_action, safety_result, state_estimate, self.action_registry.get(selected_action)
            )
        if final_block_reason:
            selected_action = ActionId.NO_INTERVENTION
            no_intervention_reason = final_block_reason

        # Missing data check for informational actions
        if selected_action != ActionId.NO_INTERVENTION:
            action_def = self.action_registry.get(selected_action)
            if not action_def or not all(req in available_data_keys for req in action_def.required_data):
                selected_action = ActionId.NO_INTERVENTION
                no_intervention_reason = NoInterventionReason.MISSING_AUTHORITATIVE_DATA

        # 8. Generate Response
        response_text = None
        if selected_action != ActionId.NO_INTERVENTION:
            with tracer.start_as_current_span("generate_response"):
                response_text = self.response_generator.generate(selected_action, context)
            if not response_text:
                # Fallback if generation fails
                selected_action = ActionId.NO_INTERVENTION
                no_intervention_reason = NoInterventionReason.SYSTEM_FAILURE

        # 9. Construct Decision Record
        decision = Decision(
            decision_id=uuid4(),
            session_id=context.session.session_id,
            timestamp=now,
            state=state_estimate.state,
            state_confidence=state_estimate.confidence,
            safety_status=safety_result.status,
            safety_block_reasons=safety_result.block_reasons,
            candidate_actions=[a.action_id for a in eligible_actions],
            selected_action=selected_action,
            no_intervention_reason=no_intervention_reason,
            policy_version=selection_metadata.get({}).get("effective_policy", policy.VERSION),
            policy_metadata=selection_metadata.get({}),
            model_version=state_estimate.model_version,
            action_registry_version=self.action_registry.version,
            facts_version="1",
            reason=no_intervention_reason.value if no_intervention_reason else "Pipeline completed",
            response_text=response_text,
        )

        # 10. Return result (persistence is handled in decide())
        return DecisionResult(decision=decision, response_text=response_text, context=context)

    @staticmethod
    def _compute_available_data_keys(context: DecisionContext) -> set[str]:
        """Compute which data keys are actually available from authoritative sources.

        Only adds a key if the underlying data actually exists — never blindly
        claims availability based on container presence alone.
        """
        available: set[str] = set()

        if context.slip.stake is not None:
            available.add("stake")
        if context.slip.potential_return is not None:
            available.add("potential_return")

        if context.slip.selections:
            selection = context.slip.selections[0]
            # Only claim old_odds if odds_history actually has entries
            if selection.odds_history:
                available.add("old_odds")
            available.add("new_odds")
            available.add("selections_summary")
            available.add("selection_count")

        if context.markets:
            market = context.markets[0]
            if market.market_name:
                available.add("market_name")
            if market.event_name:
                available.add("event_name")
            if market.market_definition:
                available.add("market_definition")

        return available

    def _build_failure_decision(self, request: DecisionRequest, reason: NoInterventionReason, detail: str) -> DecisionResult:
        """Create a fail-closed decision for unexpected errors."""
        now = self.clock()

        decision = Decision(
            decision_id=uuid4(),
            session_id=request.session_id,
            timestamp=now,
            state=UncertaintyState.UNKNOWN,
            state_confidence=0.0,
            safety_status=SafetyStatus.UNKNOWN,
            candidate_actions=[ActionId.NO_INTERVENTION],
            selected_action=ActionId.NO_INTERVENTION,
            no_intervention_reason=reason,
            policy_version=self.policy_selector.VERSION,
            model_version=self.state_estimator.VERSION,
            action_registry_version=self.action_registry.version,
            reason=detail,
        )
        return DecisionResult(decision=decision)
