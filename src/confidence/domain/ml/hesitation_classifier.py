"""Hesitation classification. Harm and reconsideration rules always take priority."""

import math
from typing import Any

import numpy as np
from numpy.typing import NDArray

from confidence.domain.enums import UncertaintyState
from confidence.domain.ml.bounded import BoundedInference
from confidence.domain.models import DecisionContext, StateEstimate
from confidence.domain.state import StateEstimator


class HesitationFeatureExtractor:
    # Slot 16 is deliberately constant: harm data must not enter optimization features.
    FEATURE_NAMES = [
        "dwell_time_seconds",
        "dwell_time_log",
        "recent_backtracks",
        "selection_changes",
        "stake_changes",
        "odds_changed",
        "confirmation_attempts",
        "interaction_velocity",
        "session_age_seconds",
        "time_since_slip_creation_seconds",
        "has_odds_history",
        "odds_movement_pct",
        "stake_to_return_ratio",
        "selection_count",
        "is_live_market",
        "reserved_independence",
    ]

    def extract(self, context: DecisionContext) -> NDArray[np.float64]:
        i, slip = context.interaction, context.slip
        movement = 0.0
        if slip.selections and slip.selections[0].odds_history:
            old = float(slip.selections[0].odds_history[0].odds)
            movement = (float(slip.selections[0].odds) - old) / old if old else 0.0
        ratio = float(slip.stake / slip.potential_return) if slip.stake is not None and slip.potential_return else 0.0
        values = np.asarray(
            [
                [
                    i.dwell_time_seconds,
                    math.log1p(max(0, i.dwell_time_seconds)),
                    i.recent_backtracks,
                    i.selection_changes,
                    i.stake_changes,
                    float(i.odds_changed),
                    i.confirmation_attempts,
                    i.interaction_velocity,
                    i.session_age_seconds,
                    i.time_since_slip_creation_seconds,
                    float(any(s.odds_history for s in slip.selections)),
                    movement,
                    ratio,
                    len(slip.selections),
                    float(any(m.is_live for m in context.markets)),
                    0.0,
                ]
            ],
            dtype=np.float64,
        )
        if not np.isfinite(values).all():
            raise ValueError("Non-finite features")
        return values


class LightGBMStateEstimator(StateEstimator):
    VERSION = "lgbm-v1"

    def __init__(self, model_path: str | None = None, confidence_threshold: float = 0.5, timeout_seconds: float = 0.02) -> None:
        self.fallback = StateEstimator()
        self.extractor = HesitationFeatureExtractor()
        self.threshold = confidence_threshold
        self.model: Any = None
        self.inference = BoundedInference(timeout_seconds)
        if model_path:
            try:
                from lightgbm import Booster

                self.model = Booster(model_file=model_path)
            except Exception:
                self.model = None

    def estimate_state(self, context: DecisionContext) -> StateEstimate:
        baseline = self.fallback.estimate_state(context)
        if self.model is None or baseline.state in {UncertaintyState.POTENTIAL_HARM, UncertaintyState.LEGITIMATE_RECONSIDERATION}:
            return baseline
        try:
            features = self.extractor.extract(context)
            probabilities = np.asarray(self.inference.run(lambda: self.model.predict(features, num_threads=1)))[0]
            if probabilities.shape != (len(UncertaintyState),) or not np.isfinite(probabilities).all():
                return baseline
            if (probabilities < 0).any() or not np.isclose(probabilities.sum(), 1):
                return baseline
            index = int(np.argmax(probabilities))
            confidence = float(probabilities[index])
            if confidence < self.threshold:
                return baseline
            return StateEstimate(
                state=list(UncertaintyState)[index],
                confidence=confidence,
                model_version=self.VERSION,
                features_used=self.extractor.FEATURE_NAMES,
            )
        except Exception:
            return baseline
