"""Train on explicitly labeled JSONL contexts; never promote failing evaluations.

Usage: python -m confidence.ml.train_hesitation TRAIN.jsonl VALIDATION.jsonl OUTPUT.lgb
Training and validation actor sets must be disjoint.
"""

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

from confidence.domain.enums import UncertaintyState
from confidence.domain.ml.hesitation_classifier import HesitationFeatureExtractor
from confidence.domain.models import DecisionContext


def train(training_path: str, validation_path: str, output: str) -> dict[str, Any]:
    from lightgbm import Dataset
    from lightgbm import train as train_model
    from sklearn.metrics import classification_report, confusion_matrix

    def load(path: str) -> tuple[Any, Any, set[str]]:
        rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
        contexts = [DecisionContext.model_validate(row["context"]) for row in rows]
        return (
            np.concatenate([HesitationFeatureExtractor().extract(c) for c in contexts]),
            np.array([list(UncertaintyState).index(UncertaintyState(row["label"])) for row in rows]),
            {c.session.anonymous_actor_id for c in contexts},
        )

    features, labels, actors = load(training_path)
    test_features, test_labels, test_actors = load(validation_path)
    if actors & test_actors:
        raise ValueError("Training/validation actors overlap")
    model = train_model(
        {"objective": "multiclass", "num_class": len(UncertaintyState), "verbosity": -1, "num_threads": 1, "seed": 42},
        Dataset(features, label=labels, feature_name=HesitationFeatureExtractor.FEATURE_NAMES),
        num_boost_round=100,
    )
    predicted = np.argmax(model.predict(test_features, num_threads=1), axis=1)
    report = classification_report(
        test_labels,
        predicted,
        labels=list(range(len(UncertaintyState))),
        target_names=[s.value for s in UncertaintyState],
        output_dict=True,
        zero_division=0,
    )
    report["confusion_matrix"] = confusion_matrix(test_labels, predicted, labels=list(range(len(UncertaintyState)))).tolist()
    if report["POTENTIAL_HARM"]["recall"] <= 0.95 or report["LEGITIMATE_RECONSIDERATION"]["precision"] <= 0.8:
        raise ValueError("Safety evaluation failed; model not saved")
    model.save_model(output)
    Path(output + ".evaluation.json").write_text(json.dumps(report))
    return dict(report)


if __name__ == "__main__":
    train(*sys.argv[1:4])
