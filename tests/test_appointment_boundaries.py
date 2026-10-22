import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from utils.validators import validate_appointment_payload
from utils.exception_handler import ValidationError
from database.db_manager import init_db
from models import patient as patient_model
from models import doctor as doctor_model
from models import appointment as appointment_model


class TestAppointmentBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
    def test_valid_appointment_payload(self):
        payload = {
            "patient_id": 1,
            "doctor_id": 1,
            "appt_date": "2026-11-20",
            "appt_time": "10:30",
            "status": "Scheduled"
        }
        self.assertTrue(validate_appointment_payload(payload))

    def test_invalid_patient_id(self):
        payload = {
            "patient_id": "invalid",
            "doctor_id": 1,
            "appt_date": "2026-11-20",
            "appt_time": "10:30"
        }
        with self.assertRaises(ValidationError):
            validate_appointment_payload(payload)

    def test_invalid_doctor_id(self):
        payload = {
            "patient_id": 1,
            "doctor_id": -5,
            "appt_date": "2026-11-20",
            "appt_time": "10:30"
        }
        with self.assertRaises(ValidationError):
            validate_appointment_payload(payload)

    def test_invalid_date_format(self):
        payload = {
            "patient_id": 1,
            "doctor_id": 1,
            "appt_date": "20-11-2026",
            "appt_time": "10:30"
        }
        with self.assertRaises(ValidationError):
            validate_appointment_payload(payload)

    def test_invalid_time_format(self):
        payload = {
            "patient_id": 1,
            "doctor_id": 1,
            "appt_date": "2026-11-20",
            "appt_time": "25:70"
        }
        with self.assertRaises(ValidationError):
            validate_appointment_payload(payload)

    def test_invalid_status(self):
        payload = {
            "patient_id": 1,
            "doctor_id": 1,
            "appt_date": "2026-11-20",
            "appt_time": "10:30",
            "status": "UnknownStatus"
        }
        with self.assertRaises(ValidationError):
            validate_appointment_payload(payload)

    def test_model_level_validation_and_conflict(self):
        pid = patient_model.add("Appointment Test Patient", "Male", "1992-05-10", "A+", "+91-91234-99887", "Dehradun", None)
        doc_id = doctor_model.add("Dr. Conflict Checker", "Cardiology", "+91-98765-43210")
        
        # Add valid appointment
        appt_id = appointment_model.add(pid, doc_id, "2026-12-01", "11:00", "Scheduled")
        self.assertIsNotNone(appt_id)

        # Confirm conflict detected
        conflict = appointment_model.has_conflict(doc_id, "2026-12-01", "11:00")
        self.assertIsNotNone(conflict)

        # Confirm different time has no conflict
        no_conflict = appointment_model.has_conflict(doc_id, "2026-12-01", "14:00")
        self.assertIsNone(no_conflict)


if __name__ == "__main__":
    unittest.main()
