"""
ML inference layer — loads saved model/preprocessor and runs predictions.
Training logic lives in bankloanfraud.ipynb; this module is inference only.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

import joblib
import pandas as pd

MODEL_PATH = "loan_fraud_ensemble_model.pkl"
PREPROCESSOR_PATH = "preprocessor.pkl"
DATASET_PATH = "loan_applications.csv"

def calculate_dynamic_threshold(form_data: dict[str, Any]) -> float:
    """Calculates a precise fraud threshold tailored to the applicant's profile."""
    BASE_FRAUD_THRESHOLD = 0.40
    threshold = BASE_FRAUD_THRESHOLD
    
    # Extract key metrics safely
    try: cibil = int(float(form_data.get("cibil", 600)))
    except: cibil = 600
    
    try: dti = float(form_data.get("dti", 0.4))
    except: dti = 0.4
    
    try:
        emis = float(form_data.get("emis", 0))
        income = float(form_data.get("income", 1))
        emi_burden = emis / income if income > 0 else 0
    except: emi_burden = 0

    # Adjust threshold based on risk gravity
    # Very poor credit score = stricter (lower) threshold to catch fraud
    if cibil < 500:
        threshold -= 0.10
    elif cibil > 750:
        threshold += 0.10  # Exceptional credit = relaxed threshold

    # High debt-to-income ratio reduces threshold tolerance
    if dti > 0.6:
        threshold -= 0.05
        
    # High EMI burden reduces threshold tolerance
    if emi_burden > 0.5:
        threshold -= 0.05
        
    # Clamp threshold between 20% and 60%
    return max(0.20, min(0.60, threshold))


@dataclass
class PredictionResult:
    label: str
    probability: float
    probability_display: str
    is_fraud: bool
    applied_threshold: float
    record_index: int | None = None
    actual_label: str | None = None


class FraudPredictor:
    """Wraps ensemble model inference without altering training or model artifacts."""

    def __init__(
        self,
        model_path: str = MODEL_PATH,
        preprocessor_path: str = PREPROCESSOR_PATH,
        dataset_path: str = DATASET_PATH,
    ):
        self.model = joblib.load(model_path)
        self.preprocessor = joblib.load(preprocessor_path)
        self.dataset = pd.read_csv(dataset_path)

    def _safe_float(self, val: Any, default: float = 0.0) -> float:
        try: return float(val) if val else default
        except (ValueError, TypeError): return default

    def _safe_int(self, val: Any, default: int = 0) -> int:
        try: return int(float(val)) if val else default
        except (ValueError, TypeError): return default

    def form_to_model_row(self, form_data: dict[str, Any]) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "loan_type": form_data.get("loan_type", "Personal Loan"),
                    "loan_amount_requested": self._safe_float(form_data.get("loan_amount")),
                    "loan_tenure_months": self._safe_int(form_data.get("tenure")),
                    "interest_rate_offered": self._safe_float(form_data.get("interest")),
                    "purpose_of_loan": form_data.get("purpose", "Other"),
                    "employment_status": form_data.get("employment", "Unemployed"),
                    "monthly_income": self._safe_float(form_data.get("income")),
                    "cibil_score": self._safe_int(form_data.get("cibil"), 500),
                    "existing_emis_monthly": self._safe_float(form_data.get("emis")),
                    "debt_to_income_ratio": self._safe_float(form_data.get("dti")),
                    "property_ownership_status": form_data.get("property", "Rented"),
                    "applicant_age": self._safe_int(form_data.get("age"), 30),
                    "gender": form_data.get("gender", "Other"),
                    "number_of_dependents": self._safe_int(form_data.get("dependents")),
                }
            ]
        )

    def predict_from_form(self, form_data: dict[str, Any]) -> PredictionResult:
        dynamic_thresh = calculate_dynamic_threshold(form_data)
        input_df = self.form_to_model_row(form_data)
        return self._predict_dataframe(input_df, dynamic_thresh)

    def predict_random_dataset_record(self) -> tuple[PredictionResult, int, pd.Series]:
        record_index = random.randint(0, len(self.dataset) - 1)
        row = self.dataset.iloc[record_index]
        
        # Convert raw row into proper ML format dataframe safely, dropping system ids
        form_mock = {
            "loan_type": str(row.get("loan_type", "")),
            "loan_amount": float(row.get("loan_amount_requested", 0)),
            "tenure": int(row.get("loan_tenure_months", 0)),
            "interest": float(row.get("interest_rate_offered", 0)),
            "purpose": str(row.get("purpose_of_loan", "")),
            "employment": str(row.get("employment_status", "")),
            "income": float(row.get("monthly_income", 0)),
            "cibil": int(row.get("cibil_score", 0)),
            "emis": float(row.get("existing_emis_monthly", 0)),
            "dti": float(row.get("debt_to_income_ratio", 0)),
            "property": str(row.get("property_ownership_status", "")),
            "age": int(row.get("applicant_age", 0)),
            "gender": str(row.get("gender", "")),
            "dependents": int(row.get("number_of_dependents", 0))
        }
        
        dynamic_thresh = calculate_dynamic_threshold(form_mock)
        feature_df = self.form_to_model_row(form_mock)
        result = self._predict_dataframe(feature_df, dynamic_thresh)
        
        actual_label = "FRAUD 🚨" if row.get("fraud_flag", 0) == 1 else "GENUINE ✅"
        result.record_index = record_index
        result.actual_label = actual_label
        return result, record_index, row

    def _predict_dataframe(self, input_df: pd.DataFrame, threshold: float) -> PredictionResult:
        X = self.preprocessor.transform(input_df)
        probability_value = float(self.model.predict_proba(X)[0][1])
        is_fraud = probability_value >= threshold
        label = "FRAUD 🚨" if is_fraud else "GENUINE ✅"
        return PredictionResult(
            label=label,
            probability=probability_value,
            probability_display=f"{probability_value:.2%}",
            is_fraud=is_fraud,
            applied_threshold=threshold,
        )

    @staticmethod
    def generate_random_form_data() -> dict[str, Any]:
        return {
            "loan_type": random.choice(
                [
                    "Home Loan",
                    "Personal Loan",
                    "Car Loan",
                    "Education Loan",
                    "Business Loan",
                ]
            ),
            "loan_amount": random.randint(100000, 5000000),
            "tenure": random.randint(12, 360),
            "interest": round(random.uniform(7.0, 18.0), 2),
            "purpose": random.choice(
                [
                    "Business Expansion",
                    "Debt Consolidation",
                    "Education",
                    "Home Renovation",
                    "Medical Emergency",
                    "Vehicle Purchase",
                    "Wedding",
                ]
            ),
            "employment": random.choice(
                [
                    "Salaried",
                    "Self-Employed",
                    "Business Owner",
                    "Student",
                    "Unemployed",
                    "Retired",
                ]
            ),
            "income": random.randint(15000, 200000),
            "cibil": random.randint(300, 900),
            "emis": random.randint(0, 50000),
            "dti": round(random.uniform(0.1, 0.9), 2),
            "property": random.choice(["Owned", "Rented", "Jointly Owned"]),
            "age": random.randint(18, 70),
            "gender": random.choice(["Male", "Female", "Other"]),
            "dependents": random.randint(0, 5),
        }
