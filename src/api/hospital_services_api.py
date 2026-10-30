"""
hospital_services_api.py -- REST API Blueprint for Extended Hospital Services & Clinical Specialties
Covers:
  1. Medical Records (MRD)
  2. Mortuary Register & Decedents
  3. Central Sterile Services (CSSD)
  4. Laundry and Linen
  5. Infection Control & HAI Surveillance
  6. Dialysis Scheduling & Hemodialysis
  7. Maternity, Labour & Nursery
  8. Physiotherapy Sessions & Rehabilitation
  9. Health Checkup Packages
  10. Vaccination & Immunization Register
  11. Referral Management (Inbound / Outbound)
  12. Patient Feedback & Complaints
  13. Telemedicine Appointments & Virtual Care
  14. Security Gate & Campus Access Log
  15. Pharmacy Returns & Medicine Credit
  16. Mortality & Morbidity (M&M) Review
  17. Medical Gas & Fire Safety Checklists
"""
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from database.db_manager import get_connection, log_audit
from auth.permissions import require_permission
from utils.exception_handler import ValidationError

hospital_services_bp = Blueprint("hospital_services_api", __name__)


# -------------------------------------------------------------
# 1. MEDICAL RECORDS (MRD)
# -------------------------------------------------------------
@hospital_services_bp.route("/medical-records", methods=["GET"])
@hospital_services_bp.route("/mrd", methods=["GET"])
@require_permission("mrd", "view")
def list_medical_records():
    conn = get_connection()
    try:
        q = request.args.get("q", "").strip().lower()
        if q:
            rows = conn.execute(
                "SELECT * FROM medical_records WHERE LOWER(uhid) LIKE ? OR LOWER(patient_name) LIKE ? OR LOWER(icd_code) LIKE ? ORDER BY record_id DESC",
                (f"%{q}%", f"%{q}%", f"%{q}%")
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM medical_records ORDER BY record_id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@hospital_services_bp.route("/medical-records", methods=["POST"])
@require_permission("mrd", "create")
def create_medical_record():
    data = request.get_json() or {}
    uhid = data.get("uhid", "").strip()
    patient_name = data.get("patient_name", "").strip()
    location_shelf = data.get("location_shelf", "").strip()
    if not uhid or not patient_name or not location_shelf:
        return jsonify({"error": "UHID, patient name, and storage location shelf are required"}), 400

    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO medical_records (uhid, patient_name, icd_code, diagnosis, location_shelf, status, requested_by, issue_date, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (uhid, patient_name, data.get("icd_code", "Z00.0"), data.get("diagnosis", ""), location_shelf, data.get("status", "Archived"), data.get("requested_by"), data.get("issue_date"), now_str)
        )
        rec_id = cur.lastrowid
        log_audit(conn, "medical_records", rec_id, "INSERT", f"Archived medical record for {patient_name} ({uhid}) at {location_shelf}", user)
        conn.commit()
        return jsonify({"message": "Medical record registered successfully", "record_id": rec_id}), 201
    finally:
        conn.close()


@hospital_services_bp.route("/medical-records/<int:rec_id>/status", methods=["PUT"])
@require_permission("mrd", "edit")
def update_medical_record_status(rec_id):
    data = request.get_json() or {}
    status = data.get("status", "").strip()
    requested_by = data.get("requested_by", "").strip()
    if not status:
        return jsonify({"error": "Status is required"}), 400

    user = session.get("username", "admin")
    now_str = datetime.now().isoformat(timespec="seconds")
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE medical_records SET status = ?, requested_by = ?, issue_date = ? WHERE record_id = ?",
            (status, requested_by or None, now_str if status == "Issued" else None, rec_id)
        )
        log_audit(conn, "medical_records", rec_id, "UPDATE", f"MRD record status updated to {status}", user)
        conn.commit()
        return jsonify({"message": f"Record status updated to {status}"}), 200
    finally:
        conn.close()


# -------------------------------------------------------------
# 2. MORTUARY REGISTER & DECEDENTS
# -------------------------------------------------------------
@hospital_services_bp.route("/mortuary", methods=["GET"])
@require_permission("mortuary", "view")
def list_mortuary_cases():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM mortuary_register ORDER BY case_id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@hospital_services_bp.route("/mortuary", methods=["POST"])
@require_permission("mortuary", "create")
def admit_mortuary_case():
    data = request.get_json() or {}
    patient_name = data.get("patient_name", "").strip()
    freezer_number = data.get("freezer_number", "").strip()
    death_time = data.get("date_time_of_death", "").strip()
    if not patient_name or not freezer_number or not death_time:
        return jsonify({"error": "Decedent name, freezer number, and date/time of death are required"}), 400

    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO mortuary_register (deceased_uhid, patient_name, age, gender, cause_of_death, date_time_of_death, freezer_number, status, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (data.get("deceased_uhid", ""), patient_name, int(data.get("age", 0)), data.get("gender", "Unknown"), data.get("cause_of_death", ""), death_time, freezer_number, "Admitted", now_str)
        )
        case_id = cur.lastrowid
        log_audit(conn, "mortuary_register", case_id, "INSERT", f"Admitted decedent {patient_name} to {freezer_number}", user)
        conn.commit()
        return jsonify({"message": "Mortuary case logged", "case_id": case_id}), 201
    finally:
        conn.close()


