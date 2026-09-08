"""VW action dependent features constrained to an already safe candidate set."""

import math
import random
from contextvars import ContextVar
from typing import Any

from confidence.application.reward_join import RewardSignal
from confidence.domain.actions import ActionDefinition
from confidence.domain.enums import ActionId
from confidence.domain.ml.bounded import BoundedInference
from confidence.domain.models import DecisionContext, StateEstimate
from confidence.domain.policy import PolicySelector

selection_metadata: ContextVar[dict[str, Any]] = ContextVar("selection_metadata")
FEATURES = ("dwell_time_seconds", "recent_backtracks")


def format_example(
    features: dict[str, float], actions: list[ActionId], chosen: ActionId | None = None, cost: float = 0.0, probability: float = 1.0
) -> str:
    if set(features) != set(FEATURES) or not all(math.isfinite(x) for x in features.values()):
        raise ValueError("Invalid policy feature schema")
    lines = ["shared |context " + " ".join(f"{name}:{features[name]}" for name in FEATURES)]
    for action in actions:
        label = f"0:{cost}:{probability} " if action == chosen else ""
        lines.append(f"{label}|action {action.value}")
    return "\n".join(lines)


class BanditPolicySelector(PolicySelector):
    VERSION = "bandit-v1"

    def __init__(self, model_path: str | None = None, fallback: PolicySelector | None = None, exploration_rate: float = 0.1) -> None:
        super().__init__()
        self.fallback = fallback or PolicySelector()
        self.model: Any = None
        self.inference = BoundedInference()
        self.random = random.Random()
        if model_path:
            try:
                from vowpalwabbit import Workspace

                self.model = Workspace(cb_explore_adf=True, epsilon=exploration_rate, initial_regressor=model_path, quiet=True)
            except Exception:
                self.model = None

    def select_action(self, context: DecisionContext, state_estimate: StateEstimate, eligible_actions: list[ActionDefinition]) -> ActionId:
        selection_metadata.set({"effective_policy": self.fallback.VERSION, "selection_probability": 1.0})
        ids = [a.action_id for a in eligible_actions]
        if len(ids) == 1:
            return ids[0]
        if self.model is not None and ids:
            try:
                features = {name: float(getattr(context.interaction, name)) for name in FEATURES}
                probabilities = list(self.inference.run(lambda: self.model.predict(format_example(features, ids))))
                if len(probabilities) != len(ids) or not all(math.isfinite(p) and p >= 0 for p in probabilities):
                    raise ValueError("Invalid probabilities")
                if not math.isclose(sum(probabilities), 1.0, abs_tol=1e-6):
                    raise ValueError("Invalid distribution")
                index = self.random.choices(range(len(ids)), weights=probabilities)[0]
                selection_metadata.set(
                    {"effective_policy": self.VERSION, "selection_probability": probabilities[index], "context_features": features}
                )
                return ids[index]
            except Exception:
                pass
        return self.fallback.select_action(context, state_estimate, eligible_actions)

    def learn(self, reward_signal: RewardSignal) -> bool:
        if self.model is None or reward_signal.is_late_join or reward_signal.action_taken not in reward_signal.candidate_actions:
            return False
        try:
            example = format_example(
                reward_signal.context_features,
                reward_signal.candidate_actions,
                reward_signal.action_taken,
                -reward_signal.reward,
                reward_signal.selection_probability,
            )
            self.inference.run(lambda: self.model.learn(example))
            return True
        except Exception:
            return False
