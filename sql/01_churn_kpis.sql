-- Import data/processed/telco_clean.csv into SQLite as `customers`.
SELECT
    COUNT(*) AS customers,
    SUM(ChurnFlag) AS churned_customers,
    ROUND(100.0 * AVG(ChurnFlag), 2) AS churn_rate_pct,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges,
    ROUND(SUM(CASE WHEN ChurnFlag = 1 THEN MonthlyCharges ELSE 0 END), 2)
        AS churned_monthly_charge_exposure
FROM customers;
