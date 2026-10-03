# Critical to Quality (CTQ) Tree

## Customer Need: Accurate Hospital Records

```text
Accurate Hospital Records
│
├── Correct Patient Data
│   ├── Phone number is in standard format
│   ├── Blood group, gender, and address are correctly classified
│   └── Duplicate patient profiles are prevented
│
├── Safe Record Operations
│   ├── Update operations require explicit confirmation
│   ├── Delete operations require explicit confirmation
│   └── Every change is logged with timestamp and user action
│
└── Data Traceability
    ├── All INSERTs are recorded in audit log
    ├── All UPDATEs are recorded in audit log
    └── All DELETEs are recorded in audit log
```

## Measurable CTQs

| CTQ | Measure | Target |
|---|---|---|
| Phone accuracy | Malformed phone entries per 100 submissions | 0 |
| Field accuracy | Categorical typos per 100 submissions | 0 |
| Duplicate prevention | Duplicate patient records per 100 registrations | 0 |
| Deletion safety | Unconfirmed deletes | 0 |
| Audit coverage | Write operations without an audit record | 0 |
