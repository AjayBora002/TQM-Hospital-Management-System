"""
auth.py -- REST API Blueprint for Authentication, Password Management, and RBAC Me Endpoint.
"""
import time
import os
from flask import Blueprint, request, jsonify, session
from models import user as user_model
from auth.permissions import get_user_permissions, require_permission, SESSION_IDLE_TIMEOUT_SECONDS
from utils.exception_handler import ValidationError
from database.db_manager import get_connection, log_audit

auth_bp = Blueprint("auth", __name__)


# 21 Demo Account personas available in Demo/Dev Mode
DEMO_PERSONAS = [
    {"username": "admin", "role": "Admin", "name": "Dr. Ajay Bora (System Admin)", "password": "admin123", "domain": "Administration"},
    {"username": "hospital_manager", "role": "Hospital Manager", "name": "Dr. Sunita Rao (Medical Supt.)", "password": "hosp123", "domain": "Hospital Oversight"},
    {"username": "doctor", "role": "Doctor", "name": "Dr. Rajesh Sharma (Lead Cardiologist)", "password": "doctor123", "domain": "Clinical Consultation"},
    {"username": "nurse", "role": "Nurse", "name": "Sister Sunita Patel (Head Nurse)", "password": "nurse123", "domain": "Nursing Station & MAR"},
    {"username": "ward_manager", "role": "Ward Manager", "name": "Vikram Joshi (Ward Supervisor)", "password": "ward123", "domain": "Inpatient Beds"},
    {"username": "receptionist", "role": "Receptionist", "name": "Priya Verma (Front Desk Lead)", "password": "recep123", "domain": "Front Office & Queue"},
    {"username": "lab_tech", "role": "Lab Technician", "name": "Anil Kumar (Sr. Lab Tech)", "password": "lab123", "domain": "Laboratory & LIS"},
    {"username": "pharmacist", "role": "Pharmacist", "name": "Meena Iyer (Chief Pharmacist)", "password": "pharma123", "domain": "Pharmacy & Dispensing"},
    {"username": "cashier", "role": "Cashier", "name": "Ramesh Gupta (Billing Officer)", "password": "cash123", "domain": "Finance & Cashier"},
    {"username": "patient", "role": "Patient", "name": "Rohan Sharma (Patient)", "password": "patient123", "domain": "Patient Portal"},
    {"username": "quality_mgr", "role": "Quality Manager", "name": "Dr. Ananya Roy (NABH Lead)", "password": "quality123", "domain": "Quality & Governance"},
    {"username": "radiologist", "role": "Radiologist", "name": "Dr. Deepak Varma (Radiologist)", "password": "radio123", "domain": "Radiology & Imaging"},
    {"username": "ot_mgr", "role": "OT Manager", "name": "Dr. Sanjay Malhotra (OT Lead)", "password": "ot123", "domain": "Operation Theatre"},
    {"username": "blood_tech", "role": "Blood Bank Technician", "name": "Kavita Nair (Blood Officer)", "password": "blood123", "domain": "Blood Bank"},
    {"username": "housekeeping_sup", "role": "Housekeeping Supervisor", "name": "Mohan Lal (Sanitation Sup.)", "password": "clean123", "domain": "Housekeeping"},
    {"username": "biomed_eng", "role": "Biomedical Engineer", "name": "Eng. Suresh Nair (BioMed)", "password": "biomed123", "domain": "Medical Equipment"},
    {"username": "hr_mgr", "role": "HR Manager", "name": "Pooja Hegde (HR Director)", "password": "hr123", "domain": "Staff & Roster"},
    {"username": "store_mgr", "role": "Store/Inventory Manager", "name": "Alok Mathur (Stores)", "password": "store123", "domain": "Stores & Consumables"},
    {"username": "tpa_desk", "role": "Insurance/TPA Desk", "name": "Neha Kothari (TPA Lead)", "password": "tpa123", "domain": "Insurance & Claims"},
    {"username": "ambulance_dispatch", "role": "Ambulance Dispatcher", "name": "Gopal Singh (EMS Lead)", "password": "ems123", "domain": "Fleet & Dispatch"},
    {"username": "dietitian", "role": "Dietitian", "name": "Dt. Shalini Menon (Dietitian)", "password": "diet123", "domain": "Diet & Nutrition"}
]


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        user = user_model.authenticate(username, password)
    except ValidationError as err:
        return jsonify({"error": err.message, "field": err.field}), 400

    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    # Establish secure session
    session.clear()
    session["user_id"] = user["user_id"]
    session["username"] = user["username"]
    session["role"] = user["role"]
    session["full_name"] = user["full_name"]
    session["last_activity"] = time.time()

    # Log successful login event
    try:
        conn = get_connection()
        try:
            log_audit(
                conn=conn,
                table_name="users",
                record_id=user["user_id"],
                action="UPDATE",
                details=f"User '{user['username']}' logged in successfully (Role: {user['role']})",
                user=user["username"]
            )
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        print(f"[Login Audit Log Error] {e}")

    permissions = get_user_permissions(user["role"])

    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": user,
        "permissions": permissions,
        "timeout_seconds": SESSION_IDLE_TIMEOUT_SECONDS
    }), 200


