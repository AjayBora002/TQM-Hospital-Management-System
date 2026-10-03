"""bill.py -- Data-access functions for the bills table (Billing/Invoicing module)."""
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import get_connection, log_audit  # noqa: E402


def now():
    return datetime.now().isoformat(timespec="seconds")


def list_all():
    conn = get_connection()
    rows = conn.execute("""
        SELECT b.*, p.full_name AS patient_name
        FROM bills b JOIN patients p ON p.patient_id = b.patient_id
        ORDER BY b.bill_id DESC
    """).fetchall()
    conn.close()
    return rows


def add(patient_id, room_charges, consultation_charges, medicine_charges,
        payment_method, payment_status):
    total = round(room_charges + consultation_charges + medicine_charges, 2)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO bills (patient_id, room_charges, consultation_charges, medicine_charges, "
        "total_amount, payment_method, payment_status, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (patient_id, room_charges, consultation_charges, medicine_charges, total,
         payment_method, payment_status, now())
    )
    new_id = cur.lastrowid
    log_audit(conn, "bills", new_id, "INSERT", f"Generated bill (total {total})")
    conn.commit()
    conn.close()
    return new_id, total


def update_status(bill_id, payment_status):
    conn = get_connection()
    conn.execute("UPDATE bills SET payment_status=? WHERE bill_id=?", (payment_status, bill_id))
    log_audit(conn, "bills", bill_id, "UPDATE", f"Payment status set to {payment_status}")
    conn.commit()
    conn.close()


def delete(bill_id):
    conn = get_connection()
    conn.execute("DELETE FROM bills WHERE bill_id=?", (bill_id,))
    log_audit(conn, "bills", bill_id, "DELETE", "Bill deleted")
    conn.commit()
    conn.close()
