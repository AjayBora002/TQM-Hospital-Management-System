# Quality Features — Q07 Improve Data Accuracy

| ID | Feature | Quality Purpose | Measurement |
|---|---|---|---|
| QF-01 | Input Masking | Prevent malformed phone entries | Phone format error rate |
| QF-02 | Dropdown Lists | Prevent categorical field typos | Invalid entry rejection rate |
| QF-03 | Auto-Complete | Prevent duplicate patient records | Duplicate patient rate |
| QF-04 | Confirmation Modals | Prevent accidental record destruction | Unintended delete rate |
| QF-05 | Audit Logs | Ensure all changes are traceable | Audit coverage rate |

## QF-01 Input Masking

Phone numbers are auto-formatted to `+91-XXXXX-XXXXX` as the user types. Non-numeric keystrokes are rejected before reaching the database. The widget is written once in `src/widgets/phone_mask_entry.py` and reused in the Patients, Doctors, and Staff screens.

## QF-02 Dropdown Lists

All categorical fields — Gender, Blood Group, Department, Appointment Status, Room Type, Room Status, Staff Role, Staff Shift, Medicine Category, Payment Method, Payment Status — use read-only `ttk.Combobox` widgets bound to fixed lists defined in `src/config.py`. Free-text entry is not possible.

## QF-03 Auto-Complete

The `AutocompleteEntry` widget in `src/widgets/autocomplete_entry.py` queries existing patient names as the user types and displays matching suggestions. This surfaces an existing record before a new one is created, preventing duplicate patient profiles.

## QF-04 Confirmation Modals

Every Update and Delete operation across all eight data-entry modules triggers a `messagebox.askyesno` confirmation dialog before the database write is executed. The widget is written once in `src/widgets/confirm_dialog.py`.

## QF-05 Audit Logs

The `log_audit()` function in `src/database/db_manager.py` is called inside every model write function. It records the table name, record ID, action type (INSERT, UPDATE, DELETE), a description, and a timestamp. The Audit Log tab provides a read-only view of the complete history.
