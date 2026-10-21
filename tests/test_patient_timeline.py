"""
test_patient_timeline.py -- Unit tests for Patient 360° Comprehensive Medical Journey View.
"""
import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

import config
config.DB_PATH = os.path.join(BASE_DIR, "tests", "test_timeline.db")

from database.db_manager import init_db
from models import patient as patient_model
from models import doctor as doctor_model
from models import appointment as appointment_model
from models import medicine as medicine_model
from models import prescription as prescription_model
from models import bill as bill_model


class TestPatientTimeline(unittest.TestCase):
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

    def test_01_comprehensive_patient_timeline_aggregation(self):
        # 1. Register Patient
        p_id = patient_model.add("Rohan Mehra", "Male", "1988-06-25", "B+", "9876543200", "Pune", None, "Penicillin")
        self.assertIsNotNone(p_id)

        # 2. Record Triage Vitals
        patient_model.record_vitals(p_id, systolic=125, diastolic=82, pulse=74, temperature=98.6, spo2=99, triage_status="Normal")

        # 3. Create Doctor & Book Appointment
        d_id = doctor_model.add("Dr. Shalini Kapoor", "Cardiology", "9876543299")
        appt_id = appointment_model.add(p_id, d_id, "2026-11-05", "10:30", "Regular cardiac follow-up")

        # 4. Prescribe Medication
        med_id = medicine_model.add("Atorvastatin 20mg", "Tablet", 50, 10.0, 10, batch_no="BAT-ATV-05", expiry_date="2028-10-30")
        rx_id = prescription_model.create_prescription(p_id, d_id, med_id, "20mg", "Once at bedtime", 30)

        # 5. Generate Billing Invoice
        bill_id, total = bill_model.add(p_id, 0.0, 500.0, 300.0, "Card", "Paid")

        # Fetch Patient 360° Timeline
        timeline_data = patient_model.get_patient_360_timeline(p_id)
        self.assertIsNotNone(timeline_data)
        self.assertEqual(timeline_data["patient"]["full_name"], "Rohan Mehra")
        self.assertEqual(timeline_data["patient"]["allergies"], "Penicillin")

        # Must have at least 5 events: Registration, Vitals, Appointment, Prescription, Billing
        self.assertGreaterEqual(timeline_data["total_events"], 5)

        event_types = [e["event_type"] for e in timeline_data["timeline"]]
        self.assertIn("Registration", event_types)
        self.assertIn("Triage Vitals", event_types)
        self.assertIn("Appointment", event_types)
        self.assertIn("Prescription", event_types)
        self.assertIn("Billing & Invoicing", event_types)

    def test_02_nonexistent_patient_timeline(self):
        self.assertIsNone(patient_model.get_patient_360_timeline(99999))


if __name__ == "__main__":
    unittest.main()
