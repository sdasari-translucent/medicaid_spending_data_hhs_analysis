#!/usr/bin/env python3
"""
MCO Variance Correlation Analysis
Analyze correlation between Medicaid payment variance and MCO prevalence
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def load_and_clean_data():
    """Load and clean the CSV data files"""

    # Load 99214 variance data (state-level)
    variance_99214 = pd.read_csv('medicaid_state_variance_99214_sql.csv')

    # Load MCO delivery breakdown 2022
    mco_breakdown = pd.read_csv('medicaid_delivery_breakdown_2022.csv', skiprows=2)

    # Clean MCO breakdown data
    mco_breakdown = mco_breakdown[mco_breakdown['Location'] != 'United States'].copy()
    mco_breakdown = mco_breakdown.rename(columns={'Location': 'state'})

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

    mco_breakdown['state_code'] = mco_breakdown['state'].map(state_mapping)

    return variance_99214, mco_breakdown

def analyze_correlation():
    """Perform correlation analysis"""

    variance_99214, mco_breakdown = load_and_clean_data()

    # Merge datasets on state
    merged = pd.merge(variance_99214, mco_breakdown, left_on='state', right_on='state_code', how='inner')

    print("=== MCO VARIANCE CORRELATION ANALYSIS ===\n")
    print(f"Total states with data: {len(merged)}")
    print(f"States analyzed: {sorted(merged['state_x'].unique())}\n")

    # Key variables for analysis
    variance_measures = ['p75_p25_spread', 'p90_p50_ratio']
    mco_measures = ['Percent of Medicaid Population in MCO']

    print("=== CORRELATION RESULTS ===\n")

    # Filter out states with no MCO data
    analysis_data = merged[merged['Percent of Medicaid Population in MCO'].notna()].copy()

    print(f"States with MCO data: {len(analysis_data)}")

    for variance_var in variance_measures:
        for mco_var in mco_measures:
            # Calculate correlations
            valid_data = analysis_data[[variance_var, mco_var]].dropna()

            if len(valid_data) < 5:
                print(f"Insufficient data for {variance_var} vs {mco_var}")
                continue

            # Simple correlation coefficient calculation
            correlation = np.corrcoef(valid_data[variance_var], valid_data[mco_var])[0, 1]

            print(f"{variance_var} vs {mco_var}:")
            print(f"  Correlation coefficient: {correlation:.3f}")
            print(f"  N = {len(valid_data)} states\n")

    # Detailed state analysis
    print("=== TOP VARIANCE STATES VS MCO PREVALENCE ===\n")

    top_variance = analysis_data.nlargest(10, 'p75_p25_spread')[['state_x', 'p75_p25_spread', 'p90_p50_ratio', 'Percent of Medicaid Population in MCO', 'total_claims']]
    print("Top 10 Highest Variance States (99214):")
    print(top_variance.round(3))
    print()

    high_mco = analysis_data[analysis_data['Percent of Medicaid Population in MCO'] >= 0.8][['state_x', 'p75_p25_spread', 'p90_p50_ratio', 'Percent of Medicaid Population in MCO', 'total_claims']]
    print("High MCO States (>=80%):")
    print(high_mco.round(3))
    print()

    low_mco = analysis_data[analysis_data['Percent of Medicaid Population in MCO'] <= 0.2][['state_x', 'p75_p25_spread', 'p90_p50_ratio', 'Percent of Medicaid Population in MCO', 'total_claims']]
    print("Low MCO States (<=20%):")
    print(low_mco.round(3))
    print()

    # Summary statistics
    high_mco_states = analysis_data[analysis_data['Percent of Medicaid Population in MCO'] >= 0.8]
    low_mco_states = analysis_data[analysis_data['Percent of Medicaid Population in MCO'] <= 0.2]

    print("=== SUMMARY STATISTICS ===\n")
    print(f"High MCO states (>=80%) - Average variance (p75-p25): ${high_mco_states['p75_p25_spread'].mean():.2f}")
    print(f"Low MCO states (<=20%) - Average variance (p75-p25): ${low_mco_states['p75_p25_spread'].mean():.2f}")
    print(f"High MCO states - Average ratio (p90/p50): {high_mco_states['p90_p50_ratio'].mean():.2f}")
    print(f"Low MCO states - Average ratio (p90/p50): {low_mco_states['p90_p50_ratio'].mean():.2f}")

    return analysis_data

def create_visualizations(data):
    """Create correlation visualizations"""

    plt.style.use('default')
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

    # Scatter plot: MCO % vs P75-P25 Spread
    ax1.scatter(data['Percent of Medicaid Population in MCO'], data['p75_p25_spread'],
                alpha=0.7, s=60, color='steelblue')
    ax1.set_xlabel('MCO Penetration (%)')
    ax1.set_ylabel('Payment Variance (P75-P25 Spread, $)')
    ax1.set_title('MCO Penetration vs Payment Variance (99214)')
    ax1.grid(True, alpha=0.3)

    # Add state labels for extreme points
    for _, row in data.iterrows():
        if row['p75_p25_spread'] > 40 or row['Percent of Medicaid Population in MCO'] < 0.2:
            ax1.annotate(row['state_x'], (row['Percent of Medicaid Population in MCO'], row['p75_p25_spread']),
                        xytext=(5, 5), textcoords='offset points', fontsize=8)

    # Scatter plot: MCO % vs P90/P50 Ratio
    ax2.scatter(data['Percent of Medicaid Population in MCO'], data['p90_p50_ratio'],
                alpha=0.7, s=60, color='darkorange')
    ax2.set_xlabel('MCO Penetration (%)')
    ax2.set_ylabel('Payment Ratio (P90/P50)')
    ax2.set_title('MCO Penetration vs Payment Ratio (99214)')
    ax2.grid(True, alpha=0.3)

    # Box plots: High vs Low MCO states
    high_mco = data[data['Percent of Medicaid Population in MCO'] >= 0.8]['p75_p25_spread']
    low_mco = data[data['Percent of Medicaid Population in MCO'] <= 0.2]['p75_p25_spread']

    ax3.boxplot([high_mco.dropna(), low_mco.dropna()], labels=['High MCO\n(>=80%)', 'Low MCO\n(<=20%)'])
    ax3.set_ylabel('Payment Variance (P75-P25 Spread, $)')
    ax3.set_title('Variance Distribution: High vs Low MCO States')
    ax3.grid(True, alpha=0.3)

    # Histogram of MCO penetration
    ax4.hist(data['Percent of Medicaid Population in MCO'].dropna(), bins=15, alpha=0.7, color='lightgreen', edgecolor='black')
    ax4.set_xlabel('MCO Penetration (%)')
    ax4.set_ylabel('Number of States')
    ax4.set_title('Distribution of MCO Penetration Rates')
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('mco_variance_correlation_analysis.png', dpi=300, bbox_inches='tight')
    print("\n=== VISUALIZATION SAVED ===")
    print("Chart saved as: mco_variance_correlation_analysis.png")

    plt.show()

if __name__ == "__main__":
    # Run the analysis
    analysis_data = analyze_correlation()
    create_visualizations(analysis_data)