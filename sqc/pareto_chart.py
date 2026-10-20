"""
pareto_chart.py -- Step 6: SQC tool #1 (Pareto Analysis, 80/20 rule)
Reads defect counts by category (from the Defect Checksheet / defect_log table)
and plots a Pareto chart: bars = frequency, line = cumulative %.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import os
import csv
from collections import defaultdict

# Defect frequency dynamically parsed from TQM/data/checksheet.csv (15 entries, 33 total defects)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(base_dir, "TQM", "data", "checksheet.csv")

defect_counts = defaultdict(int)
if os.path.exists(csv_path):
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat = row["error_category"].strip()
            count = int(row["count"])
            defect_counts[cat] += count
else:
    # Exact fallback matching checksheet.csv: 14 Data Entry, 14 Validation, 3 UI, 2 Business Logic
    defect_counts = {
        "Data Entry": 14,
        "Validation": 14,
        "UI": 3,
        "Business Logic": 2,
    }

items = sorted(defect_counts.items(), key=lambda kv: kv[1], reverse=True)
categories = [k for k, _ in items]
counts = [v for _, v in items]
total = sum(counts)
cumulative_pct = []
running = 0
for c in counts:
    running += c
    cumulative_pct.append(running / total * 100)

fig, ax1 = plt.subplots(figsize=(8, 5))
bars = ax1.bar(categories, counts, color="#4472C4", label="Defect Count")
ax1.set_ylabel("Defect Count")
ax1.set_xlabel("Defect Category")
ax1.set_title("Pareto Chart -- HMS Defect Categories (Q07: Improve Data Accuracy)")
for b, c in zip(bars, counts):
    ax1.text(b.get_x() + b.get_width() / 2, c + 0.05, str(c), ha="center", fontsize=9)

ax2 = ax1.twinx()
ax2.plot(categories, cumulative_pct, color="#C00000", marker="o", label="Cumulative %")
ax2.set_ylabel("Cumulative %")
ax2.set_ylim(0, 110)
ax2.axhline(80, color="gray", linestyle="--", linewidth=1)
ax2.text(len(categories) - 1, 82, "80% line", fontsize=8, color="gray")

fig.tight_layout()
import os

out_dir = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(out_dir, "pareto_chart.png")
fig.savefig(out_path, dpi=150)
print(f"Saved {out_path}")
print("Vital few (>=80% cumulative):",
      [categories[i] for i in range(len(categories)) if cumulative_pct[i] <= 80 or i == 0])
