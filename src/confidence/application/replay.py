"""Replay persisted events with historical authority snapshots and isolated state."""

from uuid import UUID

from pydantic import BaseModel

from confidence.application.context_builder import ContextBuilder, DecisionRequest
from confidence.application.engine import DecisionEngine
from confidence.application.event_processor import EventProcessor
from confidence.config import ShadowConfig
from confidence.domain.models import Decision, DecisionContext, InteractionContext
from confidence.infrastructure.persistence import DatabasePersistenceProvider
from confidence.infrastructure.shadow_mode import ShadowModeController


class ReplayReport(BaseModel):
    sessions: int
    replayed_decisions: int
    comparisons: int
    action_matches: int
    missing_snapshots: int


class SnapshotBuilder(ContextBuilder):
    def __init__(self, context: DecisionContext | None) -> None:
        self.context = context

    async def build(self, request: DecisionRequest) -> DecisionContext:
        if self.context is None:
            raise RuntimeError("Historical authoritative context unavailable")
        return self.context.model_copy(update={"interaction": request.interaction}, deep=True)


class ReplayManager:
    def __init__(self, persistence: DatabasePersistenceProvider, engine: DecisionEngine) -> None:
        self.persistence = persistence
        self.engine = engine
        self.comparisons = 0
        self.action_matches = 0
        self.missing_snapshots = 0

    async def replay_session(self, session_id: UUID) -> list[Decision]:
        events = await self.persistence.get_events(session_id)
        originals = await self.persistence.get_session_decisions(session_id)
        results = []
        interaction = InteractionContext()
        for event in events:
            changes = interaction.model_dump()
            for key, value in EventProcessor.interaction_updates(event).items():
                changes[key] = (
                    changes[key] + value
                    if key in {"recent_backtracks", "stake_changes", "selection_changes", "confirmation_attempts"}
                    else value
                )
            interaction = InteractionContext.model_validate(changes)
            # Never borrow facts from a future decision.
            eligible = [d for d in originals if d.timestamp <= event.timestamp]
            original = eligible[-1] if eligible else None
            context = await self.persistence.get_context(original.decision_id) if original else None
            if context is None:
                self.missing_snapshots += 1
            engine = DecisionEngine(
                SnapshotBuilder(context),
                self.engine.safety_contract,
                self.engine.state_estimator,
                self.engine.action_registry,
                self.engine.policy_selector,
                self.engine.response_generator,
                self.persistence,
                timeout_ms=self.engine.timeout_ms,
                clock=event.timestamp.astimezone,
                persist=False,
                shadow_controller=ShadowModeController(ShadowConfig(shadow_mode="off")),
            )
            result = await engine.decide(
                DecisionRequest(
                    session_id=session_id,
                    anonymous_actor_id=event.anonymous_actor_id,
                    client_version=event.client_version,
                    slip_id=context.slip.slip_id if context else "unavailable",
                    interaction=interaction,
                )
            )
            results.append(result.decision)
            if original:
                self.comparisons += 1
                self.action_matches += int(original.selected_action == result.decision.selected_action)
        return results

    async def replay_batch(self, session_ids: list[UUID]) -> ReplayReport:
        self.comparisons = self.action_matches = self.missing_snapshots = 0
        count = 0
        for session_id in session_ids:
            count += len(await self.replay_session(session_id))
        return ReplayReport(
            sessions=len(session_ids),
            replayed_decisions=count,
            comparisons=self.comparisons,
            action_matches=self.action_matches,
            missing_snapshots=self.missing_snapshots,
        )
