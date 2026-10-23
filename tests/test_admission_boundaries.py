import unittest
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from utils.exception_handler import ValidationError
from database.db_manager import init_db, get_connection
from models import patient as patient_model
from models import room as room_model
from models import admission as admission_model


class TestAdmissionBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        # Create a test patient and test room
        self.patient_id = patient_model.add(
            full_name="Test Inpatient Stay",
            gender="Male",
            dob="1980-05-15",
            blood_group="A+",
            phone="9811122233",
            address="Ward 4B"
        )

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO rooms (room_number, room_type, status, rate_per_day) VALUES (?, ?, 'Available', 1500.0)",
                (f"TEST-{datetime.now().strftime('%f')[:4]}", "General")
            )
            self.room_id = cur.lastrowid
            conn.commit()
        finally:
            conn.close()

    def test_admit_and_discharge_chronology(self):
        # Admission date: 2 days ago
        adm_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        adm_id = admission_model.admit_patient(
            patient_id=self.patient_id,
            room_id=self.room_id,
            admission_date=adm_date,
            diagnosis="Observation"
        )
        self.assertGreater(adm_id, 0)

        # Discharge earlier than admission date must fail
        earlier_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        with self.assertRaises(ValidationError) as ctx:
            admission_model.discharge_admission(adm_id, discharge_date=earlier_date)
        self.assertEqual(ctx.exception.field, "discharge_date")

        # Discharge on or after admission date succeeds
        disch_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        admission_model.discharge_admission(adm_id, discharge_date=disch_date, discharge_notes="Recovered")

        # Re-discharging should raise ValidationError
        with self.assertRaises(ValidationError) as ctx2:
            admission_model.discharge_admission(adm_id, discharge_date=disch_date)
        self.assertEqual(ctx2.exception.field, "admission_id")

    def test_invalid_admission_date_format_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            admission_model.admit_patient(
                patient_id=self.patient_id,
                room_id=self.room_id,
                admission_date="2026/12/31"
            )
        self.assertEqual(ctx.exception.field, "admission_date")

    def test_future_admission_date_rejected(self):
        future_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        with self.assertRaises(ValidationError) as ctx:
            admission_model.admit_patient(
                patient_id=self.patient_id,
                room_id=self.room_id,
                admission_date=future_date
            )
        self.assertEqual(ctx.exception.field, "admission_date")

    def test_invalid_discharge_date_format_rejected(self):
        adm_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        adm_id = admission_model.admit_patient(
            patient_id=self.patient_id,
            room_id=self.room_id,
            admission_date=adm_date
        )
        with self.assertRaises(ValidationError) as ctx:
            admission_model.discharge_admission(adm_id, discharge_date="invalid-date")
        self.assertEqual(ctx.exception.field, "discharge_date")


if __name__ == "__main__":
    unittest.main()
