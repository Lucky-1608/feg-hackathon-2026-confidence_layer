import time
from unittest.mock import Mock

import numpy as np
import pytest

from confidence.domain.enums import UncertaintyState
from confidence.domain.ml.hesitation_classifier import HesitationFeatureExtractor, LightGBMStateEstimator
from confidence.domain.models import HarmIndicators
from confidence.domain.state import StateEstimator
from confidence.infrastructure.model_registry import FileModelRegistry


def test_features(sample_context):
    x = HesitationFeatureExtractor().extract(sample_context)
    assert x.shape == (1, 16)
    assert x[0, 0] == 15
    assert x[0, 15] == 0
    sample_context.safety.harm_indicators = HarmIndicators(rapid_loss_chasing=True)
    np.testing.assert_equal(x, HesitationFeatureExtractor().extract(sample_context))


@pytest.mark.parametrize("kind", ["missing", "low", "exception", "timeout", "nan", "good"])
def test_prediction_fallbacks(sample_context, kind):
    estimator = LightGBMStateEstimator(timeout_seconds=0.005)
    expected = StateEstimator().estimate_state(sample_context)
    p = np.zeros((1, len(UncertaintyState)))
    p[0, list(UncertaintyState).index(UncertaintyState.MARKET_MEANING)] = 1
    if kind != "missing":
        estimator.model = Mock()
        estimator.model.predict.return_value = p
        if kind == "low":
            estimator.model.predict.return_value = np.full_like(p, 0.1)
        if kind == "nan":
            estimator.model.predict.return_value = p * float("nan")
        if kind == "exception":
            estimator.model.predict.side_effect = ValueError()
        if kind == "timeout":
            estimator.model.predict.side_effect = lambda *a, **kw: time.sleep(0.03)
    result = estimator.estimate_state(sample_context)
    assert result.model_version == ("lgbm-v1" if kind == "good" else expected.model_version)
    estimator.inference.close()


def test_registry(tmp_path):
    source = tmp_path / "model"
    source.write_text("data")
    registry = FileModelRegistry(tmp_path / "registry")
    metadata = dict(training_date="today", evaluation_metrics={}, feature_names=["x"], safety_constraints_met=True)
    path = registry.register("state", "v1", source, metadata)
    assert registry.load("state", "v1")[0] == path
    path.write_text("tampered")
    with pytest.raises(ValueError):
        registry.load("state", "v1")
    with pytest.raises(ValueError):
        registry.directory("../escape", "v1")
    with pytest.raises(ValueError):
        registry.register("state", "v2", source, {})


def test_real_lightgbm_file(sample_context, tmp_path):
    from lightgbm import Dataset, train

    values = np.tile(HesitationFeatureExtractor().extract(sample_context), (100, 1))
    labels = np.arange(100) % len(UncertaintyState)
    model = train(
        {"objective": "multiclass", "num_class": len(UncertaintyState), "verbosity": -1, "num_threads": 1},
        Dataset(values, label=labels),
        num_boost_round=1,
    )
    path = tmp_path / "model.lgb"
    model.save_model(str(path))
    estimator = LightGBMStateEstimator(str(path))
    assert estimator.model is not None
    # Uninformative training must abstain to rules, not produce confident interventions.
    assert estimator.estimate_state(sample_context).model_version == "rules-v1"
    estimator.inference.close()
