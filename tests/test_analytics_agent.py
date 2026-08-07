from agents.analytics_agent import AnalyticsAgent
from agents.detection_agent import DetectionReport
from ml.anomaly_detector import AnomalyResult
from ml.predictor import PredictionResult


def _detection(probability=0.1, is_fraud=False, anomaly=None):
    prediction = PredictionResult(
        label="GENUINE" if not is_fraud else "FRAUD",
        probability=probability,
        probability_display=f"{probability:.2%}",
        is_fraud=is_fraud,
        applied_threshold=0.40,
    )
    return DetectionReport(
        agent_name="Detection Agent",
        role="ML Fraud Scoring",
        status="alert" if is_fraud else "success",
        prediction=prediction,
        summary="",
        confidence_band="High Risk" if is_fraud else "Low Risk",
        anomaly=anomaly,
    )


def test_clean_application_scores_low_risk():
    form_data = {
        "cibil": 780,
        "dti": 0.2,
        "income": 100000,
        "loan_amount": 200000,
        "emis": 5000,
        "employment": "Salaried",
        "age": 35,
    }
    report = AnalyticsAgent().analyze(form_data, _detection())

    assert report.risk_level == "Low"
    assert report.status == "success"
    assert report.risk_score < 25


def test_risky_application_flags_multiple_signals_and_high_score():
    form_data = {
        "cibil": 400,
        "dti": 0.8,
        "income": 10000,
        "loan_amount": 5000000,
        "emis": 8000,
        "employment": "Unemployed",
        "age": 19,
    }
    report = AnalyticsAgent().analyze(form_data, _detection(probability=0.9, is_fraud=True))

    factors = {signal.factor for signal in report.signals}
    assert "CIBIL Score" in factors
    assert "Debt-to-Income" in factors
    assert "Employment Status" in factors
    assert report.risk_level in ("High", "Critical")
    assert report.risk_score == 100


def test_no_signals_falls_back_to_profile_placeholder():
    form_data = {
        "cibil": 780,
        "dti": 0.1,
        "income": 100000,
        "loan_amount": 100000,
        "emis": 0,
        "employment": "Salaried",
        "age": 40,
    }
    report = AnalyticsAgent().analyze(form_data, _detection())

    assert len(report.signals) == 1
    assert report.signals[0].factor == "Profile"


def test_flagged_anomaly_adds_deep_signal_and_boosts_score():
    form_data = {
        "cibil": 780,
        "dti": 0.1,
        "income": 100000,
        "loan_amount": 100000,
        "emis": 0,
        "employment": "Salaried",
        "age": 40,
    }
    anomaly = AnomalyResult(reconstruction_error=0.9, threshold=0.2, is_anomaly=True)
    clean_report = AnalyticsAgent().analyze(form_data, _detection())
    flagged_report = AnalyticsAgent().analyze(form_data, _detection(anomaly=anomaly))

    factors = {signal.factor for signal in flagged_report.signals}
    assert "Deep Anomaly Signal" in factors
    assert flagged_report.risk_score == clean_report.risk_score + 15
