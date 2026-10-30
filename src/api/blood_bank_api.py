"""
blood_bank_api.py -- REST API Blueprint for Blood Bank & Transfusion Medicine.
Donor registry, component unit inventory, cross-matching, and issuance.
"""
from flask import Blueprint, request, jsonify, session
from database.db_manager import get_connection, log_audit
from auth.permissions import require_permission
from utils.exception_handler import ValidationError
from datetime import datetime

blood_bank_bp = Blueprint("blood_bank", __name__)


@blood_bank_bp.route("/blood-bank/units", methods=["GET"])
@blood_bank_bp.route("/blood-bank/inventory", methods=["GET"])
@require_permission("diagnostics", "view")
def list_blood_inventory():
    blood_group = request.args.get("blood_group")
    status = request.args.get("status")

    query = """
        SELECT b.*, d.full_name as donor_name, d.phone as donor_phone
        FROM blood_inventory b
        LEFT JOIN blood_donors d ON b.donor_id = d.donor_id
        WHERE 1=1
    """
    params = []
    if blood_group:
        query += " AND b.blood_group = ?"
        params.append(blood_group)
    if status:
        query += " AND b.status = ?"
        params.append(status)
    query += " ORDER BY b.expiry_date ASC"

    conn = get_connection()
    try:
        rows = conn.execute(query, params).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@blood_bank_bp.route("/blood-bank/donors", methods=["GET"])
@require_permission("diagnostics", "view")
def list_blood_donors():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM blood_donors ORDER BY donor_id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@blood_bank_bp.route("/blood-bank/donors", methods=["POST"])
@require_permission("diagnostics", "create")
def register_donor():
    data = request.get_json() or {}
    full_name = data.get("full_name", "").strip()
    blood_group = data.get("blood_group", "").strip()
    phone = data.get("phone", "").strip()
    age = data.get("age")
    weight_kg = data.get("weight_kg")
    hemoglobin = data.get("hemoglobin")
    component_type = data.get("component_type", "Packed Red Cells (PRBC)")
    bag_number = data.get("bag_number", "").strip()
    expiry_date = data.get("expiry_date", "").strip()
    user = session.get("username", "blood_tech")

    if not full_name:
        raise ValidationError("Donor full name is required", field="full_name")
    if blood_group not in ("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"):
        raise ValidationError("Invalid blood group", field="blood_group")
    if not age or int(age) < 18 or int(age) > 65:
        raise ValidationError("Donor age must be between 18 and 65 years", field="age")
    if not weight_kg or float(weight_kg) < 45.0:
        raise ValidationError("Donor weight must be at least 45.0 kg", field="weight_kg")
    if not hemoglobin or float(hemoglobin) < 12.5:
        raise ValidationError("Donor hemoglobin must be >= 12.5 g/dL for donation safety", field="hemoglobin")
    if not bag_number:
        raise ValidationError("Blood unit barcode/bag number is required", field="bag_number")
    if not expiry_date:
        raise ValidationError("Component expiry date is required", field="expiry_date")

    today_str = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    try:
        # Check duplicate bag number
        exists = conn.execute("SELECT 1 FROM blood_inventory WHERE bag_number = ?", (bag_number,)).fetchone()
        if exists:
            raise ValidationError(f"Bag number '{bag_number}' already exists in inventory", field="bag_number")

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO blood_donors (full_name, blood_group, phone, age, weight_kg, hemoglobin, donation_date, screening_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Passed')
        """, (full_name, blood_group, phone, age, weight_kg, hemoglobin, today_str))
        donor_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO blood_inventory (donor_id, blood_group, component_type, bag_number, collection_date, expiry_date, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Available')
        """, (donor_id, blood_group, component_type, bag_number, today_str, expiry_date))
        unit_id = cursor.lastrowid

        log_audit(conn, "blood_inventory", unit_id, "INSERT", f"Added blood unit {bag_number} ({blood_group} {component_type})", user)
        conn.commit()
        return jsonify({"message": "Donor and blood unit registered successfully", "donor_id": donor_id, "unit_id": unit_id}), 201
    finally:
        conn.close()


@blood_bank_bp.route("/blood-bank/requests", methods=["GET"])
@require_permission("diagnostics", "view")
def list_blood_requests():
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT r.*, p.full_name as patient_name, d.full_name as doctor_name
            FROM blood_requests r
            JOIN patients p ON r.patient_id = p.patient_id
            JOIN doctors d ON r.doctor_id = d.doctor_id
            ORDER BY r.request_id DESC
        """).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@blood_bank_bp.route("/blood-bank/requests", methods=["POST"])
@require_permission("clinical", "create")
def request_blood():
    data = request.get_json() or {}
    patient_id = data.get("patient_id")
    doctor_id = data.get("doctor_id")
    blood_group = data.get("blood_group")
    component_type = data.get("component_type", "Packed Red Cells (PRBC)")
    units_requested = data.get("units_requested", 1)
    urgency = data.get("urgency", "Routine")
    user = session.get("username", "doc_user")

    if not patient_id:
        raise ValidationError("Patient is required", field="patient_id")
    if not doctor_id:
        raise ValidationError("Doctor is required", field="doctor_id")
    if blood_group not in ("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"):
        raise ValidationError("Valid patient blood group is required", field="blood_group")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO blood_requests (patient_id, doctor_id, blood_group, component_type, units_requested, urgency, status, requested_at)
            VALUES (?, ?, ?, ?, ?, ?, 'Requested', ?)
        """, (patient_id, doctor_id, blood_group, component_type, units_requested, urgency, now_str))
        req_id = cursor.lastrowid
        log_audit(conn, "blood_requests", req_id, "INSERT", f"Blood request for {units_requested} unit(s) of {blood_group} {component_type}", user)
        conn.commit()
        return jsonify({"message": "Blood request created successfully", "request_id": req_id}), 201
    finally:
        conn.close()


@blood_bank_bp.route("/blood-bank/requests/<int:request_id>/crossmatch", methods=["PUT"])
@require_permission("diagnostics", "edit")
def crossmatch_and_issue_blood(request_id):
    data = request.get_json() or {}
    unit_id = data.get("unit_id")
    action = data.get("action", "Crossmatch")  # 'Crossmatch' or 'Issue'
    user = session.get("username", "blood_tech")

    conn = get_connection()
    try:
        req = conn.execute("SELECT * FROM blood_requests WHERE request_id = ?", (request_id,)).fetchone()
        if not req:
            return jsonify({"error": "Blood request not found"}), 404

        unit = conn.execute("SELECT * FROM blood_inventory WHERE unit_id = ?", (unit_id,)).fetchone()
        if not unit:
            return jsonify({"error": "Blood unit not found"}), 404

        # Poka-Yoke Blood group compatibility safety check
        if action == "Issue" and unit["status"] == "Expired":
            raise ValidationError("Safety Violation: Cannot issue an expired blood unit!", field="unit_id")

        new_req_status = "Crossmatched" if action == "Crossmatch" else "Issued"
        new_unit_status = "Reserved" if action == "Crossmatch" else "Transfused"

        conn.execute("UPDATE blood_requests SET status = ?, issued_unit_id = ? WHERE request_id = ?", (new_req_status, unit_id, request_id))
        conn.execute("UPDATE blood_inventory SET status = ? WHERE unit_id = ?", (new_unit_status, unit_id))
        log_audit(conn, "blood_requests", request_id, "UPDATE", f"{action} blood unit {unit['bag_number']} for patient {req['patient_id']}", user)
        conn.commit()
        return jsonify({"message": f"Blood unit {action} completed successfully"}), 200
    finally:
        conn.close()

