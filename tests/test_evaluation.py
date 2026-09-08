from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from confidence.application.context_builder import DecisionRequest
from confidence.application.engine import DecisionEngine
from confidence.domain.enums import ActionId, UncertaintyState
from confidence.domain.models import StateEstimate
from confidence.domain.policy import PolicySelector
from confidence.domain.response import ResponseGenerator
from confidence.domain.sqs import SessionQualityResult
from confidence.domain.state import StateEstimator
from confidence.evaluation.ab_test import ExperimentManager
from confidence.evaluation.harm_analysis import HarmNeutralityAnalyzer, SessionData
from confidence.evaluation.holdout import HoldoutManager
from confidence.evaluation.metrics import StateEstimatorEvaluator
from confidence.evaluation.reports import ReportGenerator
from confidence.evaluation.sqs_analysis import SQSAnalyzer
from tests.test_outcomes import outcome_setup  # noqa: F401


def test_classifier_metrics():
    states = list(UncertaintyState)
    predictions = [StateEstimate(state=s, confidence=1, model_version="test") for s in states]
    report = StateEstimatorEvaluator().evaluate(predictions, states)
    assert report.macro_f1 == 1
    assert report.safety_constraints_met
    with pytest.raises(ValueError):
        StateEstimatorEvaluator().evaluate([], [])


def test_sqs_analysis():
    scores = [
        SessionQualityResult(raw_score=x, clamped_score=x, action_value=max(0, x), discovery_efficiency=0, harm_indicator_load=max(0, -x))
        for x in [-0.5, 0, 0.5]
    ]
    result = SQSAnalyzer().analyze(scores, actions=["a", "a", "b"], states=["x", "x", "y"])
    assert result.mean == result.median == 0
    assert result.by_action == {"a": -0.25, "b": 0.5}
    assert result.harm_correlation < 0
    assert SQSAnalyzer().analyze([]).count == 0


def cohort(n, harmed):
    return [SessionData(session_id=uuid4(), indicators={"loss_chasing": i < harmed}) for i in range(n)]


def test_harm_inference():
    analyzer = HarmNeutralityAnalyzer()
    assert analyzer.analyze(cohort(100, 50), cohort(100, 0)).verdict == "fail"
    assert analyzer.analyze(cohort(10000, 0), cohort(10000, 0)).verdict == "pass"
    assert analyzer.analyze(cohort(10, 1), cohort(10, 1)).verdict == "insufficient_evidence"
    assert analyzer.analyze([], []).verdict == "insufficient_evidence"


async def test_experiments_and_reports(outcome_setup, sample_context, action_registry, safety_contract):  # noqa: F811
    persistence, decision, _ = outcome_setup
    database = persistence.session_factory.kw["bind"]
    manager = ExperimentManager(database)
    identifier = await manager.create_experiment("name", "description", "policy", {"active": True, "treatment_percentage": 100})
    await manager.refresh()
    assert await manager.get_assignment(decision.session_id, identifier) == "treatment"
    assert manager.active.experiment_id == identifier
    builder = AsyncMock()
    builder.build.return_value = sample_context
    engine = DecisionEngine(
        builder,
        safety_contract,
        StateEstimator(),
        action_registry,
        PolicySelector(),
        ResponseGenerator(action_registry),
        persistence,
        experiment_manager=manager,
        persist=False,
    )
    result = await engine.decide(
        DecisionRequest(
            session_id=decision.session_id,
            anonymous_actor_id="actor",
            client_version="1",
            slip_id="s",
            interaction=sample_context.interaction,
        )
    )
    assert result.decision.policy_metadata["assignment"] == "treatment"
    await persistence.persist_decision(result.decision, sample_context)
    assert (await manager.get_results(identifier)).treatment_sessions == 1
    report = await ReportGenerator(database).generate_daily_report(datetime.now(UTC).date())
    assert report.total_decisions == 2
    holdout = HoldoutManager()
    session = next(s for s in (uuid4() for _ in range(1000)) if holdout.is_holdout(s))
    assert all(holdout.is_holdout(session) for _ in range(20))
    engine.holdout_manager = holdout
    result = await engine.decide(
        DecisionRequest(
            session_id=session, anonymous_actor_id="actor", client_version="1", slip_id="s", interaction=sample_context.interaction
        )
    )
    assert result.decision.reason == "holdout"
    assert result.decision.selected_action == ActionId.NO_INTERVENTION
