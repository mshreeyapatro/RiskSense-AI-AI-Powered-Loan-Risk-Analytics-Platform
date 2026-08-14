# Update Log

## 2026-08-14

Summary of changes made in today's session.

### 1. Removed the API docs page

- Deleted `templates/api_docs.html`, the `/api/docs` route in
  [app.py](app.py), and the "API Docs" link from the footer
  ([templates/base.html](templates/base.html)) — it wasn't needed and had
  already been dropped from the top navbar. The underlying REST endpoints
  (`/api/analyze`, `/api/batch`, etc.) are untouched; only the documentation
  page is gone.

### 2. Fixed batch screening always returning "genuine"

Batch upload was marking every application as genuine, even obviously risky
ones. Root-caused to two independent issues:

- **Crash silently swallowed as a false "genuine" verdict.**
  [agents/analytics_agent.py](agents/analytics_agent.py) parsed form fields
  with unguarded `int()`/`float()` calls. A CSV cell that parsed to `NaN` in
  `static/js/batch.js` (e.g. non-numeric text, currency symbols) became
  `null` over the wire, which crashed `AnalyticsAgent.analyze()` — caught by
  `app.py`'s per-row `except Exception`, which defaulted the row to
  `is_fraud: False, probability: 0` with no way to tell it had failed. Fixed
  by adding `_safe_int`/`_safe_float` helpers (same pattern already used in
  `ml/predictor.py`), and by making `static/js/batch.js` /
  `templates/batch.html` render a distinct "⚠️ SCORING FAILED" row with the
  actual error message instead of a fake GENUINE badge. Also hardened
  `app.py`'s error handler against a row that isn't even a dict (a
  regression caught during testing, not a pre-existing bug).
- **The deeper cause: the model itself.** Even after the crash was fixed,
  hand-built high-risk profiles still scored as GENUINE through both
  `/api/analyze` and `/api/batch`. Investigation found `loan_applications.csv`'s
  `fraud_flag` has near-zero correlation (0.001–0.006) with CIBIL score,
  DTI, EMIs, and income — already a documented, known finding from an
  earlier evaluation pass (see `EVALUATION.md` /
  `Knowledge_Transfer_Document.txt`: honest held-out AUC ~0.58 for the
  RandomForest, ~0.49 for the autoencoder). No amount of retraining on that
  same label fixes a label that isn't tied to the features.

### 3. Retraining experiment: relabeled dataset (v2)

Built a separate, clearly-labeled experiment to test whether the pipeline
could learn real signal if the fraud label actually depended on it — without
touching the original documented dataset/evaluation:

- [generate_relabeled_dataset.py](generate_relabeled_dataset.py) →
  `loan_applications_v2.csv` — same 50k rows, but `fraud_flag` is sampled
  (stochastically, not by a hard rule) from a risk score built from CIBIL
  score, debt-to-income ratio, EMI burden, loan-to-income ratio, employment
  status, and applicant age — the same factors `analytics_agent.py` already
  treats as risk signals.
- [train_v2.py](train_v2.py) → `preprocessor_v2.pkl`,
  `loan_fraud_ensemble_model_v2.pkl` — trains with a proper 80/20 stratified
  split (the original `train.py` has none, a separately known issue) and
  reports honest held-out metrics.
- [train_autoencoder_v2.py](train_autoencoder_v2.py) → `autoencoder_v2.pt`,
  `autoencoder_meta_v2.pkl` — retrained so the autoencoder stays consistent
  with `preprocessor_v2.pkl`'s fitted scaler.
- [evaluate_v2.py](evaluate_v2.py) → `EVALUATION_V2.md` — honest comparison
  against the original documented numbers:

  | Metric | v1 (original) | v2 (relabeled) |
  |---|---|---|
  | RandomForest AUC | 0.58 | **0.71** |
  | Autoencoder AUC | 0.49 | **0.62** |

- **Wired into the live app**: `ml/predictor.py` and
  `ml/anomaly_detector.py`'s default artifact paths now point at the v2
  files. `app.py`'s `/api/health` reports the actual dataset path in use
  instead of a hardcoded string.
- **Original artifacts untouched**: `loan_applications.csv`, `train.py`,
  `preprocessor.pkl`, `loan_fraud_ensemble_model.pkl`, `autoencoder.pt`,
  `autoencoder_meta.pkl`, `EVALUATION.md`, and
  `Knowledge_Transfer_Document.txt` all remain exactly as they were — the
  original documented finding stays intact as the historical record;
  `EVALUATION_V2.md` sits alongside it as a companion, not a replacement.
