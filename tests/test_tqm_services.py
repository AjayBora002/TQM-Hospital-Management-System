"""
test_tqm_services.py -- Test suite for logging_service and exception_handler.
"""
import sys
import os
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import utils.logging_service as ls
from utils.logging_service import (
    log_audit_event,
    log_error_event,
    log_defect,
)
from utils.exception_handler import safe_operation, ValidationError


class TestTQMServices(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test CSVs to prevent polluting real TQM data
        self.test_dir = tempfile.mkdtemp()
        self.orig_audit = ls.AUDIT_LOG_CSV
        self.orig_error = ls.ERROR_LOG_CSV
        self.orig_checksheet = ls.CHECKSHEET_CSV

        test_audit = os.path.join(self.test_dir, "test_audit.csv")
        test_error = os.path.join(self.test_dir, "test_error.csv")
        test_checksheet = os.path.join(self.test_dir, "test_checksheet.csv")

        ls.AUDIT_LOG_CSV = test_audit
        ls.ERROR_LOG_CSV = test_error
        ls.CHECKSHEET_CSV = test_checksheet

        os.environ["HMS_AUDIT_LOG_CSV"] = test_audit
        os.environ["HMS_ERROR_LOG_CSV"] = test_error
        os.environ["HMS_CHECKSHEET_CSV"] = test_checksheet

    def tearDown(self):
        ls.AUDIT_LOG_CSV = self.orig_audit
        ls.ERROR_LOG_CSV = self.orig_error
        ls.CHECKSHEET_CSV = self.orig_checksheet
        os.environ.pop("HMS_AUDIT_LOG_CSV", None)
        os.environ.pop("HMS_ERROR_LOG_CSV", None)
        os.environ.pop("HMS_CHECKSHEET_CSV", None)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_audit_logging_writes_csv(self):
        log_audit_event("TEST_MODULE", "TEST_ACTION", 999, "SUCCESS", "Unit test description")
        self.assertTrue(os.path.exists(ls.AUDIT_LOG_CSV))
        with open(ls.AUDIT_LOG_CSV, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("TEST_MODULE", content)
            self.assertIn("TEST_ACTION", content)

    def test_error_logging_writes_csv(self):
        err_id = log_error_event("TEST_MODULE", "RuntimeError", "HIGH", "Simulated unit test failure")
        self.assertTrue(err_id.startswith("ERR-"))
        self.assertTrue(os.path.exists(ls.ERROR_LOG_CSV))
        with open(ls.ERROR_LOG_CSV, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn(err_id, content)

    def test_defect_logging_writes_csv(self):
        log_defect("TEST_MODULE", "FormatError", 3, "Test defect remarks")
        self.assertTrue(os.path.exists(ls.CHECKSHEET_CSV))
        with open(ls.CHECKSHEET_CSV, "r", encoding="utf-8") as f:
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
