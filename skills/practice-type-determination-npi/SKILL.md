---
name: practice-type-determination-npi
description: Reference for determining practice type categories (solo, small group, large group, health systems) from NPI data using Mimilabs datasets. Covers key tables, classification methods, data limitations, and crosswalk strategies for provider organization analysis.
---

# Practice Type Determination: NPI to Organization Structure Analysis

## When to Use This Skill

Before starting any analysis involving:
- Provider organization type classification (solo vs. group vs. health system)
- Practice consolidation trends
- Market concentration analysis by practice type
- Provider affiliation and organizational structure
- Health system identification and membership

Read this first. It will save you from using incomplete or inappropriate data sources.

---

## Key Data Sources for Practice Type Classification

### Primary: `payermrf.npi_to_tin` ⭐ RECOMMENDED

**Source:** Payer machine-readable files (MRF), aggregated by Mimilabs

**Scope:** Current US providers with comprehensive TIN-to-NPI linkages from commercial payer networks

**Key fields:**
- `npi` — provider NPI
- `tin` — Tax Identification Number (organization identifier)
- `tin_size` — unique NPIs per TIN/organization
- `src_count` — number of payer sources reporting this NPI-TIN linkage (indicates strength)

**Classification logic:**
- **Solo practice:** `tin_size = 1`
- **Small group:** `tin_size = 2-9`
- **Medium group:** `tin_size = 10-99`
- **Large group:** `tin_size >= 100`
- **Note:** Health system classification is ONLY from AHRQ data, not TIN size

**Advantages:**
- Most current and comprehensive coverage
- Reflects actual billing relationships (not just registrations)
- Higher `src_count` = more reliable affiliation data

**Limitations:**
- Does not distinguish between true practice partnerships and billing service arrangements
- May miss providers who only bill Medicare/Medicaid (not commercial)

### Secondary: `ahrq.compendium_grouppractice_linkage` ⭐ BEST FOR HEALTH SYSTEMS

**Source:** AHRQ Compendium of U.S. Health Systems

**Scope:** Group practices and health system affiliations, 2016-2018 snapshots

**Key fields:**
- `pecos_pac_ids` — Provider enrollment IDs (crosswalk to NPI needed)
- `md_do_md_ppas` — physician count per TIN/group practice
- `health_sys_id` / `health_sys_name` — health system identification
- `tin` — organization tax ID

**Classification logic:**
- Use `health_sys_id` IS NOT NULL for health system identification ONLY
- Other providers classified by TIN size: solo (1), small (2-9), medium (10-99), large (100+)

**NPI crosswalk required:**
```sql
-- Link AHRQ data to NPIs
SELECT a.*, e.npi
FROM ahrq.compendium_grouppractice_linkage a
JOIN mimilabs.entity_linkages e
  ON a.pecos_pac_ids = e.pac_id
WHERE e.npi IS NOT NULL
```

**Advantages:**
- Explicit health system identification with names
- Curated data source designed for organizational analysis
- Clear distinction between independent groups and health system members

**Limitations:**
- Historical data (2016-2018), may not reflect current affiliations
- Requires crosswalk through entity_linkages
- Less comprehensive coverage than payer MRF

### Tertiary: `provdatacatalog.dac_ndf` (Medicare DAC National Downloadable File)

**Source:** Medicare provider enrollment data

**Scope:** Medicare-enrolled clinicians and their organizational affiliations

**Key fields:**
- `npi` — provider NPI
- `org_pac_id` — organization provider enrollment ID
- `num_org_mem` — number of clinicians in the organization
- `mimi_src_file_date` — data extraction date (use latest)

**Classification logic:**
- Use `num_org_mem` for organization size
- Filter to latest `mimi_src_file_date`
- Deduplicate by NPI (providers can have multiple org affiliations)

**Limitations:**
- Medicare enrollment only (may miss Medicaid-only providers)
- Organization structure reflects enrollment, not necessarily practice structure
- Requires careful deduplication

---

## Recommended Analysis Approach: Hybrid Strategy

### 1. Explicit Health System Identification (Primary Step)
```sql
-- Step 1: NPI → PAC → Health System
WITH npi_to_pac AS (
  SELECT DISTINCT npi, pac_id
  FROM mimilabs.entity_linkages
  WHERE pac_id IS NOT NULL
    AND confidence_score >= 0.95
),
pac_to_system AS (
  SELECT
    pac.value AS pac_id,
    a.health_sys_id,
    a.health_sys_name,
    a.md_do_md_ppas
  FROM ahrq.compendium_grouppractice_linkage a
  LATERAL VIEW explode(split(pecos_pac_ids, ',')) pac
  WHERE health_sys_id IS NOT NULL
    AND mimi_src_file_date = (SELECT MAX(mimi_src_file_date) FROM ahrq.compendium_grouppractice_linkage)
),
health_system_npis AS (
  SELECT DISTINCT n.npi, p.health_sys_name, p.health_sys_id
  FROM npi_to_pac n
  JOIN pac_to_system p ON n.pac_id = p.pac_id
)
```

