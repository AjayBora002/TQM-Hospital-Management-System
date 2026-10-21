"""
test_quality_audits.py -- Unit tests for NABH & ISO 9001 Hospital Quality Inspection Checklists.
"""
import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

import config
config.DB_PATH = os.path.join(BASE_DIR, "tests", "test_quality_audits.db")

from database.db_manager import init_db
from models import quality_audit as audit_model
from utils.exception_handler import ValidationError


class TestQualityAudits(unittest.TestCase):
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

    def test_01_seed_audits_exist(self):
        audits = audit_model.list_all()
        self.assertGreaterEqual(len(audits), 6)
        codes = [a["standard_code"] for a in audits]
        self.assertIn("NABH-AAC.1", codes)
        self.assertIn("NABH-MOM.3", codes)
        self.assertIn("ISO-9001-8.2", codes)

    def test_02_add_audit_classification(self):
        # 1. Compliant entry (score 9/10)
        id1 = audit_model.add_audit_entry("Laboratory", "NABH-LMS.1", "Equipment calibration and QC check", 9, 10)
        self.assertIsNotNone(id1)

        # 2. Minor Non-conformance (score 6/10)
        id2 = audit_model.add_audit_entry("Housekeeping", "NABH-HIC.4", "Disinfection frequency logging", 6, 10, corrective_action="Deploy digital checklist")
        all_audits = audit_model.list_all()
        a2 = next(a for a in all_audits if a["audit_id"] == id2)
        self.assertEqual(a2["compliance_status"], "Minor Non-Conformance")

        # 3. Major Non-conformance (score 3/10)
        id3 = audit_model.add_audit_entry("Emergency", "NABH-COP.1", "Ambulance oxygen equipment inspection", 3, 10)
        all_audits = audit_model.list_all()
        a3 = next(a for a in all_audits if a["audit_id"] == id3)
        self.assertEqual(a3["compliance_status"], "Major Non-Conformance")

    def test_03_compliance_summary(self):
        summary = audit_model.get_compliance_summary()
        self.assertGreater(summary["total_criteria"], 0)
        self.assertGreater(summary["compliance_percentage"], 50.0)
        self.assertIn("Patient Registration", summary["departments"])
        self.assertGreaterEqual(summary["non_conformances_count"], 1)

    def test_04_score_bounds_validation(self):
        with self.assertRaises(ValidationError):
            audit_model.add_audit_entry("Billing", "ISO-TEST", "Test", score=15, max_score=10)
        with self.assertRaises(ValidationError):
            audit_model.add_audit_entry("Billing", "ISO-TEST", "Test", score=-1, max_score=10)


if __name__ == "__main__":
    unittest.main()
