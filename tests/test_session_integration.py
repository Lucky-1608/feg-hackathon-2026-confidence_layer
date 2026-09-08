from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from confidence.application.context_builder import ContextBuilder, DecisionRequest
from confidence.demo.providers import DummyMarketProvider, DummySafetyProvider, DummySlipProvider
from confidence.domain.models import InteractionContext


@pytest.mark.parametrize(
    "accumulated,signals,expected",
    [
        (InteractionContext(recent_backtracks=3, stake_changes=4, dwell_time_seconds=2), {"dwell_time_seconds": 10}, (3, 4, 10)),
        (None, {"dwell_time_seconds": 5}, (0, 0, 5)),
        (InteractionContext(recent_backtracks=3), {"recent_backtracks": 0}, (0, 0, 0)),
    ],
)
async def test_merge(accumulated, signals, expected):
    provider = AsyncMock()
    provider.get_interaction_state.return_value = accumulated
    builder = ContextBuilder(DummySafetyProvider(), DummySlipProvider(), DummyMarketProvider(), provider)
    result = await builder.build(
        DecisionRequest(
            session_id=uuid4(),
            anonymous_actor_id="actor-1",
            client_version="1",
            slip_id="slip-1",
            interaction=InteractionContext(**signals),
        )
    )
    assert (result.interaction.recent_backtracks, result.interaction.stake_changes, result.interaction.dwell_time_seconds) == expected
