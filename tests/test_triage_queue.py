"""
test_triage_queue.py -- Unit tests for Emergency Triage Priority Queue.
Verifies automated physiological severity evaluation (Code Red, Yellow, Green) and sorting.
"""
import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

import config
config.DB_PATH = os.path.join(BASE_DIR, "tests", "test_triage_queue.db")

from database.db_manager import init_db
from models import patient as patient_model
from models import triage as triage_model


class TestTriageQueue(unittest.TestCase):
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

    def test_01_evaluate_triage_tier_logic(self):
        # Code Red (Hypoxemic)
        red = triage_model.evaluate_triage_tier(systolic=120, diastolic=80, pulse=80, temperature=98.6, spo2=86)
        self.assertEqual(red["tier"], "Code Red")
        self.assertEqual(red["priority"], 1)

        # Code Red (Hypertensive Crisis)
        red_bp = triage_model.evaluate_triage_tier(systolic=195, diastolic=115, pulse=85, temperature=98.6, spo2=98)
        self.assertEqual(red_bp["tier"], "Code Red")

        # Code Yellow (Fever & Borderline BP)
        yellow = triage_model.evaluate_triage_tier(systolic=145, diastolic=92, pulse=95, temperature=101.8, spo2=96)
        self.assertEqual(yellow["tier"], "Code Yellow")
        self.assertEqual(yellow["priority"], 2)

        # Code Green (All Normal)
        green = triage_model.evaluate_triage_tier(systolic=118, diastolic=78, pulse=72, temperature=98.4, spo2=99)
        self.assertEqual(green["tier"], "Code Green")
        self.assertEqual(green["priority"], 3)

    def test_02_queue_sorting_prioritizes_code_red(self):
        # Add 3 patients
        p_stable = patient_model.add("Amit Normal", "Male", "1990-01-01", "A+", "9876543201", "Delhi", None, "None")
        p_urgent = patient_model.add("Bina Fever", "Female", "1985-02-02", "B+", "9876543202", "Delhi", None, "None")
        p_critical = patient_model.add("Chetan Critical", "Male", "1960-03-03", "O+", "9876543203", "Delhi", None, "None")

        # Record vitals: Stable first, then Fever, then Critical
        patient_model.record_vitals(p_stable, systolic=120, diastolic=80, pulse=72, temperature=98.4, spo2=99)
        patient_model.record_vitals(p_urgent, systolic=148, diastolic=92, pulse=100, temperature=101.5, spo2=96)
        patient_model.record_vitals(p_critical, systolic=85, diastolic=50, pulse=138, temperature=104.2, spo2=84)

        queue = triage_model.get_emergency_queue()
        self.assertGreaterEqual(len(queue), 3)

        # First in queue MUST be Code Red (Critical)
        self.assertEqual(queue[0]["patient_id"], p_critical)
        self.assertEqual(queue[0]["tier"], "Code Red")

        # Second in queue MUST be Code Yellow (Fever)
        self.assertEqual(queue[1]["patient_id"], p_urgent)
        self.assertEqual(queue[1]["tier"], "Code Yellow")

        # Third in queue MUST be Code Green (Stable)
        self.assertEqual(queue[2]["patient_id"], p_stable)
        self.assertEqual(queue[2]["tier"], "Code Green")


if __name__ == "__main__":
    unittest.main()
