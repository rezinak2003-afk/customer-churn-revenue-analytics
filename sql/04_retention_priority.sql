SELECT
    Contract, TenureBand, RetentionPriority,
    COUNT(*) AS customers,
    ROUND(100.0 * AVG(ChurnFlag), 2) AS observed_churn_rate_pct,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges
FROM customers
GROUP BY Contract, TenureBand, RetentionPriority
ORDER BY observed_churn_rate_pct DESC, customers DESC;
