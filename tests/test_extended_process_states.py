"""
test_extended_process_states.py -- Unit tests for extended NABH/Guideline process states.
"""
import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

import config
from utils.validators import validate_appointment_payload, validate_room_payload
from utils.exception_handler import ValidationError


class TestExtendedProcessStates(unittest.TestCase):
    def test_appointment_extended_states_accepted(self):
        for status in ["Scheduled", "Confirmed", "Checked-in", "Waiting", "In consultation", "Completed", "Cancelled", "No-show"]:
            payload = {
                "patient_id": 1,
                "doctor_id": 1,
                "appt_date": "2026-11-20",
                "appt_time": "11:00",
                "status": status
            }
            self.assertTrue(validate_appointment_payload(payload))

    def test_appointment_invalid_state_rejected(self):
        payload = {
            "patient_id": 1,
            "doctor_id": 1,
            "appt_date": "2026-11-20",
            "appt_time": "11:00",
            "status": "In Limbo"
        }
        with self.assertRaises(ValidationError):
            validate_appointment_payload(payload)

    def test_room_extended_states_accepted(self):
        for status in ["Available", "Occupied", "Under Maintenance", "Cleaning / Sanitizing", "Reserved", "Blocked"]:
            payload = {
                "room_number": "999",
                "room_type": "Private",
                "status": status,
                "rate_per_day": 1000.0
            }
            self.assertTrue(validate_room_payload(payload))

    def test_room_invalid_state_rejected(self):
        payload = {
            "room_number": "999",
            "room_type": "Private",
            "status": "Demolished",
            "rate_per_day": 1000.0
        }
        with self.assertRaises(ValidationError):
            validate_room_payload(payload)


if __name__ == "__main__":
    unittest.main()