@hospital_services_bp.route("/mortuary/<int:case_id>/status", methods=["PUT"])
@require_permission("mortuary", "edit")
def update_mortuary_status(case_id):
    data = request.get_json() or {}
    status = data.get("status", "Released")
    claimant = data.get("claimant_name", "").strip()
    id_proof = data.get("id_proof_type", "").strip()
    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE mortuary_register SET status = ?, claimant_name = ?, id_proof_type = ?, release_date = ? WHERE case_id = ?",
            (status, claimant, id_proof, now_str if status == "Released" else None, case_id)
        )
        log_audit(conn, "mortuary_register", case_id, "UPDATE", f"Mortuary case released to {claimant}", user)
        conn.commit()
        return jsonify({"message": f"Mortuary status updated to {status}"}), 200
    finally:
        conn.close()


# -------------------------------------------------------------
# 3. CENTRAL STERILE SERVICES (CSSD)
# -------------------------------------------------------------
@hospital_services_bp.route("/cssd", methods=["GET"])
@require_permission("cssd", "view")
def list_cssd_cycles():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM cssd_cycles ORDER BY cycle_id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@hospital_services_bp.route("/cssd", methods=["POST"])
@require_permission("cssd", "create")
def log_cssd_cycle():
    data = request.get_json() or {}
    set_name = data.get("set_name", "").strip()
    autoclave_id = data.get("autoclave_id", "").strip()
    if not set_name or not autoclave_id:
        return jsonify({"error": "Instrument set name and autoclave unit are required"}), 400

    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO cssd_cycles (set_name, set_code, department_name, autoclave_id, cycle_type, temp_c, pressure_psi, bio_indicator, status, operator_name, cycle_date, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (set_name, data.get("set_code", "SET-GEN"), data.get("department_name", "Operation Theatre"), autoclave_id, data.get("cycle_type", "Pre-Vacuum Steam 134C"), float(data.get("temp_c", 134.0)), float(data.get("pressure_psi", 30.5)), data.get("bio_indicator", "Passed (Negative)"), data.get("status", "Sterilizing"), user, now_str[:10], now_str)
        )
        cycle_id = cur.lastrowid
        log_audit(conn, "cssd_cycles", cycle_id, "INSERT", f"Loaded CSSD sterilization cycle for {set_name}", user)
        conn.commit()
        return jsonify({"message": "CSSD sterilization cycle logged", "cycle_id": cycle_id}), 201
    finally:
        conn.close()


@hospital_services_bp.route("/cssd/<int:cycle_id>/status", methods=["PUT"])
@require_permission("cssd", "edit")
def update_cssd_cycle_status(cycle_id):
    data = request.get_json() or {}
    status = data.get("status", "Sterile - Released")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        conn.execute("UPDATE cssd_cycles SET status = ? WHERE cycle_id = ?", (status, cycle_id))
        log_audit(conn, "cssd_cycles", cycle_id, "UPDATE", f"CSSD cycle status updated to {status}", user)
        conn.commit()
        return jsonify({"message": f"Cycle status updated to {status}"}), 200
    finally:
        conn.close()


# -------------------------------------------------------------
# 4. LAUNDRY & LINEN MANAGEMENT
# -------------------------------------------------------------
@hospital_services_bp.route("/laundry", methods=["GET"])
@require_permission("laundry", "view")
def list_laundry_linen():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM laundry_linen ORDER BY linen_id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@hospital_services_bp.route("/laundry", methods=["POST"])
@require_permission("laundry", "create")
def log_laundry_linen():
    data = request.get_json() or {}
    ward_name = data.get("ward_name", "").strip()
    linen_type = data.get("linen_type", "").strip()
    if not ward_name or not linen_type:
        return jsonify({"error": "Ward name and linen type are required"}), 400

    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO laundry_linen (ward_name, linen_type, qty_clean, qty_soiled, qty_dispatched, status, updated_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (ward_name, linen_type, int(data.get("qty_clean", 0)), int(data.get("qty_soiled", 0)), int(data.get("qty_dispatched", 0)), data.get("status", "In Circulation"), now_str)
        )
        linen_id = cur.lastrowid
        log_audit(conn, "laundry_linen", linen_id, "INSERT", f"Added laundry tracking for {linen_type} in {ward_name}", user)
        conn.commit()
        return jsonify({"message": "Linen inventory logged", "linen_id": linen_id}), 201
    finally:
        conn.close()


