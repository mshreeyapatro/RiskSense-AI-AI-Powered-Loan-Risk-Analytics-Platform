# Update Log — 2026-08-07

Summary of changes made in today's session. Nothing below has been committed to
git yet — see `git status` for the full file list.

## 1. Security & hygiene

- **Removed hardcoded `SECRET_KEY` fallback** ([app.py](app.py)). The old
  code fell back to a fixed, publicly-visible-in-source string
  (`"risksense-dev-key-change-in-prod"`), which is forgeable if deployed
  without setting the env var. It now auto-generates a random key per
  process when `SECRET_KEY` isn't set, with a warning logged — no crash, but
  no longer a predictable default either. Multi-worker deployments (e.g.
  gunicorn) still need `SECRET_KEY` set explicitly, since each worker would
  otherwise generate its own key and break session validation across
  workers.
- Added `.env.example` documenting `SECRET_KEY` / `FLASK_DEBUG`.
- Added `.gitignore` (pycache, `.env`, and future `.pkl`/`.csv`/`.docx`
  artifacts). Files already tracked in git — the model, dataset, and reports
  — stay tracked; this only stops new large binaries from being added by
  accident.
- Fixed bare `except:` clauses in [ml/predictor.py](ml/predictor.py) that were
  silently swallowing all exceptions.

## 2. Fixed a dead feature

- Wired up the orphaned Case Management page: added a `/cases` route in
  `app.py` and a nav link in `templates/base.html`. The page was already
  fully built (`templates/cases.html` + `static/js/cases.js`,
  localStorage-based) but had no route pointing to it.

## 3. Deployment

- [dockerfile](dockerfile) now runs the app via `gunicorn` (4 workers)
  instead of Flask's development server; `gunicorn==23.0.0` pinned in
  `requirements.txt`.

## 4. Testing & CI

- Added a `tests/` suite (pytest): pure-logic coverage for
  `calculate_dynamic_threshold` and `AnalyticsAgent.analyze`, plus Flask
  integration tests for `/api/health` and `/api/analyze`.
- Added `requirements-dev.txt` for test dependencies.
- Added `.github/workflows/ci.yml` — runs the test suite on every push/PR to
  `main`.

## 5. New deep learning component: autoencoder anomaly detector

The fraud model was a plain scikit-learn `RandomForestClassifier` — no
learned/deep component. Added a genuine deep learning layer alongside it:

- [ml/autoencoder_model.py](ml/autoencoder_model.py) — a small PyTorch
  `TabularAutoencoder` (28 → 16 → 8 → 16 → 28).
- [train_autoencoder.py](train_autoencoder.py) — trains it **unsupervised**
  on the 44,077 genuine (non-fraud) applications in the dataset, reusing the
  existing `preprocessor.pkl` for feature encoding. Sets the anomaly
  threshold at the 97.5th percentile of genuine validation reconstruction
  error. Produces `autoencoder.pt` (weights) and `autoencoder_meta.pkl`
  (input dim + threshold) — both already trained and committed-ready.
- [ml/anomaly_detector.py](ml/anomaly_detector.py) — inference wrapper;
  returns `None` gracefully if the artifacts aren't present, so the app
  still runs without it.
- Wired into the pipeline:
  - `agents/detection_agent.py` — `DetectionReport` gains an `anomaly` field.
  - `agents/analytics_agent.py` — `analyze()` now takes the full
    `DetectionReport` (was just the prediction) and adds a
    `"Deep Anomaly Signal"` to the risk-signal list (+15 score) when
    reconstruction error exceeds the threshold.
  - `agents/orchestrator.py` — constructs and passes the `AnomalyDetector`
    into the `DetectionAgent`.
  - `app.py` — `/api/analyze` returns an `anomaly` object,
    `/api/batch` returns an `is_anomaly` flag per row, `/api/health` reports
    `deep_anomaly_detector` status.
- No template changes needed — the UI already renders `analytics.signals`
  generically, so the new signal shows up on the Prediction page
  automatically.
- `torch==2.8.0` added to `requirements.txt`, pinned to the CPU-only wheel
  index so CI/deploys don't pull multi-GB CUDA packages.
- 7 new tests added (17 total, all passing):
  `tests/test_anomaly_detector.py`, plus an added case in
  `tests/test_analytics_agent.py`.
- Verified end-to-end via the Flask test client: an intentionally extreme
  application (CIBIL 320, DTI 0.95, unemployed, age 19) correctly returned
  `is_anomaly: true` and surfaced `"Deep Anomaly Signal"` in the response.

## 6. Documentation

- `README.md` updated with an "Deep learning: autoencoder anomaly detector"
  section and updated architecture diagram/requirements.
- Drafted a project abstract (see conversation — not yet saved to a file;
  ask if you want it added as `ABSTRACT.md` or similar).

## Known follow-ups (not done today)

- `scikit-learn` version mismatch: the pickled RandomForest was saved with
  sklearn 1.9.0 but `requirements.txt` pins 1.6.1, producing an
  `InconsistentVersionWarning` on every load. Fix by bumping the pin or
  re-running `train.py` with the installed version.
- Real session-based auth + route guards (currently `/login` doesn't
  actually gate anything).
- Case data persistence (currently browser-only `localStorage`, no backend
  DB or audit trail).
- SHAP-based explainability to replace the Analytics Agent's hardcoded rule
  thresholds.
- Probability calibration (`CalibratedClassifierCV`) for the RandomForest.
- `/api/batch` still loops the pipeline synchronously per application.
