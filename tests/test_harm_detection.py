from datetime import UTC, datetime, timedelta
from unittest.mock import Mock
from uuid import uuid4

import numpy as np
import pytest

from confidence.domain.enums import SafetyStatus
from confidence.domain.harm.detector import HarmClassifier, HarmFeatureExtractor
from confidence.domain.ml.hesitation_classifier import HesitationFeatureExtractor
from confidence.domain.models import HarmIndicators, SafetyContext, SessionSummary
from confidence.domain.safety import SafetyContract


def history():
    now = datetime.now(UTC)
    return [
        SessionSummary(
            session_id=uuid4(),
            started_at=now - timedelta(days=2 - i),
            ended_at=now - timedelta(days=2 - i, hours=-3),
            total_stake=10 * (i + 1),
            total_return=0,
            net_result=-10 * (i + 1),
            bet_count=4,
            financial_data_complete=True,
        )
        for i in range(2)
    ]


def test_independent_features_and_safety():
    assert not set(HarmFeatureExtractor.FEATURE_NAMES) & set(HesitationFeatureExtractor.FEATURE_NAMES)
    classifier = HarmClassifier()
    assert classifier.extractor.extract(history()).shape == (1, 14)
    result = classifier.classify(history())
    assert result.has_any()
    assert result.evidence
    assert 0 <= result.composite_harm_score <= 1
    safety = SafetyContext(harm_indicators=result, data_freshness=datetime.now(UTC))
    assert SafetyContract().evaluate_safety(safety, datetime.now(UTC)).status == SafetyStatus.BLOCKED
    assert SafetyContext(harm_indicators=HarmIndicators()).harm_indicators.has_any() is False
    classifier.inference.close()


@pytest.mark.parametrize("value", [np.array([[0.2] * 4]), np.array([[float("nan")] * 4]), ValueError()])
def test_model_fallback_and_sensitivity(value):
    model = Mock()
    if isinstance(value, Exception):
        model.predict_proba.side_effect = value
    else:
        model.predict_proba.return_value = value
    classifier = HarmClassifier(model, {name: 0.1 for name in HarmClassifier.INDICATORS})
    assert classifier.classify(history()).has_any()
    classifier.inference.close()


def test_empty_and_incomplete():
    classifier = HarmClassifier()
    assert not classifier.classify([]).has_any()
    rows = history()
    rows[0].financial_data_complete = False
    assert classifier.classify(rows).has_any()
    with pytest.raises(ValueError):
        HarmClassifier(thresholds={"rapid_loss_chasing": 0})
    classifier.inference.close()
