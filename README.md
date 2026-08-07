# RiskSense AI

**Agentic Banking Fraud Analytics and Advisory Platform**

Multi-agent orchestration layer on top of your existing loan fraud ensemble model. ML training (`bankloanfraud.ipynb`), model artifacts, and inference logic are preserved.

## Architecture

```
Application → Orchestrator → Detection Agent (ML + Deep Anomaly Detector) → Analytics Agent → Advisory Agent → Report
```

| Agent | Role |
|-------|------|
| **Detection Agent** | Runs `loan_fraud_ensemble_model.pkl` + `preprocessor.pkl` (dynamic threshold), plus the PyTorch autoencoder anomaly detector |
| **Analytics Agent** | Explains CIBIL, DTI, income, employment risk signals, and deep-anomaly signals |
| **Advisory Agent** | Banking actions: block, manual review, or standard path |

### Deep learning: autoencoder anomaly detector

A `TabularAutoencoder` ([ml/autoencoder_model.py](ml/autoencoder_model.py), PyTorch) is trained unsupervised on genuine (non-fraud) applications only ([train_autoencoder.py](train_autoencoder.py)). It learns to reconstruct normal applicant profiles; applications whose reconstruction error exceeds the learned threshold (97.5th percentile of genuine validation error) are flagged as anomalous — surfacing patterns the supervised RandomForest wasn't trained to recognize. Wired into the pipeline via [ml/anomaly_detector.py](ml/anomaly_detector.py), it contributes a `Deep Anomaly Signal` to the Analytics Agent's report and is included in `/api/analyze` and `/api/batch` responses. If `autoencoder.pt`/`autoencoder_meta.pkl` aren't present, the app runs fine without it (reported as `unavailable` in `/api/health`).

## Requirements

Place these files in the project root (from your notebook training):

- `loan_fraud_ensemble_model.pkl`
- `preprocessor.pkl`
- `loan_fraud_smote_balanced_dataset.csv`

Then train the anomaly detector (reuses `preprocessor.pkl`):

```bash
python train_autoencoder.py
```

## Run

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000

## API

`POST /api/analyze` with JSON application fields returns agentic pipeline results.

## Pages

- `/` — Home
- `/prediction` — Agentic fraud analysis
- `/agents` — Agent architecture
- `/advisor` — Conversational advisor (context-aware after prediction)
- `/about` — Platform overview
