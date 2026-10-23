import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from utils.exception_handler import ValidationError
from database.db_manager import init_db
from models import quality_audit as audit_model


class TestQualityAuditBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_zero_or_negative_max_score_rejected(self):
        # max_score = 0 must not cause ZeroDivisionError
        with self.assertRaises(ValidationError) as ctx:
            audit_model.add_audit_entry("ICU", "NABH-COP.2", "Emergency cart check", score=0, max_score=0)
        self.assertEqual(ctx.exception.field, "max_score")

        with self.assertRaises(ValidationError) as ctx2:
            audit_model.add_audit_entry("ICU", "NABH-COP.2", "Emergency cart check", score=0, max_score=-5)
        self.assertEqual(ctx2.exception.field, "max_score")

    def test_score_exceeding_max_score_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            audit_model.add_audit_entry("ICU", "NABH-COP.2", "Emergency cart check", score=11, max_score=10)
        self.assertEqual(ctx.exception.field, "score")

        with self.assertRaises(ValidationError) as ctx2:
            audit_model.add_audit_entry("ICU", "NABH-COP.2", "Emergency cart check", score=-2, max_score=10)
        self.assertEqual(ctx2.exception.field, "score")

    def test_empty_required_fields_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            audit_model.add_audit_entry("   ", "NABH-COP.2", "Emergency cart check", score=8, max_score=10)
        self.assertEqual(ctx.exception.field, "department")

        with self.assertRaises(ValidationError) as ctx2:
            audit_model.add_audit_entry("ICU", "   ", "Emergency cart check", score=8, max_score=10)
        self.assertEqual(ctx2.exception.field, "standard_code")

        with self.assertRaises(ValidationError) as ctx3:
            audit_model.add_audit_entry("ICU", "NABH-COP.2", "   ", score=8, max_score=10)
        self.assertEqual(ctx3.exception.field, "criterion")

    def test_invalid_audit_date_format_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            audit_model.add_audit_entry("ICU", "NABH-COP.2", "Cart check", score=9, max_score=10, audit_date="2026/10/23")
        self.assertEqual(ctx.exception.field, "audit_date")

    def test_valid_audit_entry_creation(self):
        entry_id = audit_model.add_audit_entry(
            department="Pathology",
            standard_code="ISO-15189",
            criterion="Daily control run documentation",
            score=10,
            max_score=10,
            audit_date="2026-10-23"
        )
        self.assertGreater(entry_id, 0)


if __name__ == "__main__":
    unittest.main()
