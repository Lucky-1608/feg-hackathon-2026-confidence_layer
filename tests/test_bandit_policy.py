from unittest.mock import Mock
from uuid import uuid4

import pytest

from confidence.application.reward_join import RewardSignal
from confidence.domain.enums import ActionId
from confidence.domain.ml.contextual_bandit import BanditPolicySelector, format_example, selection_metadata
from confidence.domain.state import StateEstimator


def test_sampling_and_learning(sample_context, action_registry):
    policy = BanditPolicySelector()
    policy.model = Mock()
    actions = [action_registry.get(ActionId.NO_INTERVENTION), action_registry.get(ActionId.EXPLAIN_ODDS_CHANGE)]
    policy.model.predict.return_value = [0.5, 0.5]
    state = StateEstimator().estimate_state(sample_context)
    policy.random.seed(42)
    chosen = {policy.select_action(sample_context, state, actions) for _ in range(40)}
    assert chosen == {a.action_id for a in actions}
    assert selection_metadata.get()["selection_probability"] == 0.5
    reward = RewardSignal(
        decision_id=uuid4(),
        session_id=uuid4(),
        action_taken=actions[0].action_id,
        context_features={"dwell_time_seconds": 2.0, "recent_backtracks": 0.0},
        reward=0.6,
        join_latency_ms=1,
        candidate_actions=[a.action_id for a in actions],
        selection_probability=0.5,
    )
    assert policy.learn(reward)
    assert "0:-0.6:0.5" in policy.model.learn.call_args[0][0]
    policy.model.predict.side_effect = ValueError()
    assert policy.select_action(sample_context, state, actions) in chosen
    assert policy.select_action(sample_context, state, [actions[0]]) == ActionId.NO_INTERVENTION
    policy.inference.close()


def test_invalid_features():
    with pytest.raises(ValueError):
        format_example({"harm": 1.0}, [ActionId.NO_INTERVENTION])


async def test_real_vw_checkpoint_resume(tmp_path):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock

    from vowpalwabbit import Workspace

    from confidence.infrastructure.model_registry import FileModelRegistry
    from confidence.workers.bandit_trainer import BanditTrainer

    policy = BanditPolicySelector()
    policy.model = Workspace(cb_explore_adf=True, epsilon=0.1, quiet=True)
    # Real VW import/startup is outside request inference; a generous test budget avoids scheduler noise.
    policy.inference.timeout = 1
    reward = RewardSignal(
        outcome_id=uuid4(),
        decision_id=uuid4(),
        session_id=uuid4(),
        action_taken=ActionId.NO_INTERVENTION,
        candidate_actions=[ActionId.NO_INTERVENTION, ActionId.OFFER_DEFER],
        context_features={"dwell_time_seconds": 2, "recent_backtracks": 0},
        reward=0.6,
        join_latency_ms=1,
        selection_probability=0.5,
    )
    message = SimpleNamespace(value=reward.model_dump_json(), topic="confidence.rewards", partition=0, offset=0)
    trainer = BanditTrainer(policy, FileModelRegistry(tmp_path))
    consumer = AsyncMock()
    await trainer.process(consumer, message)
    restored = BanditTrainer(BanditPolicySelector(), FileModelRegistry(tmp_path))
    assert str(reward.outcome_id) in restored.processed
    await restored.process(consumer, message)
    assert restored.offsets["confidence.rewards:0"] == 1
    message.offset = 1
    await restored.process(consumer, message)  # duplicate publication, new Kafka offset
    assert len(restored.processed) == 1
    restored.policy.inference.close()
    policy.inference.close()
