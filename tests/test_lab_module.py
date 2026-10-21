"""
test_lab_module.py -- Unit tests for Diagnostic Laboratory & Radiology Testing Module.
Verifies Poka-Yoke automated flagging of abnormal biological reference values.
"""
import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

import config
config.DB_PATH = os.path.join(BASE_DIR, "tests", "test_lab_module.db")

from database.db_manager import init_db
from models import patient as patient_model
from models import doctor as doctor_model
from models import lab_test as lab_model
from utils.exception_handler import ValidationError


class TestLabModule(unittest.TestCase):
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

    def setUp(self):
        self.p_id = patient_model.add("Pooja Sharma", "Female", "1995-04-12", "B+", "9876543210", "Noida", None, "None")
        self.d_id = doctor_model.add("Dr. Vikram Rathore", "General Medicine", "9876543211")

    def test_01_order_lab_test_with_template(self):
        test_id = lab_model.order_test(
            patient_id=self.p_id,
            doctor_id=self.d_id,
            test_name="Hemoglobin"
        )
        self.assertIsNotNone(test_id)
        test = lab_model.get_by_id(test_id)
        self.assertEqual(test["test_name"], "Hemoglobin")
        self.assertEqual(test["category"], "Hematology")
        self.assertEqual(test["unit"], "g/dL")
        self.assertEqual(test["ref_min"], 12.0)
        self.assertEqual(test["ref_max"], 17.5)
        self.assertEqual(test["status"], "Pending")
        self.assertEqual(test["abnormal_flag"], 0)

    def test_02_record_normal_result(self):
        test_id = lab_model.order_test(
            patient_id=self.p_id,
            doctor_id=self.d_id,
            test_name="Fasting Blood Sugar"
        )
        # Normal value between 70.0 and 99.0
        updated = lab_model.record_result(test_id, 85.0, notes="Fasting specimen taken at 8 AM")
        self.assertEqual(updated["status"], "Completed")
        self.assertEqual(updated["result_value"], 85.0)
        self.assertEqual(updated["abnormal_flag"], 0)

    def test_03_record_abnormal_result_poka_yoke(self):
        test_id = lab_model.order_test(
            patient_id=self.p_id,
            doctor_id=self.d_id,
            test_name="Serum Creatinine"
        )
        # Standard normal: 0.6 - 1.2 mg/dL. We input 2.8 (Severely Elevated!)
        updated = lab_model.record_result(test_id, 2.8, notes="Critical elevation detected")
        self.assertEqual(updated["status"], "Completed")
        self.assertEqual(updated["result_value"], 2.8)
        self.assertEqual(updated["abnormal_flag"], 1)

        # Check list_abnormal filter
        abnormals = lab_model.list_abnormal()
        self.assertTrue(any(t["test_id"] == test_id for t in abnormals))

    def test_04_validation_safeguards(self):
        with self.assertRaises(ValidationError):
            lab_model.order_test(patient_id=99999, doctor_id=self.d_id, test_name="Hemoglobin")
        with self.assertRaises(ValidationError):
            lab_model.order_test(patient_id=self.p_id, doctor_id=99999, test_name="Hemoglobin")
        with self.assertRaises(ValidationError):
            lab_model.order_test(patient_id=self.p_id, doctor_id=self.d_id, test_name="")


if __name__ == "__main__":
    unittest.main()
