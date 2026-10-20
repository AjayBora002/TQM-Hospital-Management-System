"""
export.py -- REST API Blueprint for Data Exporting (CSV format).
Supports exporting Patients, Bills, Appointments, and Medicines.
"""
import csv
import io
from datetime import datetime
from flask import Blueprint, Response
from database.db_manager import get_connection

export_bp = Blueprint("export", __name__)


def _generate_csv(rows, fieldnames):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(dict(row))
    return output.getvalue()


@export_bp.route("/export/patients", methods=["GET"])
def export_patients():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT p.patient_id, p.full_name, p.gender, p.dob, p.blood_group, "
            "p.phone, p.allergies, r.room_number, p.created_at "
            "FROM patients p LEFT JOIN rooms r ON p.room_id = r.room_id "
            "ORDER BY p.patient_id"
        ).fetchall()
        fieldnames = ["patient_id", "full_name", "gender", "dob", "blood_group", "phone", "allergies", "room_number", "created_at"]
        csv_data = _generate_csv(rows, fieldnames)
        filename = f"hms_patients_{datetime.now().strftime('%Y%m%d')}.csv"
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    finally:
        conn.close()


@export_bp.route("/export/bills", methods=["GET"])
def export_bills():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT b.bill_id, p.full_name as patient_name, p.phone as patient_phone, "
            "b.room_charges, b.consultation_charges, b.medicine_charges, "
            "b.total_amount, b.payment_method, b.payment_status, b.created_at "
            "FROM bills b JOIN patients p ON b.patient_id = p.patient_id "
            "ORDER BY b.bill_id"
        ).fetchall()
        fieldnames = ["bill_id", "patient_name", "patient_phone", "room_charges", "consultation_charges", "medicine_charges", "total_amount", "payment_method", "payment_status", "created_at"]
        csv_data = _generate_csv(rows, fieldnames)
        filename = f"hms_billing_export_{datetime.now().strftime('%Y%m%d')}.csv"
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    finally:
        conn.close()


@export_bp.route("/export/appointments", methods=["GET"])
def export_appointments():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT a.appointment_id, p.full_name as patient_name, d.full_name as doctor_name, "
            "d.department, a.appt_date, a.appt_time, a.status, a.notes, a.created_at "
            "FROM appointments a "
            "JOIN patients p ON a.patient_id = p.patient_id "
            "JOIN doctors d ON a.doctor_id = d.doctor_id "
            "ORDER BY a.appointment_id DESC"
        ).fetchall()
        fieldnames = ["appointment_id", "patient_name", "doctor_name", "department", "appt_date", "appt_time", "status", "notes", "created_at"]
        csv_data = _generate_csv(rows, fieldnames)
        filename = f"hms_appointments_{datetime.now().strftime('%Y%m%d')}.csv"
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    finally:
        conn.close()
