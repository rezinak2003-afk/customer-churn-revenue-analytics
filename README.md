.\.venv\Scripts\python.exe -m pip install -r requirements.txt# Customer Churn & Revenue Analytics

An end-to-end analytics portfolio project using Python, pandas, SQL, and Streamlit, with a Power BI build guide. It analyses the IBM Telco Customer Churn sample dataset to explore churn rates, segment differences, and retention-screening priorities.

> **Dataset:** IBM Telco Customer Churn sample (7,043 customer records; fictional telecom company). Dataset is downloaded locally and excluded from GitHub. Source: https://github.com/IBM/telco-customer-churn-on-icp4d

## Business questions
1. What is the overall churn rate and monthly charge exposure associated with churned customers?
2. How do churn rates vary by contract, tenure, internet service, payment method, and service add-ons?
3. Which active customer groups could be prioritised for retention outreach?
4. What are the limitations of observational churn analysis?

## Tech stack
Python, pandas, NumPy, Matplotlib, SQLite SQL, Streamlit, pytest, Git/GitHub, Power BI.

## Quick start (Windows PowerShell)
Open a terminal in the folder containing `app.py` and `requirements.txt`.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\download_data.py
.\.venv\Scripts\python.exe scripts\run_analysis.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If `.venv` already exists, do not recreate it; run the commands after the first line. Open the Local URL shown in the terminal (normally `http://localhost:8501`).

## Deliverables
- Data download and checksum validation script.
- Cleaning, validation, feature engineering, and aggregate analysis pipeline.
- SQL queries for overall KPIs, contract churn, tenure groups, and retention priority.
- Interactive Streamlit dashboard with KPI cards, sidebar filters, four analysis tabs, and aggregate segment CSV export.
- Power BI Desktop measures and page design in `powerbi/BUILD_GUIDE.md`.
- Automated tests and GitHub Actions test workflow.
- Aggregate outputs and charts generated locally by the analysis script.

## Methodology
- Converts `TotalCharges` to numeric and handles source blanks for zero-tenure customers after validation.
- Validates unique customer IDs, churn labels, and tenure range.
- Uses churn rates to compare segments.
- Reports monthly charges associated with churned customers as **charge exposure**, not a forecast of lost revenue.
- Uses a transparent, rule-based retention priority score. It is not a trained model or calibrated churn probability.

## Interpretation and limitations
The dataset is cross-sectional and represents a fictional telecom provider. Observed relationships are not causal. A customer group with a high churn rate may merit further investigation, but retention actions should be tested against a holdout group and evaluated using incremental retention, margin, and campaign cost.

## Power BI
See `powerbi/BUILD_GUIDE.md`. The `.pbix` must be created and saved in Power BI Desktop; the guide includes the data model, measures, and page layout. The Streamlit dashboard is the immediately runnable interactive dashboard.

## Privacy and repository hygiene
The raw dataset and cleaned customer-level data are excluded from Git. Do not publish row-level exports or screenshots containing customer IDs. Publish only aggregate findings.
