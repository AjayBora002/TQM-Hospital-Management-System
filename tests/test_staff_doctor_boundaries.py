import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from utils.validators import validate_doctor_payload, validate_staff_payload
from utils.exception_handler import ValidationError
from database.db_manager import init_db
from models import doctor as doctor_model
from models import staff as staff_model


class TestStaffDoctorBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_valid_doctor_payload(self):
        payload = {
            "full_name": "Dr. Rohit Joshi",
            "department": "Cardiology",
            "phone": "9876543210"
        }
        self.assertTrue(validate_doctor_payload(payload))

    def test_doctor_invalid_department_rejected(self):
        payload = {
            "full_name": "Dr. Astrology Specialist",
            "department": "Astrology",
            "phone": "9876543210"
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_doctor_payload(payload)
        self.assertEqual(ctx.exception.field, "department")

    def test_doctor_invalid_phone_rejected(self):
        payload = {
            "full_name": "Dr. Valid Name",
            "department": "Neurology",
            "phone": "12345"
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_doctor_payload(payload)
        self.assertEqual(ctx.exception.field, "phone")

    def test_valid_staff_payload(self):
        payload = {
            "full_name": "Kiran Negi",
            "role": "Nurse",
            "shift": "Morning",
            "phone": "9876543210"
        }
        self.assertTrue(validate_staff_payload(payload))

    def test_staff_invalid_role_rejected(self):
        payload = {
            "full_name": "Kiran Negi",
            "role": "Astronaut",
            "shift": "Morning",
            "phone": "9876543210"
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_staff_payload(payload)
        self.assertEqual(ctx.exception.field, "role")

    def test_staff_invalid_shift_rejected(self):
        payload = {
            "full_name": "Kiran Negi",
            "role": "Nurse",
            "shift": "Midnight Graveyard",
            "phone": "9876543210"
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_staff_payload(payload)
        self.assertEqual(ctx.exception.field, "shift")

    def test_model_level_doctor_and_staff_validation(self):
        with self.assertRaises(ValidationError):
            doctor_model.add("Dr. Fake", "MagicDepartment", "9876543210")

        with self.assertRaises(ValidationError):
            staff_model.add("Fake Staff", "InvalidRole", "Morning", "9876543210")


if __name__ == "__main__":
    unittest.main()