@hospital_services_bp.route("/laundry/<int:linen_id>/status", methods=["PUT"])
@require_permission("laundry", "edit")
def update_laundry_status(linen_id):
    data = request.get_json() or {}
    status = data.get("status", "In Circulation")
    clean = int(data.get("qty_clean", 0))
    soiled = int(data.get("qty_soiled", 0))
    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE laundry_linen SET status = ?, qty_clean = ?, qty_soiled = ?, updated_at = ? WHERE linen_id = ?",
            (status, clean, soiled, now_str, linen_id)
        )
        log_audit(conn, "laundry_linen", linen_id, "UPDATE", f"Linen status updated to {status}", user)
        conn.commit()
        return jsonify({"message": f"Linen status updated to {status}"}), 200
    finally:
        conn.close()


# -------------------------------------------------------------
# 5. INFECTION CONTROL & HAI SURVEILLANCE
# -------------------------------------------------------------
@hospital_services_bp.route("/infection-control", methods=["GET"])
@require_permission("infection_control", "view")
def list_infection_surveillance():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM infection_control_surveillance ORDER BY surveillance_id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@hospital_services_bp.route("/infection-control", methods=["POST"])
@require_permission("infection_control", "create")
def log_infection_surveillance():
    data = request.get_json() or {}
    uhid = data.get("uhid", "").strip()
    patient_name = data.get("patient_name", "").strip()
    infection_type = data.get("infection_type", "").strip()
    if not uhid or not patient_name or not infection_type:
        return jsonify({"error": "UHID, patient name, and infection type are required"}), 400

    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO infection_control_surveillance (uhid, patient_name, infection_type, organism_isolated, ward_name, isolation_flag, status, onset_date, reported_by, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (uhid, patient_name, infection_type, data.get("organism_isolated", "Pending Culture"), data.get("ward_name", "ICU"), data.get("isolation_flag", "Contact Precaution"), "Active Surveillance", data.get("onset_date", now_str[:10]), user, now_str)
        )
        surv_id = cur.lastrowid
        log_audit(conn, "infection_control_surveillance", surv_id, "INSERT", f"Flagged HAI infection {infection_type} for {patient_name} ({uhid})", user)
        conn.commit()
        return jsonify({"message": "Infection surveillance flagged", "surveillance_id": surv_id}), 201
    finally:
        conn.close()


@hospital_services_bp.route("/infection-control/<int:surv_id>/status", methods=["PUT"])
@require_permission("infection_control", "edit")
def update_infection_surveillance_status(surv_id):
    data = request.get_json() or {}
    status = data.get("status", "Resolved")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        conn.execute("UPDATE infection_control_surveillance SET status = ? WHERE surveillance_id = ?", (status, surv_id))
        log_audit(conn, "infection_control_surveillance", surv_id, "UPDATE", f"Infection surveillance marked {status}", user)
        conn.commit()
        return jsonify({"message": f"Infection surveillance marked {status}"}), 200
    finally:
        conn.close()


# -------------------------------------------------------------
# 6. DIALYSIS SESSIONS
# -------------------------------------------------------------
@hospital_services_bp.route("/dialysis", methods=["GET"])
@require_permission("dialysis", "view")
def list_dialysis_sessions():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM dialysis_sessions ORDER BY session_id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@hospital_services_bp.route("/dialysis", methods=["POST"])
@require_permission("dialysis", "create")
def schedule_dialysis_session():
    data = request.get_json() or {}
    uhid = data.get("uhid", "").strip()
    patient_name = data.get("patient_name", "").strip()
    machine_no = data.get("machine_no", "").strip()
    if not uhid or not patient_name or not machine_no:
        return jsonify({"error": "UHID, patient name, and dialysis machine are required"}), 400

    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO dialysis_sessions (uhid, patient_name, machine_no, dialyzer_type, pre_weight, post_weight, heparin_units, session_date, doctor_name, status, bill_id, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (uhid, patient_name, machine_no, data.get("dialyzer_type", "High-Flux Polysulfone 1.8"), float(data.get("pre_weight", 0.0) or 0.0), None, int(data.get("heparin_units", 5000) or 5000), data.get("session_date", now_str[:10]), data.get("doctor_name", "Dr. Priya Nair"), "Scheduled", data.get("bill_id"), now_str)
        )
        sess_id = cur.lastrowid
        log_audit(conn, "dialysis_sessions", sess_id, "INSERT", f"Scheduled hemodialysis for {patient_name} on {machine_no}", user)
        conn.commit()
        return jsonify({"message": "Dialysis session scheduled", "session_id": sess_id}), 201
    finally:
        conn.close()


