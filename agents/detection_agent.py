"""
Detection Agent — delegates fraud scoring to the trained ensemble model.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ml.predictor import FraudPredictor, PredictionResult


@dataclass
class DetectionReport:
    agent_name: str
    role: str
    status: str
    prediction: PredictionResult
    summary: str
    confidence_band: str


class DetectionAgent:
    AGENT_NAME = "Detection Agent"
    ROLE = "ML Fraud Scoring"

    def __init__(self, predictor: FraudPredictor):
        self.predictor = predictor

    def score_application(self, form_data: dict[str, Any]) -> DetectionReport:
        prediction = self.predictor.predict_from_form(form_data)
        return self._build_report(prediction)

    def score_dataset_record(self) -> tuple[DetectionReport, int]:
        prediction, record_index, _ = self.predictor.predict_random_dataset_record()
        return self._build_report(prediction), record_index

    def _build_report(self, prediction: PredictionResult) -> DetectionReport:
        prob_pct = prediction.probability * 100
        if prediction.is_fraud:
            band = "High Risk"
            summary = (
                f"Ensemble model flagged this application as fraudulent "
                f"({prediction.probability_display} fraud probability, computed threshold {prediction.applied_threshold:.0%})."
            )
            status = "alert"
        elif prob_pct >= 30:
            band = "Elevated Risk"
            summary = (
                f"Below fraud threshold but probability is elevated "
                f"({prediction.probability_display}). Recommend enhanced review."
            )
            status = "warning"
        else:
            band = "Low Risk"
            summary = (
                f"Model classifies application as genuine "
                f"({prediction.probability_display} fraud probability)."
            )
            status = "success"

        return DetectionReport(
            agent_name=self.AGENT_NAME,
            role=self.ROLE,
            status=status,
            prediction=prediction,
            summary=summary,
            confidence_band=band,
        )
