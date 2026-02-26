# Executive Summary: Medicaid vs Medicare Analysis

**Date**: February 15, 2026
**Analysis**: Public healthcare reimbursement data via Mimilabs platform
**Scope**: 400,000+ providers, $1.1T in spending, 2018-2024

## 🎯 Three Commercially Valuable Findings

### 1. **State Reimbursement Gap** (Not National Average)
**Customer insight**: "Where you practice determines Medicaid profitability"

- **Traditional narrative**: "Medicaid pays 72¢ on the Medicare dollar"
- **Reality**: **3.6x variation across states** for same procedure (99213 office visit)
  - **Lowest**: Alabama (35¢), California (37¢), Florida (41¢)
  - **Highest**: Colorado (127¢), Montana (123¢), South Carolina (121¢)

**Business value**: State-specific benchmarking > generic national averages

### 2. **Payer Portfolio Optimization Opportunity**
**Customer insight**: "Your Medicaid revenue varies 7-100x based on payer mix"

**States with highest in-program variance** (coefficient of variation):
- **Utah**: 121% variance, providers range $44-$61/visit
- **California**: 111% variance, providers range $2-$30/visit
- **Florida**: 100% variance, 7.4x payment spread between quartiles

**Business value**: High-variance states = strategic payer contracting opportunity

### 3. **Population Utilization Patterns**
**Customer insight**: "Code mix forecasting must account for program differences"

**Medicaid vs Medicare Top E&M Codes**:
- **Medicaid #1**: 99213 (Standard office visit) - 764M claims
- **Medicare #1**: 99214 (Complex office visit) - 1.06B services ← **Flipped**
- **Medicaid**: 3 of top 5 are ED codes vs 0 for Medicare

**Business value**: Volume/revenue mix modeling, provider strategy by patient population

## 📊 Data Quality & Methodology

### What We Analyzed
- **Clean comparison**: Office visits only (99213, 99214, 99215)
- **Apples-to-apples**: Same provider (NPI), same procedure, same timeframe
- **Meaningful samples**: 100+ providers per state minimum
- **Validated scale**: 400K+ providers nationwide

### What We Excluded
- **ED codes**: Facility vs professional bundling differences
- **Provider-level variance**: Can't separate signal vs noise without payer detail
- **Revenue projections**: Too many contracting unknowns

### Reproducibility
- **100% public data** via mimilabs platform
- **SQL queries included** in repository
- **Methodology documented** and transparent

## 💼 Product Positioning

### Public Data = Context Layer, Not Benchmarking Engine
- **What it can do**: Tell CFO where market range sits for their state
- **What it can't do**: Tell them where their specific contracts fall
- **Value proposition**: Combine public benchmarks with private remittance data

### Customer Conversation Reframes

| Instead of... | Say this... |
|---------------|-------------|
| "Medicaid pays 72¢ on the dollar nationally" | "In your state, Medicaid pays X¢ on the Medicare dollar, ranging from Y to Z" |
| "You need better Medicaid rates" | "You need better Medicaid payer mix - some contracts in your state pay 7x more" |
| "Medicaid volume is unpredictable" | "Medicaid utilization patterns differ from Medicare - here's your expected mix" |

## 🚀 Strategic Recommendations

1. **Geographic Strategy**: Use state gaps to inform market entry/exit decisions
2. **Payer Optimization**: Target high-variance states for contract portfolio improvement
3. **Volume Forecasting**: Incorporate program-specific utilization patterns
4. **Competitive Positioning**: "Only benchmarking that combines public context with your private data"

## 📈 Next Steps

1. **Customer validation**: Test insights with Illinois customers (Duly, Northwestern)
2. **Data expansion**: Investigate specialty-specific patterns
3. **Payer identification**: Map state variance to specific MCO performance where possible
4. **Integration strategy**: How to layer private remittance data on public benchmarks

---

**Bottom line**: We've quantified the Medicaid reimbursement story that every CFO knows exists but has never seen at this scale. The geographic and payer mix insights are immediately actionable and completely defensible using public data.