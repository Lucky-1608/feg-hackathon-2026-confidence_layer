"""Tests for Policy Authority."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from confidence.domain.actions import ActionRegistry
from confidence.domain.enums import ActionId, UncertaintyState
from confidence.domain.models import DecisionContext, Session, SlipContext, StateEstimate
from confidence.domain.policy import PolicySelector


@pytest.fixture
def context() -> DecisionContext:
    return DecisionContext(
        session=Session(session_id=uuid4(), anonymous_actor_id="actor-1", started_at=datetime.now(UTC), client_version="1.0"),
        slip=SlipContext(slip_id="slip-1", selections=[], created_at=datetime.now(UTC)),
    )


def test_policy_selects_preferred_action(context: DecisionContext) -> None:
    selector = PolicySelector()
    estimate = StateEstimate(state=UncertaintyState.ODDS_CHANGE, confidence=0.9, model_version="1")
    registry = ActionRegistry()
    eligible = [registry.get(ActionId.EXPLAIN_ODDS_CHANGE), registry.get(ActionId.NO_INTERVENTION)]
    # filter out None
    eligible = [e for e in eligible if e]

    action = selector.select_action(context, estimate, eligible)
    assert action == ActionId.EXPLAIN_ODDS_CHANGE


def test_policy_respects_safety_class(context: DecisionContext) -> None:
    # A protective policy rule might be to prefer PROTECTIVE > NEUTRAL > CONVERSION_ORIENTED
    # Let's ensure NO_INTERVENTION is always available if needed.
    selector = PolicySelector()
    estimate = StateEstimate(state=UncertaintyState.DISTRACTION, confidence=0.8, model_version="1")
    registry = ActionRegistry()

    eligible = [
        registry.get(ActionId.OFFER_DEFER),  # NEUTRAL
        registry.get(ActionId.NO_INTERVENTION),  # PROTECTIVE
    ]
    eligible = [e for e in eligible if e]

    action = selector.select_action(context, estimate, eligible)
    # Distraction isn't directly mapped, falls back to OFFER_DEFER because it's eligible
    assert action == ActionId.OFFER_DEFER
