import pandas as pd
import pytest
from src.analysis import load_and_clean

def test_cleaning_converts_total_charges_and_flags_churn(tmp_path):
    df = pd.DataFrame({
        "customerID": ["A", "B"],
        "gender": ["Female", "Male"],
        "SeniorCitizen": [0, 0],
        "Partner": ["Yes", "No"],
        "Dependents": ["No", "No"],
        "tenure": [0, 5],
        "PhoneService": ["No", "Yes"],
        "MultipleLines": ["No phone service", "No"],
        "InternetService": ["DSL", "Fiber optic"],
        "OnlineSecurity": ["No", "Yes"],
        "OnlineBackup": ["No", "No"],
        "DeviceProtection": ["No", "No"],
        "TechSupport": ["No", "No"],
        "StreamingTV": ["No", "No"],
        "StreamingMovies": ["No", "No"],
        "Contract": ["Month-to-month", "One year"],
        "PaperlessBilling": ["Yes", "No"],
        "PaymentMethod": ["Electronic check", "Mailed check"],
        "MonthlyCharges": [30.0, 50.0],
        "TotalCharges": ["", "250.0"],
        "Churn": ["Yes", "No"]
    })
    p = tmp_path / "test.csv"
    df.to_csv(p, index=False)
    result = load_and_clean(p)
    assert result["TotalCharges"].tolist() == [0.0, 250.0]
    assert result["ChurnFlag"].tolist() == [1, 0]
    assert result["RetentionPriority"].notna().all()

def test_duplicate_customer_ids_are_rejected(tmp_path):
    df = _make_minimal_df()
    df.loc[1, "customerID"] = df.loc[0, "customerID"]
    p = tmp_path / "duplicate.csv"
    df.to_csv(p, index=False)
    with pytest.raises(ValueError, match="unique"):
        load_and_clean(p)

def _make_minimal_df():
    return pd.DataFrame({
        "customerID": ["A", "B"], "tenure": [1, 2], "Contract": ["Month-to-month", "One year"],
        "InternetService": ["DSL", "Fiber optic"], "PaymentMethod": ["Electronic check", "Mailed check"],
        "MonthlyCharges": [30.0, 50.0], "TotalCharges": ["30", "100"], "Churn": ["Yes", "No"]
    })
