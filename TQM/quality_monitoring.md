# Quality Monitoring

## Monitoring Sources

| Source | What It Measures |
|---|---|
| Audit Log (`audit_log` table) | Every INSERT, UPDATE, DELETE with table, record, and timestamp |
| Defect Checksheet (`defect_log` table) | Defects by category, description, and severity |
| Pareto Chart (`sqc/pareto_chart.png`) | Which defect categories drive 80% of errors |
| Fishbone Diagram (`sqc/fishbone_diagram.png`) | Root causes of data inaccuracy |
| Unit Test Results (`tests/test_db.py`) | Whether all data-access models behave correctly |

## Dashboard Metrics

The Dashboard tab displays live counts from the database:

- Total registered patients
- Total doctors on roster
- Scheduled appointments today
- Available rooms
- Pharmacy items at or below reorder level
- Unpaid bills
- Total audit log entries
- Total logged defects

## How to Generate SQC Evidence

```bash
# Pareto chart from defect_log table
python sqc/pareto_chart.py

# Fishbone diagram
python sqc/fishbone_diagram.py

# FMEA Excel workbook
python docs/build_fmea.py

# Unit tests
python tests/test_db.py
```

## Monitoring Rule

Quality monitoring should be based on actual data recorded in the running system. No monitoring output should be fabricated.
