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
10. Persist audit
11. Return result
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from confidence.application.context_builder import ContextBuilder, DecisionRequest
from confidence.domain.actions import ActionRegistry
from confidence.domain.enums import ActionId, NoInterventionReason, SafetyStatus
from confidence.domain.models import Decision, DecisionContext
from confidence.domain.policy import PolicySelector
from confidence.domain.response import ResponseGenerator
from confidence.domain.safety import SafetyContract
from confidence.domain.state import StateEstimator


class DecisionResult:
    """The result of the decision pipeline."""

    def __init__(self, decision: Decision, response_text: str | None = None) -> None:
        self.decision = decision
        self.response_text = response_text


class PersistenceProvider(Protocol):
    """Interface for async audit logging."""

    async def persist_decision(self, decision: Decision, context: DecisionContext) -> None: ...


class DecisionEngine:
    """Central orchestrator for the Confidence Layer."""

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
            return await asyncio.wait_for(
                self._execute_pipeline(request),
                timeout=self.timeout_ms / 1000.0,
            )
        except TimeoutError:
            return self._build_failure_decision(
                request, NoInterventionReason.TIMEOUT, "Execution exceeded timeout"
            )
        except Exception as e:
            return self._build_failure_decision(
                request, NoInterventionReason.SYSTEM_FAILURE, f"Unexpected error: {e}"
            )

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
        available_data_keys = set()
        if context.slip.stake is not None:
            available_data_keys.add("stake")
        if context.slip.potential_return is not None:
            available_data_keys.add("potential_return")
        if context.slip.selections:
            available_data_keys.add("old_odds")
            available_data_keys.add("new_odds")
            available_data_keys.add("selections_summary")
        if context.markets:
            available_data_keys.add("market_name")
            available_data_keys.add("event_name")
            available_data_keys.add("market_definition")

        eligible_actions = self.action_registry.get_eligible_for_state(
            state_estimate.state, available_data_keys
        )

        # 6. Check if primary action for state is missing authoritative data
        no_intervention_reason = None
        preferred_action_id = self.policy_selector.state_to_preferred_action.get(
            state_estimate.state
        )
        if preferred_action_id:
            preferred_def = self.action_registry.get(preferred_action_id)
            if preferred_def and not all(
                req in available_data_keys for req in preferred_def.required_data
            ):
                selected_action = ActionId.NO_INTERVENTION
                no_intervention_reason = NoInterventionReason.MISSING_AUTHORITATIVE_DATA
                # Skip policy selection
                eligible_actions = []
            else:
                selected_action = self.policy_selector.select_action(
                    context, state_estimate, eligible_actions
                )
        else:
            selected_action = self.policy_selector.select_action(
                context, state_estimate, eligible_actions
            )

        # Determine NO_INTERVENTION reason if applicable
        if no_intervention_reason is None:
            if confidence_reason:
                selected_action = ActionId.NO_INTERVENTION
                no_intervention_reason = confidence_reason
            elif recon_reason:
                selected_action = ActionId.NO_INTERVENTION
                no_intervention_reason = recon_reason
            elif safety_result.status != SafetyStatus.SAFE:
                no_intervention_reason = (
                    self.safety_contract.safety_block_to_no_intervention_reason(
                        safety_result.block_reasons
                    )
                )

        # 7. Final Safety Check
        final_block_reason = self.safety_contract.final_safety_check(
            selected_action, safety_result, state_estimate
        )
        if final_block_reason:
            selected_action = ActionId.NO_INTERVENTION
            no_intervention_reason = final_block_reason

        # Missing data check for informational actions
        if selected_action != ActionId.NO_INTERVENTION:
            action_def = self.action_registry.get(selected_action)
            if not action_def or not all(
                req in available_data_keys for req in action_def.required_data
            ):
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
            reason="Pipeline completed",
            response_text=response_text,
        )

        # 10. Persist Audit Asynchronously (fire and forget)
        # We don't await this directly if it blocks, but here we just await it
        # (in reality we'd use a background task or message queue)
        from contextlib import suppress

        with suppress(Exception):
            # We use a short timeout for persistence to not block the response
            # But the requirement says "Audit persistence is downstream and
            # must not turn a safe decision into a failure."
            # In FastAPI, we would use BackgroundTasks. Here we'll just await with broad except.
            await self.persistence.persist_decision(decision, context)

        # 11. Return result
        return DecisionResult(decision=decision, response_text=response_text)

    def _build_failure_decision(
        self, request: DecisionRequest, reason: NoInterventionReason, detail: str
    ) -> DecisionResult:
        """Create a fail-closed decision for unexpected errors."""
        now = datetime.now(UTC)
        from confidence.domain.enums import UncertaintyState

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
            policy_version="unknown",
            model_version="unknown",
            action_registry_version="unknown",
            reason=detail,
        )
        return DecisionResult(decision=decision)
