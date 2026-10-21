"""
test_login_dialog.py -- Unit tests for Desktop GUI Authentication & Role Management.
"""
import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

import config
config.DB_PATH = os.path.join(BASE_DIR, "tests", "test_auth_dialog.db")

from database.db_manager import init_db
from models import user as user_model


class TestLoginDialog(unittest.TestCase):
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

    def test_01_all_roles_authenticated(self):
        admin = user_model.authenticate("admin", "admin123")
        self.assertIsNotNone(admin)
        self.assertEqual(admin["role"], "Admin")

        doctor = user_model.authenticate("doctor", "doctor123")
        self.assertIsNotNone(doctor)
        self.assertEqual(doctor["role"], "Doctor")

        recep = user_model.authenticate("receptionist", "recep123")
        self.assertIsNotNone(recep)
        self.assertEqual(recep["role"], "Receptionist")

    def test_02_invalid_credentials_fail(self):
        self.assertIsNone(user_model.authenticate("admin", "wrongpass"))
        self.assertIsNone(user_model.authenticate("nonexistent", "secret"))


if __name__ == "__main__":
    unittest.main()