@hospital_services_bp.route("/dialysis/<int:sess_id>/status", methods=["PUT"])
@require_permission("dialysis", "edit")
def update_dialysis_status(sess_id):
    data = request.get_json() or {}
    status = data.get("status", "Completed")
    post_weight = data.get("post_weight")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE dialysis_sessions SET status = ?, post_weight = COALESCE(?, post_weight) WHERE session_id = ?",
            (status, float(post_weight) if post_weight else None, sess_id)
        )
        log_audit(conn, "dialysis_sessions", sess_id, "UPDATE", f"Dialysis session updated to {status}", user)
        conn.commit()
        return jsonify({"message": f"Dialysis session marked {status}"}), 200
    finally:
        conn.close()


# -------------------------------------------------------------
# 7. MATERNITY & NURSERY REGISTER
# -------------------------------------------------------------
@hospital_services_bp.route("/maternity", methods=["GET"])
@require_permission("maternity", "view")
def list_maternity_records():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM maternity_nursery ORDER BY delivery_id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@hospital_services_bp.route("/maternity", methods=["POST"])
@require_permission("maternity", "create")
def log_delivery():
    data = request.get_json() or {}
    mother_uhid = data.get("mother_uhid", "").strip()
    mother_name = data.get("mother_name", "").strip()
    if not mother_uhid or not mother_name:
        return jsonify({"error": "Mother UHID and name are required"}), 400

    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO maternity_nursery (mother_uhid, mother_name, baby_gender, birth_weight_kg, birth_datetime, apgar_1min, apgar_5min, delivery_type, pediatrician_name, nursery_bed, status, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (mother_uhid, mother_name, data.get("baby_gender", "Female"), float(data.get("birth_weight_kg", 3.0)), data.get("birth_datetime", now_str), int(data.get("apgar_1min", 8)), int(data.get("apgar_5min", 9)), data.get("delivery_type", "Normal Delivery"), data.get("pediatrician_name", "Dr. Sneha Kulkarni"), data.get("nursery_bed", "Crib-01"), "Delivered", now_str)
        )
        deliv_id = cur.lastrowid
        log_audit(conn, "maternity_nursery", deliv_id, "INSERT", f"Registered newborn delivery for mother {mother_name} ({mother_uhid})", user)
        conn.commit()
        return jsonify({"message": "Birth event registered", "delivery_id": deliv_id}), 201
    finally:
        conn.close()


@hospital_services_bp.route("/maternity/<int:deliv_id>/status", methods=["PUT"])
@require_permission("maternity", "edit")
def update_maternity_status(deliv_id):
    data = request.get_json() or {}
    status = data.get("status", "Discharged")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        conn.execute("UPDATE maternity_nursery SET status = ? WHERE delivery_id = ?", (status, deliv_id))
        log_audit(conn, "maternity_nursery", deliv_id, "UPDATE", f"Maternity status updated to {status}", user)
        conn.commit()
        return jsonify({"message": f"Maternity record updated to {status}"}), 200
    finally:
        conn.close()


# -------------------------------------------------------------
# 8. PHYSIOTHERAPY & REHABILITATION SESSIONS
# -------------------------------------------------------------
@hospital_services_bp.route("/physiotherapy", methods=["GET"])
@require_permission("physiotherapy", "view")
def list_physiotherapy_sessions():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM physiotherapy_sessions ORDER BY session_id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@hospital_services_bp.route("/physiotherapy", methods=["POST"])
@require_permission("physiotherapy", "create")
def log_physiotherapy_session():
    data = request.get_json() or {}
    uhid = data.get("uhid", "").strip()
    patient_name = data.get("patient_name", "").strip()
    protocol = data.get("protocol", "").strip()
    if not uhid or not patient_name or not protocol:
        return jsonify({"error": "UHID, patient name, and rehabilitation protocol are required"}), 400

    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO physiotherapy_sessions (uhid, patient_name, diagnosis, protocol, session_number, total_sessions, therapist_name, status, bill_id, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (uhid, patient_name, data.get("diagnosis", "Rehab Evaluation"), protocol, int(data.get("session_number", 1)), int(data.get("total_sessions", 10)), data.get("therapist_name", "Dr. Shalini Menon"), "Scheduled", data.get("bill_id"), now_str)
        )
        sess_id = cur.lastrowid
        log_audit(conn, "physiotherapy_sessions", sess_id, "INSERT", f"Scheduled PT session for {patient_name} ({uhid})", user)
        conn.commit()
        return jsonify({"message": "Physiotherapy session scheduled", "session_id": sess_id}), 201
    finally:
        conn.close()


@hospital_services_bp.route("/physiotherapy/<int:sess_id>/status", methods=["PUT"])
@require_permission("physiotherapy", "edit")
def update_physiotherapy_status(sess_id):
    data = request.get_json() or {}
    status = data.get("status", "Completed")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        conn.execute("UPDATE physiotherapy_sessions SET status = ? WHERE session_id = ?", (status, sess_id))
        log_audit(conn, "physiotherapy_sessions", sess_id, "UPDATE", f"Physiotherapy session updated to {status}", user)
        conn.commit()
        return jsonify({"message": f"Session status updated to {status}"}), 200
    finally:
        conn.close()


