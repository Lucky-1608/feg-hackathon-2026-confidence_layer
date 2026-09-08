"""Harm comparison with Newcombe/Wilson intervals and an explicit margin."""

import math
from uuid import UUID

from pydantic import BaseModel, Field
from scipy.stats import chi2_contingency, fisher_exact, norm


class SessionData(BaseModel):
    session_id: UUID
    indicators: dict[str, bool] = Field(default_factory=dict)


class IndicatorComparison(BaseModel):
    treatment_rate: float
    control_rate: float
    difference: float
    confidence_interval: tuple[float, float]
    p_value: float
    test: str


class HarmNeutralityResult(BaseModel):
    overall: IndicatorComparison | None
    per_indicator: dict[str, IndicatorComparison]
    verdict: str
    noninferiority_margin: float


def wilson(successes: int, total: int, z: float) -> tuple[float, float]:
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    width = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return center - width, center + width


class HarmNeutralityAnalyzer:
    def analyze(
        self, treatment: list[SessionData], control: list[SessionData], significance: float = 0.05, margin: float = 0.02
    ) -> HarmNeutralityResult:
        if not 0 < significance < 1 or not 0 <= margin <= 1:
            raise ValueError("Invalid inference parameters")
        if not treatment or not control:
            return HarmNeutralityResult(overall=None, per_indicator={}, verdict="insufficient_evidence", noninferiority_margin=margin)
        if len({s.session_id for s in treatment + control}) != len(treatment) + len(control):
            raise ValueError("Independent sessions required")
        labels = sorted({key for s in treatment + control for key in s.indicators})
        # Missing indicator data cannot be interpreted as a negative observation.
        if not labels or any(set(s.indicators) != set(labels) for s in treatment + control):
            return HarmNeutralityResult(overall=None, per_indicator={}, verdict="insufficient_evidence", noninferiority_margin=margin)
        z = float(norm.ppf(1 - significance / (2 * (len(labels) + 1))))

        def compare(a: int, b: int) -> IndicatorComparison:
            n, m = len(treatment), len(control)
            p, q = a / n, b / m
            low_p, high_p = wilson(a, n, z)
            low_q, high_q = wilson(b, m, z)
            interval = (p - q - math.sqrt((p - low_p) ** 2 + (high_q - q) ** 2), p - q + math.sqrt((high_p - p) ** 2 + (q - low_q) ** 2))
            table = [[a, n - a], [b, m - b]]
            if min(a, n - a, b, m - b) < 5:
                p_value = float(fisher_exact(table).pvalue)
                test = "fisher_exact"
            else:
                p_value = float(chi2_contingency(table, correction=False).pvalue)
                test = "chi_squared"
            return IndicatorComparison(
                treatment_rate=p, control_rate=q, difference=p - q, confidence_interval=interval, p_value=p_value, test=test
            )

        per_indicator = {
            label: compare(sum(s.indicators[label] for s in treatment), sum(s.indicators[label] for s in control)) for label in labels
        }
        overall = compare(sum(any(s.indicators.values()) for s in treatment), sum(any(s.indicators.values()) for s in control))
        comparisons = [overall, *per_indicator.values()]
        verdict = "pass" if all(c.confidence_interval[1] <= margin for c in comparisons) else "insufficient_evidence"
        if any(c.confidence_interval[0] > margin for c in comparisons):
            verdict = "fail"
        return HarmNeutralityResult(overall=overall, per_indicator=per_indicator, verdict=verdict, noninferiority_margin=margin)
