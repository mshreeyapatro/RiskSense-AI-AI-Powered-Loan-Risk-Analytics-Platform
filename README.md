# RiskSense AI

**Agentic Banking Fraud Analytics and Advisory Platform**

Multi-agent orchestration layer on top of your existing loan fraud ensemble model. ML training (`bankloanfraud.ipynb`), model artifacts, and inference logic are preserved.

## Architecture

```
Application → Orchestrator → Detection Agent (ML) → Analytics Agent → Advisory Agent → Report
```

| Agent | Role |
|-------|------|
| **Detection Agent** | Runs `loan_fraud_ensemble_model.pkl` + `preprocessor.pkl` (40% threshold) |
| **Analytics Agent** | Explains CIBIL, DTI, income, employment risk signals |
| **Advisory Agent** | Banking actions: block, manual review, or standard path |

## Requirements

Place these files in the project root (from your notebook training):

- `loan_fraud_ensemble_model.pkl`
- `preprocessor.pkl`
- `loan_fraud_smote_balanced_dataset.csv`

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
