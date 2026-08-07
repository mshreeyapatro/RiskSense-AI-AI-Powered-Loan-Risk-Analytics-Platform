import pytest

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as client:
        yield client


def test_health_endpoint_reports_healthy(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_analyze_rejects_missing_fields(client):
    response = client.post("/api/analyze", json={"loan_type": "Personal Loan"})
    assert response.status_code == 400


def test_analyze_returns_full_report_for_valid_application(client):
    payload = {
        "loan_type": "Personal Loan",
        "loan_amount": 200000,
        "tenure": 36,
        "interest": 12.5,
        "purpose": "Debt Consolidation",
        "employment": "Salaried",
        "income": 60000,
        "cibil": 700,
        "emis": 5000,
        "dti": 0.3,
        "property": "Owned",
        "age": 30,
        "gender": "Other",
        "dependents": 1,
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    body = response.get_json()
    assert "prediction" in body
    assert "analytics" in body
    assert "advisory" in body
