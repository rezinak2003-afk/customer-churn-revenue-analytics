SELECT
    TenureBand,
    COUNT(*) AS customers,
    ROUND(100.0 * AVG(ChurnFlag), 2) AS churn_rate_pct,
    ROUND(AVG(MonthlyCharges), 2) AS avg_monthly_charges
FROM customers
GROUP BY TenureBand
ORDER BY CASE TenureBand
    WHEN '0–12 months' THEN 1
    WHEN '13–24 months' THEN 2
    WHEN '25–48 months' THEN 3
    ELSE 4
END;
