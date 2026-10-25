"""patient.py -- Data-access functions for the patients table."""
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import get_connection, log_audit  # noqa: E402


import config


def now():
    return datetime.now().isoformat(timespec="seconds")


def format_uhid(patient_id) -> str:
    """Institutional Unique Hospital Identifier (UHID) complying with NABH & ABDM requirements."""
    if not patient_id:
        return ""
    try:
        return f"{config.UHID_PREFIX}{int(patient_id):05d}"
    except (ValueError, TypeError):
        return f"{config.UHID_PREFIX}{patient_id}"


def list_all(name_filter=""):
    conn = get_connection()
    query = """
        SELECT p.*, r.room_number, r.room_type, r.status AS room_status
        FROM patients p
        LEFT JOIN rooms r ON p.room_id = r.room_id
    """
    if name_filter:
        query += " WHERE p.full_name LIKE ? ORDER BY p.patient_id DESC"
        rows = conn.execute(query, (f"%{name_filter}%",)).fetchall()
    else:
        query += " ORDER BY p.patient_id DESC"
        rows = conn.execute(query).fetchall()
    conn.close()
    return rows


def name_candidates(prefix, limit=8):
    conn = get_connection()
    rows = conn.execute(
        "SELECT full_name FROM patients WHERE full_name LIKE ? LIMIT ?",
        (f"{prefix}%", limit)
    ).fetchall()
    conn.close()
    return [r["full_name"] for r in rows]


def get_id_by_name(name):
    conn = get_connection()
    row = conn.execute("SELECT patient_id FROM patients WHERE full_name = ?", (name,)).fetchone()
    conn.close()
    return row["patient_id"] if row else None


def get_by_id(patient_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT p.*, r.room_number, r.room_type, r.rate_per_day, r.status AS room_status "
        "FROM patients p "
        "LEFT JOIN rooms r ON p.room_id = r.room_id "
        "WHERE p.patient_id = ?",
        (patient_id,)
    ).fetchone()
    conn.close()
    return row


def add(full_name, gender, dob, blood_group, phone, address, room_id=None, allergies="None"):
    from utils.validators import validate_patient_payload
    validate_patient_payload({
        "full_name": full_name,
        "gender": gender,
        "dob": dob,
        "blood_group": blood_group,
        "phone": phone
    })
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO patients (full_name, gender, dob, blood_group, phone, address, allergies, room_id, "
        "created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (full_name, gender, dob, blood_group, phone, address, allergies or "None", room_id, now(), now())
    )
    new_id = cur.lastrowid
    log_audit(conn, "patients", new_id, "INSERT", f"Added patient '{full_name}' (Allergies: {allergies or 'None'})")
    if room_id:
        cur.execute("UPDATE rooms SET status='Occupied' WHERE room_id=?", (room_id,))
        log_audit(conn, "rooms", room_id, "UPDATE", f"Bed allocated (Occupied) for admitted patient '{full_name}'")
    conn.commit()
    conn.close()
    return new_id


def update(patient_id, full_name, gender, dob, blood_group, phone, address, room_id=None, allergies="None"):
    from utils.validators import validate_patient_payload
    validate_patient_payload({
        "full_name": full_name,
        "gender": gender,
        "dob": dob,
        "blood_group": blood_group,
        "phone": phone
    })
    conn = get_connection()
    cur = conn.cursor()
    old = cur.execute("SELECT room_id, full_name, allergies FROM patients WHERE patient_id=?", (patient_id,)).fetchone()
    old_room_id = old["room_id"] if old else None

    cur.execute(
        "UPDATE patients SET full_name=?, gender=?, dob=?, blood_group=?, phone=?, address=?, "
        "allergies=?, room_id=?, updated_at=? WHERE patient_id=?",
        (full_name, gender, dob, blood_group, phone, address, allergies or "None", room_id, now(), patient_id)
    )
    log_audit(conn, "patients", patient_id, "UPDATE", f"Patient record updated (Allergies: {allergies or 'None'})")

    # Automated bed allocation & clearance on room reassignment
    if old_room_id != room_id:
        if old_room_id:
            cur.execute("UPDATE rooms SET status='Available' WHERE room_id=?", (old_room_id,))
            log_audit(conn, "rooms", old_room_id, "UPDATE",
                      f"Automated bed clearance: Room freed (Available) on patient room transfer")
        if room_id:
            cur.execute("UPDATE rooms SET status='Occupied' WHERE room_id=?", (room_id,))
            log_audit(conn, "rooms", room_id, "UPDATE",
                      f"Bed allocated (Occupied) for admitted patient '{full_name}'")

    conn.commit()
    conn.close()


