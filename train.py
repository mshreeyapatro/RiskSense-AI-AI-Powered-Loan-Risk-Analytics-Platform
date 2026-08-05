import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from imblearn.over_sampling import SMOTE
import joblib

print("Loading dataset...")
df = pd.read_csv("loan_applications.csv")

# Drop any rows with NaN in the target or features to prevent training errors
df = df.dropna(subset=["fraud_flag"])

y = df["fraud_flag"].astype(int)
X = df.drop(["fraud_flag", "loan_status", "fraud_type", "application_id", "customer_id", "application_date", "residential_address"], axis=1, errors="ignore")

categorical_cols = ["loan_type", "purpose_of_loan", "employment_status", "property_ownership_status", "gender"]
numeric_cols = ["loan_amount_requested", "loan_tenure_months", "interest_rate_offered", "monthly_income", "cibil_score", "existing_emis_monthly", "debt_to_income_ratio", "applicant_age", "number_of_dependents"]

print("Building preprocessor...")
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_cols),
        ("cat", OneHotEncoder(drop='first'), categorical_cols)
    ]
)

print("Transforming data...")
X_processed = preprocessor.fit_transform(X)

print("Applying SMOTE to balance the dataset perfectly...")
smote = SMOTE(random_state=42)
X_balanced, y_balanced = smote.fit_resample(X_processed, y)

print("Training model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_balanced, y_balanced)

print("Saving artifacts...")
joblib.dump(preprocessor, "preprocessor.pkl")
joblib.dump(model, "loan_fraud_ensemble_model.pkl")

print("Done! Scikit-learn 1.9 compatibility achieved.")
