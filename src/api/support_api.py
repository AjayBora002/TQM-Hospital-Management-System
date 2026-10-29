"""
support_api.py -- REST API Blueprint for Hospital Support Services:
Housekeeping & Sanitation, Clinical Dietetics, Ambulance Dispatch, Biomedical Engineering, and Facility Tickets.
"""
from flask import Blueprint, request, jsonify, session
from database.db_manager import get_connection, log_audit
from auth.permissions import require_permission
from utils.exception_handler import ValidationError
from datetime import datetime

support_bp = Blueprint("support_services", __name__)


# ---------------- HOUSEKEEPING ----------------
@support_bp.route("/support/housekeeping", methods=["GET"])
@require_permission("support_services", "view")
def list_housekeeping_tasks():
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT h.*, r.room_number, w.name as ward_name
            FROM housekeeping_tasks h
            LEFT JOIN rooms r ON h.room_id = r.room_id
            LEFT JOIN wards w ON h.ward_id = w.ward_id
            ORDER BY 
                CASE h.priority WHEN 'Immediate' THEN 1 WHEN 'Urgent' THEN 2 ELSE 3 END,
                h.task_id DESC
        """).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@support_bp.route("/support/housekeeping", methods=["POST"])
@require_permission("support_services", "create")
def create_housekeeping_task():
    data = request.get_json() or {}
    room_id = data.get("room_id")
    ward_id = data.get("ward_id")
    area_name = data.get("area_name", "").strip()
    task_type = data.get("task_type", "Routine Sanitization")
    priority = data.get("priority", "Routine")
    notes = data.get("notes", "")
    user = session.get("username", "staff")

    if not area_name:
        raise ValidationError("Area or room name is required", field="area_name")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO housekeeping_tasks (room_id, ward_id, area_name, task_type, priority, status, requested_by, requested_at, notes)
            VALUES (?, ?, ?, ?, ?, 'Pending', ?, ?, ?)
        """, (room_id, ward_id, area_name, task_type, priority, user, now_str, notes))
        task_id = cursor.lastrowid
        log_audit(conn, "housekeeping_tasks", task_id, "INSERT", f"Housekeeping task '{task_type}' for {area_name}", user)
        conn.commit()
        return jsonify({"message": "Housekeeping task generated", "task_id": task_id}), 201
    finally:
        conn.close()


@support_bp.route("/support/housekeeping/<int:task_id>/complete", methods=["PUT"])
@require_permission("support_services", "edit")
def complete_housekeeping_task(task_id):
    data = request.get_json() or {}
    assigned_to = data.get("assigned_to", "Sanitation Team")
    user = session.get("username", "housekeeping_sup")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    try:
        task = conn.execute("SELECT * FROM housekeeping_tasks WHERE task_id = ?", (task_id,)).fetchone()
        if not task:
            return jsonify({"error": "Task not found"}), 404

        conn.execute("""
            UPDATE housekeeping_tasks 
            SET status = 'Completed', assigned_to = ?, completed_at = ?
            WHERE task_id = ?
        """, (assigned_to, now_str, task_id))

        # If task was associated with a room currently in 'Cleaning / Sanitizing', release to 'Available'
        if task["room_id"]:
            conn.execute("UPDATE rooms SET status = 'Available' WHERE room_id = ? AND status = 'Cleaning / Sanitizing'", (task["room_id"],))

        log_audit(conn, "housekeeping_tasks", task_id, "UPDATE", f"Completed task {task['task_type']} for {task['area_name']}", user)
        conn.commit()
        return jsonify({"message": "Housekeeping task marked complete; room sanitized"}), 200
    finally:
        conn.close()


# ---------------- CLINICAL DIETETICS ----------------
@support_bp.route("/support/diet-orders", methods=["GET"])
@require_permission("support_services", "view")
def list_diet_orders():
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT d.*, p.full_name as patient_name, p.gender, p.blood_group,
                   r.room_number, w.name as ward_name
            FROM diet_orders d
            JOIN patients p ON d.patient_id = p.patient_id
            LEFT JOIN admissions a ON d.admission_id = a.admission_id
            LEFT JOIN rooms r ON a.room_id = r.room_id
            LEFT JOIN wards w ON r.ward_id = w.ward_id
            ORDER BY d.order_id DESC
        """).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@support_bp.route("/support/diet-orders", methods=["POST"])
@require_permission("support_services", "create")
def prescribe_diet_order():
    data = request.get_json() or {}
    patient_id = data.get("patient_id")
    admission_id = data.get("admission_id")
    diet_type = data.get("diet_type", "Normal / Standard")
    meal_type = data.get("meal_type", "Lunch")
    allergies = data.get("allergies", "")
    calories_kcal = data.get("calories_kcal", 1800)
    dietitian_notes = data.get("dietitian_notes", "")
    delivery_date = data.get("delivery_date", datetime.now().strftime("%Y-%m-%d"))
    user = session.get("username", "dietitian")

    if not patient_id:
        raise ValidationError("Patient is required", field="patient_id")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO diet_orders (patient_id, admission_id, diet_type, meal_type, allergies, calories_kcal, dietitian_notes, status, delivery_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Ordered', ?)
        """, (patient_id, admission_id, diet_type, meal_type, allergies, calories_kcal, dietitian_notes, delivery_date))
        order_id = cursor.lastrowid
        log_audit(conn, "diet_orders", order_id, "INSERT", f"Prescribed diet plan: {diet_type} for patient {patient_id}", user)
        conn.commit()
        return jsonify({"message": "Clinical diet order created", "order_id": order_id}), 201
    finally:
        conn.close()


