---
name: medicaid-provider-spending-dataset-analysis
description: Reference for analyzing public Medicaid claims dataset (T-MSIS provider spending). Covers dataset scope, known pitfalls, clean filters, and what questions the data can and cannot answer. Use before starting any analysis on this table.
---

# Healthcare Claims Data Analysis: Public Medicaid Dataset

## When to Use This Skill

Before starting any analysis involving:
- `datamedicaidgov.medicaid_provider_spending` (Medicaid provider-level claims)
- Provider-level reimbursement benchmarking within Medicaid
- Payer mix or coding pattern analysis within Medicaid

Read this first. It will save you hours of dead ends.

---

## Dataset Reference

### Medicaid: `datamedicaidgov.medicaid_provider_spending`

**Source:** T-MSIS claims data, published on opendata.hhs.gov

**Scope:** Provider-level Medicaid spending aggregated by NPI × HCPCS × month. Covers January 2018 through December 2024. Includes **fee-for-service, managed care (MCO), PCCM, and CHIP claims**.

**Key fields:**
- `npi` — billing provider (join with `mimi_ws_1.nppes.npidata` to get provider state from `provider_business_practice_location_address_state_name`)
- `hcpcs_code` — procedure code
- `total_paid` — what the provider actually received
- `total_claims` — claim count
- `state` — provider state (derived from NPPES data)
- `year_month` — service period

**What's NOT in this data:**
This dataset is T-MSIS claims grouped by NPI × HCPCS × month (i.e., does not capture all Medicaid spending). Anything in T-MSIS that doesn't have both a provider NPI and an HCPCS code falls out: capitation payments (non-claim financial transactions, no HCPCS), pharmacy claims (billed by NDC, not HCPCS), institutional claims billed on revenue codes without HCPCS, DSH and supplemental payments.

Additional exclusions:
- **Which payer (FFS vs. specific MCO) made the payment** — aggregated away

This is roughly 20-25% of total Medicaid program spending (~$1.1T in the dataset vs ~$4.5T total). The exclusions are known and structural, not data quality issues. This makes the dataset MORE trustworthy for what it contains.

**Critical data quality caveat:** OIG found that about half of states did not provide complete or accurate managed care payment data in T-MSIS. MCO encounter payment amounts may be incomplete or inaccurate in some states. FFS payments are reliable.

---

## Known Pitfalls & Required Filters

### 1. Dual-Eligible $0 Payment Records

**Problem:** Dual-eligible patients (Medicare + Medicaid) have Medicare pay first. Medicaid picks up residual cost-sharing — often $0 to $5. These show up as legitimate claims with valid HCPCS codes but near-zero payment.

**Impact:** Hundreds of thousands of records at $0-$5 per claim. Dramatically skews averages downward.

**Fix:** Filter to `medicaid_per_claim >= $15` for office visit E&M codes (99213-99215). Real Medicaid FFS rates for these codes are never below $15 even in the lowest-paying states. Adjust threshold by code family.

### 2. FFS vs. MCO vs. PCCM Blending

**Problem:** The Medicaid dataset aggregates FFS, MCO, and PCCM payments at the provider level. You cannot separate them.

**Impact:** You'll see a cluster of providers at the FFS fee schedule rate (e.g., $15-16 for IL 99214) and a spread above that reflecting different MCO contracts. You cannot attribute variance to specific MCOs or PCCM arrangements.

**Implication:** Within-state variance is real and interpretable as MCO/PCCM pricing differentiation signal. But you cannot benchmark against a specific MCO's or PCCM's market rate.

### 3. HCPCS Code Categories for Analysis

**Clean codes for consistent analysis:**
- 99213, 99214, 99215 (established patient office visits)
- 99203, 99204, 99205 (new patient office visits)
- 99283, 99284, 99285 (ED visits)

These codes show clear variance patterns and are suitable for within-Medicaid variance analysis. ED visits may show MORE interesting variance because MCOs negotiate ED rates aggressively.

---

## What the Data Can and Cannot Support

### ✅ CAN support:

**1. Within-state Medicaid provider variance by code**
- For each state × HCPCS, calculate CV, IQR, or P10/P90 spread
- High variance = MCO contracting creating price differentiation
- This appears unpublished — existing literature uses fee schedules (not paid amounts) and compares across states (not within)
- The dataset is new and researchers haven't published this cut yet

**Example queries:**

```sql
-- Query 1: State variance analysis for single code (CPT 99214)
-- Purpose: Identify states with highest payment variance for office visits
-- High variance indicates mixed payer environment = contracting opportunity

WITH state_medicaid_variance AS (
  SELECT
    state,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY total_paid / total_claims), 2) as p25_payment,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY total_paid / total_claims), 2) as p50_payment,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_paid / total_claims), 2) as p75_payment,
    ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY total_paid / total_claims), 2) as p90_payment,
    COUNT(*) as provider_count
  FROM mimi_ws_1.datamedicaidgov.medicaid_provider_spending
  WHERE hcpcs_code = '99214'
    AND total_claims >= 10
    AND LEFT(year_month, 4) IN ('2023', '2024')
  GROUP BY state
  HAVING COUNT(*) >= 50
)
SELECT
  state,
  p25_payment,
  p50_payment,
  p75_payment,
  p90_payment,
  ROUND(p75_payment - p25_payment, 2) as p75_p25_spread,
  ROUND(try_divide(p90_payment, p50_payment), 2) as p90_p50_ratio,
  provider_count
FROM state_medicaid_variance
ORDER BY p90_p50_ratio DESC;
```

