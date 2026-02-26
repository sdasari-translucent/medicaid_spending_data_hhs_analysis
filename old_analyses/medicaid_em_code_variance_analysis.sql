-- MEDICAID MULTI-CODE VARIANCE ANALYSIS - 2023-2024
-- Compare variance across office visit codes (99213, 99214, 99215) vs ED codes (99283, 99284, 99285)
-- Hypothesis: ED codes show wider variance due to aggressive MCO negotiation

WITH code_state_variance AS (
  SELECT
    m.hcpcs_code,
    rndrng_prvdr_state_abrvtn as state,
    CASE
      WHEN m.hcpcs_code IN ('99213', '99214', '99215') THEN 'Office Visit'
      WHEN m.hcpcs_code IN ('99283', '99284', '99285') THEN 'ED Code'
      ELSE 'Other'
    END as code_category,
    ROUND(AVG(total_paid / total_claims), 2) as avg_payment,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY total_paid / total_claims), 2) as p25_payment,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY total_paid / total_claims), 2) as p50_payment,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_paid / total_claims), 2) as p75_payment,
    ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY total_paid / total_claims), 2) as p90_payment,
    COUNT(*) as provider_count,
    SUM(total_claims) as total_claims
  FROM mimi_ws_1.datamedicaidgov.medicaid_provider_spending m
  JOIN mimi_ws_1.datacmsgov.mupphy mp ON m.billing_provider_npi_num = mp.rndrng_npi
  WHERE m.hcpcs_code IN ('99213', '99214', '99215', '99283', '99284', '99285')
    AND m.total_claims >= 10
    AND mp.hcpcs_cd = m.hcpcs_code
    AND rndrng_prvdr_state_abrvtn IS NOT NULL
    AND LEFT(m.year_month, 4) IN ('2023', '2024')
  GROUP BY m.hcpcs_code, rndrng_prvdr_state_abrvtn
  HAVING COUNT(*) >= 25  -- Lower threshold due to multiple codes
)
SELECT
  hcpcs_code,
  state,
  code_category,
  avg_payment,
  p25_payment,
  p50_payment,
  p75_payment,
  p90_payment,
  ROUND(p90_payment - p25_payment, 2) as p90_p25_spread,
  ROUND(p75_payment - p25_payment, 2) as p75_p25_spread,
  ROUND(try_divide(p90_payment, p25_payment), 2) as p90_p25_ratio,
  provider_count,
  total_claims
FROM code_state_variance
WHERE p90_payment - p25_payment > 0  -- Filter out zero variance cases
ORDER BY p90_p25_spread DESC
LIMIT 20;

/*
HYPOTHESIS TESTING:
- ED codes (99283, 99284, 99285) expected to show higher variance than office visits
- MCOs negotiate ED rates more aggressively than routine office visits
- Higher variance = more contracting opportunity

KEY METRICS:
- p90_p25_spread: Absolute dollar difference between 90th and 25th percentile
- p75_p25_spread: Interquartile range (IQR) for core distribution
- p90_p25_ratio: Multiplicative difference (how many times higher)
- p25/p50/p75/p90: Full quartile distribution for payment patterns
- code_category: Office Visit vs ED Code for pattern analysis

BUSINESS INSIGHTS:
- Top variance codes/states = prime negotiation targets
- ED vs office visit variance patterns inform contracting strategy
- State-specific code patterns reveal market dynamics
*/