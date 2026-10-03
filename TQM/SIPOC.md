# SIPOC — Hospital Management Process

| SIPOC Element | Hospital Management System |
|---|---|
| Suppliers | Patients, Doctors, Pharmacists, Receptionists, Hospital Administration |
| Inputs | Patient data, doctor details, appointment requests, room availability, medicine stock, billing charges |
| Process | Register → Validate → Schedule → Allocate → Dispense → Bill → Log |
| Outputs | Patient records, appointment confirmations, room assignments, pharmacy stock status, invoices, audit trail |
| Customers | Hospital Administration, Attending Doctors, Billing Staff, Pharmacists, Hospital Management |

## Core Process

```text
Supplier
  ↓
Input
  ↓
Hospital Process
  ↓
Q07 Validation / Control
  ↓
Output
  ↓
Customer
```

The SIPOC shows that every input passes through Q07 controls (masking, dropdowns, auto-complete, confirmation, audit) before reaching the database output layer.
