"""
test_web_app.py -- Automated unit and integration tests for HMS Web Application
BBAT104 Quality Goal: Q07 - Improve Data Accuracy
"""
import unittest
import json
from src.web_app import app
from src.database.db_manager import init_db


class TestWebApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = app.test_client()

    def test_index_page(self):
        """Verify the main web app index page renders with all assets."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Hospital Management System", response.data)
        self.assertIn(b"style.css", response.data)
        self.assertIn(b"app.js", response.data)

    def test_static_css(self):
        """Verify the extracted CSS stylesheet is served properly."""
        response = self.client.get("/static/css/style.css")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"--primary:", response.data)

    def test_static_js(self):
        """Verify the extracted client JavaScript file is served properly."""
        response = self.client.get("/static/js/app.js")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"loadDashboardData", response.data)

    def test_dashboard_stats_api(self):
        """Verify the dashboard stats API endpoint returns valid metrics."""
        response = self.client.get("/api/dashboard/stats")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("total_patients", data)
        self.assertIn("total_doctors", data)
        self.assertIn("scheduled_appts", data)
        self.assertIn("available_rooms", data)

    def test_patients_api(self):
        """Verify patients GET and autocomplete endpoints."""
        response = self.client.get("/api/patients")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

        auto_resp = self.client.get("/api/patients/autocomplete?prefix=A")
        self.assertEqual(auto_resp.status_code, 200)
        self.assertIsInstance(auto_resp.get_json(), list)

    def test_doctors_and_rooms_choices_api(self):
        """Verify dropdown choices endpoints."""
        doc_resp = self.client.get("/api/doctors/choices")
        self.assertEqual(doc_resp.status_code, 200)
        self.assertIsInstance(doc_resp.get_json(), list)

        room_resp = self.client.get("/api/rooms/choices?available_only=1")
        self.assertEqual(room_resp.status_code, 200)
        self.assertIsInstance(room_resp.get_json(), list)


if __name__ == "__main__":
    unittest.main()
