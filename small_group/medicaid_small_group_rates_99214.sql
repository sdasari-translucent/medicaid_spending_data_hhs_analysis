-- Medicaid Provider Rate Distributions by State - Small Groups Only
-- Analysis of office visit code 99214 with dual-eligible filtering (2023-2024 only)
-- Filters to small group providers (TIN size 2-9) EXCLUDING health systems
-- Provides P25, P50, P75, P90, Max rates and provider counts for each state

WITH
-- Step 1: Get explicit health system NPIs from AHRQ data (to exclude)
npi_to_pac AS (
  SELECT DISTINCT npi, pac_id
  FROM mimi_ws_1.mimilabs.entity_linkages
  WHERE pac_id IS NOT NULL
    AND confidence_score >= 0.95
),
pac_to_system AS (
  SELECT
    pac.value AS pac_id,
    a.health_sys_id,
    a.health_sys_name,
    a.md_do_md_ppas
  FROM mimi_ws_1.ahrq.compendium_grouppractice_linkage a
  LATERAL VIEW explode(split(pecos_pac_ids, ',')) pac AS pac
  WHERE health_sys_id IS NOT NULL
    AND mimi_src_file_date = (SELECT MAX(mimi_src_file_date) FROM mimi_ws_1.ahrq.compendium_grouppractice_linkage)
),
health_system_npis AS (
  SELECT DISTINCT n.npi, p.health_sys_name, p.health_sys_id
  FROM npi_to_pac n
  JOIN pac_to_system p ON n.pac_id = p.pac_id
),
-- Step 2: Get small group providers (TIN size 2-9) excluding health systems
small_group_providers AS (
  SELECT
    npi,
    tin,
    tin_size,
    src_count
  FROM mimi_ws_1.payermrf.npi_to_tin
  WHERE tin_size >= 2
    AND tin_size <= 9
    AND src_count >= 2  -- Confidence threshold
    AND npi NOT IN (SELECT npi FROM health_system_npis)  -- Exclude health systems
),
-- Step 3: Filter Medicaid data to small group providers only
provider_rates AS (
  SELECT
    n.provider_business_practice_location_address_state_name AS state,
    mps.billing_provider_npi_num,
    mps.hcpcs_code,
    mps.total_paid / mps.total_claims AS rate_per_claim
  FROM mimi_ws_1.datamedicaidgov.medicaid_provider_spending mps
  JOIN mimi_ws_1.nppes.npidata n ON mps.billing_provider_npi_num = n.npi
  JOIN small_group_providers sg ON mps.billing_provider_npi_num = sg.npi  -- Small group filter
  WHERE mps.hcpcs_code = '99214'  -- Established patient office visit, moderate complexity
    AND mps.total_paid / mps.total_claims >= 15  -- Filter dual-eligible noise
    AND n.provider_business_practice_location_address_state_name IS NOT NULL
    AND mps.total_claims >= 12  -- Minimum claims for statistical validity
    AND mps.claim_from_month >= '2023-01'  -- 2023-2024 only
)
SELECT
  state,
  COUNT(DISTINCT billing_provider_npi_num) AS provider_count,
  ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY rate_per_claim), 2) AS p25_rate,
  ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY rate_per_claim), 2) AS p50_rate,
  ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY rate_per_claim), 2) AS p75_rate,
  ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY rate_per_claim), 2) AS p90_rate,
  ROUND(MAX(rate_per_claim), 2) AS max_rate
FROM provider_rates
GROUP BY state
ORDER BY p50_rate;

-- Notes:
-- - Small groups defined as TIN size 2-9 providers (from payermrf.npi_to_tin)
-- - Explicitly EXCLUDES health systems identified from AHRQ Compendium data
-- - Uses src_count >= 2 for confidence in TIN relationships
-- - Uses $15 minimum per-claim threshold to filter dual-eligible cost-sharing records
-- - Focuses on 99214 code for clean cross-state comparison
-- - Joins with NPPES to get provider state from business practice location
-- - Filters to 2023-2024 data only for recent rate analysis
-- - Removed avg_tin_size for cleaner output focused on rate distributions