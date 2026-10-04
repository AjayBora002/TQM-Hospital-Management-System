"""
test_validators.py -- Unit tests for Q07 Data Accuracy validators and constraints.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from utils.validators import (
    is_valid_date,
    is_valid_time,
    is_valid_phone_digits,
    validate_patient_payload,
    validate_appointment_payload,
    validate_billing_payload
)
from utils.exception_handler import ValidationError


class TestValidators(unittest.TestCase):
    def test_date_validation(self):
        self.assertTrue(is_valid_date("2026-10-04"))
        self.assertFalse(is_valid_date("04-10-2026"))
        self.assertFalse(is_valid_date("2026-02-30"))  # Invalid day
        self.assertFalse(is_valid_date(""))

    def test_time_validation(self):
        self.assertTrue(is_valid_time("09:30"))
        self.assertTrue(is_valid_time("23:59"))
        self.assertFalse(is_valid_time("24:00"))
        self.assertFalse(is_valid_time("9:30"))
        self.assertFalse(is_valid_time(""))

    def test_phone_validation(self):
        self.assertTrue(is_valid_phone_digits("9876543210"))
        self.assertTrue(is_valid_phone_digits("+91-98765-43210"))
        self.assertFalse(is_valid_phone_digits("12345"))
        self.assertFalse(is_valid_phone_digits("abcdefghij"))

    def test_patient_payload_validation_success(self):
        payload = {
            "full_name": "Rohan Mehra",
            "gender": "Male",
            "dob": "1994-08-15",
            "blood_group": "O+",
            "phone": "9876543210"
        }
        self.assertTrue(validate_patient_payload(payload))

    def test_patient_payload_validation_failure(self):
        # Invalid blood group
        bad_payload = {
            "full_name": "Rohan Mehra",
            "gender": "Male",
            "dob": "1994-08-15",
            "blood_group": "Z+",
            "phone": "9876543210"
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_patient_payload(bad_payload)
        self.assertEqual(ctx.exception.field, "blood_group")

    def test_billing_payload_validation(self):
        valid_bill = {
            "patient_id": 1,
            "room_charges": 1500,
            "consultation_charges": 500,
            "medicine_charges": 250
        }
        self.assertTrue(validate_billing_payload(valid_bill))

        invalid_bill = {
            "patient_id": 1,
            "room_charges": -200,
            "consultation_charges": 500,
            "medicine_charges": 250
        }
        with self.assertRaises(ValidationError):
            validate_billing_payload(invalid_bill)


if __name__ == "__main__":
    unittest.main()
