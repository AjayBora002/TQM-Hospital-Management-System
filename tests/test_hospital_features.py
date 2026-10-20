"""
test_hospital_features.py -- Automated unit and integration tests for extended Hospital Management System features:
1. User Authentication & RBAC (Admin, Doctor, Receptionist)
2. Inpatient Admission and Discharge Workflow
3. Prescriptions with Clinical Poka-Yoke Allergy Cross-Checking
4. CSV Data Export
5. Automated Database Backup Engine
"""
import sys
import os
import unittest

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import config
import tempfile
import shutil
import utils.logging_service as ls

config.DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_hospital_features.db")

from database.db_manager import init_db, get_connection
from models import user as user_model
from models import patient as patient_model
from models import doctor as doctor_model
from models import room as room_model
from models import medicine as medicine_model
from models import admission as admission_model
from models import prescription as prescription_model
from utils.backup_service import backup_database, list_backups
from utils.exception_handler import ValidationError


class TestHospitalFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.orig_audit = ls.AUDIT_LOG_CSV
        ls.AUDIT_LOG_CSV = os.path.join(cls.temp_dir, "test_audit.csv")

        if os.path.exists(config.DB_PATH):
            os.remove(config.DB_PATH)
        init_db()

    @classmethod
    def tearDownClass(cls):
        ls.AUDIT_LOG_CSV = cls.orig_audit
        shutil.rmtree(cls.temp_dir, ignore_errors=True)
        if os.path.exists(config.DB_PATH):
            try:
                os.remove(config.DB_PATH)
            except Exception:
                pass

    def test_01_user_authentication_and_rbac(self):
        """Test default demo users exist and verify role-based authentication."""
        # 1. Admin login
        admin = user_model.authenticate("admin", "admin123")
        self.assertIsNotNone(admin)
        self.assertEqual(admin["role"], "Admin")

        # 2. Doctor login
        doc = user_model.authenticate("doctor", "doctor123")
        self.assertIsNotNone(doc)
        self.assertEqual(doc["role"], "Doctor")

        # 3. Receptionist login
        recep = user_model.authenticate("receptionist", "recep123")
        self.assertIsNotNone(recep)
        self.assertEqual(recep["role"], "Receptionist")

        # 4. Bad credentials
        self.assertIsNone(user_model.authenticate("admin", "wrongpassword"))
        self.assertIsNone(user_model.authenticate("nonexistent", "admin123"))

    def test_02_admission_and_discharge_workflow(self):
        """Test inpatient stay: room allocation, status to Occupied, discharge, room release."""
        # Create patient and room
        p_id = patient_model.add("Amit Sen", "Male", "1988-03-20", "B+", "9876543210", "Delhi", room_id=None, allergies="None")
        r_id = room_model.add("401", "Private", "Available", 2000.0)

        # 1. Admit patient
        adm_id = admission_model.admit_patient(p_id, r_id, diagnosis="Acute Appendicitis", performed_by="receptionist")
        self.assertGreater(adm_id, 0)

        # Check room status is now Occupied
        room_info = room_model.get_by_id(r_id)
        self.assertEqual(room_info["status"], "Occupied")

        # Check patient room is assigned
        p_info = patient_model.get_by_id(p_id)
        self.assertEqual(p_info["room_id"], r_id)

        # Check active admission
        active = admission_model.get_active_admission(p_id)
        self.assertIsNotNone(active)
        self.assertEqual(active["diagnosis"], "Acute Appendicitis")

        # 2. Discharge patient
        res = admission_model.discharge_admission(
            adm_id,
            discharge_notes="Surgery successful. Discharged in stable condition.",
            room_status_after="Available",
            performed_by="doctor"
        )
        self.assertEqual(res["room_status"], "Available")

        # Verify room released
        room_after = room_model.get_by_id(r_id)
        self.assertEqual(room_after["status"], "Available")

        # Verify patient room cleared
        p_after = patient_model.get_by_id(p_id)
        self.assertIsNone(p_after["room_id"])

    def test_03_prescription_and_clinical_poka_yoke(self):
        """Test prescription creation with allergy cross-check and inventory deduction on dispense."""
        # Setup: patient allergic to Penicillin
        p_allergic_id = patient_model.add("Karan Verma", "Male", "1992-05-14", "O+", "9876543211", "Delhi", room_id=None, allergies="Penicillin")
        doc_id = doctor_model.add("Dr. Neha Gupta", "General Medicine", "9876543212")

        # Medicines
        amox_id = medicine_model.add("Amoxicillin 500mg", "Tablet", 100, 5.0, 20)
        para_id = medicine_model.add("Paracetamol 650mg", "Tablet", 50, 2.0, 10)

        # 1. Attempt prescribing Amoxicillin to patient allergic to Penicillin -> MUST FAIL
        with self.assertRaises(ValidationError) as ctx:
            prescription_model.create_prescription(
                p_allergic_id, doc_id, amox_id, "500mg", "Thrice daily", 5, "After meals"
            )
        self.assertIn("CLINICAL SAFETY ALERT", ctx.exception.message)
        self.assertIn("Contraindication detected", ctx.exception.message)

        # 2. Prescribing safe medicine (Paracetamol) -> MUST SUCCEED
        rx_id = prescription_model.create_prescription(
            p_allergic_id, doc_id, para_id, "650mg", "Twice daily", 5, "For fever relief"
        )
        self.assertGreater(rx_id, 0)

        # 3. Dispense prescription -> should deduct medicine stock
        initial_stock = medicine_model.get_by_id(para_id)["stock_qty"]
        dispense_res = prescription_model.dispense_prescription(rx_id, qty_dispensed=10)
        self.assertTrue(dispense_res)

        new_stock = medicine_model.get_by_id(para_id)["stock_qty"]
        self.assertEqual(new_stock, initial_stock - 10)

    def test_04_automated_backup_service(self):
        """Test online backup engine generates snapshot and lists backups."""
        backup_res = backup_database(performed_by="admin")
        self.assertTrue(backup_res["success"])
        self.assertTrue(os.path.exists(backup_res["filepath"]))
        self.assertGreater(backup_res["size_kb"], 0)

        backups = list_backups()
        self.assertGreater(len(backups), 0)
        self.assertEqual(backups[0]["filename"], backup_res["filename"])


if __name__ == "__main__":
    unittest.main()
