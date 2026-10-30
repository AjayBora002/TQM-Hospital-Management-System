"""
people_api.py -- REST API Blueprint for Staff Duty Rosters, Shift Scheduling, and Leaves (HR).
"""
from flask import Blueprint, request, jsonify, session
from database.db_manager import get_connection, log_audit
from auth.permissions import require_permission
from utils.exception_handler import ValidationError
from datetime import datetime

people_bp = Blueprint("people", __name__)


@people_bp.route("/people/shifts", methods=["GET"])
@require_permission("people", "view")
def list_staff_shifts():
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT sh.*, st.full_name as staff_name, st.role as staff_role, st.phone
            FROM staff_shifts sh
            JOIN staff st ON sh.staff_id = st.staff_id
            ORDER BY sh.shift_date DESC, sh.shift_id DESC
        """).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@people_bp.route("/people/shifts", methods=["POST"])
@require_permission("people", "create")
def assign_shift():
    data = request.get_json() or {}
    staff_id = data.get("staff_id")
    shift_date = data.get("shift_date", "").strip()
    shift_type = data.get("shift_type", "Morning")
    department = data.get("department", "").strip()
    notes = data.get("notes", "")
    user = session.get("username", "hr_mgr")

    if not staff_id:
        raise ValidationError("Staff member is required", field="staff_id")
    if not shift_date:
        raise ValidationError("Shift date is required", field="shift_date")
    if not department:
        raise ValidationError("Department assignment is required", field="department")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO staff_shifts (staff_id, shift_date, shift_type, department, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (staff_id, shift_date, shift_type, department, notes))
        shift_id = cursor.lastrowid
        log_audit(conn, "staff_shifts", shift_id, "INSERT", f"Assigned {shift_type} shift on {shift_date} in {department}", user)
        conn.commit()
        return jsonify({"message": "Staff shift scheduled successfully", "shift_id": shift_id}), 201
    finally:
        conn.close()


@people_bp.route("/people/leaves", methods=["GET"])
@require_permission("people", "view")
def list_staff_leaves():
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT l.*, st.full_name as staff_name, st.role as staff_role
            FROM staff_leaves l
            JOIN staff st ON l.staff_id = st.staff_id
            ORDER BY l.leave_id DESC
        """).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@people_bp.route("/people/leaves", methods=["POST"])
@require_permission("people", "create")
def apply_leave():
    data = request.get_json() or {}
    staff_id = data.get("staff_id")
    leave_type = data.get("leave_type", "Casual Leave")
    start_date = data.get("start_date", "").strip()
    end_date = data.get("end_date", "").strip()
    reason = data.get("reason", "").strip()
    user = session.get("username", "staff")

    if not staff_id or not start_date or not end_date or not reason:
        raise ValidationError("Staff, dates, and reason are required", field="reason")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO staff_leaves (staff_id, leave_type, start_date, end_date, reason, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'Pending', ?)
        """, (staff_id, leave_type, start_date, end_date, reason, now_str))
        leave_id = cursor.lastrowid
        log_audit(conn, "staff_leaves", leave_id, "INSERT", f"Applied {leave_type} from {start_date} to {end_date}", user)
        conn.commit()
        return jsonify({"message": "Leave application submitted", "leave_id": leave_id}), 201
    finally:
        conn.close()


@people_bp.route("/people/leaves/<int:leave_id>/decision", methods=["PUT"])
@require_permission("people", "approve")
def approve_or_reject_leave(leave_id):
    data = request.get_json() or {}
    status = data.get("status", "Approved")  # 'Approved' or 'Rejected'
    user = session.get("username", "hr_mgr")

    if status not in ("Approved", "Rejected"):
        raise ValidationError("Status must be Approved or Rejected", field="status")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE staff_leaves SET status = ?, approved_by = ? WHERE leave_id = ?", (status, user, leave_id))
        if cursor.rowcount == 0:
            return jsonify({"error": "Leave request not found"}), 404
        log_audit(conn, "staff_leaves", leave_id, "UPDATE", f"Leave decision: {status} by {user}", user)
        conn.commit()
        return jsonify({"message": f"Leave {status.lower()} successfully"}), 200
    finally:
        conn.close()

