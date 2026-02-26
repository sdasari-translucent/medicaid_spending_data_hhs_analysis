-- MEDICAID IN-STATE PROVIDER VARIANCE ANALYSIS
-- Identifies states with highest payment variance within Medicaid program
-- High variance = mixed payer environment = contracting opportunity

WITH medicaid_by_provider AS (
  -- Calculate average Medicaid payment per claim for each provider
  SELECT
    billing_provider_npi_num as npi,
    SUM(total_paid) / SUM(total_claims) as medicaid_payment_per_claim,
    SUM(total_claims) as total_claims
  FROM mimi_ws_1.datamedicaidgov.medicaid_provider_spending
  WHERE hcpcs_code = '99213'  -- Standard office visit
    AND total_claims >= 10    -- Minimum volume for meaningful data
  GROUP BY billing_provider_npi_num
),

medicare_with_state AS (
  -- Get state info from Medicare data (Medicaid data lacks state field)
  SELECT
    rndrng_npi as npi,
    rndrng_prvdr_state_abrvtn as state,
    avg_mdcr_pymt_amt as medicare_payment
  FROM mimi_ws_1.datacmsgov.mupphy
  WHERE hcpcs_cd = '99213'
    AND tot_srvcs >= 10      -- Minimum volume for meaningful data
),

state_variance AS (
  -- Calculate variance metrics by state
  SELECT
    m.state,
    COUNT(*) as providers,
    ROUND(AVG(med.medicaid_payment_per_claim), 2) as avg_medicaid_payment,
    ROUND(STDDEV(med.medicaid_payment_per_claim), 2) as stddev_medicaid_payment,

    -- Coefficient of variation = key metric for identifying high-variance states
    ROUND(try_divide(STDDEV(med.medicaid_payment_per_claim), AVG(med.medicaid_payment_per_claim)), 3) as coefficient_of_variation,

    -- Quartile analysis
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY med.medicaid_payment_per_claim), 2) as p25_payment,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY med.medicaid_payment_per_claim), 2) as p75_payment,

    -- P75/P25 ratio shows spread between top and bottom quartile providers
    ROUND(try_divide(
      PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY med.medicaid_payment_per_claim),
      PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY med.medicaid_payment_per_claim)
    ), 2) as p75_p25_ratio

  FROM medicaid_by_provider med
  JOIN medicare_with_state m ON med.npi = m.npi
  GROUP BY m.state
  HAVING providers >= 100    -- Filter for states with meaningful sample size
)

-- Final results with variance categorization
SELECT
  state,
  providers,
  avg_medicaid_payment,
  coefficient_of_variation,
  p25_payment,
  p75_payment,
  p75_p25_ratio,

  -- Categorize variance levels
  CASE
    WHEN coefficient_of_variation > 0.6 THEN 'High Variance'
    WHEN coefficient_of_variation > 0.4 THEN 'Medium Variance'
    ELSE 'Low Variance'
  END as variance_category,

  -- Business insight
  CASE
    WHEN coefficient_of_variation > 0.8 THEN 'Prime contracting opportunity'
    WHEN coefficient_of_variation > 0.6 THEN 'Strong contracting opportunity'
    WHEN coefficient_of_variation > 0.4 THEN 'Moderate contracting opportunity'
    ELSE 'Limited contracting opportunity'
  END as contracting_opportunity

FROM state_variance
ORDER BY coefficient_of_variation DESC;

/*
KEY INSIGHTS:
- High coefficient of variation = mixed payer environment within state
- Large P75/P25 ratios indicate significant payment spread among providers
- Target states: UT (121% CoV), CA (111% CoV), AL (111% CoV), FL (100% CoV)
- Strategy: Optimize payer mix toward higher-paying Medicaid contracts

BUSINESS VALUE:
- Identifies markets where payer portfolio optimization could be most impactful
- "Your Medicaid revenue could vary 7-100x based on your payer mix"
- More strategic than provider-level benchmarking - this is payer portfolio optimization

DATA LIMITATIONS:
- No direct FFS vs MCO breakdown in public data
- Uses NPI join to get state info (some providers may be missed)
- Variance could include legitimate differences (rural vs urban, complexity, etc.)
*/