@auth_bp.route("/auth/logout", methods=["POST"])
def logout():
    username = session.get("username", "anonymous")
    user_id = session.get("user_id")

    if user_id:
        try:
            conn = get_connection()
            try:
                log_audit(
                    conn=conn,
                    table_name="users",
                    record_id=user_id,
                    action="UPDATE",
                    details=f"User '{username}' logged out",
                    user=username
                )
                conn.commit()
            finally:
                conn.close()
        except Exception:
            pass

    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/auth/me", methods=["GET"])
def get_current_session_info():
    """
    Returns the currently authenticated user and complete permissions dictionary.
    Checks 15-minute idle timeout.
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({
            "authenticated": False,
            "user": None,
            "permissions": {}
        }), 200

    now = time.time()
    last_act = session.get("last_activity")
    if last_act and (now - last_act > SESSION_IDLE_TIMEOUT_SECONDS):
        session.clear()
        return jsonify({
            "authenticated": False,
            "timed_out": True,
            "message": "Session timed out due to 15 minutes of inactivity",
            "user": None,
            "permissions": {}
        }), 200

    # Refresh last activity
    session["last_activity"] = now

    user = user_model.get_by_id(user_id)
    if not user:
        session.clear()
        return jsonify({
            "authenticated": False,
            "user": None,
            "permissions": {}
        }), 200

    role = user["role"]
    permissions = get_user_permissions(role)

    return jsonify({
        "authenticated": True,
        "user": user,
        "role": role,
        "permissions": permissions,
        "idle_timeout_seconds": SESSION_IDLE_TIMEOUT_SECONDS,
        "expires_in_seconds": int(SESSION_IDLE_TIMEOUT_SECONDS - (time.time() - now))
    }), 200


@auth_bp.route("/auth/current", methods=["GET"])
def current_user():
    """
    Returns user details if authenticated.
    No silent Admin fallback!
    """
    user_id = session.get("user_id")
    if user_id:
        user = user_model.get_by_id(user_id)
        if user:
            return jsonify({"user": user, "authenticated": True}), 200

    return jsonify({"user": None, "authenticated": False}), 200


@auth_bp.route("/auth/change-password", methods=["POST"])
def change_password():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication required", "status_code": 401}), 401

    data = request.get_json() or {}
    curr_pw = data.get("current_password", "")
    new_pw = data.get("new_password", "")

    try:
        user_model.change_password(user_id, curr_pw, new_pw)
        return jsonify({"message": "Password changed successfully"}), 200
    except ValidationError as err:
        return jsonify({"error": err.message, "field": err.field}), 400


@auth_bp.route("/auth/admin-reset-password", methods=["POST"])
@require_permission("admin", "edit")
def admin_reset_password():
    data = request.get_json() or {}
    target_username = data.get("username", "")
    new_pw = data.get("new_password", "")
    performed_by = session.get("username", "admin")

    try:
        user_model.admin_reset_password(target_username, new_pw, performed_by)
        return jsonify({"message": f"Password reset successfully for user '{target_username}'"}), 200
    except ValidationError as err:
        return jsonify({"error": err.message, "field": err.field}), 400


@auth_bp.route("/auth/demo-accounts", methods=["GET"])
def get_demo_accounts():
    """Returns demo accounts for quick role switching when HMS_DEMO=1."""
    demo_enabled = os.environ.get("HMS_DEMO", "1") != "0"
    if not demo_enabled:
        return jsonify({"enabled": False, "accounts": []}), 200

    return jsonify({
        "enabled": True,
        "accounts": DEMO_PERSONAS
    }), 200


@auth_bp.route("/auth/users", methods=["GET"])
@require_permission("admin", "view")
def list_users():
    users = user_model.list_users()
    return jsonify(users), 200


@auth_bp.route("/auth/users", methods=["POST"])
@require_permission("admin", "create")
def create_new_user():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    role = data.get("role", "")
    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip()
    performed_by = session.get("username", "admin")

    try:
        user_id = user_model.create_user(username, password, role, full_name, email, performed_by)
        return jsonify({"message": f"User '{username}' created successfully", "user_id": user_id}), 201
    except ValidationError as err:
        return jsonify({"error": err.message, "field": err.field}), 400
