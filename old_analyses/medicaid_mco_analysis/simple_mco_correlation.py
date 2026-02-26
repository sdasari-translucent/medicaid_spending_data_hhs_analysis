#!/usr/bin/env python3
"""
Simple MCO Variance Correlation Analysis
Analyze correlation between Medicaid payment variance and MCO prevalence
"""

import pandas as pd
import numpy as np

def analyze_correlation():
    """Perform correlation analysis"""

    # Load 99214 variance data (state-level)
    variance_99214 = pd.read_csv('medicaid_state_variance_99214_sql.csv')

    # Load MCO delivery breakdown 2022
    mco_breakdown = pd.read_csv('medicaid_delivery_breakdown_2022.csv', skiprows=2)

    # Clean MCO breakdown data
    mco_breakdown = mco_breakdown[mco_breakdown['Location'] != 'United States'].copy()
    mco_breakdown = mco_breakdown.rename(columns={'Location': 'state_name'})

    # Convert percentages to numeric, handle '-' as NaN
    for col in ['Percent of Medicaid Population in MCO', 'Percent of Medicaid Population in PCCM', 'Percent of Medicaid Population in FFS/Other']:
        mco_breakdown[col] = pd.to_numeric(mco_breakdown[col].replace('-', np.nan), errors='coerce')

    # Create state code mapping for merging
    state_mapping = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
        'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
        'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
        'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
        'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
        'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
        'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
        'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
        'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
        'District of Columbia': 'DC'
    }

    mco_breakdown['state_code'] = mco_breakdown['state_name'].map(state_mapping)

    # Merge datasets on state
    merged = pd.merge(variance_99214, mco_breakdown, left_on='state', right_on='state_code', how='inner')

    print("=== MCO VARIANCE CORRELATION ANALYSIS ===\n")
    print(f"Total states with both variance and MCO data: {len(merged)}")

    # Filter out states with no MCO data
    analysis_data = merged[merged['Percent of Medicaid Population in MCO'].notna()].copy()
    print(f"States with valid MCO data: {len(analysis_data)}")

    if len(analysis_data) < 5:
        print("Insufficient data for analysis")
        return

    # Calculate correlation
    variance_col = 'p75_p25_spread'
    mco_col = 'Percent of Medicaid Population in MCO'

    correlation = np.corrcoef(analysis_data[variance_col], analysis_data[mco_col])[0, 1]

    print(f"\n=== CORRELATION RESULTS ===")
    print(f"Payment Variance (P75-P25 spread) vs MCO Penetration:")
    print(f"Correlation coefficient: {correlation:.3f}")
    print(f"Sample size: {len(analysis_data)} states\n")

    # Detailed state analysis
    print("=== STATE-BY-STATE BREAKDOWN ===")
    results = analysis_data[['state', 'p75_p25_spread', 'p90_p50_ratio', 'Percent of Medicaid Population in MCO', 'total_claims']].copy()
    results = results.sort_values('p75_p25_spread', ascending=False)

    # Format for display
    results['MCO_pct'] = results['Percent of Medicaid Population in MCO']
    results['Variance_$'] = results['p75_p25_spread'].round(2)
    results['Ratio'] = results['p90_p50_ratio'].round(2)
    results['Claims'] = results['total_claims']

    display_cols = ['state', 'Variance_$', 'Ratio', 'MCO_pct', 'Claims']
    print("Top variance states (99214 payments):")
    print(results[display_cols].head(15).to_string(index=False))

    # Summary statistics
    print(f"\n=== SUMMARY STATISTICS ===")

    # High vs Low MCO states
    high_mco = analysis_data[analysis_data['Percent of Medicaid Population in MCO'] >= 0.8]
    low_mco = analysis_data[analysis_data['Percent of Medicaid Population in MCO'] <= 0.3]

    if len(high_mco) > 0:
        print(f"High MCO states (>=80%): {len(high_mco)} states")
        print(f"  Average variance (P75-P25): ${high_mco['p75_p25_spread'].mean():.2f}")
        print(f"  Average ratio (P90/P50): {high_mco['p90_p50_ratio'].mean():.2f}")
        print(f"  States: {', '.join(high_mco['state'].tolist())}")

    if len(low_mco) > 0:
        print(f"\nLow MCO states (<=30%): {len(low_mco)} states")
        print(f"  Average variance (P75-P25): ${low_mco['p75_p25_spread'].mean():.2f}")
        print(f"  Average ratio (P90/P50): {low_mco['p90_p50_ratio'].mean():.2f}")
        print(f"  States: {', '.join(low_mco['state'].tolist())}")

    # Overall relationship interpretation
    print(f"\n=== INTERPRETATION ===")
    if correlation > 0.3:
        print("POSITIVE correlation: Higher MCO penetration tends to correlate with HIGHER payment variance")
        print("This suggests MCO competition may increase, not decrease, payment variation")
    elif correlation < -0.3:
        print("NEGATIVE correlation: Higher MCO penetration tends to correlate with LOWER payment variance")
        print("This suggests MCO standardization may reduce payment variation")
    else:
        print("WEAK correlation: Little relationship between MCO penetration and payment variance")
        print("Other factors may be more important than delivery system type")

    return analysis_data

if __name__ == "__main__":
    analyze_correlation()