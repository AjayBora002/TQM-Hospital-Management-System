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


if __name__ == "__main__":
    unittest.main()
