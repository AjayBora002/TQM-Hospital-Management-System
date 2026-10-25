"""
test_institutional_uhid.py -- Unit tests for institutional UHID generation and alignment.
"""
import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

import config
from models import patient as patient_model


class TestInstitutionalUHID(unittest.TestCase):
    def test_format_uhid_standard_integer(self):
        uhid = patient_model.format_uhid(1)
        self.assertEqual(uhid, "UHID-2026-00001")

    def test_format_uhid_large_integer(self):
        uhid = patient_model.format_uhid(425)
        self.assertEqual(uhid, "UHID-2026-00425")

    def test_format_uhid_string_id(self):
        uhid = patient_model.format_uhid("12")
        self.assertEqual(uhid, "UHID-2026-00012")

    def test_format_uhid_none_or_empty(self):
        self.assertEqual(patient_model.format_uhid(None), "")
        self.assertEqual(patient_model.format_uhid(0), "")

    def test_uhid_prefix_configuration(self):
        self.assertTrue(hasattr(config, "UHID_PREFIX"))
        self.assertEqual(config.UHID_PREFIX, "UHID-2026-")


if __name__ == "__main__":
    unittest.main()
