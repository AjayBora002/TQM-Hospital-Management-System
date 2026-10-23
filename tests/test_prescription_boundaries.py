import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from database.db_manager import init_db
from models import patient as patient_model
from models import doctor as doctor_model
from models import medicine as medicine_model
from models import prescription as prescription_model
from utils.exception_handler import ValidationError
from web_app import app


class TestPrescriptionBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = app.test_client()

    def setUp(self):
        self.p_id = patient_model.add("Rahul Verma", "Male", "1990-01-01", "A+", "9876543210", "Dehradun")
        self.d_id = doctor_model.add("Dr. Deepak Rawat", "General Medicine", "9876543211")
        self.m_id = medicine_model.add("Azithromycin 500mg", "Tablet", 40, 15.0, 10, batch_no="BAT-AZ-01", expiry_date="2028-12-31")

    def test_dispense_with_negative_qty_rejected(self):
        rx_id = prescription_model.create_prescription(self.p_id, self.d_id, self.m_id, "500mg", "Once daily", 5)
        with self.assertRaises(ValidationError) as ctx:
            prescription_model.dispense_prescription(rx_id, qty_dispensed=-3)
        self.assertEqual(ctx.exception.field, "qty_dispensed")

    def test_dispense_with_zero_qty_rejected(self):
        rx_id = prescription_model.create_prescription(self.p_id, self.d_id, self.m_id, "500mg", "Once daily", 5)
        with self.assertRaises(ValidationError) as ctx:
            prescription_model.dispense_prescription(rx_id, qty_dispensed=0)
        self.assertEqual(ctx.exception.field, "qty_dispensed")

    def test_double_dispense_rejected(self):
        rx_id = prescription_model.create_prescription(self.p_id, self.d_id, self.m_id, "500mg", "Once daily", 5)
        self.assertTrue(prescription_model.dispense_prescription(rx_id, qty_dispensed=5))

        # Second dispense must be rejected
        with self.assertRaises(ValidationError) as ctx:
            prescription_model.dispense_prescription(rx_id, qty_dispensed=5)
        self.assertEqual(ctx.exception.field, "prescription_id")

    def test_api_invalid_qty_returns_400(self):
        rx_id = prescription_model.create_prescription(self.p_id, self.d_id, self.m_id, "500mg", "Once daily", 5)
        resp = self.client.post(f"/api/prescriptions/{rx_id}/dispense", json={"qty": "invalid_number"})
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