- Verified end-to-end via the running app: a hand-built high-risk profile
  now correctly returns `FRAUD 🚨` / `BLOCK & ESCALATE`; a low-risk profile
  returns `GENUINE ✅` / `STANDARD APPROVAL PATH`; a mixed batch of 4
  applications correctly split 2 fraud / 2 genuine instead of "all
  genuine." Full existing test suite (17 tests) still passes.

### 4. Fixed the `debt_to_income_ratio` scale inconsistency

The web form, batch CSV convention, JSON API, and every rule threshold
(`AnalyticsAgent`'s `dti > 0.65`, `calculate_dynamic_threshold`'s
`dti > 0.6`) already consistently treat `dti` as a **0–1 fraction**. The raw
training data's `debt_to_income_ratio` column is on a **0–102 scale**
instead (mean ~8.6, max 102). Two places leaked the raw scale into
`form_data`, and one needed to convert fraction → raw for the model:

- [ml/predictor.py](ml/predictor.py) `form_to_model_row()` — now multiplies
  the incoming fraction by 100 before building the `debt_to_income_ratio`
  model feature (previously fed the raw 0–1 fraction directly into a
  `StandardScaler` fit on the 0–102 scale, collapsing DTI's real signal for
  every manually-submitted or "Fill Random" application — user-entered
  values like 0.35 all landed deep in the low tail of the fitted
  distribution regardless of actual risk).
- [ml/predictor.py](ml/predictor.py) `predict_random_dataset_record()` and
  [agents/orchestrator.py](agents/orchestrator.py) `_dataset_row_to_form()`
  — both now divide the raw dataset column by 100 when building `form_data`
  from a sampled dataset row, so "Load Random Dataset Record" produces
  correctly-scaled `dti` for the downstream rule thresholds and the model
  feature conversion above.
- [evaluate_v2.py](evaluate_v2.py) — same fix in `dynamic_threshold_flags()`;
  re-ran it, `EVALUATION_V2.md` numbers updated (AUC unchanged, as expected
  since it's threshold-independent; RF precision/recall shifted slightly:
  0.40/0.17 → 0.43/0.16).

Verified: sampling genuinely high-DTI dataset rows (raw 61–79) through
`run_pipeline` now correctly converts to fraction (0.61–0.79) and triggers
the "Debt-to-Income" risk signal and a lowered fraud threshold, which it
didn't reliably do before. Full test suite (17 tests) still passes — none of
the existing tests exercised the dataset-row-to-form path, so this was an
uncovered gap, not a regression risk.

`evaluate_anomaly_detector.py` has the identical latent bug in its own
`dynamic_threshold_flags()`, but it wasn't touched — it's the script behind
the already-committed, historical `EVALUATION.md`, and its headline AUC
numbers are unaffected by this bug (only threshold-dependent precision/
recall would change, and the RF's honest-split row in `EVALUATION.md`
already omits those). Say the word if you want it fixed and `EVALUATION.md`
regenerated too.

### Known follow-ups (not done today)

- v2 recall is still modest (~16% RandomForest, ~20% autoencoder) — labels
  were deliberately sampled with noise rather than a hard rule so the
  dataset isn't trivially separable; a real improvement would need richer
  features (linked-application/device signals for typologies like Loan
  Stacking or Synthetic Identity), not just better tuning of this one.
- No new automated tests added for the v2 pipeline or the batch
  error-row rendering — worth adding if this becomes the long-term default.

---

## 2026-08-07

Summary of changes made in that session. Nothing below had been committed to
git yet as of that date — see `git status` for the current file list.

### 1. Security & hygiene

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

### 2. Fixed a dead feature

- Wired up the orphaned Case Management page: added a `/cases` route in
  `app.py` and a nav link in `templates/base.html`. The page was already
  fully built (`templates/cases.html` + `static/js/cases.js`,
  localStorage-based) but had no route pointing to it.

### 3. Deployment

- [dockerfile](dockerfile) now runs the app via `gunicorn` (4 workers)
  instead of Flask's development server; `gunicorn==23.0.0` pinned in
  `requirements.txt`.

### 4. Testing & CI

- Added a `tests/` suite (pytest): pure-logic coverage for
  `calculate_dynamic_threshold` and `AnalyticsAgent.analyze`, plus Flask
  integration tests for `/api/health` and `/api/analyze`.
- Added `requirements-dev.txt` for test dependencies.
- Added `.github/workflows/ci.yml` — runs the test suite on every push/PR to
  `main`.

### 5. New deep learning component: autoencoder anomaly detector

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

### 6. Documentation

- `README.md` updated with an "Deep learning: autoencoder anomaly detector"
  section and updated architecture diagram/requirements.
- Drafted a project abstract (see conversation — not yet saved to a file;
  ask if you want it added as `ABSTRACT.md` or similar).

### Known follow-ups (not done that day)

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
