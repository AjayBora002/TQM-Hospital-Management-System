"""
test_report_generator.py -- Unit tests for Medical Invoice and Discharge Summary HTML Report Generation.
"""
import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

import config
config.DB_PATH = os.path.join(BASE_DIR, "tests", "test_reports.db")

from database.db_manager import init_db
from models import patient as patient_model
from models import room as room_model
from models import bill as bill_model
from models import admission as admission_model
from utils.report_generator import generate_bill_receipt_html, generate_discharge_summary_html
from utils.exception_handler import ValidationError


class TestReportGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.path.exists(config.DB_PATH):
            try:
                os.remove(config.DB_PATH)
            except Exception:
                pass
        init_db()
        cls.p_id = patient_model.add("Sunita Rao", "Female", "1975-11-20", "O+", "9876543210", "Hyderabad", None, "None")
        cls.r_id = room_model.add("202", "Deluxe", "Available", 1500.0)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(config.DB_PATH):
            try:
                os.remove(config.DB_PATH)
            except Exception:
                pass

    def test_01_generate_bill_receipt_html(self):
        b_id, total = bill_model.add(
            patient_id=self.p_id,
            room_charges=3000.0,
            consultation_charges=800.0,
            medicine_charges=450.0,
            payment_method="UPI",
            payment_status="Paid"
        )
        html = generate_bill_receipt_html(b_id)
        self.assertIn("TQM HOSPITAL & RESEARCH INSTITUTE", html)
        self.assertIn("Sunita Rao", html)
        self.assertIn(f"INV-{b_id:05d}", html)
        self.assertIn("4,250.00", html)
        self.assertIn("UPI", html)
        self.assertIn("Paid", html)

    def test_02_generate_discharge_summary_html(self):
        adm_id = admission_model.admit_patient(
            patient_id=self.p_id,
            room_id=self.r_id,
            admission_date="2026-10-15",
            diagnosis="Acute Bronchitis & Fever"
        )
        admission_model.discharge_admission(
            admission_id=adm_id,
            discharge_date="2026-10-18",
            discharge_notes="Patient recovered satisfactorily. Complete oral antibiotics course."
        )

        html = generate_discharge_summary_html(adm_id)
        self.assertIn("TQM HOSPITAL & RESEARCH INSTITUTE", html)
        self.assertIn("Formal Discharge Summary Report", html)
        self.assertIn("Sunita Rao", html)
        self.assertIn("Acute Bronchitis & Fever", html)
        self.assertIn("2026-10-15", html)
        self.assertIn("2026-10-18", html)

    def test_03_invalid_id_raises_error(self):
        with self.assertRaises(ValidationError):
            generate_bill_receipt_html(99999)
        with self.assertRaises(ValidationError):
            generate_discharge_summary_html(99999)


if __name__ == "__main__":
    unittest.main()
