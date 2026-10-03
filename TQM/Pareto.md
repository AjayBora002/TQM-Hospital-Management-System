# Pareto Analysis

Pareto analysis will be generated from the actual defect checksheet.

## Planned Input

`src/database/hms.db` — `defect_log` table, exported via `sqc/pareto_chart.py`

## Planned Categories

- Data Entry
- Validation
- UI
- Database
- Business Logic
- Pharmacy / Stock
- Billing
- Other

## Method

1. Count defects by category from the defect_log table.
2. Sort categories by frequency (highest to lowest).
3. Calculate cumulative percentage.
4. Generate a Pareto chart using Python and Matplotlib.
5. Identify categories contributing to 80% of observed defects.
6. Use the result to prioritize corrective action.

## Script

```bash
python sqc/pareto_chart.py
```

Output: `sqc/pareto_chart.png`

No final Pareto conclusion should be written until actual defect data has been collected from testing.
