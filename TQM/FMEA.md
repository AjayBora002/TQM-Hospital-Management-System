# FMEA — Initial Risk Analysis

**RPN = Severity × Occurrence × Detection**

Ratings will be reviewed using actual project and test evidence.

| Process | Failure Mode | Effect | Cause | Current/Planned Control | S | O | D | RPN | Action |
|---|---|---|---|---|---:|---:|---:|---:|---|
| Patient Registration | Malformed phone number saved | Emergency contact unreachable | Free-text phone field | Input Masking (`PhoneMaskEntry`) | 8 | 7 | 8 | 448 | Enforce `+91-XXXXX-XXXXX` format |
| Patient Registration | Incorrect blood group saved | Clinical risk | Free-text categorical field | Dropdown (read-only Combobox) | 9 | 6 | 7 | 378 | Bind field to fixed blood group list |
| Patient Registration | Duplicate patient created | Fragmented medical history | No pre-check before save | Auto-Complete search | 7 | 5 | 6 | 210 | Surface existing matches before submission |
| Record Management | Active record accidentally deleted | Data loss | No confirmation step | Confirmation Modal (`messagebox.askyesno`) | 9 | 4 | 8 | 288 | Block delete without explicit confirmation |
| Record Management | Change made without traceability | Untraceable data error | No change logging | Audit Logging (`log_audit()`) | 8 | 5 | 9 | 360 | Log all INSERT, UPDATE, DELETE with timestamp |
| Appointment Booking | Appointment for wrong patient | Clinical scheduling error | Free-text patient search | Auto-Complete patient search | 8 | 4 | 6 | 192 | Restrict patient selection to registered list |
| Billing | Incorrect total amount | Financial error | Manual charge entry | Auto-calculation (`total = room + consult + medicine`) | 7 | 5 | 5 | 175 | Compute total automatically, no manual override |

## Note

These are **initial planning ratings**, not measured production results. They must be reviewed and updated when actual testing and defect data are available.
