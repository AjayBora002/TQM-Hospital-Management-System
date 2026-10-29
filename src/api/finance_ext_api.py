"""
finance_ext_api.py -- REST API Blueprint for Advance Deposits & Insurance/TPA Claims.
"""
from flask import Blueprint, request, jsonify, session
from database.db_manager import get_connection, log_audit
from auth.permissions import require_permission
from utils.exception_handler import ValidationError
from datetime import datetime

finance_ext_bp = Blueprint("finance_ext", __name__)


# ---------------- ADVANCE DEPOSITS ----------------
@finance_ext_bp.route("/finance/advance-deposits", methods=["GET"])
@require_permission("finance", "view")
def list_advance_deposits():
    patient_id = request.args.get("patient_id")
    query = """
        SELECT d.*, p.full_name as patient_name, p.gender, p.blood_group
        FROM advance_deposits d
        JOIN patients p ON d.patient_id = p.patient_id
        WHERE 1=1
    """
    params = []
    if patient_id:
        query += " AND d.patient_id = ?"
        params.append(patient_id)
    query += " ORDER BY d.deposit_id DESC"

    conn = get_connection()
    try:
        rows = conn.execute(query, params).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@finance_ext_bp.route("/finance/advance-deposits", methods=["POST"])
@require_permission("finance", "create")
def collect_advance_deposit():
    data = request.get_json() or {}
    patient_id = data.get("patient_id")
    admission_id = data.get("admission_id")
    amount = float(data.get("amount", 0.0))
    payment_method = data.get("payment_method", "Cash")
    transaction_ref = data.get("transaction_ref", "").strip()
    notes = data.get("notes", "")
    user = session.get("username", "cashier")

    if not patient_id:
        raise ValidationError("Patient is required", field="patient_id")
    if amount <= 0:
        raise ValidationError("Deposit amount must be greater than zero", field="amount")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO advance_deposits (patient_id, admission_id, amount, payment_method, transaction_ref, received_by, receipt_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (patient_id, admission_id, amount, payment_method, transaction_ref, user, now_str, notes))
        deposit_id = cursor.lastrowid
        log_audit(conn, "advance_deposits", deposit_id, "INSERT", f"Collected advance deposit of Rs. {amount:.2f} via {payment_method}", user)
        conn.commit()
        return jsonify({"message": "Advance deposit recorded successfully", "deposit_id": deposit_id, "receipt_no": f"REC-ADV-{deposit_id:04d}"}), 201
    finally:
        conn.close()


# ---------------- INSURANCE & TPA CLAIMS ----------------
@finance_ext_bp.route("/finance/insurance-claims", methods=["GET"])
@require_permission("finance", "view")
def list_insurance_claims():
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT c.*, p.full_name as patient_name, b.total_amount as bill_total
            FROM insurance_claims c
            JOIN patients p ON c.patient_id = p.patient_id
            LEFT JOIN bills b ON c.bill_id = b.bill_id
            ORDER BY c.claim_id DESC
        """).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@finance_ext_bp.route("/finance/insurance-claims", methods=["POST"])
@require_permission("finance", "create")
def submit_insurance_claim():
    data = request.get_json() or {}
    patient_id = data.get("patient_id")
    bill_id = data.get("bill_id")
    tpa_name = data.get("tpa_name", "").strip()
    policy_number = data.get("policy_number", "").strip()
    claim_amount = float(data.get("claim_amount", 0.0))
    pre_auth_number = data.get("pre_auth_number", "").strip()
    notes = data.get("notes", "")
    user = session.get("username", "tpa_desk")

    if not patient_id:
        raise ValidationError("Patient selection is required", field="patient_id")
    if not tpa_name or not policy_number:
        raise ValidationError("TPA company name and Policy Number are required", field="tpa_name")
    if claim_amount <= 0:
        raise ValidationError("Claim amount must be greater than zero", field="claim_amount")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO insurance_claims (patient_id, bill_id, tpa_name, policy_number, claim_amount, approved_amount, pre_auth_status, pre_auth_number, claim_status, submission_date, notes)
            VALUES (?, ?, ?, ?, ?, 0.0, 'Approved' if pre_auth_number else 'Pending', ?, 'Submitted', ?, ?)
        """, (patient_id, bill_id, tpa_name, policy_number, claim_amount, pre_auth_number, now_str, notes))
        claim_id = cursor.lastrowid
        log_audit(conn, "insurance_claims", claim_id, "INSERT", f"Submitted TPA claim Rs. {claim_amount:.2f} to {tpa_name}", user)
        conn.commit()
        return jsonify({"message": "Insurance claim submitted", "claim_id": claim_id}), 201
    finally:
        conn.close()


@finance_ext_bp.route("/finance/insurance-claims/<int:claim_id>/settle", methods=["PUT"])
@require_permission("finance", "edit")
def settle_claim(claim_id):
    data = request.get_json() or {}
    approved_amount = float(data.get("approved_amount", 0.0))
    claim_status = data.get("claim_status", "Settled")
    notes = data.get("notes", "")
    user = session.get("username", "tpa_desk")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE insurance_claims 
            SET approved_amount = ?, claim_status = ?, settled_date = ?, notes = ?
            WHERE claim_id = ?
        """, (approved_amount, claim_status, now_str, notes, claim_id))
        if cursor.rowcount == 0:
            return jsonify({"error": "Claim not found"}), 404
        log_audit(conn, "insurance_claims", claim_id, "UPDATE", f"Settled claim {claim_id}: Approved Rs. {approved_amount:.2f} ({claim_status})", user)
        conn.commit()
        return jsonify({"message": "Claim status updated successfully"}), 200
    finally:
        conn.close()
