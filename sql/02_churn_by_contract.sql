SELECT
    Contract,
    COUNT(DISTINCT customerID) AS customers,
    SUM(ChurnFlag) AS churned_customers,
    ROUND(100.0 * AVG(ChurnFlag), 2) AS churn_rate_pct,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges
FROM customers
GROUP BY Contract
ORDER BY churn_rate_pct DESC;