# -------------------------------------------------------------
# 9. HEALTH CHECKUP PACKAGES
# -------------------------------------------------------------
@hospital_services_bp.route("/health-packages", methods=["GET"])
@require_permission("health_packages", "view")
def list_health_packages():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM health_packages ORDER BY package_id ASC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@hospital_services_bp.route("/health-packages", methods=["POST"])
@require_permission("health_packages", "create")
def create_health_package():
    data = request.get_json() or {}
    name = data.get("package_name", "").strip()
    code = data.get("code", "").strip().upper()
    price = data.get("price")
    if not name or not code or price is None:
        return jsonify({"error": "Package name, unique code, and price are required"}), 400

    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO health_packages (package_name, code, description, price, tests_included, active, created_at) "
            "VALUES (?,?,?,?,?,1,?)",
            (name, code, data.get("description", ""), float(price), data.get("tests_included", "CBC, LFT, KFT"), now_str)
        )
        pkg_id = cur.lastrowid
        log_audit(conn, "health_packages", pkg_id, "INSERT", f"Created wellness package {name} ({code})", user)
        conn.commit()
        return jsonify({"message": "Health package created", "package_id": pkg_id}), 201
    finally:
        conn.close()


@hospital_services_bp.route("/health-packages/<int:pkg_id>/status", methods=["PUT"])
@require_permission("health_packages", "edit")
def toggle_health_package_status(pkg_id):
    data = request.get_json() or {}
    active = int(data.get("active", 1))
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        conn.execute("UPDATE health_packages SET active = ? WHERE package_id = ?", (active, pkg_id))
        log_audit(conn, "health_packages", pkg_id, "UPDATE", f"Health package active state set to {active}", user)
        conn.commit()
        return jsonify({"message": f"Package active state updated to {active}"}), 200
    finally:
        conn.close()


# -------------------------------------------------------------
# 10. VACCINATION REGISTER
# -------------------------------------------------------------
@hospital_services_bp.route("/vaccination", methods=["GET"])
@require_permission("vaccination", "view")
def list_vaccinations():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM vaccination_register ORDER BY vac_id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@hospital_services_bp.route("/vaccination", methods=["POST"])
@require_permission("vaccination", "create")
def log_vaccination():
    data = request.get_json() or {}
    uhid = data.get("uhid", "").strip()
    patient_name = data.get("patient_name", "").strip()
    vaccine_name = data.get("vaccine_name", "").strip()
    if not uhid or not patient_name or not vaccine_name:
        return jsonify({"error": "UHID, patient name, and vaccine name are required"}), 400

    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO vaccination_register (uhid, patient_name, vaccine_name, dose_number, batch_number, expiry_date, administered_by, administration_date, next_due_date, status, bill_id, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (uhid, patient_name, vaccine_name, int(data.get("dose_number", 1)), data.get("batch_number", "BAT-VACC-01"), data.get("expiry_date", "2027-12-31"), user, data.get("administration_date", now_str[:10]), data.get("next_due_date"), "Administered", data.get("bill_id"), now_str)
        )
        vac_id = cur.lastrowid
        log_audit(conn, "vaccination_register", vac_id, "INSERT", f"Administered {vaccine_name} to {patient_name} ({uhid})", user)
        conn.commit()
        return jsonify({"message": "Vaccination record logged", "vac_id": vac_id}), 201
    finally:
        conn.close()


@hospital_services_bp.route("/vaccination/<int:vac_id>/status", methods=["PUT"])
@require_permission("vaccination", "edit")
def update_vaccination_status(vac_id):
    data = request.get_json() or {}
    status = data.get("status", "Administered")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        conn.execute("UPDATE vaccination_register SET status = ? WHERE vac_id = ?", (status, vac_id))
        log_audit(conn, "vaccination_register", vac_id, "UPDATE", f"Vaccination status updated to {status}", user)
        conn.commit()
        return jsonify({"message": f"Vaccination status updated to {status}"}), 200
    finally:
        conn.close()


# -------------------------------------------------------------
# 11. REFERRALS MANAGEMENT
# -------------------------------------------------------------
@hospital_services_bp.route("/referrals", methods=["GET"])
@require_permission("referrals", "view")
def list_referrals():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM referrals ORDER BY referral_id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@hospital_services_bp.route("/referrals", methods=["POST"])
@require_permission("referrals", "create")
def create_referral():
    data = request.get_json() or {}
    uhid = data.get("uhid", "").strip()
    patient_name = data.get("patient_name", "").strip()
    partner_hospital = data.get("partner_hospital", "").strip()
    if not uhid or not patient_name or not partner_hospital:
        return jsonify({"error": "UHID, patient name, and partner hospital are required"}), 400

    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO referrals (uhid, patient_name, referral_type, partner_hospital, doctor_name, specialty, clinical_reason, status, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (uhid, patient_name, data.get("referral_type", "OUTBOUND"), partner_hospital, data.get("doctor_name", "Dr. Rajesh Sharma"), data.get("specialty", "Cardiology"), data.get("clinical_reason", ""), "Pending", now_str)
        )
        ref_id = cur.lastrowid
        log_audit(conn, "referrals", ref_id, "INSERT", f"Initiated referral for {patient_name} to/from {partner_hospital}", user)
        conn.commit()
        return jsonify({"message": "Referral logged successfully", "referral_id": ref_id}), 201
    finally:
        conn.close()


