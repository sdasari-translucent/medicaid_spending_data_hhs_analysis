# Translucent Mimilabs Analysis

Comprehensive healthcare reimbursement analysis by **practice type** using Mimilabs MCP integration. Analyzes how Medicaid payment patterns vary across solo providers, small groups, large groups, and health systems to identify contracting opportunities and market positioning strategies.

## Project Goal

Segment healthcare provider reimbursement analysis by practice type to understand:
- **Negotiating power differentials** between solo providers and health systems
- **Market positioning** within state-specific reimbursement distributions
- **Contracting opportunities** based on payment variance by organization size
- **Strategic insights** for practice consolidation and payer portfolio optimization

## Key Findings

### 🎯 Finding #1: State-Level Medicaid Reimbursement Gap
**Not** "Medicaid pays 72¢ on the dollar" — **Instead**: **3.6x spread across states**

- **Bottom**: Alabama (35¢), California (37¢), Florida (41¢) on the Medicare dollar
- **Top**: Colorado (127¢), Montana (123¢), South Carolina (121¢) on the Medicare dollar
- **Same procedure, same provider type, 3.6x payment difference**

### 🎯 Finding #2: Code Mix Differences Reveal Population Patterns
**Medicaid vs Medicare utilization patterns:**

**Medicaid Top 5 E&M:**
1. 99213 (Office Visit) - 764M claims
2. 99214 (Office Visit) - 502M claims
3. **99284 (ED Code)** - 171M claims
4. **99283 (ED Code)** - 158M claims
5. **99285 (ED Code)** - 111M claims

**Medicare Top 5 E&M:**
1. **99214** (Complex Office Visit) - 1.06B services ← **Flipped from Medicaid**
2. 99213 (Standard Office Visit) - 973M services
3. 99232 (Hospital Visit) - 474M services
4. 99233 (Hospital Visit) - 251M services
5. 99212 (Simple Office Visit) - 120M services

**Key insight**: Medicaid = higher ED utilization, Medicare = higher complexity office visits

### 🔥 Finding #3: In-State Medicaid Variance = Payer Contracting Opportunity
**High variance within a state's Medicaid program indicates mixed payer environment**

**Highest Variance States (99213 Office Visits):**
- **Utah**: 121% coefficient of variation, P75/P25 ratio = 1.4x
- **California**: 111% coefficient of variation, P75/P25 ratio = 17.9x
- **Alabama**: 111% coefficient of variation, P75/P25 ratio = ∞
- **Florida**: 100% coefficient of variation, P75/P25 ratio = 7.4x

**Strategic insight**: High-variance states = "Your Medicaid revenue could vary 7-100x based on your payer mix"

## Project Structure

### Practice Type Directories
- `solo_provider/` - Solo practitioner analysis and queries
- `small_group/` - Small group practice (2-10 providers) analysis
- `large_group/` - Large group practice (11-50 providers) analysis
- `health_system/` - Health system provider analysis
- `combined/` - Cross-practice-type comparative analysis

### Reference Documentation
- `skills/medicaid-provider-spending-dataset-analysis/` - T-MSIS dataset methodology and sample queries
- `skills/practice-type-determination-npi/` - Practice type classification methodology and SQL examples

### Analysis Scripts
- `medicaid_medicare_analysis.py` - Clean visualization script (2 defensible charts only)
- `collect_all_data.py` - Data collection across practice types

### Data Sources

#### Claims Data
- **Medicaid**: `mimi_ws_1.datamedicaidgov.medicaid_provider_spending` (2018-2024)
  - Provider-level T-MSIS claims aggregated by NPI × HCPCS × month
  - Includes FFS, MCO, PCCM, and CHIP payments
  - ~$1.1T in dataset (~25% of total Medicaid spending)
- **Medicare**: `mimi_ws_1.datacmsgov.mupphy` (physician utilization)

#### Practice Type Classification
- **Primary**: `payermrf.npi_to_tin` - Commercial payer MRF TIN-to-NPI linkages
- **Health Systems**: `ahrq.compendium_grouppractice_linkage` - AHRQ health system compendium
- **Crosswalk**: `mimilabs.entity_linkages` - NPI to PAC/CCN identifier mapping

### Methodology

#### Practice Type Classification
Using hybrid approach combining explicit health system identification with TIN-based classification:

1. **Health System Identification** (Primary)
   - NPI → PAC → AHRQ Compendium health system mapping
   - Explicit health system names and IDs from curated data

2. **TIN-based Classification** (Secondary)
   - Solo Practice: `tin_size = 1`
   - Small Group: `tin_size = 2-10`
   - Large Group: `tin_size = 11-50`
   - Quality filter: `src_count >= 2` for reliable affiliations

#### Reimbursement Analysis
- **Office visits only**: 99213, 99214, 99215 (clean cross-program comparison)
- **Same provider** (NPI), same procedure (HCPCS), same time period
- **Minimum sample sizes**: 25-100+ providers per state/practice type for statistical validity
- **Dual-eligible filtering**: Payment floor thresholds to remove $0-$5 cost-sharing records
- **All data publicly available** through mimilabs platform

## What We Excluded (Data Quality Issues)

### **ED Code Ratios** - Major Data Quality Issue
- **99283, 99284, 99285** were **3 of Medicaid's top 5 codes by volume** - $52B combined spending in dataset
- **Problem**: Absurdly high Medicaid-to-Medicare ratios (Minnesota 99283 at 3.3x Medicare rates, etc.)
- **Root cause**: Medicaid likely bundles facility + professional fees while `mupphy` only has professional component
- **Decision**: Excluded from rate gap analysis despite massive volume to maintain data integrity

### **Other Exclusions**
- **Provider-level variation decomposition** - Can't separate signal vs noise without payer detail
- **Revenue impact projections** - Too many unknowns in contracting

## Product Insights

### 1. **Public Data = Context Layer, Not Benchmarking Engine**
- Can tell CFO where market range sits
- Can't tell them where their specific contracts fall
- Value is **combining** public benchmarks with private remittance data

### 2. **Customer Conversation Reframing**
- Instead of: "Medicaid pays 72¢ on the dollar nationally"
- Say: "In your state, Medicaid pays X¢ on the Medicare dollar, ranging from Y to Z"
- More relevant than generic national averages

### 3. **Payer Portfolio Optimization**
- High-variance states = strategic contracting opportunity
- Focus on **payer mix optimization** rather than individual rate negotiation
- "Which Medicaid payers in your state pay the best rates?"

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Generate visualizations
python medicaid_medicare_analysis.py

# Run SQL analysis (requires mimilabs access)
# Execute medicaid_instate_variance_analysis.sql in mimilabs platform
```

## Reproducibility

All findings are **completely reproducible** using public datasets:
- SQL queries included in repository
- Results validated across 400,000+ providers nationwide
- Methodology documented and transparent