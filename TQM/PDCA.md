# PDCA Continuous Improvement

## PLAN

- Identify the data accuracy problem.
- Define a measurable quality objective.
- Select the relevant Q07 control.
- Plan and implement the corrective widget or validation.

## DO

- Implement input masking, dropdown, auto-complete, confirmation modal, or audit log.
- Log defects found during testing in the Defect Checksheet tab.
- Run module tests after each change.

## CHECK

- Compare defect rates before and after the Q07 control is applied.
- Review the audit log to confirm all changes are captured.
- Run `python tests/test_db.py` to verify no regression.
- Generate Pareto chart to confirm the targeted defect category has reduced.

## ACT

- Standardize successful Q07 controls as the default for all new forms.
- Update validation rules if new edge cases are found.
- Begin the next improvement cycle for any remaining defect categories.

## Example — Cycle 1

**Problem:** Phone number field accepts arbitrary text and symbols.

**Plan:** Apply `PhoneMaskEntry` widget enforcing `+91-XXXXX-XXXXX` format.

**Do:** Implemented `src/widgets/phone_mask_entry.py` with keystroke filtering. Applied to Patients, Doctors, and Staff forms.

**Check:** Tested 20 patient registrations — phone format errors dropped to 0. Defect checksheet confirmed no new Data Entry category entries for phone format.

**Act:** Established `PhoneMaskEntry` as the mandatory widget for all phone fields in any future module.
