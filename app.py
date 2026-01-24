from flask import Flask, render_template, request
import pandas as pd
import joblib
import random

app = Flask(__name__)

# --------------------------------------------------
# Load model, preprocessor, dataset (MATCH YOUR FILES)
# --------------------------------------------------
model = joblib.load("loan_fraud_ensemble_model.pkl")
preprocessor = joblib.load("preprocessor.pkl")
df = pd.read_csv("loan_fraud_smote_balanced_dataset.csv")

# --------------------------------------------------
# Random value generator for form
# --------------------------------------------------
def generate_random_form_data():
    return {
        "loan_type": random.choice([
            "Home Loan", "Personal Loan", "Car Loan",
            "Education Loan", "Business Loan"
        ]),
        "loan_amount": random.randint(100000, 5000000),
        "tenure": random.randint(12, 360),
        "interest": round(random.uniform(7.0, 18.0), 2),
        "purpose": random.choice([
            "Business Expansion", "Debt Consolidation",
            "Education", "Home Renovation",
            "Medical Emergency", "Vehicle Purchase", "Wedding"
        ]),
        "employment": random.choice([
            "Salaried", "Self-Employed", "Business Owner",
            "Student", "Unemployed", "Retired"
        ]),
        "income": random.randint(15000, 200000),
        "cibil": random.randint(300, 900),
        "emis": random.randint(0, 50000),
        "dti": round(random.uniform(0.1, 0.9), 2),
        "property": random.choice(["Owned", "Rented", "Jointly Owned"]),
        "age": random.randint(18, 70),
        "gender": random.choice(["Male", "Female", "Other"]),
        "dependents": random.randint(0, 5)
    }

# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/prediction", methods=["GET", "POST"])
def prediction():
    result = None
    probability = None
    probability_value = None
    random_data = None
    form_data = None
    record_index = None
    actual_label = None

    # Clear form on GET ?clear=true
    clear_form = request.method == "GET" and request.args.get("clear") == "true"

    if request.method == "POST":
        mode = request.form.get("mode")

        # ---------- Fill Random Form ----------
        if mode == "fill_random":
            random_data = generate_random_form_data()

        # ---------- Manual Prediction ----------
        elif mode == "manual":
            form_data = dict(request.form)

            input_df = pd.DataFrame([{
                "loan_type": form_data["loan_type"],
                "loan_amount_requested": float(form_data["loan_amount"]),
                "loan_tenure_months": int(form_data["tenure"]),
                "interest_rate_offered": float(form_data["interest"]),
                "purpose_of_loan": form_data["purpose"],
                "employment_status": form_data["employment"],
                "monthly_income": float(form_data["income"]),
                "cibil_score": int(form_data["cibil"]),
                "existing_emis_monthly": float(form_data["emis"]),
                "debt_to_income_ratio": float(form_data["dti"]),
                "property_ownership_status": form_data["property"],
                "applicant_age": int(form_data["age"]),
                "gender": form_data["gender"],
                "number_of_dependents": int(form_data["dependents"])
            }])

            X = preprocessor.transform(input_df)
            probability_value = model.predict_proba(X)[0][1]
            probability = f"{probability_value:.2%}"
            result = "FRAUD 🚨" if probability_value >= 0.4 else "GENUINE ✅"

        # ---------- Random Dataset Record ----------
        elif mode == "random_index":
            record_index = random.randint(0, len(df) - 1)
            row = df.iloc[record_index]

            X = pd.DataFrame([row.drop("fraud_flag")])
            probability_value = model.predict_proba(X)[0][1]
            probability = f"{probability_value:.2%}"
            result = "FRAUD 🚨" if probability_value >= 0.4 else "GENUINE ✅"
            actual_label = "FRAUD 🚨" if row["fraud_flag"] == 1 else "GENUINE ✅"

    if clear_form:
        random_data = None
        form_data = None

    return render_template(
        "prediction.html",
        result=result,
        probability=probability,
        probability_value=probability_value,
        random_data=random_data,
        form_data=form_data,
        record_index=record_index,
        actual_label=actual_label
    )

# --------------------------------------------------
# Run App
# --------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
