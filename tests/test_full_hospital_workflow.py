"""
test_full_hospital_workflow.py -- Comprehensive End-to-End Automated Tests for:
1. All 10 Stakeholder Roles & Authentication (Admin, Manager, Recep, Doc, Nurse, Ward Mgr, Lab, Pharma, Cashier, Patient)
2. Hospital Departments & Specialized Doctor Profiles (Qualifications, Fees, OPD Rooms)
3. Outpatient (OPD) Token Queue Engine (Waiting -> Called -> Completed)
4. Doctor-to-Nurse Clinical Orders & Execution Workflow (Ordered -> Acknowledged -> Completed)
5. Doctor <-> Nurse Inter-Professional Messaging & Code Red Alert Broadcast
6. Inpatient Ward Bed Board Matrix, Bed Turnaround & Occupancy Analytics
7. NABH Nursing Shift Handover Protocol
8. Structured Clinical Encounter & SOAP Notes Documentation
"""
import sys
import os
import unittest
import tempfile
import shutil

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import config
import utils.logging_service as ls

config.DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_full_hospital.db")

from database.db_manager import init_db, get_connection
from models import user as user_model
from models import department as dept_model
from models import doctor_profile as doc_profile_model
from models import opd_queue as queue_model
from models import clinical_order as order_model
from models import communication as comm_model
from models import ward_bed as ward_model
from models import shift_handover as handover_model
from models import encounter as encounter_model
from models import patient as patient_model
from models import doctor as doctor_model


class TestFullHospitalWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.orig_audit = ls.AUDIT_LOG_CSV
        ls.AUDIT_LOG_CSV = os.path.join(cls.temp_dir, "test_audit.csv")

        if os.path.exists(config.DB_PATH):
            try:
                os.remove(config.DB_PATH)
            except Exception:
                pass
        init_db()

    @classmethod
    def tearDownClass(cls):
        ls.AUDIT_LOG_CSV = cls.orig_audit
        shutil.rmtree(cls.temp_dir, ignore_errors=True)
        if os.path.exists(config.DB_PATH):
            try:
                os.remove(config.DB_PATH)
            except Exception:
                pass

    def test_01_all_10_roles_authentication(self):
        """Verify distinct authentication and role assignment for all 10 hospital roles."""
        role_credentials = [
            ("admin", "admin123", "Admin"),
            ("hospital_manager", "hosp123", "Hospital Manager"),
            ("receptionist", "recep123", "Receptionist"),
            ("doctor", "doctor123", "Doctor"),
            ("nurse", "nurse123", "Nurse"),
            ("ward_manager", "ward123", "Ward Manager"),
            ("lab_tech", "lab123", "Lab Technician"),
            ("pharmacist", "pharma123", "Pharmacist"),
            ("cashier", "cash123", "Cashier"),
            ("patient", "patient123", "Patient"),
        ]
        for uname, pwd, expected_role in role_credentials:
            user = user_model.authenticate(uname, pwd)
            self.assertIsNotNone(user, f"Authentication failed for {uname}")
            self.assertEqual(user["role"], expected_role, f"Role mismatch for {uname}")

    def test_02_departments_and_specialized_doctors(self):
        """Verify department directory and specialized doctor profiles with credentials and fees."""
        depts = dept_model.list_departments()
        self.assertGreaterEqual(len(depts), 8, "Expected at least 8 hospital departments")
        dept_names = [d["name"] for d in depts]
        self.assertIn("Cardiology", dept_names)
        self.assertIn("Orthopedics", dept_names)
        self.assertIn("General Medicine", dept_names)

        # Query specialized doctors
        docs = doc_profile_model.list_specialized_doctors()
        self.assertGreaterEqual(len(docs), 1)
        lead_doc = docs[0]
        self.assertIn("specialization", lead_doc)
        self.assertIn("qualifications", lead_doc)
        self.assertIn("consultation_fee", lead_doc)
        self.assertIn("room_number", lead_doc)
        self.assertGreater(lead_doc["consultation_fee"], 0)

    def test_03_opd_token_queue_lifecycle(self):
        """Verify OPD queue: token generation, waiting status, call patient, complete consultation."""
        p_id = patient_model.add("Harish Patel", "Male", "1990-04-15", "O+", "9876543220", "Delhi")
        d_id = 1

        # 1. Generate Token
        token_info = queue_model.generate_token(p_id, d_id, priority="Urgent")
        self.assertIn("token_number", token_info)
        self.assertGreater(token_info["token_number"], 0)
        q_id = token_info.get("queue_id")

        # 2. Check today's queue
        queue = queue_model.get_today_queue(doctor_id=d_id)
        self.assertGreaterEqual(len(queue), 1)
        target = [q for q in queue if q["patient_id"] == p_id][0]
        self.assertEqual(target["priority"], "Urgent")
        self.assertEqual(target["status"], "Waiting")

        # 3. Doctor calls token
        if q_id:
            res = queue_model.call_patient(q_id)
            self.assertTrue(res)
            # 4. Doctor completes consultation
            res_comp = queue_model.complete_consultation(q_id)
            self.assertTrue(res_comp)

    def test_04_doctor_to_nurse_clinical_orders(self):
        """Verify Doctor -> Nurse workflow: STAT order creation, acknowledgment, execution."""
        p_id = patient_model.add("Kiran Sharma", "Female", "1982-08-10", "A+", "9876543221", "Delhi")
        d_id = 1

        # 1. Doctor creates STAT medication order
        order_id = order_model.create_order(
            patient_id=p_id,
            doctor_id=d_id,
            doctor_name="Dr. Rajesh Sharma",
            order_type="Medication",
            order_text="Administer IV Ondansetron 4mg STAT for severe nausea",
            urgency="STAT (Immediate)",
            ward_id=1,
            bed_number="CCW-Bed-01"
        )
        self.assertGreater(order_id, 0)

        # 2. Nurse views pending orders
        pending = order_model.list_orders(patient_id=p_id, status="Ordered")
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["urgency"], "STAT (Immediate)")

        # 3. Nurse acknowledges order
        ack_res = order_model.acknowledge_order(order_id, nurse_name="Sister Sunita Patel")
        self.assertTrue(ack_res)

        # 4. Nurse administers medication and completes order
        comp_res = order_model.complete_order(order_id, nurse_name="Sister Sunita Patel", execution_notes="Administered IV at 20:30, vitals stable")
        self.assertTrue(comp_res)

        # 5. Verify order status is Completed
        all_orders = order_model.list_orders(patient_id=p_id)
        self.assertEqual(all_orders[0]["status"], "Completed")
        self.assertIn("Sister Sunita Patel", all_orders[0]["completed_by"])

    def test_05_doctor_nurse_messaging_and_codered_alert(self):
        """Verify inter-professional communication and physiological Code Red alert broadcast."""
        p_id = patient_model.add("Naveen Joshi", "Male", "1975-01-20", "B+", "9876543222", "Delhi")

        # 1. Nurse sends clinical query to doctor
        msg_id = comm_model.send_message(
            sender_user_id=4,
            sender_name="Sister Sunita Patel",
            sender_role="Nurse",
            recipient_role="Doctor",
            subject="SpO2 Observation in CCW-Bed-01",
            message_body="Patient breathing comfortably on 2L O2. Current SpO2 96%.",
            urgency="Normal",
            patient_id=p_id
        )
        self.assertGreater(msg_id, 0)

        # 2. Verify message in doctor's feed
        msgs = comm_model.list_messages(role="Doctor")
        self.assertGreaterEqual(len(msgs), 1)
        msg_subjects = [m["subject"] for m in msgs]
        self.assertIn("SpO2 Observation in CCW-Bed-01", msg_subjects)

        # 3. Broadcast Code Red Emergency Alert
        alert_id = comm_model.broadcast_vitals_alert(
            patient_id=p_id,
            vital_summary="SpO2: 84%, Pulse: 135 bpm, BP: 70/40 mmHg (Severe Shock)",
            sender_name="Sister Sunita Patel",
            sender_role="Nurse"
        )
        self.assertGreater(alert_id, 0)
        alerts = comm_model.list_messages(limit=10)
        code_reds = [m for m in alerts if m["urgency"] == "Code Red"]
        self.assertGreaterEqual(len(code_reds), 1)

    def test_06_ward_bed_matrix_and_turnaround(self):
        """Verify bed board matrix, bed status changes, and occupancy calculations."""
        wards = ward_model.list_wards()
        self.assertGreaterEqual(len(wards), 1)

        # Query bed board matrix
        beds = ward_model.get_ward_bed_matrix()
        self.assertGreaterEqual(len(beds), 1)
        first_bed = beds[0]
        self.assertIn("room_number", first_bed)
        self.assertIn("status", first_bed)

        # Update bed status (Turnover Poka-Yoke: Available -> Cleaning -> Available)
        bed_id = first_bed["room_id"]
        ward_model.update_bed_status(bed_id, "Cleaning / Sanitizing")
        conn = get_connection()
        s1 = conn.execute("SELECT status FROM rooms WHERE room_id = ?", (bed_id,)).fetchone()["status"]
        self.assertEqual(s1, "Cleaning / Sanitizing")

        ward_model.update_bed_status(bed_id, "Available")
        s2 = conn.execute("SELECT status FROM rooms WHERE room_id = ?", (bed_id,)).fetchone()["status"]
        self.assertEqual(s2, "Available")
        conn.close()

        # Occupancy stats
        occ = ward_model.get_ward_occupancy_stats()
        self.assertIn("total_beds", occ)
        self.assertIn("occupancy_rate_percent", occ)

    def test_07_nabh_shift_handover(self):
        """Verify NABH nursing shift handover logging and auditing."""
        h_id = handover_model.create_handover(
            department="Cardiology",
            shift_from="Morning",
            shift_to="Evening",
            outgoing_nurse="Sister Sunita Patel",
            incoming_nurse="Nurse Rekha Sharma",
            critical_patients="Bed 101: post-angina, stable; Bed 102: SpO2 watch",
            pending_orders="Troponin-I sample at 21:00",
            general_notes="Defibrillator battery tested OK"
        )
        self.assertGreater(h_id, 0)

        handovers = handover_model.list_handovers(department="Cardiology")
        self.assertGreaterEqual(len(handovers), 1)
        self.assertEqual(handovers[0]["outgoing_nurse_name"], "Sister Sunita Patel")
        self.assertEqual(handovers[0]["incoming_nurse_name"], "Nurse Rekha Sharma")

    def test_08_clinical_encounter_soap_notes(self):
        """Verify outpatient clinical encounter documentation with SOAP notes."""
        p_id = patient_model.add("Tarun Kapoor", "Male", "1988-12-05", "AB+", "9876543223", "Delhi")
        d_id = 1

        enc_id = encounter_model.create_encounter(
            patient_id=p_id,
            doctor_id=d_id,
            chief_complaint="Chest discomfort on exertion for 3 days",
            diagnosis="Exertional Angina Pectoris (I20.9)",
            history_illness="No prior cardiac history, non-smoker, hypertensive",
            examination="BP: 140/90 mmHg, S1/S2 audible, no murmurs",
            plan="Start Tab Sorbitrate 5mg SOS, Aspirin 75mg, ECG & ECHO scheduled",
            doctor_notes="Counselled on lifestyle modifications and red-flag symptoms",
            follow_up_date="2026-11-05"
        )
        self.assertGreater(enc_id, 0)

        history = encounter_model.get_patient_encounters(p_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["diagnosis"], "Exertional Angina Pectoris (I20.9)")
        self.assertEqual(history[0]["follow_up_date"], "2026-11-05")


if __name__ == "__main__":
    unittest.main()

