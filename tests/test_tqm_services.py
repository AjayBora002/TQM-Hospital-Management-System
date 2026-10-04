"""
test_tqm_services.py -- Test suite for logging_service and exception_handler.
"""
import sys
import os
import unittest
import csv

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from utils.logging_service import (
    log_audit_event,
    log_error_event,
    log_defect,
    AUDIT_LOG_CSV,
    ERROR_LOG_CSV,
    CHECKSHEET_CSV
)
from utils.exception_handler import safe_operation, ValidationError


class TestTQMServices(unittest.TestCase):
    def test_audit_logging_writes_csv(self):
        log_audit_event("TEST_MODULE", "TEST_ACTION", 999, "SUCCESS", "Unit test description")
        self.assertTrue(os.path.exists(AUDIT_LOG_CSV))
        with open(AUDIT_LOG_CSV, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("TEST_MODULE", content)
            self.assertIn("TEST_ACTION", content)

    def test_error_logging_writes_csv(self):
        err_id = log_error_event("TEST_MODULE", "RuntimeError", "HIGH", "Simulated unit test failure")
        self.assertTrue(err_id.startswith("ERR-"))
        self.assertTrue(os.path.exists(ERROR_LOG_CSV))
        with open(ERROR_LOG_CSV, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn(err_id, content)

    def test_defect_logging_writes_csv(self):
        log_defect("TEST_MODULE", "FormatError", 3, "Test defect remarks")
        self.assertTrue(os.path.exists(CHECKSHEET_CSV))
        with open(CHECKSHEET_CSV, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("FormatError", content)

    def test_safe_operation_decorator(self):
        @safe_operation(module_name="TEST_SAFE")
        def faulty_func():
            raise ValidationError("Invalid test field", field="test_input")

        res = faulty_func()
        self.assertFalse(res["success"])
        self.assertEqual(res["field"], "test_input")
        self.assertIn("Invalid test field", res["error"])


if __name__ == "__main__":
    unittest.main()
