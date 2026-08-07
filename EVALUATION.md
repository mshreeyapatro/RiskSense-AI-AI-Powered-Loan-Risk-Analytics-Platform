# Model Evaluation

Generated from `evaluate_anomaly_detector.py` plus a follow-up diagnostic on
the RandomForest. This report exists to answer one question honestly: **does
either model actually detect fraud on data it hasn't seen before?**

## Critical finding: the committed RandomForest was never evaluated on held-out data

`train.py` (pre-existing, not part of today's changes) fits the preprocessor,
applies SMOTE, and trains the RandomForest on **100% of the dataset** — there
is no train/test split anywhere in the training pipeline. Scoring the
committed `loan_fraud_ensemble_model.pkl` on the same data it was trained on
gives:

- **AUC: 1.0000, Precision/Recall/F1: 1.0000** — a perfect score.

That is not evidence of a good model — with unlimited-depth trees, a
RandomForest can memorize its training set almost exactly, especially at
n_estimators=100 with no depth/leaf constraints. To check, we retrained an
identical RandomForest (same architecture, same SMOTE step) on an 80/20
stratified split, held out and never trained on:

- **Honest test AUC on unseen data: 0.5847**

That's barely better than a coin flip (AUC 0.5 = random). This is the real
headline result: **on this dataset, the fraud label does not appear to be
strongly predictable from the given applicant features**, at least not by a
RandomForest of this configuration. The platform's UI and API currently
present the memorized model's confident-looking probabilities without this
context.

## Autoencoder anomaly detector

### Methodology

The autoencoder trains only on genuine (non-fraud) applications
(`train_autoencoder.py`), using a 90/10 train/validation split. Scoring it on
genuine rows it trained on would inflate its apparent performance, so this
evaluation uses only:

- The held-out 10% validation split of genuine records (4,897 rows) — never seen during training.
- All labeled fraud records (1,026 rows) — the autoencoder never trains on fraud at all.

Evaluation-set fraud rate is 17.3% (vs. ~2.1% in the full dataset) — a side
effect of excluding the 90% of genuine rows used for training, not a claim
about real-world prevalence. AUC is the primary metric for that reason.

### Results

| Metric | RandomForest — as deployed (evaluated on training data) | RandomForest — honest (held-out 20% split) | Autoencoder (unsupervised, held-out) |
|---|---|---|---|
| ROC-AUC | 1.0000 | 0.5847 | 0.4947 |
| Precision | 1.0000 | — | 0.2013 |
| Recall | 1.0000 | — | 0.0302 |
| F1 | 1.0000 | — | 0.0525 |

(Precision/recall for the honest RF split weren't computed in this pass — AUC
alone already makes the point. Ask if you want the full confusion matrix
there too.)

## Interpretation

Neither model separates fraud from genuine applications well on unseen data:
the honestly-evaluated RandomForest (AUC 0.58) is weakly better than chance,
and the autoencoder (AUC 0.49) is indistinguishable from chance. The
complementarity analysis (does the autoencoder catch fraud the RandomForest
misses?) is not meaningful to report on top of this, since the RandomForest's
apparent "0 missed frauds" in the original evaluation was purely a training-data
memorization artifact, not real detection.

The most likely explanation is that this dataset's `fraud_flag` was
synthetically generated in a way that isn't strongly correlated with the
applicant features retained here (CIBIL, DTI, income, loan amount,
employment, etc.) — i.e., there may be little real signal in these columns
for either a supervised or unsupervised model to learn, regardless of
architecture.

**Confirmed directly**: comparing per-feature means between fraud and
genuine rows shows they are nearly identical (e.g. CIBIL 699.1 vs. 699.5,
DTI 8.57 vs. 8.95, income ₹50,852 vs. ₹50,523), and every categorical
feature's fraud rate is flat at ~2% regardless of category (loan type,
purpose, employment status, property ownership, gender all vary by <1
percentage point). There is no meaningful univariate signal in this dataset
for `fraud_flag` at all.

## Second finding: a live feature-scale mismatch (independent of the above)

`debt_to_income_ratio` in the training CSV ranges from 0 to 102 (mean 8.57,
std 9.59) — not a 0–1 fraction. But:

- The web form ([templates/prediction.html:431](templates/prediction.html)) prompts users with
  `placeholder="e.g. 0.35"`.
- `calculate_dynamic_threshold()` and `AnalyticsAgent.analyze()` both apply
  rules like `dti > 0.6` / `dti > 0.65`, assuming a 0–1 scale.
- `FraudPredictor.generate_random_form_data()` generates DTI as
  `random.uniform(0.1, 0.9)`.

Every prediction submitted through the UI as intended (a 0–1 fraction) is
fed into the trained `StandardScaler`/RandomForest on a scale it never saw
a single training example of — the model was fit entirely on DTI values
in the 0–102 range. This is independent of the weak-signal finding above
and would need fixing regardless: either rescale the CSV's
`debt_to_income_ratio` at training time to match the intended 0–1 fraction
the app uses everywhere else, or change the app's DTI input/threshold logic
to match the training data's actual scale.

## Recommendation

This is a more valuable finding for a deep learning course report than a
flattering-but-meaningless "100% accuracy" — it demonstrates the actual
methodological skill of catching an evaluation flaw via proper train/test
discipline. Suggested next steps, in priority order:

1. **Fix the DTI scale mismatch** — this is a straightforward, unambiguous
   bug regardless of the signal question above, and likely the single
   highest-leverage fix: live predictions are currently scored on a feature
   value the model has never seen the real range of.
2. **Fix `train.py` to include a proper train/test split** and report honest
   metrics as the model's real documented performance, instead of the
   memorized 100%.
3. State the weak-signal finding directly in the report as a finding, with
   the evaluation methodology as the contribution — real fraud datasets in
   industry are also often weakly labeled/low-signal, so identifying that
   here (rather than presenting an inflated number) is realistic, defensible
   ML practice.