@hospital_services_bp.route("/referrals/<int:ref_id>/status", methods=["PUT"])
@require_permission("referrals", "edit")
def update_referral_status(ref_id):
    data = request.get_json() or {}
    status = data.get("status", "Accepted")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        conn.execute("UPDATE referrals SET status = ? WHERE referral_id = ?", (status, ref_id))
        log_audit(conn, "referrals", ref_id, "UPDATE", f"Referral status updated to {status}", user)
        conn.commit()
        return jsonify({"message": f"Referral status updated to {status}"}), 200
    finally:
        conn.close()


# -------------------------------------------------------------
# 12. PATIENT FEEDBACK & COMPLAINTS
# -------------------------------------------------------------
@hospital_services_bp.route("/feedback", methods=["GET"])
@require_permission("feedback", "view")
def list_feedback():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM patient_feedback ORDER BY feedback_id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@hospital_services_bp.route("/feedback", methods=["POST"])
@require_permission("feedback", "create")
def submit_feedback():
    data = request.get_json() or {}
    dept = data.get("department", "").strip()
    rating = data.get("rating")
    comments = data.get("comments", "").strip()
    if not dept or rating is None or not comments:
        return jsonify({"error": "Department, rating (1-5), and feedback comments are required"}), 400

    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "patient")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO patient_feedback (uhid, patient_name, department, rating, comments, category, status, resolution_notes, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (data.get("uhid"), data.get("patient_name", "Anonymous Patient"), dept, int(rating), comments, data.get("category", "Care Quality"), "Open", None, now_str)
        )
        fb_id = cur.lastrowid
        log_audit(conn, "patient_feedback", fb_id, "INSERT", f"Submitted patient feedback for {dept} with rating {rating}/5", user)
        conn.commit()
        return jsonify({"message": "Feedback submitted successfully", "feedback_id": fb_id}), 201
    finally:
        conn.close()


@hospital_services_bp.route("/feedback/<int:fb_id>/status", methods=["PUT"])
@require_permission("feedback", "edit")
def resolve_feedback(fb_id):
    data = request.get_json() or {}
    status = data.get("status", "Resolved")
    resolution_notes = data.get("resolution_notes", "").strip()
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE patient_feedback SET status = ?, resolution_notes = ? WHERE feedback_id = ?",
            (status, resolution_notes, fb_id)
        )
        log_audit(conn, "patient_feedback", fb_id, "UPDATE", f"Feedback status updated to {status}: {resolution_notes}", user)
        conn.commit()
        return jsonify({"message": f"Feedback marked {status}"}), 200
    finally:
        conn.close()


# -------------------------------------------------------------
# 13. TELEMEDICINE APPOINTMENTS & VIRTUAL CONSULTATIONS
# -------------------------------------------------------------
@hospital_services_bp.route("/telemedicine", methods=["GET"])
@require_permission("telemedicine", "view")
def list_telemedicine():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM telemedicine_appointments ORDER BY telemed_id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@hospital_services_bp.route("/telemedicine", methods=["POST"])
@require_permission("telemedicine", "create")
def book_telemedicine():
    data = request.get_json() or {}
    uhid = data.get("uhid", "").strip()
    patient_name = data.get("patient_name", "").strip()
    appt_time = data.get("appointment_datetime", "").strip()
    if not uhid or not patient_name or not appt_time:
        return jsonify({"error": "UHID, patient name, and appointment date/time are required"}), 400

    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "admin")
    room_hash = f"conf-{abs(hash(uhid + appt_time)) % 100000}"
    meet_link = f"https://telemed.apex-hospital.local/room/{room_hash}"
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO telemedicine_appointments (uhid, patient_name, doctor_id, doctor_name, appointment_datetime, platform_link, chief_complaint, status, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (uhid, patient_name, data.get("doctor_id", 1), data.get("doctor_name", "Dr. Ajay Bora"), appt_time, meet_link, data.get("chief_complaint", "Virtual Consultation"), "Scheduled", now_str)
        )
        tele_id = cur.lastrowid
        log_audit(conn, "telemedicine_appointments", tele_id, "INSERT", f"Booked virtual teleconsultation for {patient_name} ({uhid})", user)
        conn.commit()
        return jsonify({"message": "Telemedicine appointment confirmed", "telemed_id": tele_id, "link": meet_link}), 201
    finally:
        conn.close()


