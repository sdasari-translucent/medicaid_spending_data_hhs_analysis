# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **healthcare data analysis repository** focused on public Medicaid and Medicare claims data analysis using the **Mimilabs MCP platform**. The project generates defensible, reproducible findings about provider reimbursement patterns and utilization differences between healthcare programs.

## Key Commands

### Running Analysis
```bash
# Install Python dependencies
pip install -r requirements.txt

# Generate visualization charts
python medicaid_medicare_analysis.py

# Execute SQL queries (requires Mimilabs platform access)
# Run SQL files through Mimilabs platform:
# - medicaid_instate_variance_analysis.sql
# - state_reimbursement_comparison.sql
# - code_mix_analysis.sql
```

### Data Sources Access
The project uses Mimilabs MCP integration to access:
- **Medicaid**: `mimi_ws_1.datamedicaidgov.medicaid_provider_spending` (2018-2024)
- **Medicare**: `mimi_ws_1.datacmsgov.mupphy` (physician utilization)

## Architecture & Analysis Structure

### Core Analysis Files
- **`medicaid_medicare_analysis.py`**: Main visualization script producing clean, defensible charts
- **SQL Analysis Files**: Purpose-built queries for specific research questions:
  - `state_reimbursement_comparison.sql`: Cross-state Medicaid vs Medicare rate gaps
  - `medicaid_instate_variance_analysis.sql`: Within-state provider payment variance analysis
  - `code_mix_analysis.sql`: Utilization pattern differences between programs

### Data Quality Approach
The project follows strict data quality principles:
- **Clean comparison codes**: Office visits only (99213, 99214, 99215) for cross-program analysis
- **Same provider, same procedure**: Uses NPI joins to ensure apples-to-apples comparisons
- **Meaningful sample sizes**: Minimum 100 providers per state for statistical validity
- **Dual-eligible filtering**: Excludes $0-$5 claims that represent Medicare cost-sharing only

### Key Research Findings
1. **State Reimbursement Gap**: 3.6x variation across states (Alabama 35¢ vs Colorado 127¢ per Medicare dollar)
2. **In-State Variance**: High coefficient of variation indicates MCO contracting opportunities
3. **Code Mix Patterns**: Medicaid shows higher ED utilization, Medicare shows higher complexity office visits

### Documentation Standards
- **`executive_summary.md`**: Business-focused findings and product insights
- **`README.md`**: Technical methodology and reproducibility details
- **`skills/` directory**: Reference documentation for healthcare claims data analysis

## Important Notes

### Data Limitations to Remember
- **No payer-specific breakouts**: Cannot separate FFS vs specific MCO payments
- **ED codes excluded from cross-program comparison**: Facility vs professional bundling issues
- **Medicare Advantage not included**: `mupphy` contains FFS only
- **MCO data quality varies by state**: Some states have incomplete managed care encounter data

### Analysis Best Practices
- Always deduplicate Medicare data before joining (same NPI can appear multiple times)
- Use minimum payment thresholds to filter dual-eligible cost-sharing records
- Focus on office visit codes for clean Medicaid-Medicare comparisons
- Use within-state variance analysis for MCO contracting insights

### Product Positioning Context
This analysis supports the thesis that **public data provides market context** (distributions, ceilings, variance) while **private remittance data provides payer-specific benchmarking**. The combination creates more value than either alone.