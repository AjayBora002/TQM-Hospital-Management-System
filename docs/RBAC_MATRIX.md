# Enterprise Role-Based Access Control (RBAC) Matrix
**Hospital Management System (HMS) | BBAT104 Course Project**  
**Quality Goal:** Q07 - Improve Data Accuracy | **Author:** Ajay Bora (CSE-B)

---

## 1. Executive Summary & Security Model

The Hospital Management System implements a multi-tier, zero-trust security architecture enforcing **Server-Side Role-Based Access Control (RBAC)** on every REST API route and database transaction. 

### Core Architectural Principles:
1. **Server-Side Enforcement**: Permissions are evaluated on the backend using the `@require_permission(module, action)` decorator in `src/auth/permissions.py`. Frontend navigation hiding and field disabling are strictly for user experience; unauthorized requests receive an immediate `403 Forbidden` response.
2. **Audit Logging of Access Violations**: Every `403 Forbidden` attempt and security violation is logged immutably into `access_control` and the SQLite audit log with client IP, timestamp, role, target module, and action.
3. **Session Security & Timeout**: Sessions expire automatically after **15 minutes of user inactivity** with a proactive 2-minute client-side warning banner. 
4. **Brute-Force Protection**: After **5 consecutive failed login attempts**, the account is temporarily locked for 15 minutes, recorded in the `login_attempts` audit table.
5. **No Universal Fallbacks**: Unauthenticated requests to `/api/auth/current` or `/api/auth/me` return `401 Unauthorized` (no silent Admin fallback).
6. **Hard Clinical Restrictions**: Administrators have configuration and user management rights but are strictly barred from creating, editing, or deleting patient medical/clinical records (`create`, `edit`, `delete` on `clinical`).
7. **Principle of Least Privilege**: 
   - Cashiers and Billing Officers cannot access clinical notes or medical histories.
   - Receptionists cannot read or modify clinical consultations (SOAP notes).
   - Lab Technicians and Radiologists can report and verify diagnostics but cannot modify doctor prescriptions.
   - Nurses can record vitals and execute administered clinical orders but cannot create new consultation encounters or physician diagnosis entries.

---

## 2. 21 Stakeholder Roles & Access Rights Matrix

Legend:
- `V`: **View / Read**
- `C`: **Create**
- `E`: **Edit / Update**
- `D`: **Delete**
- `A`: **Approve / Verify**
- `-`: **No Access (HTTP 403 Forbidden)**

| # | Stakeholder Role | Front Office | Clinical Care | Diagnostics (LIS/Blood) | Inpatient (IPD) | Pharmacy & Supply | Finance & Billing | Support Services | People & HR | Quality & Governance | System Admin | Patient Portal |
|---|------------------|:------------:|:-------------:|:-----------------------:|:---------------:|:-----------------:|:-----------------:|:----------------:|:-----------:|:--------------------:|:------------:|:--------------:|
| 1 | **Administrator** | V, C, E, D | V *(Read Only)* | V, C, E, D | V, C, E, D | V, C, E, D | V, C, E, D | V, C, E, D | V, C, E, D | V, C, E, D | **V, C, E, D, A** | - |
| 2 | **Hospital Manager** | V | V | V | V | V, A | V, A | V, A | V, A | **V, A** | V | - |
| 3 | **Doctor** | V, C | **V, C, E** | V, C | V, C, E | V, C | V | V | V | V, C | - | - |
| 4 | **Nurse** | V | V, E | V | **V, C, E** | V | V | V, E | V | V, C | - | - |
| 5 | **Ward Manager** | V | V | - | **V, C, E, A** | V | V | V, E | V | V | - | - |
| 6 | **Receptionist** | **V, C, E** | - | - | V, C | - | V, C | V | - | - | - | - |
| 7 | **Lab Technician** | - | V | **V, C, E, A** | - | - | - | - | - | V | - | - |
| 8 | **Pharmacist** | - | V | - | - | **V, C, E, A** | V, C | - | - | V | - | - |
| 9 | **Cashier** | V | - | - | V | V | **V, C, E** | - | - | - | - | - |
| 10 | **Patient** | V, C | - | - | - | - | V | - | - | - | - | **V, C** |
| 11 | **Quality Manager** | V | V | V | V | V | V | V | V | **V, C, E, A** | V | - |
| 12 | **Radiologist** | - | **V, C, E, A** | V | - | - | - | - | - | V | - | - |
| 13 | **OT Manager** | - | **V, C, E, A** | - | V | V | - | V | V | V | - | - |
| 14 | **Blood Bank Tech** | - | V | **V, C, E, A** | - | - | - | - | - | V | - | - |
| 15 | **Housekeeping Sup.**| - | - | - | V, E | - | - | **V, C, E, A** | V | V | - | - |
| 16 | **Biomedical Engineer**| - | - | - | - | V | - | **V, C, E, A** | - | V | - | - |
| 17 | **HR Manager** | - | - | - | - | - | - | V | **V, C, E, A** | V | - | - |
| 18 | **Store Manager** | - | - | - | - | **V, C, E, A** | V | V | - | V | - | - |
| 19 | **Insurance Desk** | V | - | - | V | - | **V, C, E, A** | - | - | V | - | - |
| 20 | **Ambulance Disp.** | V | - | - | - | - | - | **V, C, E, A** | - | V | - | - |
| 21 | **Dietitian** | - | V | - | V | - | - | **V, C, E, A** | - | V | - | - |

---

## 3. Row-Level Security (RLS) & Compartmentalization

In addition to modular permissions, the following data-isolation rules are enforced in the API query layers:

1. **Patient Data Isolation**:
   - When authenticated as a `Patient`, database queries automatically filter records by `session["patient_id"]` or linked user UHID. Patients can only query their own appointments, invoices, prescriptions, and verified/released laboratory reports. Unreleased preliminary lab results remain invisible.
2. **Doctor Patient Scoping & Break-Glass Protocol**:
   - Under standard operations, Doctors can view and update records for patients actively assigned to their consultations, OPD tokens, surgical lists, or inpatient beds.
   - For emergency resuscitation or cross-department consultation, a **Break-Glass Access** mechanism requires the doctor to supply a mandatory clinical justification string. The break-glass invocation is permanently logged in the audit trail with an alert flag.
3. **Nursing Station Ward Scoping**:
   - Nurses can only access bed boards, medication administration records (MAR), and clinical orders for patients admitted to their assigned clinical department or ward.
4. **Cashier vs. Clinical Separation**:
   - Billing personnel can query line items, procedure codes, diagnostic billing amounts, and pharmacy pricing, but the API suppresses clinical SOAP notes, psychiatric evaluations, and sensitive diagnosis strings.

---

## 4. Verification & Testing Evidence

The RBAC implementation is validated by automated test suites in `tests/test_rbac_matrix.py`:
- `test_unauthenticated_requests_fail_with_401`: Verifies that requests without valid session tokens receive HTTP 401 across endpoints.
- `test_complete_21_role_matrix_coverage`: Iterates through all 21 stakeholder personas, asserting that each role receives HTTP 403 on at least 3 unauthorized endpoints while successfully accessing authorized endpoints (HTTP 200).
- `test_admin_clinical_restriction`: Ensures administrators cannot post new consultations or modify clinical encounters.
- `test_audit_logging_on_forbidden_access`: Asserts that security rejections write an audit entry with `[FORBIDDEN_ACCESS]` details.

