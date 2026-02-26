-- Medicaid Provider Rate Distributions by State
-- Analysis of office visit code 99214 with dual-eligible filtering (2023-2024 only)
-- Provides P25, P50, P75, P90, Max rates and provider counts for each state

WITH provider_rates AS (
  SELECT
    n.provider_business_practice_location_address_state_name AS state,
    mps.billing_provider_npi_num,
    mps.hcpcs_code,
    mps.total_paid / mps.total_claims AS rate_per_claim
  FROM mimi_ws_1.datamedicaidgov.medicaid_provider_spending mps
  JOIN mimi_ws_1.nppes.npidata n ON mps.billing_provider_npi_num = n.npi
  WHERE mps.hcpcs_code = '99214'  -- Established patient office visit, moderate complexity
    AND mps.total_paid / mps.total_claims >= 15  -- Filter dual-eligible noise
    AND n.provider_business_practice_location_address_state_name IS NOT NULL
    AND mps.total_claims >= 12  -- Minimum claims for statistical validity
    AND mps.claim_from_month >= '2023-01'  -- 2023-2024 only
)
SELECT
  state,
  COUNT(DISTINCT billing_provider_npi_num) AS provider_count,
  PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY rate_per_claim) AS p25_rate,
  PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY rate_per_claim) AS p50_rate,
  PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY rate_per_claim) AS p75_rate,
  PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY rate_per_claim) AS p90_rate,
  MAX(rate_per_claim) AS max_rate
FROM provider_rates
GROUP BY state
ORDER BY p50_rate;

-- Notes:
-- - Uses $15 minimum per-claim threshold to filter dual-eligible cost-sharing records
-- - Focuses on 99214 code for clean cross-state comparison
-- - Joins with NPPES to get provider state from business practice location
-- - Filters to 2023-2024 data only for recent rate analysis