import numpy as np
import pandas as pd
import pytest
import torch

from ml.anomaly_detector import AnomalyDetector
from ml.autoencoder_model import TabularAutoencoder


class _StubPreprocessor:
    def transform(self, df: pd.DataFrame) -> np.ndarray:
        return df.to_numpy(dtype="float32")


class _StubPredictor:
    def __init__(self):
        self.preprocessor = _StubPreprocessor()

    def form_to_model_row(self, form_data):
        return pd.DataFrame([{"a": form_data.get("a", 0.0), "b": form_data.get("b", 0.0)}])


class _ZeroAutoencoder(TabularAutoencoder):
    """Always reconstructs the zero vector, so error == mean(x**2)."""

    def forward(self, x):
        return torch.zeros_like(x)


def test_load_returns_none_when_artifacts_missing(tmp_path):
    detector = AnomalyDetector.load(
        _StubPredictor(),
        model_path=str(tmp_path / "missing.pt"),
        meta_path=str(tmp_path / "missing.pkl"),
    )
    assert detector is None


def test_score_flags_reconstruction_error_above_threshold():
    detector = AnomalyDetector(_StubPredictor(), _ZeroAutoencoder(input_dim=2), threshold=0.5)

    normal = detector.score({"a": 0.1, "b": 0.1})
    assert normal.is_anomaly is False

    anomalous = detector.score({"a": 5.0, "b": 5.0})
    assert anomalous.is_anomaly is True
    assert anomalous.reconstruction_error == pytest.approx((5.0**2 + 5.0**2) / 2)


def test_score_row_uses_series_directly():
    detector = AnomalyDetector(_StubPredictor(), _ZeroAutoencoder(input_dim=2), threshold=0.5)
    row = pd.Series({"a": 3.0, "b": 4.0})

    result = detector.score_row(row)
    assert result.reconstruction_error == pytest.approx((3.0**2 + 4.0**2) / 2)
