"""
test_extended_hospital_modules.py
Unit tests verifying the 17 new hospital modules and data-driven departments:
  1. Medical Records (MRD)
  2. Mortuary Register
  3. CSSD Cycles
  4. Laundry & Linen
  5. Infection Control Surveillance
  6. Dialysis Scheduling
  7. Maternity & Nursery
  8. Physiotherapy Sessions
  9. Health Packages
  10. Vaccination Register
  11. Referrals Management
  12. Patient Feedback
  13. Telemedicine Appointments
  14. Security Gate Log
  15. Pharmacy Returns
  16. M&M Reviews
  17. Facility Safety Checklists
  18. Departments Data-Driven Updates
"""
import os
import sys
import unittest
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from web_app import app
from database.db_manager import init_db


class TestExtendedHospitalModules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def _login(self, username, password):
        res = self.client.post("/api/auth/login", json={"username": username, "password": password})
        self.assertEqual(res.status_code, 200)

    def test_departments_crud(self):
        """Test listing and updating data-driven departments."""
        self._login("admin", "admin123")
        # List
        res = self.client.get("/api/departments")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreaterEqual(len(data), 50)

        # Update department
        dept_id = data[0]["department_id"]
        res = self.client.put(f"/api/departments/{dept_id}", json={
            "name": data[0]["name"],
            "code": data[0]["code"],
            "type": "Clinical",
            "head_of_dept": "Dr. Lead Specialist",
            "location": "Wing A - Ground Floor",
            "phone": "+91-98765-99999",
            "has_opd": 1,
            "has_ipd": 1,
            "active": 1
        })
        self.assertEqual(res.status_code, 200)

    def test_mrd_workflow(self):
        self._login("mrd_officer", "mrd123")
        # List
        res = self.client.get("/api/medical-records")
        self.assertEqual(res.status_code, 200)
        # Create
        res = self.client.post("/api/medical-records", json={
            "uhid": "UHID-2026-000001",
            "patient_name": "Rohan Sharma",
            "icd_code": "I25.1",
            "diagnosis": "Atherosclerotic heart disease",
            "location_shelf": "Shelf-D1-Bay1"
        })
        self.assertEqual(res.status_code, 201)
        rec_id = res.get_json()["record_id"]
        # Status update
        res = self.client.put(f"/api/medical-records/{rec_id}/status", json={"status": "Issued", "requested_by": "Dr. Rajesh Sharma"})
        self.assertEqual(res.status_code, 200)

    def test_mortuary_workflow(self):
        self._login("mortuary_attendant", "mort123")
        res = self.client.get("/api/mortuary")
        self.assertEqual(res.status_code, 200)
        res = self.client.post("/api/mortuary", json={
            "deceased_uhid": "UHID-2026-000009",
            "patient_name": "Test Decedent",
            "age": 70,
            "gender": "Male",
            "cause_of_death": "Respiratory Failure",
            "date_time_of_death": "2026-10-30 20:00:00",
            "freezer_number": "Freezer-05"
        })
        self.assertEqual(res.status_code, 201)
        case_id = res.get_json()["case_id"]
        res = self.client.put(f"/api/mortuary/{case_id}/status", json={"status": "Released", "claimant_name": "Next of Kin", "id_proof_type": "Passport"})
        self.assertEqual(res.status_code, 200)

    def test_cssd_workflow(self):
        self._login("cssd_tech", "cssd123")
        res = self.client.get("/api/cssd")
        self.assertEqual(res.status_code, 200)
        res = self.client.post("/api/cssd", json={
            "set_name": "Cardiothoracic Cannulation Set",
            "set_code": "SET-CTVS-02",
            "department_name": "Operation Theatre",
            "autoclave_id": "Autoclave-1 (Steam)",
            "cycle_type": "Pre-Vacuum 134C",
            "temp_c": 134.5,
            "pressure_psi": 31.0
        })
        self.assertEqual(res.status_code, 201)
        cycle_id = res.get_json()["cycle_id"]
        res = self.client.put(f"/api/cssd/{cycle_id}/status", json={"status": "Sterile - Released"})
        self.assertEqual(res.status_code, 200)

    def test_laundry_workflow(self):
        self._login("admin", "admin123")
        res = self.client.get("/api/laundry")
        self.assertEqual(res.status_code, 200)
        res = self.client.post("/api/laundry", json={
            "ward_name": "Emergency Bay",
            "linen_type": "Pillow Covers",
            "qty_clean": 50,
            "qty_soiled": 10
        })
        self.assertEqual(res.status_code, 201)
        linen_id = res.get_json()["linen_id"]
        res = self.client.put(f"/api/laundry/{linen_id}/status", json={"status": "In Circulation", "qty_clean": 40, "qty_soiled": 20})
        self.assertEqual(res.status_code, 200)

    def test_infection_control_workflow(self):
        self._login("infection_control", "ic123")
        res = self.client.get("/api/infection-control")
        self.assertEqual(res.status_code, 200)
        res = self.client.post("/api/infection-control", json={
            "uhid": "UHID-2026-000001",
            "patient_name": "Rohan Sharma",
            "infection_type": "CLABSI",
            "organism_isolated": "Klebsiella pneumoniae (KPC)",
            "ward_name": "ICU",
            "isolation_flag": "Contact & Droplet Isolation"
        })
        self.assertEqual(res.status_code, 201)
        surv_id = res.get_json()["surveillance_id"]
        res = self.client.put(f"/api/infection-control/{surv_id}/status", json={"status": "Resolved"})
        self.assertEqual(res.status_code, 200)

    def test_dialysis_workflow(self):
        self._login("doctor", "doctor123")
        res = self.client.get("/api/dialysis")
        self.assertEqual(res.status_code, 200)
        res = self.client.post("/api/dialysis", json={
            "uhid": "UHID-2026-000001",
            "patient_name": "Rohan Sharma",
            "machine_no": "HD-Machine-05",
            "pre_weight": 70.0
        })
        self.assertEqual(res.status_code, 201)
        sess_id = res.get_json()["session_id"]
        res = self.client.put(f"/api/dialysis/{sess_id}/status", json={"status": "Completed", "post_weight": 67.5})
        self.assertEqual(res.status_code, 200)

    def test_maternity_workflow(self):
        self._login("doctor", "doctor123")
        res = self.client.get("/api/maternity")
        self.assertEqual(res.status_code, 200)
        res = self.client.post("/api/maternity", json={
            "mother_uhid": "UHID-2026-000003",
            "mother_name": "Ananya Deshmukh",
            "baby_gender": "Male",
            "birth_weight_kg": 3.4,
            "delivery_type": "Normal Delivery"
        })
        self.assertEqual(res.status_code, 201)
        deliv_id = res.get_json()["delivery_id"]
        res = self.client.put(f"/api/maternity/{deliv_id}/status", json={"status": "Discharged"})
        self.assertEqual(res.status_code, 200)

    def test_physiotherapy_workflow(self):
        self._login("physiotherapist", "physio123")
        res = self.client.get("/api/physiotherapy")
        self.assertEqual(res.status_code, 200)
        res = self.client.post("/api/physiotherapy", json={
            "uhid": "UHID-2026-000001",
            "patient_name": "Rohan Sharma",
            "diagnosis": "Rotator Cuff Tendinitis",
            "protocol": "Isometric exercises, cryotherapy and TENS"
        })
        self.assertEqual(res.status_code, 201)
        sess_id = res.get_json()["session_id"]
        res = self.client.put(f"/api/physiotherapy/{sess_id}/status", json={"status": "Completed"})
        self.assertEqual(res.status_code, 200)

    def test_health_packages_workflow(self):
        self._login("admin", "admin123")
        res = self.client.get("/api/health-packages")
        self.assertEqual(res.status_code, 200)
        res = self.client.post("/api/health-packages", json={
            "package_name": "Diabetic Comprehensive Evaluation",
            f"code": f"PKG-DIAB-{int(time.time() * 1000)}",
            "price": 2499.0,
            "tests_included": "HbA1c, Fasting Glucose, Lipid, Urine Microalbumin, Fundus Exam"
        })
        self.assertEqual(res.status_code, 201)
        pkg_id = res.get_json()["package_id"]
        res = self.client.put(f"/api/health-packages/{pkg_id}/status", json={"active": 1})
        self.assertEqual(res.status_code, 200)

    def test_vaccination_workflow(self):
        self._login("doctor", "doctor123")
        res = self.client.get("/api/vaccination")
        self.assertEqual(res.status_code, 200)
        res = self.client.post("/api/vaccination", json={
            "uhid": "UHID-2026-000001",
            "patient_name": "Rohan Sharma",
            "vaccine_name": "Influenza Quadrivalent",
            "dose_number": 1
        })
        self.assertEqual(res.status_code, 201)
        vac_id = res.get_json()["vac_id"]
        res = self.client.put(f"/api/vaccination/{vac_id}/status", json={"status": "Administered"})
        self.assertEqual(res.status_code, 200)

    def test_referrals_workflow(self):
        self._login("doctor", "doctor123")
        res = self.client.get("/api/referrals")
        self.assertEqual(res.status_code, 200)
        res = self.client.post("/api/referrals", json={
            "uhid": "UHID-2026-000001",
            "patient_name": "Rohan Sharma",
            "partner_hospital": "Apollo Speciality",
            "clinical_reason": "PET-CT scan evaluation"
        })
        self.assertEqual(res.status_code, 201)
        ref_id = res.get_json()["referral_id"]
        res = self.client.put(f"/api/referrals/{ref_id}/status", json={"status": "Accepted"})
        self.assertEqual(res.status_code, 200)

    def test_patient_feedback_workflow(self):
        self._login("quality_mgr", "quality123")
        res = self.client.get("/api/feedback")
        self.assertEqual(res.status_code, 200)
        res = self.client.post("/api/feedback", json={
            "department": "Radiology",
            "rating": 5,
            "comments": "CT scan staff was efficient and kind."
        })
        self.assertEqual(res.status_code, 201)
        fb_id = res.get_json()["feedback_id"]
        res = self.client.put(f"/api/feedback/{fb_id}/status", json={"status": "Resolved", "resolution_notes": "Noted in monthly quality dashboard."})
        self.assertEqual(res.status_code, 200)

    def test_telemedicine_workflow(self):
        self._login("telemed_doc", "tele123")
        res = self.client.get("/api/telemedicine")
        self.assertEqual(res.status_code, 200)
        res = self.client.post("/api/telemedicine", json={
            "uhid": "UHID-2026-000001",
            "patient_name": "Rohan Sharma",
            "appointment_datetime": "2026-11-01 10:00:00"
        })
        self.assertEqual(res.status_code, 201)
        tele_id = res.get_json()["telemed_id"]
        res = self.client.put(f"/api/telemedicine/{tele_id}/status", json={"status": "Completed"})
        self.assertEqual(res.status_code, 200)

    def test_security_gate_workflow(self):
        self._login("security_officer", "sec123")
        res = self.client.get("/api/security-log")
        self.assertEqual(res.status_code, 200)
        res = self.client.post("/api/security-log", json={
            "visitor_name": "Karan Singhania",
            "badge_no": "BADGE-505",
            "entry_gate": "Gate 1 Main"
        })
        self.assertEqual(res.status_code, 201)
        log_id = res.get_json()["log_id"]
        res = self.client.put(f"/api/security-log/{log_id}/status", json={"status": "Exited"})
        self.assertEqual(res.status_code, 200)

    def test_pharmacy_returns_workflow(self):
        self._login("pharmacist", "pharma123")
        res = self.client.get("/api/pharmacy-returns")
        self.assertEqual(res.status_code, 200)
        res = self.client.post("/api/pharmacy-returns", json={
            "uhid": "UHID-2026-000001",
            "medicine_name": "Paracetamol 650mg",
            "qty_returned": 10,
            "refund_amount": 30.0
        })
        self.assertEqual(res.status_code, 201)
        ret_id = res.get_json()["return_id"]
        res = self.client.put(f"/api/pharmacy-returns/{ret_id}/status", json={"status": "Approved"})
        self.assertEqual(res.status_code, 200)

    def test_mm_reviews_workflow(self):
        self._login("quality_mgr", "quality123")
        res = self.client.get("/api/mm-reviews")
        self.assertEqual(res.status_code, 200)
        res = self.client.post("/api/mm-reviews", json={
            "uhid": "UHID-2026-000009",
            "patient_name": "Late Harishankar Bose",
            "primary_diagnosis": "Cardiogenic Shock"
        })
        self.assertEqual(res.status_code, 201)
        rev_id = res.get_json()["review_id"]
        res = self.client.put(f"/api/mm-reviews/{rev_id}/status", json={"status": "Closed"})
        self.assertEqual(res.status_code, 200)

    def test_safety_checklists_workflow(self):
        self._login("admin", "admin123")
        res = self.client.get("/api/safety-checklists")
        self.assertEqual(res.status_code, 200)
        res = self.client.post("/api/safety-checklists", json={
            "o2_manifold_psi": 60.0
        })
        self.assertEqual(res.status_code, 201)
        check_id = res.get_json()["check_id"]
        res = self.client.put(f"/api/safety-checklists/{check_id}/status", json={"status": "Compliant"})
        self.assertEqual(res.status_code, 200)


if __name__ == "__main__":
    unittest.main()
