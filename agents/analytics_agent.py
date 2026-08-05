"""
Analytics Agent — interprets application features and explains risk drivers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ml.predictor import PredictionResult


@dataclass
class RiskSignal:
    factor: str
    severity: str
    detail: str


@dataclass
class AnalyticsReport:
    agent_name: str
    role: str
    status: str
    risk_score: int
    risk_level: str
    signals: list[RiskSignal] = field(default_factory=list)
    narrative: str = ""


class AnalyticsAgent:
    AGENT_NAME = "Analytics Agent"
    ROLE = "Feature Risk Interpretation"

    def analyze(
        self, form_data: dict[str, Any], prediction: PredictionResult
    ) -> AnalyticsReport:
        signals: list[RiskSignal] = []
        score = 0

        cibil = int(form_data.get("cibil", 0))
        dti = float(form_data.get("dti", 0))
        income = float(form_data.get("income", 1))
        loan_amount = float(form_data.get("loan_amount", 0))
        emis = float(form_data.get("emis", 0))
        employment = form_data.get("employment", "")
        age = int(form_data.get("age", 0))

        if cibil < 550:
            score += 25
            signals.append(
                RiskSignal(
                    "CIBIL Score",
                    "high",
                    f"Score {cibil} is below acceptable lending band (<550).",
                )
            )
        elif cibil < 650:
            score += 12
            signals.append(
                RiskSignal(
                    "CIBIL Score",
                    "medium",
                    f"Score {cibil} is moderate; additional credit checks advised.",
                )
            )

        if dti > 0.65:
            score += 22
            signals.append(
                RiskSignal(
                    "Debt-to-Income",
                    "high",
                    f"DTI {dti:.2f} exceeds prudent limit (0.65).",
                )
            )
        elif dti > 0.5:
            score += 10
            signals.append(
                RiskSignal(
                    "Debt-to-Income",
                    "medium",
                    f"DTI {dti:.2f} is elevated.",
                )
            )

        loan_to_income = loan_amount / max(income * 12, 1)
        if loan_to_income > 8:
            score += 18
            signals.append(
                RiskSignal(
                    "Loan-to-Annual-Income",
                    "high",
                    f"Requested loan is {loan_to_income:.1f}x annual income.",
                )
            )

        if emis > income * 0.5:
            score += 15
            signals.append(
                RiskSignal(
                    "Existing EMIs",
                    "high",
                    f"EMIs (${emis:,.0f}) consume over 50% of monthly income.",
                )
            )

        if employment in ("Unemployed", "Student"):
            score += 20
            signals.append(
                RiskSignal(
                    "Employment Status",
                    "high",
                    f"Applicant status '{employment}' increases default and fraud exposure.",
                )
            )

        if age < 21 or age > 65:
            score += 8
            signals.append(
                RiskSignal(
                    "Applicant Age",
                    "medium",
                    f"Age {age} is outside typical prime borrowing range.",
                )
            )

        model_boost = int(prediction.probability * 40)
        score = min(100, score + model_boost)

        if score >= 70:
            level, status = "Critical", "alert"
        elif score >= 45:
            level, status = "High", "warning"
        elif score >= 25:
            level, status = "Moderate", "warning"
        else:
            level, status = "Low", "success"

        if not signals:
            signals.append(
                RiskSignal(
                    "Profile",
                    "low",
                    "No major rule-based risk flags; model score drives primary assessment.",
                )
            )

        narrative = (
            f"Composite feature risk score {score}/100 ({level}). "
            f"Identified {len(signals)} signal(s) aligned with "
            f"{'fraud' if prediction.is_fraud else 'genuine'} model output."
        )

        return AnalyticsReport(
            agent_name=self.AGENT_NAME,
            role=self.ROLE,
            status=status,
            risk_score=score,
            risk_level=level,
            signals=signals,
            narrative=narrative,
        )
