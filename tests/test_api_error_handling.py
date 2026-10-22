import unittest
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from web_app import app
from database.db_manager import init_db


class TestAPIErrorHandling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = app.test_client()

    def test_future_dob_api_returns_400(self):
        resp = self.client.post("/api/patients", json={
            "full_name": "API Future Patient",
            "gender": "Female",
            "dob": "2099-01-01",
            "blood_group": "A+",
            "phone": "9876543210"
        })
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertIn("error", data)
        self.assertEqual(data["field"], "dob")

    def test_negative_room_rate_returns_400(self):
        resp = self.client.post("/api/rooms", json={
            "room_number": "909",
            "room_type": "Private",
            "status": "Available",
            "rate_per_day": -500.0
        })
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertEqual(data["field"], "rate_per_day")

    def test_negative_medicine_stock_returns_400(self):
        resp = self.client.post("/api/medicines", json={
            "name": "Negative Inventory Item",
            "category": "Tablet",
            "stock_qty": -50,
            "unit_price": 5.0,
            "reorder_level": 10
        })
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertEqual(data["field"], "stock_qty")

    def test_invalid_doctor_department_returns_400(self):
        resp = self.client.post("/api/doctors", json={
            "full_name": "Dr. Invalid Dept",
            "department": "Astrology",
            "phone": "9876543210"
        })
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertEqual(data["field"], "department")

    def test_invalid_staff_role_returns_400(self):
        resp = self.client.post("/api/staff", json={
            "full_name": "Invalid Staff",
            "role": "SuperHero",
            "shift": "Morning",
            "phone": "9876543210"
        })
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertEqual(data["field"], "role")

    def test_negative_bill_charge_returns_400(self):
        resp = self.client.post("/api/bills", json={
            "patient_id": 1,
            "room_charges": -100.0,
            "consultation_charges": 500.0,
            "medicine_charges": 200.0,
            "payment_method": "Cash",
            "payment_status": "Paid"
        })
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
