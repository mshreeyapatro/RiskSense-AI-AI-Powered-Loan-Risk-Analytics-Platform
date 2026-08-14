"""
Builds a SEPARATE, clearly-labeled experimental dataset (loan_applications_v2.csv)
where fraud_flag is generated as a noisy function of the observable applicant
features, instead of being independent of them as in the original
loan_applications.csv (see EVALUATION.md / Knowledge_Transfer_Document.txt for
the documented finding that the original label carries almost no signal
correlated with the given features).

This does NOT modify loan_applications.csv, train.py, or any of the already
-evaluated/documented production artifacts. It exists to answer: "if the fraud
label actually depended on applicant risk factors, could these models learn
it?"

Risk factors and weights loosely mirror the heuristics already coded in
agents/analytics_agent.py (CIBIL score, debt-to-income ratio, EMI burden,
loan-to-income ratio, employment status, applicant age), so the relabeled
ground truth stays consistent with the domain logic the app already expresses
in its risk explanations.

Labels are sampled stochastically (Bernoulli on a logistic risk score), not
thresholded deterministically, so the dataset is noisy and not trivially
separable, the way `fraud_flag = 1` deterministic rules would be.
"""

import numpy as np
import pandas as pd

SOURCE_PATH = "loan_applications.csv"
OUTPUT_PATH = "loan_applications_v2.csv"
RNG_SEED = 42

# Logistic center/scale chosen empirically so the relabeled fraud rate
# (~4%) stays close to the original dataset's ~2.1% prevalence.
LOGISTIC_CENTER = 50
LOGISTIC_SCALE = 12


def risk_score(row: pd.Series) -> int:
    score = 0

    cibil = row["cibil_score"]
    if cibil < 550:
        score += 35
    elif cibil < 600:
        score += 20
    elif cibil < 650:
        score += 8

    # debt_to_income_ratio in this dataset is a ratio on a 0-102 scale, not a
    # 0-1 fraction (documented data-quality note in the KT doc).
    dti = row["debt_to_income_ratio"]
    if dti > 45:
        score += 25
    elif dti > 30:
        score += 12

    emi_burden = row["existing_emis_monthly"] / max(row["monthly_income"], 1)
    if emi_burden > 0.5:
        score += 20
    elif emi_burden > 0.35:
        score += 8

    loan_to_annual_income = row["loan_amount_requested"] / (max(row["monthly_income"], 1) * 12)
    if loan_to_annual_income > 12:
        score += 20
    elif loan_to_annual_income > 7:
        score += 8

    if row["employment_status"] in ("Unemployed", "Student"):
        score += 15

    if row["applicant_age"] < 23:
        score += 5

    return score


print("Loading source dataset...")
df = pd.read_csv(SOURCE_PATH)

print("Computing risk-based fraud probabilities...")
scores = df.apply(risk_score, axis=1)
probabilities = 1 / (1 + np.exp(-(scores - LOGISTIC_CENTER) / LOGISTIC_SCALE))

rng = np.random.default_rng(RNG_SEED)
df["fraud_flag"] = rng.binomial(1, probabilities)

print(f"Relabeled fraud rate: {df['fraud_flag'].mean():.4%} ({df['fraud_flag'].sum()} of {len(df)} rows)")
print("Feature correlations with new fraud_flag:")
for col in ["cibil_score", "debt_to_income_ratio", "existing_emis_monthly", "monthly_income"]:
    print(f"  {col}: {df['fraud_flag'].corr(df[col]):.4f}")

df.to_csv(OUTPUT_PATH, index=False)
print(f"Wrote {OUTPUT_PATH}")
