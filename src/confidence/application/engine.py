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
import contextlib
from datetime import UTC, datetime
from uuid import uuid4

from confidence.application.context_builder import ContextBuilder, DecisionRequest
from confidence.domain.actions import ActionRegistry
from confidence.domain.enums import ActionId, NoInterventionReason, SafetyStatus, UncertaintyState
from confidence.domain.models import Decision, DecisionContext
from confidence.domain.policy import PolicySelector
from confidence.domain.ports import PersistenceProvider
from confidence.domain.response import ResponseGenerator
from confidence.domain.safety import SafetyContract
from confidence.domain.state import StateEstimator
from confidence.log import get_logger

logger = get_logger("confidence.engine")


class DecisionResult:
    """The result of the decision pipeline."""

    def __init__(self, decision: Decision, response_text: str | None = None) -> None:
        self.decision = decision
        self.response_text = response_text


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
    ) -> None:
        self.context_builder = context_builder
        self.safety_contract = safety_contract
        self.state_estimator = state_estimator
        self.action_registry = action_registry
        self.policy_selector = policy_selector
        self.response_generator = response_generator
        self.persistence = persistence
        self.timeout_ms = timeout_ms

    async def decide(self, request: DecisionRequest) -> DecisionResult:
        """Execute the decision pipeline with a strict timeout."""
        try:
            result = await asyncio.wait_for(
                self._execute_pipeline(request),
                timeout=self.timeout_ms / 1000.0,
            )
        except TimeoutError:
            result = self._build_failure_decision(request, NoInterventionReason.TIMEOUT, "Execution exceeded timeout")
        except Exception as e:
            logger.error("pipeline_failure", error=str(e), session_id=str(request.session_id))
            result = self._build_failure_decision(request, NoInterventionReason.SYSTEM_FAILURE, f"Unexpected error: {e}")

        # Fire-and-forget audit persistence — NEVER blocks the response
        self._schedule_persistence(result.decision, request)

        return result

    def _schedule_persistence(self, decision: Decision, request: DecisionRequest) -> None:
        """Schedule audit persistence as a background task.

        This is intentionally fire-and-forget. If persistence fails,
        we log the error but never let it affect the decision response.
        """

        async def _persist() -> None:
            try:
                # Build a minimal context for audit — we don't re-fetch providers
                from confidence.domain.models import InteractionContext, SafetyContext, Session, SlipContext

                context = DecisionContext(
                    session=Session(
                        session_id=request.session_id,
                        anonymous_actor_id=request.anonymous_actor_id,
                        started_at=datetime.now(UTC),
                        client_version=request.client_version,
                    ),
                    slip=SlipContext(slip_id=request.slip_id, selections=[], created_at=datetime.now(UTC)),
                    safety=SafetyContext(),
                    interaction=request.interaction if isinstance(request.interaction, InteractionContext) else InteractionContext(),
                )
                await self.persistence.persist_decision(decision, context)
            except Exception as e:
                logger.error(
                    "audit_persist_failed",
                    error=str(e),
                    decision_id=str(decision.decision_id),
                )

        with contextlib.suppress(RuntimeError):
            asyncio.create_task(_persist())

    async def _execute_pipeline(self, request: DecisionRequest) -> DecisionResult:
        """The core orchestration logic."""
        now = datetime.now(UTC)

        # 1. Build Context
        context = await self.context_builder.build(request)

        # 2. Evaluate Safety (Can we intervene?)
        safety_result = self.safety_contract.evaluate_safety(context.safety, now)

        # 3. Estimate State (What is happening?)
        state_estimate = self.state_estimator.estimate_state(context)

        # 4. Check Confidence
        confidence_reason = self.safety_contract.check_state_confidence(state_estimate)

        # Also check legitimate reconsideration which forces NO_INTERVENTION
        recon_reason = self.safety_contract.check_legitimate_reconsideration(state_estimate)

        # 5. Determine Eligible Actions
        available_data_keys = self._compute_available_data_keys(context)

        eligible_actions = self.action_registry.get_eligible_for_state(state_estimate.state, available_data_keys)

        # 6. Check if primary action for state is missing authoritative data
        no_intervention_reason: NoInterventionReason | None = None
        preferred_action_id = self.policy_selector.state_to_preferred_action.get(state_estimate.state)
        if preferred_action_id:
            preferred_def = self.action_registry.get(preferred_action_id)
            if preferred_def and not all(req in available_data_keys for req in preferred_def.required_data):
                selected_action = ActionId.NO_INTERVENTION
                no_intervention_reason = NoInterventionReason.MISSING_AUTHORITATIVE_DATA
                # Skip policy selection
                eligible_actions = []
            else:
                selected_action = self.policy_selector.select_action(context, state_estimate, eligible_actions)
        else:
            selected_action = self.policy_selector.select_action(context, state_estimate, eligible_actions)

        # Determine NO_INTERVENTION reason if applicable
        if no_intervention_reason is None:
            if confidence_reason:
                selected_action = ActionId.NO_INTERVENTION
                no_intervention_reason = confidence_reason
            elif recon_reason:
                selected_action = ActionId.NO_INTERVENTION
                no_intervention_reason = recon_reason
            elif safety_result.status != SafetyStatus.SAFE:
                no_intervention_reason = self.safety_contract.safety_block_to_no_intervention_reason(safety_result.block_reasons)

        # Handle NO_UNCERTAINTY state explicitly
        if (
            selected_action == ActionId.NO_INTERVENTION
            and no_intervention_reason is None
            and state_estimate.state == UncertaintyState.NO_UNCERTAINTY
        ):
            no_intervention_reason = NoInterventionReason.NO_UNCERTAINTY_DETECTED

        # 7. Final Safety Check
        final_block_reason = self.safety_contract.final_safety_check(selected_action, safety_result, state_estimate)
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
            policy_version=self.policy_selector.VERSION,
            model_version=state_estimate.model_version,
            action_registry_version=self.action_registry.version,
            facts_version="1",
            reason="Pipeline completed",
            response_text=response_text,
        )

        # 10. Return result (persistence is handled in decide())
        return DecisionResult(decision=decision, response_text=response_text)

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
        now = datetime.now(UTC)

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
