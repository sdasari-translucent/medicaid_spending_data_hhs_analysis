import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Data from Mimilabs analysis
ma_data = {
    'Independent': {'count': 1127, 'mean': 96.91, 'median': 82.01, 'min': 5.05, 'max': 374.99},
    'System-Affiliated': {'count': 1742, 'mean': 86.44, 'median': 76.00, 'min': 5.05, 'max': 438.32}
}

md_data = {
    'Independent': {'count': 365, 'mean': 88.05, 'median': 97.24, 'min': 6.97, 'max': 138.62},
    'System-Affiliated': {'count': 259, 'mean': 76.93, 'median': 78.39, 'min': 8.99, 'max': 178.50}
}

# Create visualization
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('Medicaid 99214 Payment Distributions: System-Affiliated vs Independent Providers',
             fontsize=16, fontweight='bold')

# Massachusetts summary
ma_stats = pd.DataFrame(ma_data).T
ax1.bar(ma_stats.index, ma_stats['mean'], alpha=0.7, color=['#2E8B57', '#4169E1'])
ax1.set_title('Massachusetts - Mean Payment by Provider Type')
ax1.set_ylabel('Mean Payment ($)')
ax1.set_ylim(0, 110)
for i, (idx, row) in enumerate(ma_stats.iterrows()):
    ax1.text(i, row['mean'] + 2, f"${row['mean']:.0f}\n(n={row['count']:,})",
             ha='center', va='bottom', fontsize=10)

# Maryland summary
md_stats = pd.DataFrame(md_data).T
ax2.bar(md_stats.index, md_stats['mean'], alpha=0.7, color=['#2E8B57', '#4169E1'])
ax2.set_title('Maryland - Mean Payment by Provider Type')
ax2.set_ylabel('Mean Payment ($)')
ax2.set_ylim(0, 110)
for i, (idx, row) in enumerate(md_stats.iterrows()):
    ax2.text(i, row['mean'] + 2, f"${row['mean']:.0f}\n(n={row['count']:,})",
             ha='center', va='bottom', fontsize=10)

# Combined comparison chart
states_data = {
    'MA Independent': ma_data['Independent'],
    'MA System': ma_data['System-Affiliated'],
    'MD Independent': md_data['Independent'],
    'MD System': md_data['System-Affiliated']
}

ax3.bar(range(len(states_data)), [d['mean'] for d in states_data.values()],
        alpha=0.7, color=['#2E8B57', '#4169E1', '#2E8B57', '#4169E1'])
ax3.set_title('Cross-State Comparison: Mean Payments')
ax3.set_ylabel('Mean Payment ($)')
ax3.set_xticks(range(len(states_data)))
ax3.set_xticklabels(list(states_data.keys()), rotation=45, ha='right')

for i, (key, data) in enumerate(states_data.items()):
    ax3.text(i, data['mean'] + 2, f"${data['mean']:.0f}", ha='center', va='bottom')

# Payment range comparison
ranges = []
labels = []
for state, state_data in [('MA', ma_data), ('MD', md_data)]:
    for ptype, data in state_data.items():
        ranges.append([data['min'], data['max']])
        labels.append(f"{state} {ptype}")

ax4.barh(range(len(ranges)), [r[1] - r[0] for r in ranges],
         left=[r[0] for r in ranges], alpha=0.7, color=['#2E8B57', '#4169E1'] * 2)
ax4.set_title('Payment Range by Provider Type')
ax4.set_xlabel('Payment Amount ($)')
ax4.set_yticks(range(len(labels)))
ax4.set_yticklabels(labels)

plt.tight_layout()
plt.savefig('ma_md_provider_payment_analysis.png', dpi=300, bbox_inches='tight')
# plt.show()  # Comment out interactive display

# Summary statistics table
print("MEDICAID 99214 PAYMENT ANALYSIS SUMMARY")
print("=" * 50)
print("\nMassachusetts:")
print(f"Independent Providers: n={ma_data['Independent']['count']:,}, Mean=${ma_data['Independent']['mean']:.2f}, Median=${ma_data['Independent']['median']:.2f}")
print(f"System-Affiliated: n={ma_data['System-Affiliated']['count']:,}, Mean=${ma_data['System-Affiliated']['mean']:.2f}, Median=${ma_data['System-Affiliated']['median']:.2f}")
print(f"Independent vs System Premium: +${ma_data['Independent']['mean'] - ma_data['System-Affiliated']['mean']:.2f} ({((ma_data['Independent']['mean']/ma_data['System-Affiliated']['mean'])-1)*100:.1f}%)")

print("\nMaryland:")
print(f"Independent Providers: n={md_data['Independent']['count']:,}, Mean=${md_data['Independent']['mean']:.2f}, Median=${md_data['Independent']['median']:.2f}")
print(f"System-Affiliated: n={md_data['System-Affiliated']['count']:,}, Mean=${md_data['System-Affiliated']['mean']:.2f}, Median=${md_data['System-Affiliated']['median']:.2f}")
print(f"Independent vs System Premium: +${md_data['Independent']['mean'] - md_data['System-Affiliated']['mean']:.2f} ({((md_data['Independent']['mean']/md_data['System-Affiliated']['mean'])-1)*100:.1f}%)")

print("\nKEY FINDING: Independent providers receive HIGHER payments than system-affiliated providers")
print("This contradicts the market power hypothesis - systems may have negotiated LOWER rates or")
print("face different case mix/coding patterns than independent providers.")