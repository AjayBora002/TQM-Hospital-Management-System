"""
ward_bed.py -- Data-access and domain operations for Inpatient Wards and Bed Board.
Provides real-time interactive bed matrix, occupancy rates, and bed turnaround.
"""
from datetime import datetime
from database.db_manager import get_connection, log_audit
from utils.exception_handler import ValidationError


def list_wards():
    """Returns all hospital inpatient wards with real-time bed count and occupancy."""
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT w.ward_id, w.name, w.ward_type, w.floor_number, w.total_beds,
                   d.name AS department_name,
                   u.full_name AS manager_name,
                   (SELECT COUNT(*) FROM rooms r WHERE r.ward_id = w.ward_id) AS registered_beds,
                   (SELECT COUNT(*) FROM rooms r WHERE r.ward_id = w.ward_id AND r.status = 'Available') AS available_beds,
                   (SELECT COUNT(*) FROM rooms r WHERE r.ward_id = w.ward_id AND r.status = 'Occupied') AS occupied_beds,
                   (SELECT COUNT(*) FROM rooms r WHERE r.ward_id = w.ward_id AND r.status LIKE 'Cleaning%') AS cleaning_beds
            FROM wards w
            LEFT JOIN departments d ON d.department_id = w.department_id
            LEFT JOIN users u ON u.user_id = w.manager_user_id
            ORDER BY w.floor_number, w.ward_id
        """).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_ward_bed_matrix(ward_id: int = None):
    """
    Returns individual beds grouped by ward, including current occupant patient details.
    Used to render the visual interactive Hospital Bed Board.
    """
    conn = get_connection()
    try:
        query = """
            SELECT r.room_id, r.room_number, r.room_type, r.status, r.rate_per_day, r.ward_id,
                   w.name AS ward_name, w.floor_number,
                   p.patient_id, p.full_name AS patient_name, p.phone AS patient_phone,
                   p.gender, p.blood_group,
                   a.admission_id, a.admission_date, a.diagnosis
            FROM rooms r
            LEFT JOIN wards w ON w.ward_id = r.ward_id
            LEFT JOIN patients p ON p.room_id = r.room_id
            LEFT JOIN admissions a ON a.patient_id = p.patient_id AND a.status = 'Admitted'
        """
        params = []
        if ward_id:
            query += " WHERE r.ward_id = ?"
            params.append(ward_id)

        query += " ORDER BY r.ward_id, r.room_number"
        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_bed_status(room_id: int, new_status: str, performed_by: str = "ward_manager"):
    """
    Updates bed status (e.g., Available -> Occupied -> Cleaning -> Available).
    Enforces valid room status boundaries.
    """
    import config
    if new_status not in config.ROOM_STATUS:
        raise ValidationError(f"Invalid bed status '{new_status}'. Allowed: {config.ROOM_STATUS}", field="status")

    conn = get_connection()
    try:
        room = conn.execute("SELECT room_number, status FROM rooms WHERE room_id = ?", (room_id,)).fetchone()
        if not room:
            raise ValidationError(f"Bed #{room_id} not found", field="room_id")

        old_status = room["status"]
        conn.execute("UPDATE rooms SET status = ? WHERE room_id = ?", (new_status, room_id))
        log_audit(conn, "rooms", room_id, "UPDATE", f"Bed #{room['room_number']} status changed: '{old_status}' -> '{new_status}'", performed_by)
        conn.commit()
        return True
    finally:
        conn.close()


def get_ward_occupancy_stats():
    """Calculates overall bed occupancy percentage and bed inventory breakdown."""
    conn = get_connection()
    try:
        total = conn.execute("SELECT COUNT(*) as c FROM rooms").fetchone()["c"]
        occupied = conn.execute("SELECT COUNT(*) as c FROM rooms WHERE status = 'Occupied'").fetchone()["c"]
        available = conn.execute("SELECT COUNT(*) as c FROM rooms WHERE status = 'Available'").fetchone()["c"]
        cleaning = conn.execute("SELECT COUNT(*) as c FROM rooms WHERE status LIKE 'Cleaning%'").fetchone()["c"]
        maintenance = conn.execute("SELECT COUNT(*) as c FROM rooms WHERE status LIKE '%Maintenance%'").fetchone()["c"]

        occupancy_rate = round((occupied / total * 100), 1) if total > 0 else 0.0

        return {
            "total_beds": total,
            "occupied_beds": occupied,
            "available_beds": available,
            "cleaning_beds": cleaning,
            "maintenance_beds": maintenance,
            "occupancy_rate_percent": occupancy_rate
        }
    finally:
        conn.close()

