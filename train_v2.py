"""
Trains a RandomForest classifier on the experimental relabeled dataset
(loan_applications_v2.csv, see generate_relabeled_dataset.py) using a proper
stratified train/test split, and reports HONEST held-out metrics -- unlike
the original train.py, which fits on 100% of the data with no split
(documented issue, see EVALUATION.md).

Saves separate artifacts (preprocessor_v2.pkl, loan_fraud_ensemble_model_v2.pkl)
so the already-evaluated, documented production artifacts (preprocessor.pkl,
loan_fraud_ensemble_model.pkl) are untouched.
"""

import joblib
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATASET_PATH = "loan_applications_v2.csv"
RNG_SEED = 42

print("Loading relabeled dataset...")
df = pd.read_csv(DATASET_PATH).dropna(subset=["fraud_flag"])

y = df["fraud_flag"].astype(int)
X = df.drop(
    ["fraud_flag", "loan_status", "fraud_type", "application_id", "customer_id", "application_date", "residential_address"],
    axis=1,
    errors="ignore",
)

categorical_cols = ["loan_type", "purpose_of_loan", "employment_status", "property_ownership_status", "gender"]
numeric_cols = ["loan_amount_requested", "loan_tenure_months", "interest_rate_offered", "monthly_income", "cibil_score", "existing_emis_monthly", "debt_to_income_ratio", "applicant_age", "number_of_dependents"]

print("Splitting 80/20 stratified train/test (held-out test never trained on)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RNG_SEED, stratify=y
)

print("Building preprocessor (fit on train only)...")
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_cols),
        ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), categorical_cols),
    ]
)
X_train_t = preprocessor.fit_transform(X_train)
X_test_t = preprocessor.transform(X_test)

print("Applying SMOTE to the training split only...")
X_train_bal, y_train_bal = SMOTE(random_state=RNG_SEED).fit_resample(X_train_t, y_train)

print("Training model...")
model = RandomForestClassifier(n_estimators=100, random_state=RNG_SEED)
model.fit(X_train_bal, y_train_bal)

print("Evaluating on held-out test set...")
proba = model.predict_proba(X_test_t)[:, 1]
preds = model.predict(X_test_t)

auc = roc_auc_score(y_test, proba)
precision = precision_score(y_test, preds, zero_division=0)
recall = recall_score(y_test, preds, zero_division=0)
f1 = f1_score(y_test, preds, zero_division=0)
tn, fp, fn, tp = confusion_matrix(y_test, preds).ravel()

print()
print("=== Honest held-out results (loan_applications_v2.csv) ===")
print(f"AUC:       {auc:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1:        {f1:.4f}")
print(f"Confusion matrix: TN={tn} FP={fp} FN={fn} TP={tp}")
print()
print("=== For comparison, original documented result (loan_applications.csv) ===")
print("AUC: ~0.5847 (see EVALUATION.md)")

print()
print("Saving experimental artifacts (preprocessor_v2.pkl, loan_fraud_ensemble_model_v2.pkl)...")
joblib.dump(preprocessor, "preprocessor_v2.pkl")
joblib.dump(model, "loan_fraud_ensemble_model_v2.pkl")
print("Done.")