```sql
-- Query 2: Multi-code variance comparison (Office visits vs ED codes)
-- Purpose: Test hypothesis that ED codes show wider variance due to aggressive MCO negotiation

WITH code_state_variance AS (
  SELECT
    hcpcs_code,
    state,
    CASE
      WHEN hcpcs_code IN ('99213', '99214', '99215') THEN 'Office Visit'
      WHEN hcpcs_code IN ('99283', '99284', '99285') THEN 'ED Code'
      ELSE 'Other'
    END as code_category,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY total_paid / total_claims), 2) as p25_payment,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY total_paid / total_claims), 2) as p50_payment,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_paid / total_claims), 2) as p75_payment,
    ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY total_paid / total_claims), 2) as p90_payment,
    COUNT(*) as provider_count
  FROM mimi_ws_1.datamedicaidgov.medicaid_provider_spending
  WHERE hcpcs_code IN ('99213', '99214', '99215', '99283', '99284', '99285')
    AND total_claims >= 10
    AND LEFT(year_month, 4) IN ('2023', '2024')
  GROUP BY hcpcs_code, state
  HAVING COUNT(*) >= 25
)
SELECT
  hcpcs_code,
  state,
  code_category,
  p25_payment,
  p50_payment,
  p75_payment,
  p90_payment,
  ROUND(p90_payment - p25_payment, 2) as p90_p25_spread,
  ROUND(try_divide(p90_payment, p25_payment), 2) as p90_p25_ratio,
  provider_count
FROM code_state_variance
WHERE p90_payment - p25_payment > 0
ORDER BY p90_p25_spread DESC;
```

**2. Code utilization patterns within Medicaid**
- Top Medicaid codes include significant ED utilization (99283, 99284, 99285)
- Office visit patterns show distribution across complexity levels
- Actionable insights for provider coding and documentation patterns

**3. Market ceiling identification**
- P90 of Medicaid payments within a state = "someone in your market gets this rate"
- CFOs bring their own payer-specific rates, benchmark against the public distribution
- They know their rate; they don't know the ceiling

**4. Provider volume trends over time**
- Medicaid volume changes = COVID enrollment surge → redetermination unwinding
- MCO enrollment shifts and market dynamics

### ❌ CANNOT support:

**1. Payer-specific benchmarking**
- Cannot say "your Meridian rate is below market for Meridian"
- MCO identity is not in the public data
- Would require raw T-MSIS research files (DUA through ResDAC) or provider-contributed remittance data

**2. FFS vs. MCO vs. PCCM rate separation**
- Cannot cleanly separate fee schedule payments from MCO contracted payments or PCCM arrangements
- Can infer: cluster at floor = FFS, spread above = MCO/PCCM variation
- Cannot prove this decomposition

**3. Provider-level benchmarking (with precision)**
- Can compute per-claim average per provider, but FFS + MCO blend + data quality issues = significant caveats
- Directionally useful, not precise enough for standalone product

---

## Analytical Guardrails

### Before starting any analysis, answer these:

1. **Does my thesis require payer-level granularity?** If yes, the public data can't support it. Reframe.

2. **Am I analyzing within-Medicaid patterns?** Focus on any code for variance analysis.

3. **Am I comparing rates or volumes?** Rates are directionally useful for Medicaid (FFS + MCO blend), volumes show utilization patterns.

4. **Have I filtered dual-eligible noise?** Always. Set a per-claim floor by code family.

### The meta-pattern:

The most common failure mode is building toward a product thesis that requires more granularity than the data provides. Public data excels at **market-level context** (distributions, ceilings, variance) and **state-level comparisons** within Medicaid. It does NOT replace provider-submitted private data or raw research files.

The product play: public data provides market context the CFO can't build + private data provides payer-specific rates the CFO already has. Neither alone is sufficient.

---

## Contracting Mechanics Reference

### How Medicaid payment works:

- **FFS Medicaid** = state fee schedule. No negotiation. Provider accepts or doesn't participate.
- **MCO Medicaid** = negotiated contracts between MCOs and providers. Can pay above or below the state fee schedule. This is where variance and contracting opportunity exist.
- **PCCM Medicaid** = Primary Care Case Management, typically FFS payments with care coordination fees.

### How MCO contracts are typically structured:

- Percentage-based rates (e.g., "80% of standard fee schedule for all professional services")
- Custom fee schedule (negotiated rates for specific codes or code families)
- Per diem or case rates (facility services)
- Capitation (flat PMPM regardless of volume)

### How PCCM arrangements work:

- Primary care providers paid FFS rates for services delivered
- Additional care coordination fee (typically flat PMPM)
- May include performance bonuses or shared savings
- Specialist referrals typically still paid at FFS rates

**Important:** If most contracts use percentage-based rates, then code-level variance reflects different percentage multipliers, not code-by-code negotiation. The negotiation lever is the multiplier. Verify contract structure with your customers before building code-level benchmarking tools.

### Payment hierarchy:

| Payer Type | Typical Rate Range | Rate Setting |
|------------|-------------------|--------------|
| Commercial | Higher rates | Negotiated |
| Medicaid FFS | State fee schedule | State-determined |
| Medicaid MCO | Variable above/below FFS | Negotiated |

---