@hospital_services_bp.route("/telemedicine/<int:tele_id>/status", methods=["PUT"])
@require_permission("telemedicine", "edit")
def update_telemedicine_status(tele_id):
    data = request.get_json() or {}
    status = data.get("status", "Completed")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        conn.execute("UPDATE telemedicine_appointments SET status = ? WHERE telemed_id = ?", (status, tele_id))
        log_audit(conn, "telemedicine_appointments", tele_id, "UPDATE", f"Telemedicine appointment updated to {status}", user)
        conn.commit()
        return jsonify({"message": f"Appointment status updated to {status}"}), 200
    finally:
        conn.close()


# -------------------------------------------------------------
# 14. SECURITY GATE & CAMPUS ACCESS LOG
# -------------------------------------------------------------
@hospital_services_bp.route("/security-log", methods=["GET"])
@require_permission("security", "view")
def list_security_log():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM security_gate_log ORDER BY log_id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@hospital_services_bp.route("/security-log", methods=["POST"])
@require_permission("security", "create")
def log_security_entry():
    data = request.get_json() or {}
    visitor_name = data.get("visitor_name", "").strip()
    badge_no = data.get("badge_no", "").strip()
    entry_gate = data.get("entry_gate", "").strip()
    if not visitor_name or not badge_no or not entry_gate:
        return jsonify({"error": "Visitor name, badge number, and entry gate are required"}), 400

    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "security_officer")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO security_gate_log (visitor_name, badge_no, vehicle_no, entry_gate, purpose, patient_uhid, entry_time, exit_time, status, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (visitor_name, badge_no, data.get("vehicle_no"), entry_gate, data.get("purpose", "Visitor Entry"), data.get("patient_uhid"), now_str, None, "Inside", now_str)
        )
        log_id = cur.lastrowid
        log_audit(conn, "security_gate_log", log_id, "INSERT", f"Security gate entry badge {badge_no} issued to {visitor_name}", user)
        conn.commit()
        return jsonify({"message": "Security entry logged", "log_id": log_id}), 201
    finally:
        conn.close()


@hospital_services_bp.route("/security-log/<int:log_id>/status", methods=["PUT"])
@require_permission("security", "edit")
def log_security_exit(log_id):
    data = request.get_json() or {}
    status = data.get("status", "Exited")
    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "security_officer")
    conn = get_connection()
    try:
        conn.execute("UPDATE security_gate_log SET status = ?, exit_time = ? WHERE log_id = ?", (status, now_str if status == "Exited" else None, log_id))
        log_audit(conn, "security_gate_log", log_id, "UPDATE", f"Security badge recorded as {status}", user)
        conn.commit()
        return jsonify({"message": f"Gate log marked {status}"}), 200
    finally:
        conn.close()


# -------------------------------------------------------------
# 15. PHARMACY RETURNS & MEDICINE CREDIT
# -------------------------------------------------------------
@hospital_services_bp.route("/pharmacy-returns", methods=["GET"])
@require_permission("pharmacy_returns", "view")
def list_pharmacy_returns():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM pharmacy_returns ORDER BY return_id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@hospital_services_bp.route("/pharmacy-returns", methods=["POST"])
@require_permission("pharmacy_returns", "create")
def log_pharmacy_return():
    data = request.get_json() or {}
    uhid = data.get("uhid", "").strip()
    medicine_name = data.get("medicine_name", "").strip()
    qty = data.get("qty_returned")
    refund = data.get("refund_amount")
    if not uhid or not medicine_name or qty is None or refund is None:
        return jsonify({"error": "UHID, medicine name, returned quantity, and refund credit are required"}), 400

    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "pharmacist")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO pharmacy_returns (bill_id, patient_id, uhid, medicine_name, qty_returned, refund_amount, return_reason, approved_by, status, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (data.get("bill_id"), data.get("patient_id"), uhid, medicine_name, int(qty), float(refund), data.get("return_reason", "Discharge return"), user, "Approved", now_str)
        )
        ret_id = cur.lastrowid
        log_audit(conn, "pharmacy_returns", ret_id, "INSERT", f"Processed pharmacy return for {qty}x {medicine_name} (Refund INR {refund})", user)
        conn.commit()
        return jsonify({"message": "Pharmacy return processed and credited", "return_id": ret_id}), 201
    finally:
        conn.close()


@hospital_services_bp.route("/pharmacy-returns/<int:ret_id>/status", methods=["PUT"])
@require_permission("pharmacy_returns", "edit")
def update_pharmacy_return_status(ret_id):
    data = request.get_json() or {}
    status = data.get("status", "Approved")
    user = session.get("username", "pharmacist")
    conn = get_connection()
    try:
        conn.execute("UPDATE pharmacy_returns SET status = ? WHERE return_id = ?", (status, ret_id))
        log_audit(conn, "pharmacy_returns", ret_id, "UPDATE", f"Pharmacy return status set to {status}", user)
        conn.commit()
        return jsonify({"message": f"Return status updated to {status}"}), 200
    finally:
        conn.close()


