# Fishbone Analysis

## Problem Statement

**Inaccurate patient and clinical data in the Hospital Management System**

## Initial Cause Categories

### People

- Receptionist fatigue during peak patient intake hours
- Incomplete training on data entry procedures
- Rushed entry during emergency admissions
- Lack of awareness of duplicate patient risk

### Process

- No standardized phone number format enforced
- No confirmation step before deleting or overwriting records
- No pre-add duplicate check required before patient registration
- No change logging required by the existing process

### Software Code

- Open free-text entry fields for phone, gender, and blood group
- No input masking applied on phone number widget
- No read-only constraint on categorical dropdowns
- No auto-complete to surface existing patients before new record creation
- No confirmation dialog before destructive database operations

### Database

- No format-level constraint on phone column
- Categorical fields stored as unconstrained TEXT
- No unique constraint preventing same-name duplicate patients

### Infrastructure

- Small screen resolution causing field label misreads
- Network timeouts causing incomplete form submissions

### Measurement

- Data entry errors not logged systematically
- No defect checksheet to track and categorize entry failures
- No audit trail to detect when records were changed incorrectly

Actual root causes will be updated using evidence from the defect checksheet and test results.
