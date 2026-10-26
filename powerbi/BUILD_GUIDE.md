# Power BI Desktop Build Guide

The `.pbix` must be created in Power BI Desktop. The prepared file `data/processed/telco_clean.csv` is generated locally after running the Python pipeline.

## Load data
1. Run `python scripts/download_data.py` and `python scripts/run_analysis.py`.
2. Power BI Desktop → **Get data → Text/CSV** → select `data/processed/telco_clean.csv`.
3. Load the table as `Customers`.
4. Set `ChurnFlag` to Whole number, `MonthlyCharges` and `TotalCharges` to Decimal number, `tenure` to Whole number. Set `Churn` and categorical fields to Text.

## Measures (Modeling → New measure)
```DAX
Total Customers = DISTINCTCOUNT(Customers[customerID])

Churned Customers =
CALCULATE([Total Customers], Customers[ChurnFlag] = 1)

Churn Rate =
DIVIDE([Churned Customers], [Total Customers], 0)

Average Monthly Charges =
AVERAGE(Customers[MonthlyCharges])

Churned Monthly Charge Exposure =
CALCULATE(
    SUM(Customers[MonthlyCharges]),
    Customers[ChurnFlag] = 1
)

Average Tenure = AVERAGE(Customers[tenure])
```
Format `Churn Rate` as Percentage with 1 decimal place. Exposure is not a forecast of revenue loss.

## Page 1 — Executive Overview
- KPI cards: Total Customers, Churned Customers, Churn Rate, Churned Monthly Charge Exposure.
- Clustered bar: Churn Rate by Contract.
- Bar: Churn Rate by TenureBand.
- Slicers: Contract, InternetService, PaymentMethod.

## Page 2 — Churn Drivers
- Bar chart: Churn Rate by PaymentMethod.
- Bar chart: Churn Rate by InternetService.
- 100% stacked bar: Churn by TechSupport and OnlineSecurity.
- Matrix: Contract × TenureBand, values Churn Rate and Total Customers.

## Page 3 — Retention Prioritisation
- Bar chart: active customers by RetentionPriority.
- Scatter: MonthlyCharges vs tenure, legend RetentionPriority, size MonthlyCharges.
- Table: Contract, tenure, MonthlyCharges, TechSupport, OnlineSecurity, RetentionPriorityScore, RetentionPriority.
- Keep the customer-level table local; do not publish screenshots that expose customer IDs.

## Design
Use a consistent 16:9 canvas, a neutral background, one accent colour, clear titles, and descriptive subtitles. Add a note: “Cross-sectional sample; associations are not causal. Priority score is a rule-based screening heuristic.”
