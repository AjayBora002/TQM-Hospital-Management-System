# Process Map

## Patient Intake Process

```text
Patient Arrives at Reception
    ↓
Receptionist Opens Patients Tab
    ↓
Begins Typing Patient Name
    ↓
Auto-Complete: Existing Match Found?
    ├── YES → Select existing patient, update if needed (Confirmation Modal)
    └── NO  → Proceed to new registration
                ↓
            Enter Phone Number (Input Masking enforces format)
                ↓
            Select Gender, Blood Group (Dropdown — read-only)
                ↓
            Enter Date of Birth, Address
                ↓
            Click Add Patient
                ↓
            Database INSERT + Audit Log Record
```

## Appointment Booking Process

```text
Receptionist Opens Appointments Tab
    ↓
Type Patient Name → Auto-Complete Suggests Match
    ↓
Select Consulting Doctor from Dropdown
    ↓
Enter Appointment Date and Time
    ↓
Select Status (Scheduled / Completed / Cancelled) from Dropdown
    ↓
Click Book Appointment
    ↓
Database INSERT + Audit Log Record
```

## Billing Process

```text
Billing Staff Opens Billing Tab
    ↓
Select Patient via Auto-Complete
    ↓
Enter Room Charges, Consultation Fee, Medicine Charges
    ↓
System Auto-Calculates Total
    ↓
Select Payment Method and Status from Dropdown
    ↓
Click Generate Bill
    ↓
Database INSERT + Audit Log Record
```

## Record Modification Process

```text
Staff Selects Existing Record
    ↓
Modifies Required Fields
    ↓
Clicks Update or Delete
    ↓
Confirmation Modal: "Are you sure?"
    ├── NO  → Operation cancelled, no database change
    └── YES → Database UPDATE/DELETE + Audit Log Record
```
