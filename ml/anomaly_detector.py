"""
Inference wrapper for the tabular autoencoder — flags applications whose
feature profile reconstructs poorly against the genuine-application manifold.
Reuses FraudPredictor's fitted preprocessor and row-encoding logic so feature
handling stays consistent with the supervised model.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import joblib
import pandas as pd
import torch

from ml.autoencoder_model import TabularAutoencoder

MODEL_PATH = "autoencoder.pt"
META_PATH = "autoencoder_meta.pkl"


@dataclass
class AnomalyResult:
    reconstruction_error: float
    threshold: float
    is_anomaly: bool


class AnomalyDetector:
    """Scores applications by autoencoder reconstruction error."""

    def __init__(self, predictor, model: TabularAutoencoder, threshold: float):
        self.predictor = predictor
        self.model = model
        self.model.eval()
        self.threshold = threshold

    @classmethod
    def load(
        cls,
        predictor,
        model_path: str = MODEL_PATH,
        meta_path: str = META_PATH,
    ) -> "AnomalyDetector | None":
        if not (os.path.exists(model_path) and os.path.exists(meta_path)):
            return None
        meta = joblib.load(meta_path)
        model = TabularAutoencoder(meta["input_dim"])
        model.load_state_dict(torch.load(model_path, map_location="cpu"))
        return cls(predictor, model, meta["threshold"])

    def _score_dataframe(self, row_df: pd.DataFrame) -> AnomalyResult:
        features = self.predictor.preprocessor.transform(row_df).astype("float32")
        with torch.no_grad():
            tensor = torch.from_numpy(features)
            reconstruction = self.model(tensor)
            error = float(((reconstruction - tensor) ** 2).mean().item())
        return AnomalyResult(
            reconstruction_error=error,
            threshold=self.threshold,
            is_anomaly=error > self.threshold,
        )

    def score(self, form_data: dict[str, Any]) -> AnomalyResult:
        return self._score_dataframe(self.predictor.form_to_model_row(form_data))

    def score_row(self, row: pd.Series) -> AnomalyResult:
        return self._score_dataframe(pd.DataFrame([row]))
