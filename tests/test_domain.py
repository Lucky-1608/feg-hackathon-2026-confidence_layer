"""Tests for domain model validation.

Verifies that all Pydantic domain models validate correctly with
strict typing, reject invalid data, and serialize/deserialize properly.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from pydantic import ValidationError

from confidence.domain.enums import (
    ActionId,
    NoInterventionReason,
    SafetyBlockReason,
    SafetyStatus,
    UncertaintyState,
)
from confidence.domain.models import (
    AuditRecord,
    Decision,
    DecisionContext,
    HarmIndicators,
    OddsSnapshot,
    Outcome,
    SafetyContext,
    SafetyResult,
    Selection,
    Session,
    SlipContext,
    StateEstimate,
)

if TYPE_CHECKING:
    from datetime import datetime


class TestSession:
    def test_valid_session(self, now: datetime) -> None:
        s = Session(
            session_id=uuid4(),
            anonymous_actor_id="actor-123",
            started_at=now,
            client_version="1.0.0",
        )
        assert s.anonymous_actor_id == "actor-123"
        assert s.client_version == "1.0.0"

    def test_session_serialization_roundtrip(self, session: Session) -> None:
        data = session.model_dump()
        restored = Session.model_validate(data)
        assert restored == session


class TestHarmIndicators:
    def test_default_no_harm(self) -> None:
        h = HarmIndicators()
        assert not h.has_any()

    def test_single_indicator(self) -> None:
        h = HarmIndicators(rapid_loss_chasing=True)
        assert h.has_any()

    def test_multiple_indicators(self) -> None:
        h = HarmIndicators(rapid_loss_chasing=True, escalating_stakes=True)
        assert h.has_any()


class TestSafetyContext:
    def test_default_safe(self) -> None:
        sc = SafetyContext()
        assert not sc.is_self_excluded
        assert not sc.has_protective_restrictions
        assert not sc.harm_indicators.has_any()

    def test_self_excluded(self) -> None:
        sc = SafetyContext(is_self_excluded=True)
        assert sc.is_self_excluded


class TestSelection:
    def test_valid_selection(self) -> None:
        s = Selection(
            selection_id="sel-1",
            market_id="mkt-1",
            event_id="evt-1",
            odds=Decimal("2.50"),
        )
        assert s.odds == Decimal("2.50")
        assert s.odds_at_placement is None

    def test_selection_with_odds_history(self, now: datetime) -> None:
        s = Selection(
            selection_id="sel-1",
            market_id="mkt-1",
            event_id="evt-1",
            odds=Decimal("2.50"),
            odds_history=[
                OddsSnapshot(odds=Decimal("2.30"), timestamp=now, source="auth"),
            ],
        )
        assert len(s.odds_history) == 1


class TestSlipContext:
    def test_valid_slip(self, sample_slip: SlipContext) -> None:
        assert len(sample_slip.selections) == 1
        assert sample_slip.stake == Decimal("10.00")
        assert sample_slip.potential_return == Decimal("25.00")


class TestDecisionContext:
    def test_full_context(self, sample_context: DecisionContext) -> None:
        assert sample_context.context_version == "1"
        assert len(sample_context.markets) == 1
        assert sample_context.interaction.odds_changed is True

    def test_context_serialization_roundtrip(
        self, sample_context: DecisionContext
    ) -> None:
        data = sample_context.model_dump(mode="json")
        restored = DecisionContext.model_validate(data)
        assert restored.session.session_id == sample_context.session.session_id
        assert restored.slip.stake == sample_context.slip.stake


class TestSafetyResult:
    def test_safe_result(self, now: datetime) -> None:
        r = SafetyResult(status=SafetyStatus.SAFE, timestamp=now)
        assert r.status == SafetyStatus.SAFE
        assert r.block_reasons == []

    def test_blocked_result(self, now: datetime) -> None:
        r = SafetyResult(
            status=SafetyStatus.BLOCKED,
            block_reasons=[SafetyBlockReason.SELF_EXCLUSION],
            timestamp=now,
        )
        assert r.status == SafetyStatus.BLOCKED
        assert SafetyBlockReason.SELF_EXCLUSION in r.block_reasons


class TestStateEstimate:
    def test_valid_estimate(self) -> None:
        e = StateEstimate(
            state=UncertaintyState.ODDS_CHANGE,
            confidence=0.85,
            model_version="rules-v1",
            features_used=["odds_changed", "dwell_time"],
        )
        assert e.state == UncertaintyState.ODDS_CHANGE
        assert e.confidence == 0.85

    def test_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            StateEstimate(
                state=UncertaintyState.UNKNOWN,
                confidence=1.5,
                model_version="test",
            )
        with pytest.raises(ValidationError):
            StateEstimate(
                state=UncertaintyState.UNKNOWN,
                confidence=-0.1,
                model_version="test",
            )


class TestDecision:
    def test_valid_decision(self, now: datetime) -> None:
        d = Decision(
            decision_id=uuid4(),
            session_id=uuid4(),
            timestamp=now,
            state=UncertaintyState.ODDS_CHANGE,
            state_confidence=0.85,
            safety_status=SafetyStatus.SAFE,
            candidate_actions=[ActionId.EXPLAIN_ODDS_CHANGE, ActionId.NO_INTERVENTION],
            selected_action=ActionId.EXPLAIN_ODDS_CHANGE,
            policy_version="rules-v1",
            model_version="rules-v1",
            action_registry_version="1",
            reason="Odds changed and user hesitated",
        )
        assert d.selected_action == ActionId.EXPLAIN_ODDS_CHANGE
        assert d.no_intervention_reason is None

    def test_no_intervention_decision(self, now: datetime) -> None:
        d = Decision(
            decision_id=uuid4(),
            session_id=uuid4(),
            timestamp=now,
            state=UncertaintyState.LEGITIMATE_RECONSIDERATION,
            state_confidence=0.9,
            safety_status=SafetyStatus.SAFE,
            candidate_actions=[ActionId.NO_INTERVENTION],
            selected_action=ActionId.NO_INTERVENTION,
            no_intervention_reason=NoInterventionReason.LEGITIMATE_RECONSIDERATION,
            policy_version="rules-v1",
            model_version="rules-v1",
            action_registry_version="1",
            reason="User is legitimately reconsidering",
        )
        assert d.selected_action == ActionId.NO_INTERVENTION
        assert (
            d.no_intervention_reason
            == NoInterventionReason.LEGITIMATE_RECONSIDERATION
        )


class TestOutcome:
    def test_valid_outcome(self, now: datetime) -> None:
        o = Outcome(
            outcome_id=uuid4(),
            decision_id=uuid4(),
            session_id=uuid4(),
            timestamp=now,
            outcome_type="BET_COMPLETED",
        )
        assert o.schema_version == "1"


class TestAuditRecord:
    def test_audit_contains_full_provenance(
        self, sample_context: DecisionContext, now: datetime
    ) -> None:
        audit = AuditRecord(
            audit_id=uuid4(),
            decision_id=uuid4(),
            timestamp=now,
            context_snapshot=sample_context,
            safety_result=SafetyResult(status=SafetyStatus.SAFE, timestamp=now),
            state_estimate=StateEstimate(
                state=UncertaintyState.ODDS_CHANGE,
                confidence=0.85,
                model_version="rules-v1",
            ),
            candidate_actions=[ActionId.EXPLAIN_ODDS_CHANGE, ActionId.NO_INTERVENTION],
            selected_action=ActionId.EXPLAIN_ODDS_CHANGE,
            policy_version="rules-v1",
            model_version="rules-v1",
            action_registry_version="1",
            reason="Odds changed",
        )
        assert audit.context_snapshot.session == sample_context.session
        assert audit.outcome is None
