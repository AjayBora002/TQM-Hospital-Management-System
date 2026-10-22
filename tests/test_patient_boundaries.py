import unittest
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from utils.validators import validate_patient_payload
from utils.exception_handler import ValidationError
from database.db_manager import init_db
from models import patient as patient_model


class TestPatientBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
    def test_valid_patient_payload(self):
        payload = {
            "full_name": "Kavita Bisht",
            "gender": "Female",
            "dob": "1998-04-12",
            "blood_group": "B+",
            "phone": "9876543210"
        }
        self.assertTrue(validate_patient_payload(payload))

    def test_future_dob_rejected(self):
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        payload = {
            "full_name": "Future Baby",
            "gender": "Male",
            "dob": tomorrow,
            "blood_group": "O+",
            "phone": "9876543210"
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_patient_payload(payload)
        self.assertEqual(ctx.exception.field, "dob")
        self.assertIn("future", str(ctx.exception).lower())

    def test_far_past_dob_rejected(self):
        payload = {
            "full_name": "Ancient Person",
            "gender": "Male",
            "dob": "1840-01-01",
            "blood_group": "O+",
            "phone": "9876543210"
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_patient_payload(payload)
        self.assertEqual(ctx.exception.field, "dob")

    def test_short_name_rejected(self):
        payload = {
            "full_name": "A",
            "gender": "Female",
            "dob": "1995-01-01",
            "blood_group": "A+",
            "phone": "9876543210"
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_patient_payload(payload)
        self.assertEqual(ctx.exception.field, "full_name")

    def test_invalid_gender_rejected(self):
        payload = {
            "full_name": "Test Person",
            "gender": "UnknownGender",
            "dob": "1995-01-01",
            "blood_group": "A+",
            "phone": "9876543210"
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_patient_payload(payload)
        self.assertEqual(ctx.exception.field, "gender")

    def test_invalid_blood_group_rejected(self):
        payload = {
            "full_name": "Test Person",
            "gender": "Male",
            "dob": "1995-01-01",
            "blood_group": "X-Positive",
            "phone": "9876543210"
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_patient_payload(payload)
        self.assertEqual(ctx.exception.field, "blood_group")

    def test_invalid_phone_rejected(self):
        payload = {
            "full_name": "Test Person",
            "gender": "Male",
            "dob": "1995-01-01",
            "blood_group": "AB+",
            "phone": "12345"
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_patient_payload(payload)
        self.assertEqual(ctx.exception.field, "phone")

    def test_model_add_blocks_future_dob(self):
        future_date = "2099-12-31"
        with self.assertRaises(ValidationError):
            patient_model.add("Time Traveler", "Other", future_date, "O-", "9998887776", "Nainital")


if __name__ == "__main__":
    unittest.main()
