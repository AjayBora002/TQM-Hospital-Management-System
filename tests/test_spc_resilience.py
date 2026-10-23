import unittest
import os
import sys
import tempfile
import csv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sqc")))

from utils.spc_service import calculate_spc_metrics
from api.helpers import row_to_dict, rows_to_list


class TestSpcResilience(unittest.TestCase):
    def test_spc_metrics_with_malformed_csv(self):
        # Create a temp CSV with empty rows, bad counts, and missing dates
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv", newline="") as tf:
            writer = csv.writer(tf)
            writer.writerow(["date", "category", "count", "notes"])
            writer.writerow(["2026-10-01", "Typo", "5", "valid row"])
            writer.writerow(["", "Typo", "3", "missing date"])
            writer.writerow(["2026-10-02", "Omission", "abc", "non-numeric count"])
            writer.writerow(["2026-10-02", "Omission", "4", "valid count"])
            temp_path = tf.name

        try:
            metrics = calculate_spc_metrics(csv_path=temp_path)
            self.assertEqual(metrics["subgroups_count"], 2)
            self.assertIn("2026-10-01", [p["date"] for p in metrics["points"]])
            self.assertIn("2026-10-02", [p["date"] for p in metrics["points"]])
            # Total defects should be 5 + 0 + 4 = 9
            self.assertEqual(metrics["total_defects"], 9)
            self.assertGreater(metrics["center_line"], 0)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_api_helpers_null_safety(self):
        # row_to_dict
        self.assertIsNone(row_to_dict(None))
        self.assertEqual(row_to_dict({"a": 1}), {"a": 1})

        # rows_to_list
        self.assertEqual(rows_to_list(None), [])
        self.assertEqual(rows_to_list([]), [])
        self.assertEqual(rows_to_list([{"id": 1}, None, {"id": 2}]), [{"id": 1}, {"id": 2}])
        self.assertEqual(rows_to_list([{"x": 10}]), [{"x": 10}])


if __name__ == "__main__":
    unittest.main()
