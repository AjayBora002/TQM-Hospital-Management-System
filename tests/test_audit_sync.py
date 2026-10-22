import unittest
import os
import sys
import tempfile
import csv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from utils.exception_handler import ValidationError
from database.db_manager import init_db
from models import audit as audit_model


class TestAuditSync(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_valid_defect_logging(self):
        defect_id = audit_model.add_defect("Data Entry", "Test data entry mistype", "Low", module="Patients")
        self.assertIsNotNone(defect_id)

        all_defects = audit_model.list_defects()
        matched = [d for d in all_defects if d["defect_id"] == defect_id]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["category"], "Data Entry")
        self.assertEqual(matched[0]["severity"], "Low")
        self.assertEqual(matched[0]["status"], "Open")

    def test_invalid_category_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            audit_model.add_defect("ImaginaryCategory", "Some defect", "Low")
        self.assertEqual(ctx.exception.field, "category")

    def test_invalid_severity_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            audit_model.add_defect("Validation", "Some defect", "Catastrophic")
        self.assertEqual(ctx.exception.field, "severity")

    def test_empty_description_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            audit_model.add_defect("Validation", "   ", "Medium")
        self.assertEqual(ctx.exception.field, "description")

    def test_update_defect_status(self):
        defect_id = audit_model.add_defect("UI", "Button alignment issue", "Low")
        audit_model.update_defect_status(defect_id, "Fixed")

        defects = audit_model.list_defects()
        target = [d for d in defects if d["defect_id"] == defect_id][0]
        self.assertEqual(target["status"], "Fixed")

    def test_update_defect_invalid_status_rejected(self):
        defect_id = audit_model.add_defect("Validation", "Date boundary check", "Medium")
        with self.assertRaises(ValidationError) as ctx:
            audit_model.update_defect_status(defect_id, "NonExistentStatus")
        self.assertEqual(ctx.exception.field, "status")

    def test_dual_tier_checksheet_csv_sync(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", newline="", encoding="utf-8") as tf:
            tf.write("date,module,error_category,count,remarks\n")
            temp_csv = tf.name

        os.environ["HMS_CHECKSHEET_CSV"] = temp_csv
        try:
            audit_model.add_defect("Performance", "Database query slow on join", "Medium", module="Reporting")
            
            with open(temp_csv, "r", encoding="utf-8") as f:
                reader = list(csv.reader(f))
            
            # Must have at least header + 1 logged row
            self.assertGreaterEqual(len(reader), 2)
            last_row = reader[-1]
            self.assertEqual(last_row[1], "Reporting")
            self.assertEqual(last_row[2], "Performance")
            self.assertEqual(last_row[3], "1")
            self.assertIn("Database query slow", last_row[4])
        finally:
            if "HMS_CHECKSHEET_CSV" in os.environ:
                del os.environ["HMS_CHECKSHEET_CSV"]
            if os.path.exists(temp_csv):
                os.remove(temp_csv)


if __name__ == "__main__":
    unittest.main()
