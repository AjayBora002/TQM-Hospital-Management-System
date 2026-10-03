# Process Control

## Controlled Process Points

| Step | Control | Mechanism |
|---|---|---|
| Phone number entry | Format enforcement | `PhoneMaskEntry` auto-formats; rejects non-digits |
| Categorical field entry | Value restriction | `ttk.Combobox(state="readonly")` bound to fixed list |
| Patient search / new record | Duplicate surface | `AutocompleteEntry` shows matches as user types |
| Update operation | Confirmation required | `confirm_dialog.confirm_update()` must return True |
| Delete operation | Confirmation required | `confirm_dialog.confirm_delete()` must return True |
| Every database write | Audit recording | `log_audit()` called inside every model write function |

## Control Monitoring

The Defect Checksheet tab allows quality auditors to log any defects that bypass or circumvent these controls. Logged defects feed the Pareto analysis, which identifies which control points need reinforcement.

## Process Boundary Rule

- The UI layer is responsible for widget-level controls (masking, dropdown, auto-complete, confirmation).
- The model layer is responsible for validation assertions and audit recording.
- Both layers must independently enforce their respective controls so that a failure in one does not silently bypass quality constraints.
