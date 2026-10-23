import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from models.triage import evaluate_triage_tier


class TestTriageBoundaries(unittest.TestCase):
    def test_string_inputs_do_not_raise_type_error(self):
        # Numeric values passed as strings from web forms or JSON payloads
        res = evaluate_triage_tier(
            systolic="190",
            diastolic="110",
            pulse="85",
            temperature="98.6",
            spo2="98"
        )
        self.assertEqual(res["tier"], "Code Red")
        self.assertEqual(res["priority"], 1)

    def test_hypothermia_triggers_code_red(self):
        res = evaluate_triage_tier(
            systolic=120,
            diastolic=80,
            pulse=72,
            temperature=94.2,
            spo2=99
        )
        self.assertEqual(res["tier"], "Code Red")
        self.assertIn("Hypothermia", "".join(res["reasons"]))

    def test_crisis_diastolic_triggers_code_red(self):
        res = evaluate_triage_tier(
            systolic=135,
            diastolic=125,
            pulse=75,
            temperature=98.6,
            spo2=99
        )
        self.assertEqual(res["tier"], "Code Red")

    def test_malformed_string_gracefully_handled(self):
        # Non-numeric string should not crash
        res = evaluate_triage_tier(
            systolic="not_a_number",
            diastolic="unknown",
            pulse="N/A",
            temperature="error",
            spo2=None
        )
        self.assertEqual(res["tier"], "Code Green")

    def test_normal_vitals_code_green(self):
        res = evaluate_triage_tier(
            systolic=118,
            diastolic=78,
            pulse=72,
            temperature=98.4,
            spo2=99
        )
        self.assertEqual(res["tier"], "Code Green")
        self.assertEqual(res["priority"], 3)


if __name__ == "__main__":
    unittest.main()
