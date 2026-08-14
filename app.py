import json
import os
import secrets
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template, request

from agents.orchestrator import RiskSenseOrchestrator
from ml.predictor import DATASET_PATH, FraudPredictor

app = Flask(__name__)

_secret_key = os.environ.get("SECRET_KEY")
if not _secret_key:
    _secret_key = secrets.token_hex(32)
    app.logger.warning(
        "SECRET_KEY not set; generated a random key for this process. Sessions "
        "won't persist across restarts and will break across multiple workers "
        "(e.g. gunicorn). Set SECRET_KEY explicitly for production or "
        "multi-worker deployments."
    )
app.secret_key = _secret_key

predictor = FraudPredictor()
orchestrator = RiskSenseOrchestrator(predictor)


# ---- Page Routes -------------------------------------------------------

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/agents")
def agents():
    return render_template("agents.html")


@app.route("/compare")
def compare():
    return render_template("compare.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/batch")
def batch():
    return render_template("batch.html")


@app.route("/cases")
def cases():
    return render_template("cases.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    selected_role = None
    if request.method == "POST":
        selected_role = request.form.get("role", "analyst")
    return render_template("login.html", selected_role=selected_role)


@app.route("/advisor", methods=["GET", "POST"])
def advisor():
    reply = None
    last_application = None
    if request.method == "POST":
        user_message = request.form.get("message", "").strip()
        session_app = request.form.get("application_json")
        form_data = None
        if session_app:
            try:
                form_data = json.loads(session_app)
            except json.JSONDecodeError:
                form_data = None
        reply = orchestrator.chat_response(user_message, form_data)
        last_application = session_app
    return render_template(
        "advisor.html",
        reply=reply,
        application_json=last_application,
    )


@app.route("/prediction", methods=["GET", "POST"])
def prediction():
    agentic_report = None
    random_data = None
    form_data = None
    record_index = None

    clear_form = request.method == "GET" and request.args.get("clear") == "true"

    if request.method == "POST":
        mode = request.form.get("mode")

        if mode == "fill_random":
            random_data = predictor.generate_random_form_data()

        elif mode == "manual":
            form_data = dict(request.form)
            try:
                agentic_report = orchestrator.run_pipeline(form_data)
            except Exception as exc:
                app.logger.error("Pipeline error: %s", exc)
                agentic_report = None

        elif mode == "random_index":
            try:
                agentic_report, record_index = orchestrator.run_dataset_sample()
            except Exception as exc:
                app.logger.error("Dataset sample error: %s", exc)

    if clear_form:
        random_data = None
        form_data = None

    application_json = json.dumps(form_data) if form_data else None

    return render_template(
        "prediction.html",
        agentic_report=agentic_report,
        random_data=random_data,
        form_data=form_data,
        record_index=record_index,
        application_json=application_json,
    )


# ---- REST API ----------------------------------------------------------

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """JSON API for agentic pipeline (optional integrations)."""
    data = request.get_json(silent=True) or {}
    required = ["loan_type", "loan_amount", "tenure", "interest", "purpose"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing application fields"}), 400
    try:
        report = orchestrator.run_pipeline(data)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    pred = report.detection.prediction
    return jsonify(
        {
            "platform": report.platform,
            "timestamp": report.timestamp,
            "prediction": {
                "label": pred.label,
                "probability": pred.probability,
                "is_fraud": pred.is_fraud,
            },
            "analytics": {
                "risk_score": report.analytics.risk_score,
                "risk_level": report.analytics.risk_level,
                "signals": [
                    {"factor": s.factor, "severity": s.severity, "detail": s.detail}
                    for s in report.analytics.signals
                ],
            },
            "anomaly": (
                {
                    "reconstruction_error": report.detection.anomaly.reconstruction_error,
                    "threshold": report.detection.anomaly.threshold,
                    "is_anomaly": report.detection.anomaly.is_anomaly,
                }
                if report.detection.anomaly
                else None
            ),
            "advisory": {
                "decision": report.advisory.decision,
                "items": [
                    {"priority": i.priority, "action": i.action, "rationale": i.rationale}
                    for i in report.advisory.items
                ],
            },
            "executive_summary": report.executive_summary,
        }
    )


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """AJAX endpoint for advisor chat (used by advisor.js)."""
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    form_data = data.get("application_data")

    if not message:
        return jsonify({"error": "No message provided"}), 400

    try:
        reply = orchestrator.chat_response(message, form_data)
        return jsonify({"reply": reply})
    except Exception as exc:
        app.logger.error("Chat error: %s", exc)
        return jsonify({"error": "Advisory agent error"}), 500


@app.route("/api/dataset/random", methods=["GET"])
def api_dataset_random():
    """Returns a random record from the dataset formatted for the form."""
    try:
        _, record_index, row = predictor.predict_random_dataset_record()
        form_data = orchestrator._dataset_row_to_form(row)
        return jsonify({"record_index": record_index, "form_data": form_data})
    except Exception as exc:
        app.logger.error("Dataset random error: %s", exc)
        return jsonify({"error": "Failed to load random record"}), 500


@app.route("/api/batch", methods=["POST"])
def api_batch():
    """Batch process multiple loan applications from JSON array."""
    data = request.get_json(silent=True) or {}
    applications = data.get("applications", [])

    if not applications or not isinstance(applications, list):
        return jsonify({"error": "Expected 'applications' array"}), 400

    if len(applications) > 500:
        return jsonify({"error": "Batch limit is 500 applications"}), 400

    results = []
    fraud_count = 0
    total_amount = 0

    for i, app_data in enumerate(applications):
        try:
            report = orchestrator.run_pipeline(app_data)
            pred = report.detection.prediction
            if pred.is_fraud:
                fraud_count += 1
            try:
                amt = float(app_data.get("loan_amount", 0))
                total_amount += amt
            except Exception:
                pass

            results.append({
                "index": i + 1,
                "loan_type": app_data.get("loan_type", "Unknown"),
                "loan_amount": app_data.get("loan_amount", 0),
                "is_fraud": pred.is_fraud,
                "probability": round(pred.probability, 4),
                "label": pred.label,
                "risk_score": report.analytics.risk_score,
                "risk_level": report.analytics.risk_level,
                "decision": report.advisory.decision,
                "is_anomaly": bool(report.detection.anomaly and report.detection.anomaly.is_anomaly),
            })
        except Exception as exc:
            safe_data = app_data if isinstance(app_data, dict) else {}
            results.append({
                "index": i + 1,
                "loan_type": safe_data.get("loan_type", "Unknown"),
                "loan_amount": safe_data.get("loan_amount", 0),
                "error": str(exc),
                "is_fraud": False,
                "probability": 0,
                "risk_score": 0,
                "risk_level": "Unknown",
            })

    return jsonify({
        "total": len(results),
        "fraud_count": fraud_count,
        "genuine_count": len(results) - fraud_count,
        "fraud_rate": round(fraud_count / max(len(results), 1) * 100, 1),
        "total_portfolio_value": round(total_amount, 2),
        "estimated_fraud_exposure": round(total_amount * (fraud_count / max(len(results), 1)), 2),
        "results": results,
    })


@app.route("/api/health", methods=["GET"])
def api_health():
    """System health and model information endpoint."""
    try:
        dataset_size = len(predictor.dataset)
        model_type = type(predictor.model).__name__
        # Get feature count
        try:
            n_features = predictor.preprocessor.n_features_in_
        except Exception:
            n_features = "N/A"

        return jsonify({
            "status": "healthy",
            "platform": "RiskSense AI: Agentic Banking Fraud Analytics and Advisory Platform",
            "version": "2.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": {
                "type": model_type,
                "status": "loaded",
                "n_features": n_features,
                "threshold_range": "20%–60% (dynamic)",
            },
            "dataset": {
                "records": dataset_size,
                "path": DATASET_PATH,
                "status": "loaded",
            },
            "agents": {
                "detection": "online",
                "analytics": "online",
                "advisory": "online",
                "orchestrator": "online",
                "deep_anomaly_detector": "online" if orchestrator.anomaly_detector else "unavailable (run train_autoencoder.py)",
            },
            "features": {
                "batch_screening": True,
                "pdf_reports": True,
                "dark_mode": True,
                "role_based_access": True,
                "explainability": True,
            }
        })
    except Exception as exc:
        return jsonify({"status": "degraded", "error": str(exc)}), 500


# ---- Error Handlers ----------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


# ---- Entry Point -------------------------------------------------------

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=5000, debug=debug)
