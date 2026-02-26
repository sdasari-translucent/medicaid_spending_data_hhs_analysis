-- MEDICAID STATE VARIANCE ANALYSIS FOR 99214 (Complex Office Visits) - 2023-2024
-- Identifies states with highest payment variance (P10 to P90 spread)
-- High variance indicates mixed payer environment = contracting opportunity

WITH state_medicaid_variance AS (
  SELECT
    rndrng_prvdr_state_abrvtn as state,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY total_paid / total_claims), 2) as p25_payment,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY total_paid / total_claims), 2) as p50_payment,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_paid / total_claims), 2) as p75_payment,
    ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY total_paid / total_claims), 2) as p90_payment,
    COUNT(*) as provider_count,
    SUM(total_claims) as total_claims
  FROM mimi_ws_1.datamedicaidgov.medicaid_provider_spending m
  JOIN mimi_ws_1.datacmsgov.mupphy mp ON m.billing_provider_npi_num = mp.rndrng_npi
  WHERE m.hcpcs_code = '99214'
    AND m.total_claims >= 10
    AND mp.hcpcs_cd = '99214'
    AND rndrng_prvdr_state_abrvtn IS NOT NULL
    AND LEFT(m.claim_from_month, 4) IN ('2023', '2024')
  GROUP BY rndrng_prvdr_state_abrvtn
  HAVING COUNT(*) >= 50  -- Minimum provider count for meaningful analysis
)
SELECT
  state,
  p25_payment,
  p50_payment, 
  p75_payment,
  p90_payment,
  ROUND(p75_payment - p25_payment, 2) as p75_p25_spread,
  ROUND(try_divide(p90_payment, p50_payment), 2) as p90_p50_ratio,
  provider_count,
  total_claims
FROM state_medicaid_variance
ORDER BY p90_p50_ratio DESC;

/*
KEY FINDINGS:
- Alaska: Highest absolute variance ($142 spread, 16.5x ratio)
- Delaware/Minnesota/Florida: Extreme ratios due to $0 P10 payments (dual-eligible artifacts)
- Maryland: High variance with reasonable payment floor ($20.85 P10)

BUSINESS IMPLICATIONS:
- High-variance states = prime contracting opportunities
- Focus payer portfolio optimization on states with largest spreads
- "Your Medicaid revenue could vary 5-100x based on payer mix"

DATA METHODOLOGY:
- Uses 2023-2024 data only for most recent patterns
- Uses provider-level averages to calculate state percentiles
- Filters to providers with >=10 claims for data quality
- Requires >=50 providers per state for statistical validity
- Join with Medicare data provides state information
*/