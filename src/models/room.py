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
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO rooms (room_number, room_type, status, rate_per_day) VALUES (?,?,?,?)",
                (room_number, room_type, status, rate_per_day))
    new_id = cur.lastrowid
    log_audit(conn, "rooms", new_id, "INSERT", f"Added room '{room_number}'")
    conn.commit()
    conn.close()
    return new_id


def update(room_id, room_number, room_type, status, rate_per_day):
    conn = get_connection()
    conn.execute("UPDATE rooms SET room_number=?, room_type=?, status=?, rate_per_day=? WHERE room_id=?",
                 (room_number, room_type, status, rate_per_day, room_id))
    log_audit(conn, "rooms", room_id, "UPDATE", f"Room {room_number} status updated to {status}")
    conn.commit()
    conn.close()


def delete(room_id):
    conn = get_connection()
    conn.execute("DELETE FROM rooms WHERE room_id=?", (room_id,))
    log_audit(conn, "rooms", room_id, "DELETE", "Room record deleted")
    conn.commit()
    conn.close()
