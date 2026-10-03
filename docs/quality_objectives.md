# Measurable Quality Objectives

## QO-01 — Eliminate Malformed Phone Numbers

**Metric:** Phone entries failing the `+91-XXXXX-XXXXX` format / total phone entries.
**Target:** 0 malformed entries after input masking is applied.
**Measurement:** Defect checksheet — Data Entry category.
**Frequency:** Every testing cycle.
**Responsible Role:** Development team.

## QO-02 — Eliminate Categorical Field Typos

**Metric:** Free-text entry errors in Gender, Blood Group, Department, and Status fields.
**Target:** 0 typos after read-only dropdown lists are applied.
**Measurement:** Defect checksheet — Validation category.
**Frequency:** Every testing cycle.

## QO-03 — Prevent Duplicate Patient Records

**Metric:** Duplicate patient records reaching the database.
**Target:** 0 duplicates after auto-complete is active.
**Measurement:** Defect checksheet — Data Entry category.
**Frequency:** Every testing cycle.

## QO-04 — Prevent Accidental Record Deletion

**Metric:** Unintended deletions confirmed without user prompt.
**Target:** 0 after confirmation modals are applied.
**Measurement:** Defect checksheet — UI category.
**Frequency:** Every testing cycle.

## QO-05 — Audit Coverage

**Metric:** Database write operations that have a corresponding audit log entry.
**Target:** 100%.
**Required fields:** table_name, record_id, action, description, logged_at.
**Frequency:** Every release cycle.

## QO-06 — Module Test Coverage

**Metric:** Critical data-access models with independent unit tests.
**Target:** 100% of critical models before final submission.

## QO-07 — Billing Calculation Accuracy

**Metric:** Bills where total_amount ≠ room_charges + consultation_charges + medicine_charges.
**Target:** 0.

## QO-08 — Defect Traceability

**Metric:** Logged defects with category, severity, and status information.
**Target:** 100%.

These objectives will be reviewed using actual test evidence. No fabricated performance results are used.