### 2. TIN-based Classification for Non-Health Systems
```sql
-- Step 2: For NPIs NOT in health systems, use TIN size
tin_classification AS (
  SELECT
    npi,
    tin,
    tin_size,
    src_count,
    CASE
      WHEN tin_size = 1 THEN 'Solo Practice'
      WHEN tin_size BETWEEN 2 AND 9 THEN 'Small Group'
      WHEN tin_size BETWEEN 10 AND 99 THEN 'Medium Group'
      WHEN tin_size >= 100 THEN 'Large Group'
      ELSE 'Unknown'
    END as tin_based_category
  FROM payermrf.npi_to_tin
  WHERE src_count >= 2
)
```

### 3. Final Hybrid Classification
```sql
-- Step 3: Combine explicit health systems with TIN-based classification
SELECT
  COALESCE(t.npi, h.npi) as npi,
  h.health_sys_name,
  t.tin,
  t.tin_size,
  CASE
    WHEN h.health_sys_name IS NOT NULL THEN 'Health System'
    WHEN t.tin_size = 1 THEN 'Solo Practice'
    WHEN t.tin_size BETWEEN 2 AND 9 THEN 'Small Group'
    WHEN t.tin_size BETWEEN 10 AND 99 THEN 'Medium Group'
    WHEN t.tin_size >= 100 THEN 'Large Group'
    ELSE 'Unknown'
  END as practice_type
FROM health_system_npis h
FULL OUTER JOIN tin_classification t ON h.npi = t.npi
```

### 3. Quality Controls and Validation

**Always apply these filters:**

1. **Confidence threshold:** `src_count >= 2` in payermrf table
2. **Reasonable size limits:** `tin_size <= 10000` (filter data quality issues)
3. **Active providers only:** Join with utilization data to confirm active practice
4. **Deduplication:** Single classification per NPI (prioritize by src_count)

**Data quality checks:**
```sql
-- Check for outliers that may indicate data quality issues
SELECT tin, tin_size, COUNT(*) as npi_count
FROM payermrf.npi_to_tin
WHERE tin_size > 1000
GROUP BY tin, tin_size
ORDER BY tin_size DESC
```

---

## Known Limitations and Caveats

### 1. Billing vs. Practice Structure
- **Issue:** TIN relationships reflect billing arrangements, not necessarily practice ownership or clinical integration
- **Impact:** Billing service companies or management companies may appear as "large groups"
- **Mitigation:** Cross-reference with specialty mix and geographic clustering

### 2. Multi-TIN Providers
- **Issue:** Some providers bill under multiple TINs (e.g., hospital + private practice)
- **Impact:** May be classified inconsistently depending on which TIN relationship is captured
- **Mitigation:** Use `src_count` to prioritize most commonly reported relationships

### 3. Temporal Misalignment
- **Issue:** Practice affiliations change over time; datasets may reflect different time periods
- **Impact:** Classification may not match current affiliation status
- **Mitigation:** Use most recent data available; AHRQ data is 2016-2018, payer MRF is more current

### 4. Coverage Gaps
- **Issue:** Providers who only bill government payers may be underrepresented in commercial payer MRF
- **Impact:** May miss some solo practitioners or safety-net providers
- **Mitigation:** Supplement with DAC data for Medicare-focused analysis

---

## Use Cases and Applications

### ✅ SUPPORTED Analysis Types:

1. **Market concentration by practice type**
   - Calculate HHI or market share by size category within geographic markets
   - Track consolidation trends over time

2. **Reimbursement analysis by practice type**
   - Compare payment rates: solo vs. small group vs. health system
   - Analyze negotiating power differentials

3. **Provider network adequacy by organization type**
   - Assess payer network composition: independent vs. health system providers
   - Identify market access issues

4. **Specialty distribution by practice setting**
   - Compare specialist availability: group practice vs. health system employment
   - Analyze care delivery model differences

### ❌ NOT SUPPORTED:

1. **Ownership structure determination**
   - Cannot distinguish employee vs. independent contractor relationships
   - Cannot identify specific ownership models (partnership, corporation, etc.)

2. **Clinical integration assessment**
   - TIN relationships don't indicate care coordination or shared protocols
   - Cannot measure actual integration vs. administrative affiliation

3. **Financial relationship details**
   - Cannot determine revenue-sharing, profit distribution, or financial integration
   - Billing relationship ≠ economic relationship

---

## Cross-Reference with Other Analyses

When combining with claims analysis:
- Use practice type as a stratification variable for reimbursement analysis
- Analyze volume and complexity differences by practice setting
- Consider practice size in market concentration and competition analysis

When analyzing provider networks:
- Layer practice type onto network adequacy requirements
- Consider access implications of health system consolidation
- Evaluate payer strategy effectiveness by provider organization type

---

## Entity Linkage Reference

For crosswalking between identifier systems, use `mimilabs.entity_linkages`:

**Key crosswalks available:**
- PAC ID (PECOS) ↔ NPI
- CMS Certification Number ↔ NPI
- State license numbers ↔ NPI (varies by state)

**Usage pattern:**
```sql
SELECT DISTINCT npi, pac_id, ccn
FROM mimilabs.entity_linkages
WHERE npi = 'TARGET_NPI'
```

This enables linking AHRQ health system data (PAC-based) with claims data (NPI-based).