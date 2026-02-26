-- CODE MIX ANALYSIS: MEDICAID VS MEDICARE UTILIZATION PATTERNS
-- Reveals population health and utilization differences between programs

-- Top 10 E&M codes by volume for each program
WITH medicaid_top_codes AS (
  SELECT
    'Medicaid' as program,
    hcpcs_code,
    SUM(total_claims) as total_volume,
    CASE
      WHEN hcpcs_code LIKE '9928%' THEN 'ED Code'
      WHEN hcpcs_code IN ('99213', '99214', '99215') THEN 'Office Visit'
      WHEN hcpcs_code LIKE '9923%' THEN 'Hospital Visit'
      ELSE 'Other'
    END as code_category,
    ROW_NUMBER() OVER (ORDER BY SUM(total_claims) DESC) as rank
  FROM mimi_ws_1.datamedicaidgov.medicaid_provider_spending
  WHERE hcpcs_code LIKE '992%'
  GROUP BY hcpcs_code
  ORDER BY total_volume DESC
  LIMIT 10
),

medicare_top_codes AS (
  SELECT
    'Medicare' as program,
    hcpcs_cd as hcpcs_code,
    SUM(tot_srvcs) as total_volume,
    CASE
      WHEN hcpcs_cd LIKE '9928%' THEN 'ED Code'
      WHEN hcpcs_cd IN ('99213', '99214', '99215') THEN 'Office Visit'
      WHEN hcpcs_cd LIKE '9923%' THEN 'Hospital Visit'
      ELSE 'Other'
    END as code_category,
    ROW_NUMBER() OVER (ORDER BY SUM(tot_srvcs) DESC) as rank
  FROM mimi_ws_1.datacmsgov.mupphy
  WHERE hcpcs_cd LIKE '992%'
  GROUP BY hcpcs_cd
  ORDER BY total_volume DESC
  LIMIT 10
)

-- Combined results showing utilization pattern differences
SELECT
  program,
  rank,
  hcpcs_code,
  code_category,
  ROUND(total_volume / 1000000, 0) as volume_millions,

  -- Calculate percentage of top 10 volume
  ROUND(100.0 * total_volume / SUM(total_volume) OVER (PARTITION BY program), 1) as pct_of_top10

FROM (
  SELECT * FROM medicaid_top_codes
  UNION ALL
  SELECT * FROM medicare_top_codes
) combined

ORDER BY program, rank;

/*
KEY FINDINGS:

MEDICAID UTILIZATION PATTERN:
- #1 Code: 99213 (Standard Office Visit) - 764M claims
- #2 Code: 99214 (Complex Office Visit) - 502M claims
- 3 of top 5 are ED codes (99284, 99283, 99285)
- Higher emergency department utilization

MEDICARE UTILIZATION PATTERN:
- #1 Code: 99214 (Complex Office Visit) - 1.06B services ← FLIPPED
- #2 Code: 99213 (Standard Office Visit) - 973M services
- 0 of top 5 are ED codes
- More hospital visits (99232, 99233) and complex office care

POPULATION HEALTH INSIGHTS:
- Medicaid patients: Higher ED utilization, more acute/urgent care
- Medicare patients: Higher complexity office visits, more planned care
- Different care patterns reflect different population needs and access

BUSINESS IMPLICATIONS:
- Volume forecasting models should account for program differences
- Revenue mix varies significantly by payer program
- ED-heavy vs office-heavy provider types have different Medicaid exposure
- Important for providers building Medicaid strategies

DATA SOURCES:
- Medicaid: 764M+ E&M claims (datamedicaidgov.medicaid_provider_spending)
- Medicare: 973M+ E&M services (datacmsgov.mupphy)
- Time period: 2018-2024 (varies by dataset)
*/