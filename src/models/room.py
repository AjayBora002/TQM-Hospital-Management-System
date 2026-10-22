"""room.py -- Data-access functions for the rooms table (Ward/Room Allocation module)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import get_connection, log_audit  # noqa: E402


def list_all():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM rooms ORDER BY room_number").fetchall()
    conn.close()
    return rows


def choices_map(only_available=False):
    conn = get_connection()
    q = "SELECT room_id, room_number, room_type FROM rooms"
    if only_available:
        q += " WHERE status = 'Available'"
    rows = conn.execute(q).fetchall()
    conn.close()
    return {f"{r['room_number']} ({r['room_type']})": r["room_id"] for r in rows}


def add(room_number, room_type, status, rate_per_day):
    from utils.validators import validate_room_payload
    validate_room_payload({
        "room_number": room_number,
        "room_type": room_type,
        "status": status,
        "rate_per_day": rate_per_day
    })
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO rooms (room_number, room_type, status, rate_per_day) VALUES (?,?,?,?)",
                    (str(room_number).strip(), room_type, status, float(rate_per_day)))
        new_id = cur.lastrowid
        log_audit(conn, "rooms", new_id, "INSERT", f"Added room '{room_number}'")
        conn.commit()
        return new_id
    finally:
        conn.close()


def update(room_id, room_number, room_type, status, rate_per_day):
    from utils.validators import validate_room_payload
    validate_room_payload({
        "room_number": room_number,
        "room_type": room_type,
        "status": status,
        "rate_per_day": rate_per_day
    })
    conn = get_connection()
    try:
        conn.execute("UPDATE rooms SET room_number=?, room_type=?, status=?, rate_per_day=? WHERE room_id=?",
                     (str(room_number).strip(), room_type, status, float(rate_per_day), room_id))
        log_audit(conn, "rooms", room_id, "UPDATE", f"Room {room_number} status updated to {status}")
        conn.commit()
    finally:
        conn.close()


def delete(room_id):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM rooms WHERE room_id=?", (room_id,))
        log_audit(conn, "rooms", room_id, "DELETE", "Room record deleted")
        conn.commit()
    finally:
        conn.close()


def get_by_id(room_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM rooms WHERE room_id=?", (room_id,)).fetchone()
    conn.close()
    return row


def set_status(room_id, status):
    from config import ROOM_STATUS
    from utils.exception_handler import ValidationError
    if status not in ROOM_STATUS:
        raise ValidationError(f"Invalid room status '{status}'. Must be one of {ROOM_STATUS}", field="status")
    conn = get_connection()
    conn.execute("UPDATE rooms SET status=? WHERE room_id=?", (status, room_id))
    log_audit(conn, "rooms", room_id, "UPDATE", f"Room status set to {status}")
    conn.commit()
    conn.close()

