from pathlib import Path
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "Telco-Customer-Churn.csv"
CLEAN = ROOT / "data" / "processed" / "telco_clean.csv"
OUT = ROOT / "outputs"
FIG = OUT / "figures"

REQUIRED = {
    "customerID", "tenure", "Contract", "InternetService", "PaymentMethod",
    "MonthlyCharges", "TotalCharges", "Churn"
}

def load_and_clean(path=RAW):
    df = pd.read_csv(path)
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if df["customerID"].duplicated().any():
        raise ValueError("customerID must be unique")
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].astype(str).str.strip(), errors="coerce")
    # Source has blank TotalCharges for new customers with zero tenure.
    bad = df["TotalCharges"].isna()
    if bad.any() and not (df.loc[bad, "tenure"] == 0).all():
        raise ValueError("Unexpected TotalCharges blanks outside zero-tenure customers")
    df["TotalCharges"] = df["TotalCharges"].fillna(0)
    for col in ["MonthlyCharges", "TotalCharges", "tenure"]:
        df[col] = pd.to_numeric(df[col], errors="raise")
    if not df["Churn"].isin(["Yes", "No"]).all():
        raise ValueError("Churn must contain only Yes/No")
    if not df["tenure"].between(0, 72).all():
        raise ValueError("tenure must be between 0 and 72 months")
    df["ChurnFlag"] = df["Churn"].map({"Yes": 1, "No": 0}).astype(int)
    df["TenureBand"] = pd.cut(
        df["tenure"], bins=[-1, 12, 24, 48, 72],
        labels=["0–12 months", "13–24 months", "25–48 months", "49–72 months"]
    ).astype(str)
    df["MonthlyRevenueExposure"] = np.where(df["ChurnFlag"].eq(1), df["MonthlyCharges"], 0.0)
    # Transparent screening heuristic, not a probability estimate.
    score = (
        df["Contract"].eq("Month-to-month").astype(int) * 3
        + df["tenure"].le(12).astype(int) * 2
        + df["MonthlyCharges"].ge(df["MonthlyCharges"].median()).astype(int)
        + df.get("TechSupport", pd.Series("No", index=df.index)).eq("No").astype(int)
        + df.get("OnlineSecurity", pd.Series("No", index=df.index)).eq("No").astype(int)
    )
    df["RetentionPriorityScore"] = score
    df["RetentionPriority"] = pd.cut(
        score, bins=[-1, 2, 4, 10], labels=["Monitor", "Elevated", "High priority"]
    ).astype(str)
    return df

def safe_rate(series):
    return float(series.mean()) if len(series) else 0.0

def make_outputs(df):
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    churned = df[df["ChurnFlag"].eq(1)]
    kpis = {
        "customers": int(len(df)),
        "churned_customers": int(df["ChurnFlag"].sum()),
        "churn_rate_pct": round(safe_rate(df["ChurnFlag"]) * 100, 2),
        "avg_monthly_charges": round(float(df["MonthlyCharges"].mean()), 2),
        "churned_customer_monthly_charge_exposure": round(float(churned["MonthlyCharges"].sum()), 2),
        "median_tenure_months": round(float(df["tenure"].median()), 1),
        "data_quality": {
            "duplicate_customer_ids": int(df["customerID"].duplicated().sum()),
            "missing_values_after_cleaning": int(df.isna().sum().sum()),
            "zero_tenure_customers": int(df["tenure"].eq(0).sum())
        },
        "interpretation_note": "Monthly charges for churned customers are exposure, not a causal or forecasted revenue loss."
    }
    (OUT / "kpi_summary.json").write_text(json.dumps(kpis, indent=2), encoding="utf-8")
    segment_cols = ["Contract", "InternetService", "PaymentMethod", "TenureBand", "RetentionPriority"]
    tables = []
    for col in segment_cols:
        t = df.groupby(col, observed=False).agg(
            customers=("customerID", "nunique"),
            churned_customers=("ChurnFlag", "sum"),
            churn_rate=("ChurnFlag", "mean"),
            avg_monthly_charges=("MonthlyCharges", "mean"),
            monthly_charge_exposure=("MonthlyRevenueExposure", "sum")
        ).reset_index().rename(columns={col: "segment"})
        t.insert(0, "dimension", col)
        tables.append(t)
    pd.concat(tables, ignore_index=True).to_csv(OUT / "churn_by_segment.csv", index=False)
    priority = df.loc[df["ChurnFlag"].eq(0), [
        "customerID", "Contract", "tenure", "MonthlyCharges", "TechSupport",
        "OnlineSecurity", "RetentionPriorityScore", "RetentionPriority"
    ]].sort_values(["RetentionPriorityScore", "MonthlyCharges"], ascending=False)
    priority.head(500).to_csv(OUT / "retention_priority.csv", index=False)
    # Aggregate charts
    charts = [
        ("Contract", "Churn rate by contract type", "churn_contract.png"),
        ("TenureBand", "Churn rate by tenure band", "churn_tenure.png"),
        ("PaymentMethod", "Churn rate by payment method", "churn_payment.png"),
        ("InternetService", "Churn rate by internet service", "churn_internet.png"),
    ]
    for col, title, filename in charts:
        agg = df.groupby(col, observed=False)["ChurnFlag"].mean().sort_values(ascending=False) * 100
        fig, ax = plt.subplots(figsize=(8, 4.5))
        agg.plot(kind="bar", ax=ax)
        ax.set_title(title)
        ax.set_ylabel("Churn rate (%)")
        ax.set_xlabel("")
        ax.tick_params(axis="x", rotation=25)
        fig.tight_layout()
        fig.savefig(FIG / filename, dpi=160)
        plt.close(fig)
    df.to_csv(CLEAN, index=False)
    return kpis

def run(path=RAW):
    CLEAN.parent.mkdir(parents=True, exist_ok=True)
    df = load_and_clean(path)
    kpis = make_outputs(df)
    print(json.dumps(kpis, indent=2))
    print(f"Saved cleaned data: {CLEAN}")
    print(f"Saved aggregate outputs and charts: {OUT}")
    return df, kpis

if __name__ == "__main__":
    run()
