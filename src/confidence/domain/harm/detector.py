"""Safety classifier has its own cross-session schema and sensitivity objective."""

from datetime import UTC, datetime
from typing import Any

import numpy as np
from numpy.typing import NDArray

from confidence.domain.ml.bounded import BoundedInference
from confidence.domain.models import EnhancedHarmIndicators, SessionSummary


class HarmFeatureExtractor:
    FEATURE_NAMES = [
        "stake_increase_after_loss",
        "consecutive_loss_sessions",
        "stake_acceleration_rate",
        "loss_recovery_bet_detected",
        "session_duration_percentile",
        "sessions_last_24h",
        "sessions_last_7d",
        "late_night_session",
        "cumulative_loss_trend",
        "deposit_frequency_change",
        "max_stake_percentile",
        "time_between_bets_decreasing",
        "market_diversity_decreasing",
        "selection_complexity_decreasing",
    ]

    def extract(self, history: list[SessionSummary], now: datetime | None = None) -> NDArray[np.float64]:
        if not history:
            return np.zeros((1, 14), dtype=np.float64)
        if any(not s.financial_data_complete or s.net_result is None for s in history):
            raise ValueError("Authoritative financial history unavailable")
        now = now or datetime.now(UTC)
        rows = sorted(history, key=lambda s: s.started_at)
        current, previous = rows[-1], rows[-2] if len(rows) > 1 else rows[-1]
        consecutive = 0
        for row in reversed(rows):
            if (row.net_result or 0) >= 0:
                break
            consecutive += 1
        increase = max(0.0, current.total_stake / max(previous.total_stake, 1) - 1)
        after_loss = increase if (previous.net_result or 0) < 0 else 0.0
        durations = [max(0, ((s.ended_at or now) - s.started_at).total_seconds()) for s in rows]
        long_duration = sum(d <= durations[-1] for d in durations) / len(rows) if durations[-1] >= 7200 else 0.0
        return np.asarray(
            [
                [
                    after_loss,
                    consecutive,
                    increase,
                    float(after_loss > 0 and consecutive > 1),
                    long_duration,
                    sum((now - s.started_at).total_seconds() <= 86400 for s in rows),
                    sum((now - s.started_at).total_seconds() <= 604800 for s in rows),
                    float(current.started_at.hour < 5),
                    max(0, -sum(s.net_result or 0 for s in rows)),
                    max(0, (current.deposit_count or 0) - (previous.deposit_count or 0)),
                    sum(s.total_stake <= current.total_stake for s in rows) / len(rows) if increase > 0 else 0.0,
                    float(
                        current.mean_bet_interval_seconds is not None
                        and previous.mean_bet_interval_seconds is not None
                        and current.mean_bet_interval_seconds < previous.mean_bet_interval_seconds
                    ),
                    float(len(current.market_types) < len(previous.market_types)),
                    float(
                        current.mean_selection_complexity is not None
                        and previous.mean_selection_complexity is not None
                        and current.mean_selection_complexity < previous.mean_selection_complexity
                    ),
                ]
            ],
            dtype=np.float64,
        )


class HarmClassifier:
    VERSION = "harm-rules-v1"
    INDICATORS = ("rapid_loss_chasing", "escalating_stakes", "session_duration_extreme", "loss_recovery_pattern")

    def __init__(self, model: Any = None, thresholds: dict[str, float] | None = None) -> None:
        self.model = model
        self.thresholds = {name: 0.3 for name in self.INDICATORS} | (thresholds or {})
        if set(self.thresholds) != set(self.INDICATORS) or any(not 0 < t <= 1 for t in self.thresholds.values()):
            raise ValueError("Invalid harm thresholds")
        self.extractor = HarmFeatureExtractor()
        self.inference = BoundedInference()

    def classify(self, history: list[SessionSummary]) -> EnhancedHarmIndicators:
        try:
            features = self.extractor.extract(history)
        except Exception:
            return EnhancedHarmIndicators(composite_harm_score=1, evidence=["Authoritative history unavailable"])
        f = features[0]
        rules = np.array([min(1, f[0] + 0.15 * f[1]), min(1, f[2]), f[4], min(1, f[3])])
        probabilities = rules
        if self.model is not None:
            try:
                prediction = np.asarray(self.inference.run(lambda: self.model.predict_proba(features))).reshape(-1)
                if prediction.shape != (4,) or not np.isfinite(prediction).all() or ((prediction < 0) | (prediction > 1)).any():
                    raise ValueError("Invalid harm model output")
                probabilities = np.maximum(rules, prediction)  # A model cannot weaken a deterministic alarm.
            except Exception:
                probabilities = rules
        values = dict(zip(self.INDICATORS, (float(p) for p in probabilities), strict=True))
        evidence = [name for name, value in values.items() if value >= self.thresholds[name]]
        composite = sum(values[name] * weight for name, weight in zip(self.INDICATORS, [0.4, 0.25, 0.15, 0.2], strict=True))
        # Preserve custom sensitivity when consumed through the backwards-compatible has_any().
        if evidence:
            composite = max(0.3, composite)
        return EnhancedHarmIndicators(**values, composite_harm_score=composite, evidence=evidence)
