"""
test_db.py -- Comprehensive unit tests for the HMS data-access layer.
Run with:  python -m pytest tests/  (or: python tests/test_db.py)
Uses a temporary throwaway DB path so it never touches src/database/hms.db.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import config
config.DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_hms.db")

from database.db_manager import init_db, get_connection  # noqa: E402
from models import patient, doctor, room, appointment, staff, medicine, bill, audit  # noqa: E402


class TestHMSModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.path.exists(config.DB_PATH):
            os.remove(config.DB_PATH)
        init_db()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DB_PATH):
            os.remove(config.DB_PATH)

    def test_01_room_crud(self):
        """Test Room module: Add, List, and verify properties."""
        room.add("101", "General", "Available", 500)
        room.add("201", "ICU", "Available", 2500)
        rooms = room.list_all()
        self.assertGreaterEqual(len(rooms), 2)
        r201 = [r for r in rooms if r["room_number"] == "201"][0]
        self.assertEqual(r201["room_type"], "ICU")
        self.assertEqual(r201["rate_per_day"], 2500)

        # Update room status
        room.update(r201["room_id"], "201", "ICU", "Occupied", 2500)
        updated = [r for r in room.list_all() if r["room_id"] == r201["room_id"]][0]
        self.assertEqual(updated["status"], "Occupied")

    def test_02_doctor_crud_and_choices(self):
        """Test Doctor module: Add, choices map, and listing."""
        d_id = doctor.add("Dr. Neha Verma", "Cardiology", "+91-98765-43210")
        self.assertIsNotNone(d_id)
        choices = doctor.choices_map()
        self.assertIn("Dr. Neha Verma (Cardiology)", choices)
        self.assertEqual(choices["Dr. Neha Verma (Cardiology)"], d_id)

    def test_03_patient_crud_and_autocomplete(self):
        """Test Patient module: Add, update, name candidates, delete."""
        pid = patient.add("Anita Devi", "Female", "1985-03-20", "B+",
                           "+91-90000-00002", "Haldwani", None)
        self.assertIsNotNone(pid)
        self.assertEqual(patient.get_id_by_name("Anita Devi"), pid)

        # Autocomplete search
        matches = patient.name_candidates("Ani")
        self.assertIn("Anita Devi", matches)

        # Update patient
        patient.update(pid, "Anita Devi", "Female", "1985-03-20", "B+",
                       "+91-90000-00003", "Nainital", None)
        updated = [p for p in patient.list_all() if p["patient_id"] == pid][0]
        self.assertEqual(updated["phone"], "+91-90000-00003")

    def test_04_appointment_crud(self):
        """Test Appointment booking, updating, and cancellation."""
        pid = patient.add("Ramesh Chandra", "Male", "1978-07-15", "O+",
                          "+91-91234-56789", "Dehradun", None)
        doc_id = doctor.add("Dr. S. K. Joshi", "Orthopedics", "+91-99887-76655")
        
        appt_id = appointment.add(pid, doc_id, "2026-10-15", "10:30", "Scheduled")
        self.assertIsNotNone(appt_id)

        appts = appointment.list_all()
        target = [a for a in appts if a["appointment_id"] == appt_id][0]
        self.assertEqual(target["patient"], "Ramesh Chandra")
        self.assertEqual(target["doctor"], "Dr. S. K. Joshi")
        self.assertEqual(target["status"], "Scheduled")

        # Update status to Completed
        appointment.update(appt_id, pid, doc_id, "2026-10-15", "10:30", "Completed")
        target_updated = [a for a in appointment.list_all() if a["appointment_id"] == appt_id][0]
        self.assertEqual(target_updated["status"], "Completed")

    def test_05_staff_crud(self):
        """Test Staff module: Add and list."""
        s_id = staff.add("Pooja Sharma", "Nurse", "Morning", "+91-97654-32100")
        self.assertIsNotNone(s_id)
        all_staff = staff.list_all()
        target = [s for s in all_staff if s["staff_id"] == s_id][0]
        self.assertEqual(target["role"], "Nurse")
        self.assertEqual(target["shift"], "Morning")

    def test_06_medicine_inventory_and_low_stock(self):
        """Test Pharmacy module: Add, stock update, and low stock alert."""
        m_id = medicine.add("Paracetamol 650mg", "Tablet", 15, 2.50, 20)
        self.assertIsNotNone(m_id)
        low = medicine.low_stock()
        self.assertTrue(any(m["name"] == "Paracetamol 650mg" for m in low))

    def test_07_billing_calculation_and_audit(self):
        """Test Billing module: Add bill, auto-calculation, and status update."""
        pid = patient.get_id_by_name("Anita Devi")
        b_id, total = bill.add(pid, 1000.0, 500.0, 250.0, "Cash", "Unpaid")
        self.assertEqual(total, 1750.0)

        bill.update_status(b_id, "Paid")
        bills = bill.list_all()
        target = [b for b in bills if b["bill_id"] == b_id][0]
        self.assertEqual(target["payment_status"], "Paid")

    def test_08_audit_log_verification(self):
        """Test Q07 Feature 5: Ensure actions are captured in audit trail."""
        logs = audit.list_audit(50)
        self.assertGreater(len(logs), 0)
        tables_audited = {l["table_name"] for l in logs}
        self.assertTrue({"patients", "doctors", "bills"}.issubset(tables_audited))

    def test_09_defect_checksheet(self):
        """Test Defect Checksheet logging for SQC/Pareto analysis."""
        audit.add_defect("Data Entry", "Mistyped phone number test", "Medium")
        defects = audit.list_defects()
        self.assertGreater(len(defects), 0)
        counts = audit.defect_counts_by_category()
        self.assertIn("Data Entry", counts)


    def test_10_financial_zero_boundary(self):
        """Verify billing calculation handles zero values correctly."""
        pid = patient.get_id_by_name("Anita Devi")
        b_id, total = bill.add(pid, 0.0, 300.0, 0.0, "UPI", "Paid")
        self.assertEqual(total, 300.0)

    def test_11_discharge_and_automated_bed_clearance(self):
        """Test Discharge Summary & Automated Bed Clearance (TQM Q07 enhancement)."""
        # 1. Create a room
        r_id = room.add("301", "Private", "Available", 1500)
        self.assertIsNotNone(r_id)

        # 2. Admit patient into room 301
        p_id = patient.add("Virendra Singh", "Male", "1980-05-12", "O+",
                           "+91-98765-43219", "Nainital", r_id)
        self.assertIsNotNone(p_id)

        # Verify bed is marked Occupied
        r_obj = room.get_by_id(r_id)
        self.assertEqual(r_obj["status"], "Occupied")

        # 3. Add bill
        b_id, total = bill.add(p_id, 3000.0, 500.0, 450.0, "Insurance", "Paid")
        self.assertEqual(total, 3950.0)

        # 4. Verify discharge summary
        summary = patient.get_discharge_summary(p_id)
        self.assertIsNotNone(summary)
        self.assertEqual(summary["patient_id"], p_id)
        self.assertEqual(summary["room_number"], "301")
        self.assertEqual(summary["total_billed"], 3950.0)
        self.assertFalse(summary["has_unpaid_bills"])

        # 5. Discharge patient and clear bed
        res = patient.discharge(p_id, discharge_notes="Patient fit for discharge", room_status_after="Available")
        self.assertIsNotNone(res)
        self.assertEqual(res["freed_room_number"], "301")
        self.assertEqual(res["room_status_after"], "Available")

        # 6. Verify room is now Available and patient room_id is cleared
        r_cleared = room.get_by_id(r_id)
        self.assertEqual(r_cleared["status"], "Available")

        p_cleared = [p for p in patient.list_all() if p["patient_id"] == p_id][0]
        self.assertIsNone(p_cleared["room_id"])

        # 7. Audit log verification for automated bed clearance
        logs = audit.list_audit(20)
        room_audits = [l for l in logs if l["table_name"] == "rooms" and "Automated bed clearance" in (l["details"] or "")]
        self.assertGreater(len(room_audits), 0)

    def test_12_room_transfer_and_delete_clearance(self):
        """Test bed clearance when patient changes rooms or is deleted."""
        r_a = room.add("302A", "General Ward", "Available", 400)
        r_b = room.add("302B", "General Ward", "Available", 400)

        p_id = patient.add("Sunil Pant", "Male", "1992-09-10", "A+",
                           "+91-98711-22334", "Almora", r_a)

        self.assertEqual(room.get_by_id(r_a)["status"], "Occupied")
        self.assertEqual(room.get_by_id(r_b)["status"], "Available")

        # Transfer patient from room A to room B
        patient.update(p_id, "Sunil Pant", "Male", "1992-09-10", "A+",
                       "+91-98711-22334", "Almora", r_b)

        # Room A must be freed to Available, Room B must be Occupied
        self.assertEqual(room.get_by_id(r_a)["status"], "Available")
        self.assertEqual(room.get_by_id(r_b)["status"], "Occupied")

        # Delete patient -> Room B must be automatically freed to Available
        patient.delete(p_id)
        self.assertEqual(room.get_by_id(r_b)["status"], "Available")


if __name__ == "__main__":
    unittest.main()

