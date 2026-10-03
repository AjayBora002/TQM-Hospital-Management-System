# Software Requirements Specification

## 1. Introduction

The Hospital Management System is a software application for managing hospital records and workflows while applying TQM principles with a focus on improving data accuracy.

## 2. Scope

### In Scope

- Patient registration and records
- Doctor roster and specialties
- Appointment scheduling
- Room and ward management
- Staff administration
- Pharmacy and medicine inventory
- Billing and invoicing
- Input masking
- Dropdown validation
- Auto-complete search
- Confirmation modals
- Audit logging
- Defect checksheet

### Out of Scope for the Initial Version

- Online patient portal
- Biometric integration
- Insurance and third-party billing gateway
- Mobile application
- Medical imaging systems

These may be considered separately only if required later.

## 3. Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | The system shall allow authorized users to register and manage patient records. |
| FR-02 | The system shall allow authorized users to manage doctor and department records. |
| FR-03 | The system shall allow appointment scheduling linking patients and doctors. |
| FR-04 | The system shall manage room availability and occupancy status. |
| FR-05 | The system shall manage staff records with role and shift assignments. |
| FR-06 | The system shall track medicine inventory and flag low stock. |
| FR-07 | The system shall generate itemized bills and track payment status. |
| FR-08 | The system shall enforce phone number formatting through input masking. |
| FR-09 | The system shall restrict categorical fields to validated dropdown lists. |
| FR-10 | The system shall provide auto-complete suggestions during patient search. |
| FR-11 | The system shall require explicit confirmation before update or delete operations. |
| FR-12 | The system shall maintain an immutable audit trail for all INSERT, UPDATE, and DELETE events. |
| FR-13 | The system shall allow staff to log software defects in a checksheet for SQC analysis. |

## 4. Non-Functional Requirements

- Usability: all mandatory fields should be clearly labeled with appropriate input controls.
- Reliability: validation failures and database errors should be handled without uncontrolled crashes.
- Maintainability: models and views should have separate responsibilities with no cross-layer SQL.
- Traceability: every data change must produce a corresponding audit record.
- Data integrity: database constraints and application validation must work together.
- Testability: all data-access models must be independently testable without the GUI.

## 5. Assigned Quality Goal

**Q07 — Improve Data Accuracy**

The five required quality-goal features are:

1. Input Masking
2. Dropdown Lists
3. Auto-Complete
4. Confirmation Modals
5. Audit Logs
