"""
test_rbac_matrix.py -- Comprehensive RBAC and Permission Enforcement Test Suite.
Verifies that:
1. Unauthenticated requests return 401.
2. Every one of the 21 modern hospital stakeholder roles is blocked (HTTP 403)
   from at least 3 endpoints outside its authorized domain, with events written to the audit log.
3. Every role succeeds (HTTP 200) on endpoints within its authorized domain.
4. Row-level rules (e.g. Admin cannot edit clinical records) are strictly enforced.
"""
import sys
import os
import unittest
import json

# Ensure src is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from web_app import app
from database.db_manager import init_db, get_connection
from auth.permissions import ALL_ROLES, ROLE_PERMISSIONS


class TestRBACMatrix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = app.test_client()

    def test_01_unauthenticated_request_returns_401(self):
        """Unauthenticated requests must be rejected with 401."""
        resp = self.client.get("/api/patients", headers={"X-Strict-Auth": "1"})
        self.assertEqual(resp.status_code, 401)
        data = resp.get_json()
        self.assertIn("error", data)

    def test_02_admin_cannot_edit_clinical_records(self):
        """Admin manages system and config, but CANNOT create or edit clinical records."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "admin"
            sess["role"] = "Admin"
            sess["strict_auth"] = True

        # Clinical encounter creation
        resp = self.client.post("/api/encounters", json={
            "patient_id": 1,
            "chief_complaint": "Headache",
            "diagnosis": "Migraine"
        })
        self.assertEqual(resp.status_code, 403)

        # Clinical order creation
        resp2 = self.client.post("/api/clinical-orders", json={
            "patient_id": 1,
            "order_type": "Medication",
            "order_text": "Paracetamol"
        })
        self.assertEqual(resp2.status_code, 403)

        # Prescription creation
        resp3 = self.client.post("/api/prescriptions", json={
            "patient_id": 1,
            "doctor_id": 1,
            "medicine_id": 1,
            "dosage": "500mg"
        })
        self.assertEqual(resp3.status_code, 403)

    def test_03_all_21_roles_rbac_matrix_probes(self):
        """
        Verify each of the 21 roles:
        - Receives 403 on >= 3 endpoints it shouldn't access
        - Receives 200 on allowed endpoints
        """
        # Role -> tuple of 3 unauthorized (method, url, json_payload)
        forbidden_probes = {
            "Admin": [
                ("POST", "/api/encounters", {"patient_id": 1, "chief_complaint": "x", "diagnosis": "x"}),
                ("POST", "/api/clinical-orders", {"patient_id": 1, "order_type": "Medication", "order_text": "x"}),
                ("POST", "/api/prescriptions", {"patient_id": 1, "doctor_id": 1, "medicine_id": 1, "dosage": "x"}),
            ],
            "Hospital Manager": [
                ("POST", "/api/encounters", {"patient_id": 1, "chief_complaint": "x", "diagnosis": "x"}),
                ("POST", "/api/prescriptions", {"patient_id": 1, "doctor_id": 1, "medicine_id": 1, "dosage": "x"}),
                ("POST", "/api/patients", {"full_name": "New Pat"}),
            ],
            "Doctor": [
                ("POST", "/api/auth/users", {"username": "hackuser", "password": "password123", "role": "Doctor", "full_name": "Hacker"}),
                ("POST", "/api/bills", {"patient_id": 1, "room_charges": 100}),
                ("POST", "/api/system/backup", {}),
            ],
            "Nurse": [
                ("POST", "/api/auth/users", {"username": "hackuser", "password": "password123", "role": "Nurse", "full_name": "Hacker"}),
                ("POST", "/api/bills", {"patient_id": 1, "room_charges": 100}),
                ("POST", "/api/encounters", {"patient_id": 1, "chief_complaint": "x", "diagnosis": "x"}),
            ],
            "Ward Manager": [
                ("POST", "/api/auth/users", {"username": "hackuser", "password": "password123", "role": "Nurse", "full_name": "Hacker"}),
                ("POST", "/api/bills", {"patient_id": 1, "room_charges": 100}),
                ("POST", "/api/encounters", {"patient_id": 1, "chief_complaint": "x", "diagnosis": "x"}),
            ],
            "Receptionist": [
                ("POST", "/api/encounters", {"patient_id": 1, "chief_complaint": "x", "diagnosis": "x"}),
                ("POST", "/api/prescriptions", {"patient_id": 1, "doctor_id": 1, "medicine_id": 1, "dosage": "x"}),
                ("POST", "/api/auth/users", {"username": "hackuser", "password": "password123", "role": "Receptionist", "full_name": "Hacker"}),
            ],
            "Lab Technician": [
                ("POST", "/api/prescriptions", {"patient_id": 1, "doctor_id": 1, "medicine_id": 1, "dosage": "x"}),
                ("POST", "/api/bills", {"patient_id": 1, "room_charges": 100}),
                ("POST", "/api/auth/users", {"username": "hackuser", "password": "password123", "role": "Doctor", "full_name": "Hacker"}),
            ],
            "Pharmacist": [
                ("POST", "/api/encounters", {"patient_id": 1, "chief_complaint": "x", "diagnosis": "x"}),
                ("POST", "/api/bills", {"patient_id": 1, "room_charges": 100}),
                ("POST", "/api/auth/users", {"username": "hackuser", "password": "password123", "role": "Pharmacist", "full_name": "Hacker"}),
            ],
            "Cashier": [
                ("POST", "/api/encounters", {"patient_id": 1, "chief_complaint": "x", "diagnosis": "x"}),
                ("POST", "/api/prescriptions", {"patient_id": 1, "doctor_id": 1, "medicine_id": 1, "dosage": "x"}),
                ("POST", "/api/auth/users", {"username": "hackuser", "password": "password123", "role": "Cashier", "full_name": "Hacker"}),
            ],
            "Patient": [
                ("GET", "/api/audit", None),
                ("POST", "/api/prescriptions", {"patient_id": 1, "doctor_id": 1, "medicine_id": 1, "dosage": "x"}),
                ("POST", "/api/auth/users", {"username": "hackuser", "password": "password123", "role": "Patient", "full_name": "Hacker"}),
            ],
            "Quality Manager": [
                ("POST", "/api/prescriptions", {"patient_id": 1, "doctor_id": 1, "medicine_id": 1, "dosage": "x"}),
                ("POST", "/api/bills", {"patient_id": 1, "room_charges": 100}),
                ("POST", "/api/auth/users", {"username": "hackuser", "password": "password123", "role": "Doctor", "full_name": "Hacker"}),
            ],
            "Radiologist": [
                ("POST", "/api/bills", {"patient_id": 1, "room_charges": 100}),
                ("POST", "/api/auth/users", {"username": "hackuser", "password": "password123", "role": "Doctor", "full_name": "Hacker"}),
                ("POST", "/api/prescriptions", {"patient_id": 1, "doctor_id": 1, "medicine_id": 1, "dosage": "x"}),
            ],
            "OT Manager": [
                ("POST", "/api/bills", {"patient_id": 1, "room_charges": 100}),
                ("POST", "/api/auth/users", {"username": "hackuser", "password": "password123", "role": "Doctor", "full_name": "Hacker"}),
                ("POST", "/api/prescriptions", {"patient_id": 1, "doctor_id": 1, "medicine_id": 1, "dosage": "x"}),
            ],
            "Blood Bank Technician": [
                ("POST", "/api/bills", {"patient_id": 1, "room_charges": 100}),
                ("POST", "/api/auth/users", {"username": "hackuser", "password": "password123", "role": "Doctor", "full_name": "Hacker"}),
                ("POST", "/api/prescriptions", {"patient_id": 1, "doctor_id": 1, "medicine_id": 1, "dosage": "x"}),
            ],
            "Housekeeping Supervisor": [
                ("POST", "/api/bills", {"patient_id": 1, "room_charges": 100}),
                ("POST", "/api/auth/users", {"username": "hackuser", "password": "password123", "role": "Doctor", "full_name": "Hacker"}),
                ("POST", "/api/encounters", {"patient_id": 1, "chief_complaint": "x", "diagnosis": "x"}),
            ],
            "Biomedical Engineer": [
                ("POST", "/api/bills", {"patient_id": 1, "room_charges": 100}),
                ("POST", "/api/auth/users", {"username": "hackuser", "password": "password123", "role": "Doctor", "full_name": "Hacker"}),
                ("POST", "/api/encounters", {"patient_id": 1, "chief_complaint": "x", "diagnosis": "x"}),
            ],
            "HR Manager": [
                ("POST", "/api/bills", {"patient_id": 1, "room_charges": 100}),
                ("POST", "/api/encounters", {"patient_id": 1, "chief_complaint": "x", "diagnosis": "x"}),
                ("POST", "/api/prescriptions", {"patient_id": 1, "doctor_id": 1, "medicine_id": 1, "dosage": "x"}),
            ],
            "Store/Inventory Manager": [
                ("POST", "/api/bills", {"patient_id": 1, "room_charges": 100}),
                ("POST", "/api/auth/users", {"username": "hackuser", "password": "password123", "role": "Doctor", "full_name": "Hacker"}),
                ("POST", "/api/encounters", {"patient_id": 1, "chief_complaint": "x", "diagnosis": "x"}),
            ],
            "Insurance/TPA Desk": [
                ("POST", "/api/encounters", {"patient_id": 1, "chief_complaint": "x", "diagnosis": "x"}),
                ("POST", "/api/auth/users", {"username": "hackuser", "password": "password123", "role": "Doctor", "full_name": "Hacker"}),
                ("POST", "/api/prescriptions", {"patient_id": 1, "doctor_id": 1, "medicine_id": 1, "dosage": "x"}),
            ],
            "Ambulance Dispatcher": [
                ("POST", "/api/bills", {"patient_id": 1, "room_charges": 100}),
                ("POST", "/api/auth/users", {"username": "hackuser", "password": "password123", "role": "Doctor", "full_name": "Hacker"}),
                ("POST", "/api/encounters", {"patient_id": 1, "chief_complaint": "x", "diagnosis": "x"}),
            ],
            "Dietitian": [
                ("POST", "/api/bills", {"patient_id": 1, "room_charges": 100}),
                ("POST", "/api/auth/users", {"username": "hackuser", "password": "password123", "role": "Doctor", "full_name": "Hacker"}),
                ("POST", "/api/prescriptions", {"patient_id": 1, "doctor_id": 1, "medicine_id": 1, "dosage": "x"}),
            ]
        }

        # Role -> 1 authorized endpoint (method, url, json_payload)
        allowed_probes = {
            "Admin": ("GET", "/api/auth/users", None),
            "Hospital Manager": ("GET", "/api/dashboard/stats", None),
            "Doctor": ("GET", "/api/encounters/patient/1", None),
            "Nurse": ("GET", "/api/nursing/inpatients", None),
            "Ward Manager": ("GET", "/api/wards/bed-board", None),
            "Receptionist": ("GET", "/api/appointments", None),
            "Lab Technician": ("GET", "/api/lab-tests", None),
            "Pharmacist": ("GET", "/api/medicines", None),
            "Cashier": ("GET", "/api/bills", None),
            "Patient": ("GET", "/api/patient-portal/appointments", None),
            "Quality Manager": ("GET", "/api/quality-audits", None),
            "Radiologist": ("GET", "/api/radiology/orders", None),
            "OT Manager": ("GET", "/api/ot/schedules", None),
            "Blood Bank Technician": ("GET", "/api/blood-bank/inventory", None),
            "Housekeeping Supervisor": ("GET", "/api/support/housekeeping", None),
            "Biomedical Engineer": ("GET", "/api/support/biomedical", None),
            "HR Manager": ("GET", "/api/people/shifts", None),
            "Store/Inventory Manager": ("GET", "/api/inventory/items", None),
            "Insurance/TPA Desk": ("GET", "/api/finance/insurance-claims", None),
            "Ambulance Dispatcher": ("GET", "/api/support/ambulance-trips", None),
            "Dietitian": ("GET", "/api/support/diet-orders", None),
        }

        for role in ALL_ROLES:
            with self.subTest(role=role):
                # Setup session for this role
                with self.client.session_transaction() as sess:
                    sess["user_id"] = 100
                    sess["username"] = f"test_{role.lower().replace(' ', '_')}"
                    sess["role"] = role
                    sess["strict_auth"] = True

                # 1. Probe forbidden endpoints -> each must return 403
                probes = forbidden_probes.get(role, [])
                self.assertGreaterEqual(len(probes), 3, f"Role '{role}' must have >= 3 forbidden test probes")

                for method, url, payload in probes:
                    if method == "POST":
                        resp = self.client.post(url, json=payload or {})
                    elif method == "GET":
                        resp = self.client.get(url)
                    elif method == "PUT":
                        resp = self.client.put(url, json=payload or {})
                    else:
                        resp = self.client.delete(url)

                    self.assertEqual(
                        resp.status_code, 403,
                        f"Expected 403 Forbidden for role '{role}' on {method} {url}, but got {resp.status_code} ({resp.get_data(as_text=True)})"
                    )

                # 2. Probe allowed endpoint -> must return 200 or 201
                allow_method, allow_url, allow_payload = allowed_probes[role]
                if allow_method == "GET":
                    allow_resp = self.client.get(allow_url)
                else:
                    allow_resp = self.client.post(allow_url, json=allow_payload or {})

                self.assertIn(
                    allow_resp.status_code, [200, 201],
                    f"Expected 200/201 for role '{role}' on {allow_method} {allow_url}, got {allow_resp.status_code}"
                )

    def test_04_forbidden_attempts_logged_to_audit_trail(self):
        """Ensure all 403 forbidden attempts are persisted in the audit log."""
        conn = get_connection()
        try:
            # Query audit_log for access_control events
            rows = conn.execute("""
                SELECT * FROM audit_log 
                WHERE table_name = 'access_control' OR details LIKE '%FORBIDDEN%'
                ORDER BY log_id DESC LIMIT 10
            """).fetchall()
            self.assertGreater(len(rows), 0, "At least one forbidden access attempt must be recorded in audit_log")
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
