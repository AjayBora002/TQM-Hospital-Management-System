# Error Prevention

## Approach

Errors are prevented at the point of entry, not corrected after the fact (Poka-Yoke principle).

## Prevention Controls

| # | Control | Where Applied | What It Prevents |
|---|---|---|---|
| 1 | Input Masking | Phone fields in Patients, Doctors, Staff | Malformed phone numbers |
| 2 | Read-Only Dropdowns | Gender, Blood Group, Department, Status, Role, Shift, Category fields | Categorical typos and inconsistencies |
| 3 | Auto-Complete | Patient search in Appointments, Billing | Duplicate patient record creation |
| 4 | Confirmation Modal | Update and Delete buttons in all 8 modules | Accidental record destruction |
| 5 | Required Field Validation | All mandatory fields before database insert | Empty or null critical data |
| 6 | Date Format Validation | DOB, Appointment Date fields | Invalid calendar dates |
| 7 | Non-Negative Validation | Billing charge fields | Negative or zero financial values |

## Design Rule

Every Q07 control is implemented as a reusable module in `src/widgets/` and applied across all relevant screens, so the prevention logic is written once and cannot be accidentally omitted from a new form.
