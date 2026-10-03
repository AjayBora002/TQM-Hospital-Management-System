# Requirements Traceability

| Requirement | Q07 Feature | Implementation | Test |
|---|---|---|---|
| FR-08 Input Masking | QF-01 | `src/widgets/phone_mask_entry.py` | `test_db.py` — patient phone field |
| FR-09 Dropdown Lists | QF-02 | `src/config.py` + `ttk.Combobox` | `test_db.py` — patient gender/blood group |
| FR-10 Auto-Complete | QF-03 | `src/widgets/autocomplete_entry.py` | `test_db.py::test_04_patient_name_candidates` |
| FR-11 Confirmation Modals | QF-04 | `src/widgets/confirm_dialog.py` | Manual UI test |
| FR-12 Audit Logs | QF-05 | `src/database/db_manager.log_audit()` | `test_db.py::test_08_audit_log_verification` |
| FR-01 Patient Management | Base CRUD | `src/models/patient.py` | `test_db.py::test_03_patient_crud` |
| FR-02 Doctor Management | Base CRUD | `src/models/doctor.py` | `test_db.py::test_02_doctor_crud` |
| FR-03 Appointment Scheduling | Base CRUD | `src/models/appointment.py` | `test_db.py::test_04_appointment_crud` |
| FR-04 Room Management | Base CRUD | `src/models/room.py` | `test_db.py::test_01_room_crud` |
| FR-05 Staff Management | Base CRUD | `src/models/staff.py` | `test_db.py::test_05_staff_crud` |
| FR-06 Medicine Inventory | Base CRUD | `src/models/medicine.py` | `test_db.py::test_06_medicine_inventory` |
| FR-07 Billing | Base CRUD | `src/models/bill.py` | `test_db.py::test_07_billing_calculation` |
| FR-13 Defect Checksheet | SQC Tool | `src/models/audit.py` + `src/views/defects_view.py` | `test_db.py::test_09_defect_checksheet` |