# -------------------------------------------------------------
# 16. MORTALITY & MORBIDITY (M&M) REVIEW
# -------------------------------------------------------------
@hospital_services_bp.route("/mm-reviews", methods=["GET"])
@require_permission("mm_reviews", "view")
def list_mm_reviews():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM morbid_mortality_reviews ORDER BY review_id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@hospital_services_bp.route("/mm-reviews", methods=["POST"])
@require_permission("mm_reviews", "create")
def log_mm_review():
    data = request.get_json() or {}
    uhid = data.get("uhid", "").strip()
    patient_name = data.get("patient_name", "").strip()
    primary_diag = data.get("primary_diagnosis", "").strip()
    if not uhid or not patient_name or not primary_diag:
        return jsonify({"error": "UHID, patient name, and primary diagnosis are required"}), 400

    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO morbid_mortality_reviews (uhid, patient_name, death_date, department, primary_diagnosis, complication, root_cause, preventability, committee_chair, status, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (uhid, patient_name, data.get("death_date", now_str[:10]), data.get("department", "Cardiology"), primary_diag, data.get("complication", ""), data.get("root_cause", ""), data.get("preventability", "Potentially Preventable"), data.get("committee_chair", "Dr. Sunita Rao"), "Under Review", now_str)
        )
        rev_id = cur.lastrowid
        log_audit(conn, "morbid_mortality_reviews", rev_id, "INSERT", f"Logged M&M review case for {patient_name} ({uhid})", user)
        conn.commit()
        return jsonify({"message": "M&M clinical review case submitted", "review_id": rev_id}), 201
    finally:
        conn.close()


@hospital_services_bp.route("/mm-reviews/<int:rev_id>/status", methods=["PUT"])
@require_permission("mm_reviews", "edit")
def update_mm_review_status(rev_id):
    data = request.get_json() or {}
    status = data.get("status", "Closed")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        conn.execute("UPDATE morbid_mortality_reviews SET status = ? WHERE review_id = ?", (status, rev_id))
        log_audit(conn, "morbid_mortality_reviews", rev_id, "UPDATE", f"M&M review case marked {status}", user)
        conn.commit()
        return jsonify({"message": f"M&M case updated to {status}"}), 200
    finally:
        conn.close()


# -------------------------------------------------------------
# 17. MEDICAL GAS & FIRE SAFETY CHECKLISTS
# -------------------------------------------------------------
@hospital_services_bp.route("/safety-checklists", methods=["GET"])
@require_permission("safety_checklists", "view")
def list_safety_checklists():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM facility_safety_checklists ORDER BY check_id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200
    finally:
        conn.close()


@hospital_services_bp.route("/safety-checklists", methods=["POST"])
@require_permission("safety_checklists", "create")
def log_safety_inspection():
    data = request.get_json() or {}
    o2_psi = data.get("o2_manifold_psi")
    if o2_psi is None:
        return jsonify({"error": "O2 manifold pressure reading (PSI) is required"}), 400

    now_str = datetime.now().isoformat(timespec="seconds")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO facility_safety_checklists (inspection_date, inspector_name, o2_manifold_psi, n2o_psi, vacuum_bar, fire_extinguishers_ok, smoke_alarms_ok, emergency_exits_clear, status, remarks, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (now_str[:10], user, float(o2_psi), float(data.get("n2o_psi", 55.0)), float(data.get("vacuum_bar", -0.65)), int(data.get("fire_extinguishers_ok", 1)), int(data.get("smoke_alarms_ok", 1)), int(data.get("emergency_exits_clear", 1)), data.get("status", "Compliant"), data.get("remarks", "All safety indicators within standard limits"), now_str)
        )
        check_id = cur.lastrowid
        log_audit(conn, "facility_safety_checklists", check_id, "INSERT", f"Completed safety inspection by {user} (O2: {o2_psi} PSI)", user)
        conn.commit()
        return jsonify({"message": "Facility safety inspection logged", "check_id": check_id}), 201
    finally:
        conn.close()


@hospital_services_bp.route("/safety-checklists/<int:check_id>/status", methods=["PUT"])
@require_permission("safety_checklists", "edit")
def update_safety_checklist_status(check_id):
    data = request.get_json() or {}
    status = data.get("status", "Compliant")
    user = session.get("username", "admin")
    conn = get_connection()
    try:
        conn.execute("UPDATE facility_safety_checklists SET status = ? WHERE check_id = ?", (status, check_id))
        log_audit(conn, "facility_safety_checklists", check_id, "UPDATE", f"Safety checklist status set to {status}", user)
        conn.commit()
        return jsonify({"message": f"Checklist status marked {status}"}), 200
    finally:
        conn.close()
