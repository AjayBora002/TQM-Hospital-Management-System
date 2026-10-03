# Testing Strategy

Testing is a component of the assigned Q07 — Improve Data Accuracy quality goal.

## Testing Levels

### Unit / Module Testing

All data-access models (patient, doctor, appointment, room, staff, medicine, bill, audit) are tested independently without the GUI using a throwaway SQLite database.

### Validation Testing

Every Q07 input constraint is tested with both valid and invalid inputs to confirm acceptance and rejection behaviour.

### Integration Testing

Interactions between the widget layer, models, and database are tested end-to-end.

### Negative Testing

Invalid inputs and boundary conditions are deliberately tested.

### Regression Testing

Previously fixed defects are retested after relevant code changes.

## Test Record

Each test should record:

- Test ID
- Requirement ID
- Module
- Input
- Expected result
- Actual result
- Status
- Defect ID if applicable

## Test Areas

| Test Area | Example |
|---|---|
| Input Masking | Non-digit character rejected in phone field |
| Dropdown Lists | Blood group field rejects free text |
| Auto-Complete | Partial patient name returns matching suggestions |
| Confirmation Modal | Delete without confirmation is blocked |
| Audit Logging | Every INSERT, UPDATE, DELETE generates an audit record |
| Patient CRUD | Add, update, and delete patient round-trip |
| Appointment | Doctor-patient linking and status updates |
| Billing | Total equals sum of room + consultation + medicine charges |
| Pharmacy | Stock below reorder level flagged correctly |

## How to Run

```bash
python tests/test_db.py
```

Expected: all tests pass.
