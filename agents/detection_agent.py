"""
Detection Agent — delegates fraud scoring to the trained ensemble model.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ml.anomaly_detector import AnomalyDetector, AnomalyResult
from ml.predictor import FraudPredictor, PredictionResult


@dataclass
class DetectionReport:
    agent_name: str
    role: str
    status: str
    prediction: PredictionResult
    summary: str
    confidence_band: str
    anomaly: AnomalyResult | None = None


class DetectionAgent:
    AGENT_NAME = "Detection Agent"
    ROLE = "ML Fraud Scoring"

    def __init__(self, predictor: FraudPredictor, anomaly_detector: AnomalyDetector | None = None):
        self.predictor = predictor
        self.anomaly_detector = anomaly_detector

    def score_application(self, form_data: dict[str, Any]) -> DetectionReport:
        prediction = self.predictor.predict_from_form(form_data)
        anomaly = self.anomaly_detector.score(form_data) if self.anomaly_detector else None
        return self._build_report(prediction, anomaly)

    def score_dataset_record(self) -> tuple[DetectionReport, int]:
        prediction, record_index, row = self.predictor.predict_random_dataset_record()
        anomaly = self.anomaly_detector.score_row(row) if self.anomaly_detector else None
        return self._build_report(prediction, anomaly), record_index

    def _build_report(
        self, prediction: PredictionResult, anomaly: AnomalyResult | None = None
    ) -> DetectionReport:
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

        if anomaly and anomaly.is_anomaly:
            summary += (
                f" Deep anomaly detector also flagged this profile (reconstruction error "
                f"{anomaly.reconstruction_error:.4f} exceeds learned genuine-profile threshold "
                f"{anomaly.threshold:.4f})."
            )
            if status == "success":
                status = "warning"

        return DetectionReport(
            agent_name=self.AGENT_NAME,
            role=self.ROLE,
            status=status,
            prediction=prediction,
            summary=summary,
            confidence_band=band,
            anomaly=anomaly,
        )
