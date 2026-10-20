"""
test_clinical_poka_yoke.py -- Unit & integration tests for Clinical Poka-Yoke controls:
1. Doctor schedule double-booking prevention
2. Patient overlapping appointment prevention
3. Drug allergy contraindication and ADR checking
4. Physiological vital signs boundary & triage validation
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import config
import tempfile
import shutil
import utils.logging_service as ls

config.DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_clinical_hms.db")

from database.db_manager import init_db
import models.patient as patient_model
import models.doctor as doctor_model
import models.appointment as appointment_model
from utils.validators import (
    validate_vital_signs,
    check_drug_allergy_contraindication
)
from utils.exception_handler import ValidationError


class TestClinicalPokaYoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.orig_audit = ls.AUDIT_LOG_CSV
        ls.AUDIT_LOG_CSV = os.path.join(cls.temp_dir, "test_audit.csv")

        if os.path.exists(config.DB_PATH):
            try:
                os.remove(config.DB_PATH)
            except OSError:
                pass
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
            try:
                os.remove(config.DB_PATH)
            except OSError:
                pass

    def test_drug_allergy_contraindication_detection(self):
        # Penicillin allergy vs Amoxicillin
        check1 = check_drug_allergy_contraindication("Penicillin", "Amoxicillin 500mg", "Tablet")
        self.assertTrue(check1["contraindicated"])
        self.assertEqual(check1["allergy"], "Penicillin")
        self.assertIn("ADVERSE DRUG REACTION", check1["reason"])

        # Sulfa Drugs allergy vs Bactrim
        check2 = check_drug_allergy_contraindication("Sulfa Drugs", "Bactrim DS", "Tablet")
        self.assertTrue(check2["contraindicated"])

        # Aspirin / NSAIDs allergy vs Ibuprofen
        check3 = check_drug_allergy_contraindication("Aspirin / NSAIDs", "Ibuprofen 400mg", "Tablet")
        self.assertTrue(check3["contraindicated"])

        # Patient with no allergies or safe medication
        check4 = check_drug_allergy_contraindication("None", "Paracetamol 650mg", "Tablet")
        self.assertFalse(check4["contraindicated"])

        check5 = check_drug_allergy_contraindication("Penicillin", "Cetirizine 10mg", "Tablet")
        self.assertFalse(check5["contraindicated"])

    def test_vital_signs_boundaries_and_triage(self):
        # 1. Normal vitals
        normal_vitals = {
            "systolic": 120,
            "diastolic": 80,
            "pulse": 72,
            "temperature": 98.6,
            "spo2": 99
        }
        res_normal = validate_vital_signs(normal_vitals)
        self.assertEqual(res_normal["triage_status"], "Normal")
        self.assertEqual(len(res_normal["alerts"]), 0)

        # 2. Warning / elevated vitals
        warning_vitals = {
            "systolic": 145,
            "diastolic": 92,
            "pulse": 105,
            "temperature": 100.2,
            "spo2": 93
        }
        res_warn = validate_vital_signs(warning_vitals)
        self.assertIn(res_warn["triage_status"], ["Warning", "Critical"])
        self.assertTrue(len(res_warn["alerts"]) > 0)

        # 3. Critical hypertensive / hypoxia crisis
        critical_vitals = {
            "systolic": 195,
            "diastolic": 125,
            "pulse": 145,
            "temperature": 104.5,
            "spo2": 82
        }
        res_crit = validate_vital_signs(critical_vitals)
        self.assertEqual(res_crit["triage_status"], "Critical")

        # 4. Physically impossible / out-of-range values raise ValidationError
        bad_vitals = {"systolic": 500}
        with self.assertRaises(ValidationError):
            validate_vital_signs(bad_vitals)

        bad_temp = {"temperature": 150.0}
        with self.assertRaises(ValidationError):
            validate_vital_signs(bad_temp)

    def test_doctor_schedule_conflict_prevention(self):
        # Create test doctor and two test patients
        doc_id = doctor_model.add("Dr. Conflict Test", "Cardiology", "+91-99887-76655")
        pat1_id = patient_model.add("Patient A", "Male", "1990-01-01", "A+", "+91-98765-11111", "City", allergies="Penicillin")
        pat2_id = patient_model.add("Patient B", "Female", "1992-02-02", "B+", "+91-98765-22222", "City", allergies="None")

        test_date = "2026-11-20"
        test_slot = "10:30"

        # Book first appointment
        appt1_id = appointment_model.add(pat1_id, doc_id, test_date, test_slot, "Scheduled")
        self.assertIsNotNone(appt1_id)

        # Attempt to detect conflict for same doctor, same date, same slot
        conflict = appointment_model.has_conflict(doc_id, test_date, test_slot)
        self.assertIsNotNone(conflict)
        self.assertEqual(conflict["doctor"], "Dr. Conflict Test")

        # Patient 1 conflict check (cannot have second appointment at same time)
        pat_conflict = appointment_model.has_patient_conflict(pat1_id, test_date, test_slot)
        self.assertIsNotNone(pat_conflict)

        # Different slot on same date must have NO conflict
        no_conflict = appointment_model.has_conflict(doc_id, test_date, "11:00")
        self.assertIsNone(no_conflict)


if __name__ == "__main__":
    unittest.main()
