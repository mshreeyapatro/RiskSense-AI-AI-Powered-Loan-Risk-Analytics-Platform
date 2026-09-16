"""
RiskSense Orchestrator — coordinates Detection, Analytics, and Advisory agents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import os

from agents.advisory_agent import AdvisoryAgent, AdvisoryReport
from agents.analytics_agent import AnalyticsAgent, AnalyticsReport
from agents.detection_agent import DetectionAgent, DetectionReport
from ml.anomaly_detector import AnomalyDetector
from ml.predictor import FraudPredictor




@dataclass
class AgentStep:
    agent: str
    role: str
    status: str
    message: str


@dataclass
class AgenticReport:
    platform: str
    timestamp: str
    application_summary: dict[str, Any]
    detection: DetectionReport
    analytics: AnalyticsReport
    advisory: AdvisoryReport
    workflow_steps: list[AgentStep] = field(default_factory=list)
    executive_summary: str = ""


class RiskSenseOrchestrator:
    PLATFORM_NAME = "RiskSense AI: Agentic Banking Fraud Analytics and Advisory Platform"

    def __init__(self, predictor: FraudPredictor | None = None):
        self.predictor = predictor or FraudPredictor()
        self.anomaly_detector = AnomalyDetector.load(self.predictor)
        self.detection_agent = DetectionAgent(self.predictor, self.anomaly_detector)
        self.analytics_agent = AnalyticsAgent()
        self.advisory_agent = AdvisoryAgent()

    def run_pipeline(self, form_data: dict[str, Any]) -> AgenticReport:
        steps: list[AgentStep] = []

        steps.append(
            AgentStep(
                "Orchestrator",
                "Workflow Control",
                "active",
                "Received loan application; initiating multi-agent fraud analysis.",
            )
        )

        detection = self.detection_agent.score_application(form_data)
        steps.append(
            AgentStep(
                detection.agent_name,
                detection.role,
                detection.status,
                detection.summary,
            )
        )

        analytics = self.analytics_agent.analyze(form_data, detection)
        steps.append(
            AgentStep(
                analytics.agent_name,
                analytics.role,
                analytics.status,
                analytics.narrative,
            )
        )

        advisory = self.advisory_agent.advise(form_data, detection, analytics)
        steps.append(
            AgentStep(
                advisory.agent_name,
                advisory.role,
                advisory.status,
                f"Recommended decision: {advisory.decision}",
            )
        )

        executive = (
            f"{advisory.decision} — {detection.prediction.label} at "
            f"{detection.prediction.probability_display} fraud probability. "
            f"Feature risk: {analytics.risk_level} ({analytics.risk_score}/100)."
        )

        return AgenticReport(
            platform=self.PLATFORM_NAME,
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            application_summary=self._summarize_application(form_data),
            detection=detection,
            analytics=analytics,
            advisory=advisory,
            workflow_steps=steps,
            executive_summary=executive,
        )

    def run_dataset_sample(self) -> tuple[AgenticReport, int]:
        detection, record_index = self.detection_agent.score_dataset_record()
        row = self.predictor.dataset.iloc[record_index]
        form_data = self._dataset_row_to_form(row)
        analytics = self.analytics_agent.analyze(form_data, detection)
        advisory = self.advisory_agent.advise(form_data, detection, analytics)

        steps = [
            AgentStep(
                "Orchestrator",
                "Workflow Control",
                "active",
                f"Loaded dataset record #{record_index} for agentic evaluation.",
            ),
            AgentStep(
                detection.agent_name,
                detection.role,
                detection.status,
                detection.summary,
            ),
            AgentStep(
                analytics.agent_name,
                analytics.role,
                analytics.status,
                analytics.narrative,
            ),
            AgentStep(
                advisory.agent_name,
                advisory.role,
                advisory.status,
                f"Recommended decision: {advisory.decision}",
            ),
        ]

        executive = (
            f"{advisory.decision} — Predicted {detection.prediction.label} "
            f"(actual: {detection.prediction.actual_label}) at "
            f"{detection.prediction.probability_display}."
        )

        report = AgenticReport(
            platform=self.PLATFORM_NAME,
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            application_summary=self._summarize_application(form_data),
            detection=detection,
            analytics=analytics,
            advisory=advisory,
            workflow_steps=steps,
            executive_summary=executive,
        )
        return report, record_index

    @staticmethod
    def _summarize_application(form_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "loan_type": form_data.get("loan_type"),
            "loan_amount": form_data.get("loan_amount"),
            "employment": form_data.get("employment"),
            "cibil": form_data.get("cibil"),
            "dti": form_data.get("dti"),
            "monthly_income": form_data.get("income"),
        }

    @staticmethod
    def _dataset_row_to_form(row) -> dict[str, Any]:
        return {
            "loan_type": str(row.get("loan_type", "")),
            "loan_amount": float(row.get("loan_amount_requested", 0)),
            "tenure": int(row.get("loan_tenure_months", 0)),
            "interest": float(row.get("interest_rate_offered", 0)),
            "purpose": str(row.get("purpose_of_loan", "")),
            "employment": str(row.get("employment_status", "")),
            "income": float(row.get("monthly_income", 0)),
            "cibil": int(row.get("cibil_score", 0)),
            "emis": float(row.get("existing_emis_monthly", 0)),
            # debt_to_income_ratio in the raw dataset is on a 0-102 scale; this form_data
            # dict flows into AnalyticsAgent's dti > 0.65 rule and FraudPredictor's dti-based
            # logic, both of which expect the 0-1 fraction convention used elsewhere.
            "dti": float(row.get("debt_to_income_ratio", 0)) / 100,
            "property": str(row.get("property_ownership_status", "")),
            "age": int(row.get("applicant_age", 0)),
            "gender": str(row.get("gender", "")),
            "dependents": int(row.get("number_of_dependents", 0)),
        }

    def chat_response(self, user_message: str, form_data: dict[str, Any] | None) -> str:
        """Highly advanced local heuristic conversational engine."""
        msg = user_message.lower().strip()
        
        # ----------------------------------------------------
        # EXCLUSIVE NATIVE LOGIC ENGINE
        # ----------------------------------------------------
        if not form_data:
            if "agent" in msg or "workflow" in msg or "how" in msg:
                return (
                    "**RiskSense Agent Ecosystem**\n"
                    "I am powered by three coordinated local algorithms:\n"
                    "- 🛡️ **Detection Agent:** Rapidly evaluates thousands of trees in a random forest ensemble to calculate raw baseline fraud probability.\n"
                    "- 📊 **Analytics Agent:** Ingests the model output along with hard CIBIL/DTI boundaries to assign concrete risk gravity tiers.\n"
                    "- ⚖️ **Advisory Agent:** Translates the empirical numbers into safe, actionable banking compliance mandates.\n\n"
                    "Submit an application on the Prediction page to unleash this pipeline."
                )
            
            return (
                "**Welcome to the RiskSense AI Neural Interface.**\n\n"
                "I am fully operational. I can dynamically explain fraud risk, isolate driving variables, "
                "recommend policy actions, and summarize pipeline anomalies without requiring an external connection.\n\n"
                "*Tip: Go to the Prediction page, load a dataset record, run the Agentic Analysis, and click 'Discuss with AI Advisor' to context-link your data here.*"
            )

        # Context-Linked Responses
        report = self.run_pipeline(form_data)
        pred = report.detection.prediction
        
        # Determine sentiment and intro
        is_safe = not pred.is_fraud
        primary_sentiment = "Genuine ✅" if is_safe else "Flagged for Fraud 🚨"
        action_verb = "approve immediately" if is_safe else "quarantine for enhanced due diligence"
        
        # 1. Why / Explain / Risk / Reasons
        if "why" in msg or "explain" in msg or "risk" in msg or "reason" in msg or "detail" in msg:
            signals = ""
            if len(report.analytics.signals) > 0:
                signals = "\n".join(f"- **{s.factor}** ({s.severity}): {s.detail}" for s in report.analytics.signals)
            else:
                signals = "- All financial parameters map strictly to generic market averages. No anomalies detected."
                
            return (
                f"### Comprehensive Risk Deep-Dive\n\n"
                f"My Detection Agent mathematically calculated a **{pred.probability_display} fraud probability**. Because the system was utilizing a dynamically hardened threshold of **{pred.applied_threshold:.0%}** for this specific socio-economic profile, this application was ultimately **{primary_sentiment}**.\n\n"
                f"**The Analytics Agent flagged the following isolation drivers:**\n{signals}\n\n"
                f"**Net Gravity Score:** The composite structural risk is evaluated safely at **{report.analytics.risk_score}/100** ({report.analytics.risk_level} band).\n\n"
                f"*To see what policy mandates apply to these parameters, ask me for 'recommendations'.*"
            )

        # 2. Actions / Recommendations / Proceed
        if "action" in msg or "recommend" in msg or "what should" in msg or "proceed" in msg or "do" in msg:
            actions = "\n".join(f"- **[{a.priority.upper()}] {a.action}:** {a.rationale}" for a in report.advisory.items)
            
            return (
                f"### Standard Operating Procedure (SOP) Directives\n\n"
                f"Given the isolated risk vectors on this application (notably, the {pred.probability_display} confidence interval out of the detection phase), banking personnel should **{action_verb}**.\n\n"
                f"**Mandated Action Protocols:**\n{actions}\n\n"
                f"*{report.advisory.compliance_note}*"
            )
            
        # 3. Summary / Anything Else
        return (
            f"### Executive Intelligence Brief\n\n"
            f"> **System Verdict:** {report.advisory.decision}\n\n"
            f"{report.executive_summary}\n\n"
            f"**Recommended subsequent queries:**\n"
            f"- *'Can you explain the exact reasons for this risk level?'*\n"
            f"- *'What specific actions should the underwriter take now?'*\n"
            f"- *'How does the multi-agent workflow handle this?'*"
        )
