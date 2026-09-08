"""Classifier evaluation with explicit support and conservative safety verdicts."""

from typing import Any

from pydantic import BaseModel
from sklearn.metrics import classification_report, confusion_matrix

from confidence.domain.enums import UncertaintyState
from confidence.domain.models import StateEstimate


class EvaluationReport(BaseModel):
    per_class: dict[str, dict[str, float]]
    macro_f1: float
    weighted_f1: float
    confusion_matrix: list[list[int]]
    harm_recall: float
    reconsideration_precision: float
    abstention_rate: float
    safety_constraints_met: bool


class StateEstimatorEvaluator:
    def evaluate(self, predictions: list[StateEstimate], ground_truth: list[UncertaintyState]) -> EvaluationReport:
        if not predictions or len(predictions) != len(ground_truth):
            raise ValueError("Nonempty aligned predictions and ground truth required")
        labels = [state.value for state in UncertaintyState]
        predicted = [p.state.value for p in predictions]
        truth = [s.value for s in ground_truth]
        report: Any = classification_report(truth, predicted, labels=labels, output_dict=True, zero_division=0)
        harm = float(report["POTENTIAL_HARM"]["recall"])
        reconsideration = float(report["LEGITIMATE_RECONSIDERATION"]["precision"])
        return EvaluationReport(
            per_class={label: report[label] for label in labels},
            macro_f1=report["macro avg"]["f1-score"],
            weighted_f1=report["weighted avg"]["f1-score"],
            confusion_matrix=confusion_matrix(truth, predicted, labels=labels).tolist(),
            harm_recall=harm,
            reconsideration_precision=reconsideration,
            abstention_rate=sum(p.state == UncertaintyState.UNKNOWN or p.confidence < 0.5 for p in predictions) / len(predictions),
            safety_constraints_met=harm > 0.95 and reconsideration > 0.8,
        )
