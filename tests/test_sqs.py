from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from confidence.domain.enums import OutcomeType
from confidence.domain.models import HarmIndicators, Outcome
from confidence.domain.sqs import SQSCalculator, SQSConfig
from tests.test_outcomes import outcome_setup  # noqa: F401


@pytest.mark.parametrize("outcome_type", list(OutcomeType))
@pytest.mark.parametrize("harm", [False, True])
async def test_sqs_components(outcome_setup, sample_context, outcome_type, harm):  # noqa: F811
    persistence, decision, _ = outcome_setup
    outcome = Outcome(
        outcome_id=uuid4(),
        decision_id=decision.decision_id,
        session_id=decision.session_id,
        timestamp=datetime.now(UTC),
        outcome_type=outcome_type,
    )
    sample_context.safety.harm_indicators = HarmIndicators(escalating_stakes=harm)
    calculator = SQSCalculator()
    result = calculator.compute_sqs(decision, outcome, sample_context.safety, [])
    assert -1 <= result.clamped_score <= 1
    assert (result.raw_score <= 0) if harm else (result.raw_score >= 0)
    await persistence.persist_outcome(outcome)
    await persistence.persist_sqs(outcome, result, calculator.config.version)
    metrics = await persistence.sqs_metrics()
    assert metrics["total_sessions"] == 1
    assert metrics["harm_sessions"] == int(harm)


@pytest.mark.parametrize("weights", [{"w3_harm_indicator_load": 0.5}, {"w1_action_value": float("nan")}])
def test_invalid_weights(weights):
    with pytest.raises(ValidationError):
        SQSConfig(**weights)


async def test_empty_metrics(outcome_setup):  # noqa: F811
    assert (await outcome_setup[0].sqs_metrics())["total_sessions"] == 0
