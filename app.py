from pathlib import Path
import sys
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from src.analysis import RAW, CLEAN, run

st.set_page_config(page_title="Customer Churn | Retention Intelligence", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.block-container {padding-top:1.5rem;padding-bottom:2rem;max-width:1500px}
.hero {padding:1.35rem 1.5rem;border-radius:16px;margin-bottom:1rem;background:linear-gradient(115deg,#10243A 0%,#173D5A 60%,#176B70 100%)}
.hero h1 {color:#fff;margin:0;font-size:2rem}
.hero p {color:#D8E7F0;margin:.45rem 0 0;font-size:1rem}
.kpi {border:1px solid rgba(128,128,128,.25);border-radius:14px;padding:1rem 1.1rem;min-height:112px}
.kpi-label {font-size:.8rem;opacity:.75;margin-bottom:.4rem;letter-spacing:.04em}
.kpi-value {font-size:1.8rem;font-weight:700;line-height:1.2}
.kpi-note {font-size:.75rem;opacity:.65;margin-top:.35rem}
</style>
<div class="hero"><h1>Customer Churn &amp; Revenue Analytics</h1><p>Retention intelligence · IBM Telco sample dataset · Exploratory analytics, not a production churn model</p></div>
""", unsafe_allow_html=True)

if not CLEAN.exists():
    st.warning("The cleaned dataset is missing. Run the pipeline first.")
    st.code("python scripts/download_data.py\npython scripts/run_analysis.py")
    if st.button("Run data pipeline", type="primary"):
        try:
            with st.spinner("Preparing dataset and analysis outputs..."):
                if not RAW.exists():
                    from scripts.download_data import main as download_main
                    download_main()
                run()
            st.rerun()
        except Exception as exc:
            st.error(f"Pipeline failed: {exc}")
    st.stop()

df = pd.read_csv(CLEAN)
df["ChurnFlag"] = pd.to_numeric(df["ChurnFlag"], errors="coerce").fillna(0).astype(int)
df["MonthlyCharges"] = pd.to_numeric(df["MonthlyCharges"], errors="coerce").fillna(0)
df["tenure"] = pd.to_numeric(df["tenure"], errors="coerce").fillna(0)

with st.sidebar:
    st.header("Explore customers")
    contract = st.selectbox("Contract", ["All"] + sorted(df["Contract"].dropna().astype(str).unique()))
    internet = st.selectbox("Internet service", ["All"] + sorted(df["InternetService"].dropna().astype(str).unique()))
    payment = st.selectbox("Payment method", ["All"] + sorted(df["PaymentMethod"].dropna().astype(str).unique()))
    st.divider()
    st.caption("Filters apply across all dashboard sections.")

view = df.copy()
if contract != "All": view = view[view["Contract"].astype(str) == contract]
if internet != "All": view = view[view["InternetService"].astype(str) == internet]
if payment != "All": view = view[view["PaymentMethod"].astype(str) == payment]
if view.empty:
    st.info("No customers match these filters. Change a filter to continue.")
    st.stop()

churned = view[view["ChurnFlag"] == 1]
n = len(view)
rate = view["ChurnFlag"].mean()
exposure = churned["MonthlyCharges"].sum()
avg_tenure = view["tenure"].mean()

def kpi(label, value, note):
    st.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>', unsafe_allow_html=True)

a,b,c,d = st.columns(4)
with a: kpi("CUSTOMERS IN VIEW", f"{n:,}", "After selected filters")
with b: kpi("CHURN RATE", f"{rate:.1%}", f"{len(churned):,} churned customers")
with c: kpi("MONTHLY CHARGE EXPOSURE", f"${exposure:,.0f}", "Charges associated with churned customers")
with d: kpi("AVERAGE TENURE", f"{avg_tenure:.1f} mo", "Across customers in view")
st.caption("Monthly charge exposure is descriptive, not a forecast of revenue lost or recoverable revenue.")

overview, drivers, priorities, methodology = st.tabs(["Executive overview", "Churn drivers", "Retention priorities", "Data & methodology"])
with overview:
    left,right = st.columns(2, gap="large")
    with left:
        st.subheader("Churn rate by contract")
        st.bar_chart(view.groupby("Contract", observed=True)["ChurnFlag"].mean().mul(100).sort_values(ascending=False), y_label="Churn rate (%)")
    with right:
        st.subheader("Churn rate by tenure band")
        st.bar_chart(view.groupby("TenureBand", observed=True)["ChurnFlag"].mean().mul(100), y_label="Churn rate (%)")
    st.subheader("Customer base composition")
    st.bar_chart(view.groupby("Churn", observed=True).size().rename("Customers"), y_label="Customers")
    st.info("Compare rates, not only counts: large groups can dominate counts even when their churn rate is lower.")
with drivers:
    left,right = st.columns(2, gap="large")
    with left:
        st.subheader("Churn rate by payment method")
        st.bar_chart(view.groupby("PaymentMethod", observed=True)["ChurnFlag"].mean().mul(100).sort_values(ascending=False), y_label="Churn rate (%)")
    with right:
        st.subheader("Churn rate by internet service")
        st.bar_chart(view.groupby("InternetService", observed=True)["ChurnFlag"].mean().mul(100).sort_values(ascending=False), y_label="Churn rate (%)")
    for col,title in [("TechSupport","Churn rate by tech support"),("OnlineSecurity","Churn rate by online security")]:
        if col in view.columns:
            st.subheader(title)
            st.bar_chart(view.groupby(col, observed=True)["ChurnFlag"].mean().mul(100).sort_values(ascending=False), y_label="Churn rate (%)")
    st.caption("These are observational comparisons, not proof of causation.")
with priorities:
    st.subheader("Rule-based retention screening")
    st.write("The score is a transparent prioritisation heuristic, not a churn probability or validated predictive model.")
    active = view[view["ChurnFlag"] == 0].copy()
    if "RetentionPriority" in active.columns:
        left,right = st.columns(2, gap="large")
        with left:
            st.write("Active customers by screening tier")
            st.bar_chart(active.groupby("RetentionPriority", observed=True).size().sort_values(ascending=False), y_label="Active customers")
        with right:
            st.write("Average monthly charges by tier")
            st.bar_chart(active.groupby("RetentionPriority", observed=True)["MonthlyCharges"].mean().sort_values(ascending=False), y_label="Average monthly charges")
        active = active.sort_values(["RetentionPriorityScore","MonthlyCharges"], ascending=False)
        cols = [x for x in ["Contract","tenure","MonthlyCharges","TechSupport","OnlineSecurity","RetentionPriorityScore","RetentionPriority"] if x in active.columns]
        st.dataframe(active[cols].head(25), width="stretch", hide_index=True)
        st.caption("Customer-level rows are for local analysis only. Do not publish row-level data or customer IDs.")
    st.info("Recommended evaluation: run a retention offer against a holdout group and compare incremental retention, contribution margin, and campaign cost.")
with methodology:
    st.subheader("Data quality checks")
    quality = [
        ("Customers", f"{len(df):,}"),
        ("Duplicate customer IDs", f"{int(df['customerID'].duplicated().sum()):,}"),
        ("Missing cells after cleaning", f"{int(df.isna().sum().sum()):,}"),
        ("Zero-tenure customers", f"{int(df['tenure'].eq(0).sum()):,}"),
        ("Churn labels", ", ".join(sorted(df["Churn"].dropna().astype(str).unique()))),
    ]
    st.table(pd.DataFrame(quality, columns=["Check","Result"]))
    st.markdown("""
**Definitions**
- **Churn rate:** customers labelled churned divided by customers in the filtered view.
- **Monthly charge exposure:** sum of monthly charges for customers labelled churned; not realised or forecast lost revenue.
- **Retention priority:** rule-based screening tier using contract, tenure, charges, and selected service add-ons.
- **Limitation:** this is a cross-sectional sample. Relationships are observational and should not be interpreted as causal.
""")
    st.subheader("Export aggregate segment data")
    dim = st.selectbox("Segment dimension", ["Contract","InternetService","PaymentMethod","TenureBand","RetentionPriority"])
    agg = view.groupby(dim, observed=True).agg(customers=("customerID","nunique"), churned_customers=("ChurnFlag","sum"), churn_rate=("ChurnFlag","mean"), avg_monthly_charges=("MonthlyCharges","mean")).reset_index()
    agg["churn_rate_pct"] = (agg.pop("churn_rate")*100).round(2)
    st.dataframe(agg, width="stretch", hide_index=True)
    st.download_button("Download aggregate segment CSV", agg.to_csv(index=False).encode("utf-8"), f"churn_segments_{dim.lower()}.csv", "text/csv")
