"""
test_pharmacy_expiry.py -- Tests for Clinical Poka-Yoke Medicine Batch & Expiry Safeguards.
"""
import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

import config
config.DB_PATH = os.path.join(BASE_DIR, "tests", "test_expiry_poka_yoke.db")

from database.db_manager import init_db
from models import medicine as medicine_model
from models import patient as patient_model
from models import doctor as doctor_model
from models import prescription as prescription_model
from utils.exception_handler import ValidationError


class TestPharmacyExpiryPokaYoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.path.exists(config.DB_PATH):
            try:
                os.remove(config.DB_PATH)
            except Exception:
                pass
        init_db()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DB_PATH):
            try:
                os.remove(config.DB_PATH)
            except Exception:
                pass

    def test_01_is_expired_helper(self):
        self.assertTrue(medicine_model.is_expired("2020-01-01"))
        self.assertTrue(medicine_model.is_expired("2024-05-15"))
        self.assertFalse(medicine_model.is_expired("2099-12-31"))
        self.assertFalse(medicine_model.is_expired(""))
        self.assertFalse(medicine_model.is_expired(None))

    def test_02_add_and_list_expired_medicines(self):
        med_valid_id = medicine_model.add("Valid Aspirin 100mg", "Tablet", 100, 5.0, 10, batch_no="BAT-ASP-01", expiry_date="2028-12-31")
        med_exp_id = medicine_model.add("Expired Tetracycline 250mg", "Capsule", 20, 15.0, 5, batch_no="BAT-TET-99", expiry_date="2023-01-01")

        all_meds = medicine_model.list_all()
        self.assertTrue(any(m["name"] == "Valid Aspirin 100mg" for m in all_meds))
        self.assertTrue(any(m["name"] == "Expired Tetracycline 250mg" for m in all_meds))

        expired = medicine_model.expired_medicines()
        exp_names = [m["name"] for m in expired]
        self.assertIn("Expired Tetracycline 250mg", exp_names)
        self.assertNotIn("Valid Aspirin 100mg", exp_names)

    def test_03_prescription_blocks_expired_medicine(self):
        p_id = patient_model.add("Ramesh Patel", "Male", "1980-05-10", "O+", "9876543210", "Mumbai", None, "None")
        d_id = doctor_model.add("Dr. Meera Iyer", "General Medicine", "9876543211")
        med_exp_id = medicine_model.add("Expired Amoxicillin Batch", "Capsule", 30, 20.0, 5, batch_no="BAT-EXP-88", expiry_date="2022-01-01")

        with self.assertRaises(ValidationError) as ctx:
            prescription_model.create_prescription(
                patient_id=p_id,
                doctor_id=d_id,
                medicine_id=med_exp_id,
                dosage="500mg",
                frequency="Twice daily",
                duration_days=5
            )
        self.assertIn("CLINICAL SAFETY ALERT", str(ctx.exception))
        self.assertIn("expired medicine", str(ctx.exception).lower())

    def test_04_prescription_allows_valid_medicine(self):
        p_id = patient_model.add("Suresh Kumar", "Male", "1992-08-14", "A+", "9876543212", "Delhi", None, "None")
        d_id = doctor_model.add("Dr. Arvind Gupta", "Cardiology", "9876543213")
        med_valid_id = medicine_model.add("Fresh Atorvastatin 10mg", "Tablet", 50, 8.0, 10, batch_no="BAT-ATV-01", expiry_date="2028-06-30")

        rx_id = prescription_model.create_prescription(
            patient_id=p_id,
            doctor_id=d_id,
            medicine_id=med_valid_id,
            dosage="10mg",
            frequency="Once daily",
            duration_days=10
        )
        self.assertIsNotNone(rx_id)
        self.assertGreater(rx_id, 0)


if __name__ == "__main__":
    unittest.main()
