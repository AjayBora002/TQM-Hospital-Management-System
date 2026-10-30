"""
web_app.py -- Local Web Application for Hospital Management System (HMS)
BBAT104 Course Project | Quality Goal: Q07 - Improve Data Accuracy

Serves an interactive modern web UI on http://127.0.0.1:5000 with:
- All System Modules (Dashboard, Departments, Doctors, Patients, Appointments, OPD Queue,
  Nursing Station, Doctor-Nurse Comms, Bed Board, Admissions, Prescriptions, Staff,
  Pharmacy, Billing, Audit Log, Defect Checksheet)
- 21 Role-Based Personas with server-side RBAC
- Real-time Doctor <-> Nurse Communication & Clinical Order Execution
"""
import os
import sys
import secrets
from flask import Flask, render_template, redirect, url_for, session, request as flask_request

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

# ── Secret key: environment variable → persisted file → generated per-run ──
_secret_key = os.environ.get("HMS_SECRET_KEY")
if not _secret_key:
    _key_file = os.path.join(BASE_DIR, "..", ".secret_key")
    if os.path.exists(_key_file):
        with open(_key_file) as _f:
            _secret_key = _f.read().strip()
    else:
        _secret_key = secrets.token_hex(32)
        try:
            with open(_key_file, "w") as _f:
                _f.write(_secret_key)
        except OSError:
            pass  # read-only filesystem — use ephemeral key
app.secret_key = _secret_key

# ── Secure session cookie settings ──
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Initialize database schema and default records
init_db()

# Register modular REST API blueprints
register_api(app)


@app.route("/login")
def login_page():
    # If already logged in, go straight to the app
    if session.get("user_id"):
        return redirect(url_for("index"))
    from api.auth import DEMO_PERSONAS
    demo_enabled = os.environ.get("HMS_DEMO", "0") == "1"
    return render_template(
        "login.html",
        title=APP_TITLE,
        demo_enabled=demo_enabled,
        demo_personas=DEMO_PERSONAS
    )


@app.route("/")
def index():
    # ── Server-side session guard ──
    if not session.get("user_id"):
        next_url = flask_request.url
        return redirect(url_for("login_page") + "?next=" + next_url)
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
