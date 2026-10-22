import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from utils.validators import validate_billing_payload
from utils.exception_handler import ValidationError
from models import bill


class TestBillingValidation(unittest.TestCase):
    def test_valid_billing_payload(self):
        payload = {
            "patient_id": 1,
            "room_charges": 1200.50,
            "consultation_charges": 500.0,
            "medicine_charges": 350.25,
            "payment_method": "Cash",
            "payment_status": "Paid"
        }
        self.assertTrue(validate_billing_payload(payload))

    def test_negative_room_charges_rejected(self):
        payload = {
            "patient_id": 1,
            "room_charges": -50.0,
            "consultation_charges": 500.0,
            "medicine_charges": 100.0
        }
        with self.assertRaises(ValidationError) as ctx:
            validate_billing_payload(payload)
        self.assertIn("cannot be negative", str(ctx.exception).lower())

    def test_negative_consultation_charges_rejected(self):
        payload = {
            "patient_id": 1,
            "room_charges": 500.0,
            "consultation_charges": -100.0,
            "medicine_charges": 100.0
        }
        with self.assertRaises(ValidationError):
            validate_billing_payload(payload)

    def test_negative_medicine_charges_rejected(self):
        payload = {
            "patient_id": 1,
            "room_charges": 500.0,
            "consultation_charges": 100.0,
            "medicine_charges": -25.0
        }
        with self.assertRaises(ValidationError):
            validate_billing_payload(payload)

    def test_invalid_payment_method_rejected(self):
        payload = {
            "patient_id": 1,
            "room_charges": 500.0,
            "consultation_charges": 100.0,
            "medicine_charges": 50.0,
            "payment_method": "CryptoCurrency"
        }
        with self.assertRaises(ValidationError):
            validate_billing_payload(payload)

    def test_invalid_payment_status_rejected(self):
        payload = {
            "patient_id": 1,
            "room_charges": 500.0,
            "consultation_charges": 100.0,
            "medicine_charges": 50.0,
            "payment_status": "NeverPaidEver"
        }
        with self.assertRaises(ValidationError):
            validate_billing_payload(payload)


if __name__ == "__main__":
    unittest.main()
