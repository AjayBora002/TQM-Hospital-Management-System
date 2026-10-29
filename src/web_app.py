"""
web_app.py -- Local Web Application for Hospital Management System (HMS)
BBAT104 Course Project | Quality Goal: Q07 - Improve Data Accuracy
Student: Ajay Bora | Branch: CSE | Section: B

Serves an interactive modern web UI on http://127.0.0.1:5000 with:
- All System Modules (Dashboard, Departments, Doctors, Patients, Appointments, OPD Queue, Nursing Station, Doctor-Nurse Comms, Bed Board, Admissions, Prescriptions, Staff, Pharmacy, Billing, Audit Log, Defect Checksheet)
- All 10 Role Profiles (Admin, Doctor, Receptionist, Nurse, Ward Manager, Lab Tech, Pharmacist, Cashier, Hospital Manager, Patient)
- Real-time Doctor <-> Nurse Communication & Clinical Order Execution
"""
import os
import sys
from flask import Flask, render_template

# Ensure src directory is in Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    APP_TITLE, GENDERS, BLOOD_GROUPS, DEPARTMENTS, APPT_STATUS,
    ROOM_TYPES, ROOM_STATUS, STAFF_ROLES, SHIFTS, PAYMENT_METHODS,
    PAYMENT_STATUS, MEDICINE_CATEGORIES, DEFECT_CATEGORIES,
    DEFECT_SEVERITY, DEFECT_STATUS, ALLERGIES, STANDARD_APPOINTMENT_SLOTS,
    USER_ROLES, DOSAGE_FREQUENCIES, ADMISSION_STATUS,
    DOCTOR_SPECIALIZATIONS, ORDER_TYPES, ORDER_URGENCIES,
    ORDER_STATUSES, TOKEN_STATUSES, MESSAGE_URGENCIES
)
from database.db_manager import init_db
from api import register_api

# Locate templates and static directories relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)
app.secret_key = "hms-tqm-q07-secret-key-2026"

# Initialize database schema and default records
init_db()

# Register modular REST API blueprints
register_api(app)


@app.route("/")
def index():
    return render_template(
        "index.html",
        title=APP_TITLE,
        genders=GENDERS,
        blood_groups=BLOOD_GROUPS,
        departments=DEPARTMENTS,
        doctor_specializations=DOCTOR_SPECIALIZATIONS,
        appt_statuses=APPT_STATUS,
        room_types=ROOM_TYPES,
        room_statuses=ROOM_STATUS,
        staff_roles=STAFF_ROLES,
        shifts=SHIFTS,
        payment_methods=PAYMENT_METHODS,
        payment_statuses=PAYMENT_STATUS,
        medicine_categories=MEDICINE_CATEGORIES,
        defect_categories=DEFECT_CATEGORIES,
        defect_severities=DEFECT_SEVERITY,
        defect_statuses=DEFECT_STATUS,
        allergies=ALLERGIES,
        standard_slots=STANDARD_APPOINTMENT_SLOTS,
        user_roles=USER_ROLES,
        dosage_frequencies=DOSAGE_FREQUENCIES,
        admission_statuses=ADMISSION_STATUS,
        order_types=ORDER_TYPES,
        order_urgencies=ORDER_URGENCIES,
        order_statuses=ORDER_STATUSES,
        token_statuses=TOKEN_STATUSES,
        message_urgencies=MESSAGE_URGENCIES
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
