"""
fishbone_diagram.py -- Step 6: SQC tool #2 (Ishikawa / Fishbone diagram)
Root-cause categories for the top Pareto defect category: "Data Entry" accuracy issues
in the Hospital Management System (Q07: Improve Data Accuracy).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(11, 6.5))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis("off")

# Spine
ax.plot([1, 8.7], [3, 3], color="black", linewidth=2)
ax.annotate("", xy=(9.6, 3), xytext=(8.7, 3),
            arrowprops=dict(arrowstyle="-|>", color="black", linewidth=2))
ax.text(9.7, 3, "Data\nInaccuracy", fontsize=12, fontweight="bold", va="center")

causes = {
    "People":       ["Front-desk fatigue / rushing", "Insufficient training on forms", "No double-entry check"],
    "Process":       ["No standardized entry SOP", "No search-before-add step", "No approval for edits"],
    "Software Code": ["Free-text fields (pre-fix)", "No input masking (pre-fix)", "No validation regex (pre-fix)"],
    "Infrastructure": ["Old low-res monitors (typos)", "Slow DB causing rushed entry", "No backup/versioning"],
}

positions = [
    ("People", 2.0, "up"),
    ("Process", 5.0, "up"),
    ("Software Code", 2.0, "down"),
    ("Infrastructure", 5.0, "down"),
]

for label, x, direction in positions:
    y_end = 5.0 if direction == "up" else 1.0
    ax.plot([x, x + 1.6], [3, y_end], color="black", linewidth=1.5)
    label_y = y_end + 0.25 if direction == "up" else y_end - 0.25
    ax.text(x + 1.65, label_y, label, fontsize=11, fontweight="bold",
            color="#1F4E78", va="center")

    sub_items = causes[label]
    for i, item in enumerate(sub_items):
        frac = (i + 1) / (len(sub_items) + 1)
        bx = x + 0.2 + frac * 1.3
        by_line_start = 3 + (y_end - 3) * frac
        by = by_line_start + (0.35 if direction == "up" else -0.35)
        ax.plot([bx, bx - 0.35], [by_line_start, by], color="gray", linewidth=1)
        ax.text(bx - 0.4, by, item, fontsize=8.5, ha="right", va="center")

ax.set_title("Ishikawa (Fishbone) Diagram -- Root Causes of Data Inaccuracy in HMS",
              fontsize=13, fontweight="bold")

fig.tight_layout()
import os

out_dir = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(out_dir, "fishbone_diagram.png")
fig.savefig(out_path, dpi=150)
print(f"Saved {out_path}")