# ---------------- AMBULANCE FLEET DISPATCH ----------------
@support_bp.route("/support/ambulance-trips", methods=["GET"])
@require_permission("support_services", "view")
def list_ambulance_trips():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM ambulance_trips ORDER BY trip_id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@support_bp.route("/support/ambulance-trips", methods=["POST"])
@require_permission("support_services", "create")
def dispatch_ambulance():
    data = request.get_json() or {}
    vehicle_number = data.get("vehicle_number", "").strip()
    driver_name = data.get("driver_name", "").strip()
    paramedic_name = data.get("paramedic_name", "").strip()
    trip_type = data.get("trip_type", "Emergency Pickup")
    patient_name = data.get("patient_name", "").strip()
    pickup_location = data.get("pickup_location", "").strip()
    drop_location = data.get("drop_location", "").strip()
    notes = data.get("notes", "")
    user = session.get("username", "ems_dispatcher")

    if not vehicle_number:
        raise ValidationError("Ambulance vehicle is required", field="vehicle_number")
    if not patient_name:
        raise ValidationError("Patient name is required", field="patient_name")
    if not pickup_location:
        raise ValidationError("Pickup GPS/address is required", field="pickup_location")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ambulance_trips (vehicle_number, driver_name, paramedic_name, trip_type, patient_name, pickup_location, drop_location, status, dispatch_time, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Dispatched', ?, ?)
        """, (vehicle_number, driver_name, paramedic_name, trip_type, patient_name, pickup_location, drop_location, now_str, notes))
        trip_id = cursor.lastrowid
        log_audit(conn, "ambulance_trips", trip_id, "INSERT", f"Dispatched {vehicle_number} to {pickup_location}", user)
        conn.commit()
        return jsonify({"message": "Ambulance dispatched successfully", "trip_id": trip_id}), 201
    finally:
        conn.close()


# ---------------- BIOMEDICAL ASSETS & EQUIPMENT ----------------
@support_bp.route("/support/biomedical", methods=["GET"])
@require_permission("support_services", "view")
def list_biomedical_equipment():
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT b.*, d.name as department_name
            FROM biomedical_equipment b
            LEFT JOIN departments d ON b.department_id = d.department_id
            ORDER BY b.equip_id DESC
        """).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@support_bp.route("/support/biomedical", methods=["POST"])
@require_permission("support_services", "create")
def register_equipment():
    data = request.get_json() or {}
    equipment_name = data.get("equipment_name", "").strip()
    model = data.get("model", "").strip()
    serial_number = data.get("serial_number", "").strip()
    department_id = data.get("department_id")
    location = data.get("location", "").strip()
    vendor_contact = data.get("vendor_contact", "")
    next_service_date = data.get("next_service_date", "")
    calibration_due = data.get("calibration_due", "")
    user = session.get("username", "biomed_eng")

    if not equipment_name or not serial_number:
        raise ValidationError("Equipment name and Serial Number are required", field="serial_number")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO biomedical_equipment (equipment_name, model, serial_number, department_id, location, status, next_service_date, calibration_due, vendor_contact)
            VALUES (?, ?, ?, ?, ?, 'Operational', ?, ?, ?)
        """, (equipment_name, model, serial_number, department_id, location, next_service_date, calibration_due, vendor_contact))
        equip_id = cursor.lastrowid
        log_audit(conn, "biomedical_equipment", equip_id, "INSERT", f"Registered biomedical asset {equipment_name} (SN: {serial_number})", user)
        conn.commit()
        return jsonify({"message": "Biomedical equipment registered", "equip_id": equip_id}), 201
    finally:
        conn.close()


# ---------------- FACILITY TICKETS & MAINTENANCE ----------------
@support_bp.route("/support/facility-tickets", methods=["GET"])
@require_permission("support_services", "view")
def list_facility_tickets():
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT t.*, d.name as department_name, w.name as ward_name
            FROM facility_tickets t
            LEFT JOIN departments d ON t.department_id = d.department_id
            LEFT JOIN wards w ON t.ward_id = w.ward_id
            ORDER BY t.ticket_id DESC
        """).fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@support_bp.route("/support/facility-tickets", methods=["POST"])
@require_permission("support_services", "create")
def create_facility_ticket():
    data = request.get_json() or {}
    location = data.get("location", "").strip()
    issue_category = data.get("issue_category", "Electrical")
    description = data.get("description", "").strip()
    urgency = data.get("urgency", "Medium")
    department_id = data.get("department_id")
    ward_id = data.get("ward_id")
    user = session.get("username", "staff")

    if not location or not description:
        raise ValidationError("Location and description are required", field="description")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO facility_tickets (department_id, ward_id, location, issue_category, description, urgency, status, reported_by, reported_at)
            VALUES (?, ?, ?, ?, ?, ?, 'Open', ?, ?)
        """, (department_id, ward_id, location, issue_category, description, urgency, user, now_str))
        ticket_id = cursor.lastrowid
        log_audit(conn, "facility_tickets", ticket_id, "INSERT", f"Reported {issue_category} issue in {location}", user)
        conn.commit()
        return jsonify({"message": "Facility ticket logged successfully", "ticket_id": ticket_id}), 201
    finally:
        conn.close()