def delete(patient_id):
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute("SELECT room_id, full_name FROM patients WHERE patient_id=?", (patient_id,)).fetchone()
    if row and row["room_id"]:
        cur.execute("UPDATE rooms SET status='Available' WHERE room_id=?", (row["room_id"],))
        log_audit(conn, "rooms", row["room_id"], "UPDATE",
                  f"Automated bed clearance: Room freed (Available) due to deletion of patient '{row['full_name']}'")

    cur.execute("DELETE FROM patients WHERE patient_id=?", (patient_id,))
    log_audit(conn, "patients", patient_id, "DELETE", "Patient record deleted")
    conn.commit()
    conn.close()


def get_discharge_summary(patient_id):
    conn = get_connection()
    patient = conn.execute(
        "SELECT p.*, r.room_number, r.room_type, r.rate_per_day "
        "FROM patients p LEFT JOIN rooms r ON p.room_id = r.room_id "
        "WHERE p.patient_id = ?",
        (patient_id,)
    ).fetchone()
    if not patient:
        conn.close()
        return None

    bills = conn.execute(
        "SELECT * FROM bills WHERE patient_id = ? ORDER BY bill_id DESC",
        (patient_id,)
    ).fetchall()
    conn.close()

    total_billed = sum(b["total_amount"] for b in bills)
    total_paid = sum(b["total_amount"] for b in bills if b["payment_status"] == "Paid")
    unpaid_bills = [b for b in bills if b["payment_status"] != "Paid"]

    return {
        "patient_id": patient["patient_id"],
        "full_name": patient["full_name"],
        "gender": patient["gender"],
        "dob": patient["dob"],
        "blood_group": patient["blood_group"],
        "phone": patient["phone"],
        "admission_date": patient["created_at"],
        "room_id": patient["room_id"],
        "room_number": patient["room_number"],
        "room_type": patient["room_type"],
        "rate_per_day": patient["rate_per_day"],
        "total_billed": round(total_billed, 2),
        "total_paid": round(total_paid, 2),
        "balance_due": round(total_billed - total_paid, 2),
        "has_unpaid_bills": len(unpaid_bills) > 0,
        "is_admitted": bool(patient["room_id"])
    }


def discharge(patient_id, discharge_notes="", room_status_after="Available"):
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT p.*, r.room_number FROM patients p LEFT JOIN rooms r ON p.room_id = r.room_id WHERE p.patient_id = ?",
        (patient_id,)
    ).fetchone()
    if not row:
        conn.close()
        return None

    room_id = row["room_id"]
    room_num = row["room_number"]
    full_name = row["full_name"]
    discharge_time = now()

    # Clear patient room assignment
    cur.execute(
        "UPDATE patients SET room_id = NULL, updated_at = ? WHERE patient_id = ?",
        (discharge_time, patient_id)
    )

    details = f"Discharged patient '{full_name}'."
    if room_num:
        details += f" Released Room #{room_num} (marked as {room_status_after})."
    if discharge_notes:
        details += f" Advice: {discharge_notes}"

    log_audit(conn, "patients", patient_id, "UPDATE", details)

    # Automated bed clearance
    if room_id:
        cur.execute("UPDATE rooms SET status = ? WHERE room_id = ?", (room_status_after, room_id))
        log_audit(conn, "rooms", room_id, "UPDATE",
                  f"Automated bed clearance: Room #{room_num} set to '{room_status_after}' upon patient discharge")

    conn.commit()
    conn.close()

    return {
        "patient_id": patient_id,
        "full_name": full_name,
        "freed_room_id": room_id,
        "freed_room_number": room_num,
        "room_status_after": room_status_after,
        "discharge_time": discharge_time,
        "notes": discharge_notes
    }


