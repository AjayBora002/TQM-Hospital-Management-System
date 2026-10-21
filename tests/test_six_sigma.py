"""
test_six_sigma.py -- Unit tests for TQM Six Sigma DPMO and Process Capability Engine.
"""
import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from utils.sigma_calculator import calculate_sigma_from_dpmo, get_system_process_capability
from database.db_manager import init_db


class TestSixSigma(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
    def test_01_sigma_from_dpmo_benchmarks(self):
        # 6 Sigma benchmark: 3.4 DPMO
        self.assertEqual(calculate_sigma_from_dpmo(3.4), 6.0)
        self.assertEqual(calculate_sigma_from_dpmo(0.0), 6.0)

        # 5 Sigma benchmark: 233 DPMO
        self.assertAlmostEqual(calculate_sigma_from_dpmo(233), 5.0, delta=0.1)

        # 4 Sigma benchmark: 6210 DPMO
        self.assertAlmostEqual(calculate_sigma_from_dpmo(6210), 4.0, delta=0.1)

        # 3 Sigma benchmark: 66807 DPMO
        self.assertAlmostEqual(calculate_sigma_from_dpmo(66807), 3.0, delta=0.1)

        # 2 Sigma benchmark: 308537 DPMO
        self.assertAlmostEqual(calculate_sigma_from_dpmo(308537), 2.0, delta=0.1)

    def test_02_system_process_capability_metrics(self):
        cap = get_system_process_capability()
        self.assertGreater(cap["total_transactions_units"], 0)
        self.assertGreater(cap["total_opportunities"], 0)
        self.assertGreater(cap["defects_observed"], 0)
        self.assertGreater(cap["process_yield_percent"], 90.0)
        self.assertGreater(cap["current_sigma_level"], 3.0)

        # Check baseline comparison
        base = cap["baseline_comparison"]
        self.assertGreater(cap["current_sigma_level"], base["pre_poka_yoke_sigma"])
        self.assertGreater(base["sigma_improvement"], 0.0)
        self.assertGreater(base["error_reduction_percent"], 50.0)


if __name__ == "__main__":
    unittest.main()
