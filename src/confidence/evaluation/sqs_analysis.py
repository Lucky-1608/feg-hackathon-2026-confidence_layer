"""Distribution, temporal and cohort summaries of versioned session quality."""

from datetime import datetime

import numpy as np
from pydantic import BaseModel, Field

from confidence.domain.sqs import SessionQualityResult


class SQSReport(BaseModel):
    count: int
    mean: float
    median: float
    p25: float
    p75: float
    trend: list[float] = Field(default_factory=list)
    by_action: dict[str, float] = Field(default_factory=dict)
    by_state: dict[str, float] = Field(default_factory=dict)
    harm_correlation: float | None = None


class SQSAnalyzer:
    def analyze(
        self,
        scores: list[SessionQualityResult],
        actions: list[str] | None = None,
        states: list[str] | None = None,
        timestamps: list[datetime] | None = None,
    ) -> SQSReport:
        for values in (actions, states, timestamps):
            if values is not None and len(values) != len(scores):
                raise ValueError("Aligned metadata required")
        if not scores:
            return SQSReport(count=0, mean=0, median=0, p25=0, p75=0)
        x = np.array([s.clamped_score for s in scores])
        harm = np.array([s.harm_indicator_load for s in scores])

        def groups(labels: list[str] | None) -> dict[str, float]:
            return {label: float(np.mean([x[i] for i, key in enumerate(labels or []) if key == label])) for label in set(labels or [])}

        order = sorted(range(len(x)), key=lambda i: timestamps[i]) if timestamps else list(range(len(x)))
        return SQSReport(
            count=len(x),
            mean=float(x.mean()),
            median=float(np.median(x)),
            p25=float(np.quantile(x, 0.25)),
            p75=float(np.quantile(x, 0.75)),
            trend=[float(x[i]) for i in order],
            by_action=groups(actions),
            by_state=groups(states),
            harm_correlation=float(np.corrcoef(x, harm)[0, 1]) if x.std() > 0 and harm.std() > 0 else None,
        )