def get_allergies(patient_id):
    """Retrieve recorded allergies for a patient to support prescription Poka-Yoke."""
    conn = get_connection()
    row = conn.execute("SELECT allergies FROM patients WHERE patient_id=?", (patient_id,)).fetchone()
    conn.close()
    return row["allergies"] if row and row["allergies"] else "None"


def record_vitals(patient_id, systolic, diastolic, pulse, temperature, spo2, triage_status="Normal", user="front_desk_user"):
    """Clinical Poka-Yoke: Record triage vital signs with bounded ranges."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO vitals_log (patient_id, systolic, diastolic, pulse, temperature, spo2, triage_status, recorded_at, recorded_by) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (patient_id, systolic, diastolic, pulse, temperature, spo2, triage_status, now(), user)
    )
    vital_id = cur.lastrowid
    log_audit(
        conn, "vitals_log", vital_id, "INSERT",
        f"Recorded vitals for patient #{patient_id}: BP {systolic}/{diastolic}, HR {pulse}, Temp {temperature}F, SpO2 {spo2}% ({triage_status})",
        user=user
    )
    conn.commit()
    conn.close()
    return vital_id


def get_vitals_history(patient_id, limit=10):
    """Fetch chronological vital signs for patient chart."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM vitals_log WHERE patient_id=? ORDER BY vital_id DESC LIMIT ?",
        (patient_id, limit)
    ).fetchall()
    conn.close()
    return rows


