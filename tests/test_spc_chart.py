"""
test_spc_chart.py -- Unit tests for Statistical Process Control (SPC) Shewhart c-Chart Engine.
"""
import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from utils.spc_service import calculate_spc_metrics
from sqc.spc_chart import generate_spc_chart


class TestSPCChart(unittest.TestCase):
    def test_01_spc_metrics_calculation(self):
        metrics = calculate_spc_metrics()
        self.assertGreater(metrics["subgroups_count"], 0)
        self.assertGreater(metrics["total_defects"], 0)
        self.assertGreater(metrics["center_line"], 0.0)

        # Statistical boundary proofs
        self.assertGreater(metrics["ucl"], metrics["center_line"])
        self.assertGreaterEqual(metrics["center_line"], metrics["lcl"])
        self.assertGreaterEqual(metrics["lcl"], 0.0)
        self.assertGreater(metrics["ucl"], metrics["uwl"])

    def test_02_post_intervention_stabilization(self):
        metrics = calculate_spc_metrics()
        # Last 3 days post Poka-Yoke should be well within control limits
        last_three = metrics["points"][-3:]
        for pt in last_three:
            self.assertEqual(pt["status"], "In Control")
            self.assertFalse(pt["is_out_of_control"])

    def test_03_chart_generation(self):
        generate_spc_chart()
        chart_png = os.path.join(BASE_DIR, "sqc", "spc_control_chart.png")
        metrics_csv = os.path.join(BASE_DIR, "TQM", "data", "spc_metrics.csv")
        self.assertTrue(os.path.exists(chart_png))
        self.assertTrue(os.path.exists(metrics_csv))
        self.assertGreater(os.path.getsize(chart_png), 1000)


if __name__ == "__main__":
    unittest.main()
