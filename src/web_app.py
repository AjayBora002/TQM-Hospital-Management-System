"""
web_app.py -- Local Web Application for Hospital Management System (HMS)
BBAT104 Course Project | Quality Goal: Q07 - Improve Data Accuracy
Student: Ajay Bora | Branch: CSE | Section: B

Serves an interactive modern web UI on http://127.0.0.1:5000 with:
- All 10 System Modules (Dashboard, Patients, Doctors, Appointments, Rooms, Staff, Pharmacy, Billing, Audit Log, Defect Checksheet)
- All 5 Q07 TQM Features:
    1. Input Masking (Phone +91-XXXXX-XXXXX)
    2. Dropdown Lists (Enforced fixed sets)
    3. Auto-Complete (Instant suggestions)
    4. Confirmation Modals (Interactive safeguards)
    5. Audit Logs (Immutable action history)
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
    DEFECT_SEVERITY, DEFECT_STATUS
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
        defect_statuses=DEFECT_STATUS
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