def get_patient_360_timeline(patient_id: int):
    """
    Patient 360° Comprehensive Journey:
    Aggregates all chronological hospital touchpoints for the patient:
    Registration, Triage Vitals, Appointments, Inpatient Admissions, Prescriptions, Lab Tests, and Bills.
    Returns: {"patient": dict, "total_events": int, "timeline": list of sorted event dicts}.
    """
    conn = get_connection()
    try:
        p_row = conn.execute("""
            SELECT p.*, r.room_number, r.room_type, r.rate_per_day
            FROM patients p
            LEFT JOIN rooms r ON p.room_id = r.room_id
            WHERE p.patient_id = ?
        """, (patient_id,)).fetchone()

        if not p_row:
            return None

        patient_info = dict(p_row)
        patient_info["uhid"] = format_uhid(patient_id)
        events = []

        # 1. Registration Event
        events.append({
            "event_type": "Registration",
            "timestamp": patient_info["created_at"],
            "title": "Patient Registered",
            "badge_color": "#17a2b8",
            "icon": "📝",
            "details": f"Registered in HMS. Gender: {patient_info['gender']}, DOB: {patient_info['dob']}, Blood Group: {patient_info['blood_group']}, Allergies: {patient_info.get('allergies', 'None')}."
        })

        # 2. Vitals Events
        v_rows = conn.execute("SELECT * FROM vitals_log WHERE patient_id = ? ORDER BY recorded_at", (patient_id,)).fetchall()
        for v in v_rows:
            events.append({
                "event_type": "Triage Vitals",
                "timestamp": v["recorded_at"],
                "title": f"Vitals Recorded ({v['triage_status']})",
                "badge_color": "#28a745" if v["triage_status"] == "Normal" else "#dc3545",
                "icon": "💓",
                "details": f"BP: {v['systolic']}/{v['diastolic']} mmHg, Pulse: {v['pulse']} bpm, Temp: {v['temperature']}°F, SpO2: {v['spo2']}%. Evaluated by: {v['recorded_by']}."
            })

        # 3. Appointments
        appt_rows = conn.execute("""
            SELECT a.*, d.full_name as doctor_name, d.department
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = ?
            ORDER BY a.appt_date, a.appt_time
        """, (patient_id,)).fetchall()
        for a in appt_rows:
            events.append({
                "event_type": "Appointment",
                "timestamp": f"{a['appt_date']}T{a['appt_time']}:00",
                "title": f"Consultation with {a['doctor_name']} ({a['status']})",
                "badge_color": "#007bff" if a["status"] == "Scheduled" else ("#28a745" if a["status"] == "Completed" else "#6c757d"),
                "icon": "📅",
                "details": f"Department: {a['department']}. Slot: {a['appt_date']} at {a['appt_time']}. Notes: {a['notes'] or 'None'}."
            })

        # 4. Inpatient Admissions
        adm_rows = conn.execute("""
            SELECT a.*, r.room_number, r.room_type
            FROM admissions a
            JOIN rooms r ON a.room_id = r.room_id
            WHERE a.patient_id = ?
            ORDER BY a.admission_date
        """, (patient_id,)).fetchall()
        for adm in adm_rows:
            events.append({
                "event_type": "Inpatient Admission",
                "timestamp": adm["created_at"],
                "title": f"Admitted to Room {adm['room_number']} ({adm['room_type']})",
                "badge_color": "#6f42c1",
                "icon": "🛏️",
                "details": f"Admission Date: {adm['admission_date'][:10]}. Diagnosis: {adm.get('diagnosis') or 'Clinical admission'}. Status: {adm['status']}."
            })
            if adm["discharge_date"]:
                events.append({
                    "event_type": "Inpatient Discharge",
                    "timestamp": adm["discharge_date"] if "T" in adm["discharge_date"] else f"{adm['discharge_date']}T12:00:00",
                    "title": f"Discharged from Room {adm['room_number']}",
                    "badge_color": "#20c997",
                    "icon": "🚪",
                    "details": f"Discharge Notes: {adm.get('discharge_notes') or 'Routine discharge completed'}."
                })

        # 5. Prescriptions
        rx_rows = conn.execute("""
            SELECT pr.*, m.name as medicine_name, d.full_name as doctor_name
            FROM prescriptions pr
            JOIN medicines m ON pr.medicine_id = m.medicine_id
            JOIN doctors d ON pr.doctor_id = d.doctor_id
            WHERE pr.patient_id = ?
            ORDER BY pr.prescribed_date
        """, (patient_id,)).fetchall()
        for rx in rx_rows:
            events.append({
                "event_type": "Prescription",
                "timestamp": f"{rx['prescribed_date']}T10:00:00" if len(rx['prescribed_date']) == 10 else rx['prescribed_date'],
                "title": f"Rx: {rx['medicine_name']} ({rx['status']})",
                "badge_color": "#fd7e14",
                "icon": "💊",
                "details": f"Prescribed by {rx['doctor_name']}. Dosage: {rx['dosage']}, Frequency: {rx['frequency']}, Duration: {rx['duration_days']} days. Instructions: {rx['instructions'] or 'As directed'}."
            })

        # 6. Lab Tests
        lab_rows = conn.execute("""
            SELECT l.*, d.full_name as doctor_name
            FROM lab_tests l
            JOIN doctors d ON l.doctor_id = d.doctor_id
            WHERE l.patient_id = ?
            ORDER BY l.created_at
        """, (patient_id,)).fetchall()
        for lab in lab_rows:
            flag_str = " [ABNORMAL]" if lab["abnormal_flag"] else ""
            events.append({
                "event_type": "Diagnostic Lab Test",
                "timestamp": lab["completed_at"] or lab["created_at"],
                "title": f"Lab: {lab['test_name']}{flag_str}",
                "badge_color": "#dc3545" if lab["abnormal_flag"] else "#17a2b8",
                "icon": "🔬",
                "details": f"Category: {lab['category']}. Result: {lab['result_value'] or 'Pending'} {lab['unit']} (Ref: {lab['ref_min']}-{lab['ref_max']}). Status: {lab['status']}."
            })

        # 7. Bills
        bill_rows = conn.execute("""
            SELECT * FROM bills WHERE patient_id = ? ORDER BY created_at
        """, (patient_id,)).fetchall()
        for b in bill_rows:
            events.append({
                "event_type": "Billing & Invoicing",
                "timestamp": b["created_at"],
                "title": f"Invoice INV-{b['bill_id']:05d} ({b['payment_status']})",
                "badge_color": "#28a745" if b["payment_status"] == "Paid" else "#ffc107",
                "icon": "🧾",
                "details": f"Total Amount: ₹{float(b['total_amount']):.2f} (Room: ₹{float(b['room_charges']):.2f}, Consult: ₹{float(b['consultation_charges']):.2f}, Meds: ₹{float(b['medicine_charges']):.2f}). Paid via: {b['payment_method']}."
            })

        # Sort timeline chronologically descending (most recent first)
        events.sort(key=lambda x: x["timestamp"], reverse=True)

        return {
            "patient": patient_info,
            "total_events": len(events),
            "timeline": events
        }
    finally:
        conn.close()



