"""
prescription.py -- Model for Prescriptions and Patient Visit Medical History.
Links medicines directly to patients with automated Clinical Poka-Yoke allergy checks.
"""
from datetime import datetime
from database.db_manager import get_connection, log_audit
from utils.exception_handler import ValidationError
from utils.validators import check_drug_allergy_contraindication


def _now():
    return datetime.now().isoformat(timespec="seconds")


def create_prescription(
    patient_id: int,
    doctor_id: int,
    medicine_id: int,
    dosage: str,
    frequency: str,
    duration_days: int = 5,
    instructions: str = "",
    appointment_id: int = None,
    prescribed_date: str = None,
    performed_by: str = "doctor_user"
):
    """
    Creates a prescription record.
    Poka-Yoke: Automatically cross-references patient's registered allergies
    against the prescribed medicine before saving.
    """
    if not patient_id:
        raise ValidationError("Patient selection is required", field="patient_id")
    if not doctor_id:
        raise ValidationError("Doctor selection is required", field="doctor_id")
    if not medicine_id:
        raise ValidationError("Medicine selection is required", field="medicine_id")
    if not dosage or not dosage.strip():
        raise ValidationError("Dosage (e.g. '500mg' or '1 tablet') is required", field="dosage")
    if not frequency or not frequency.strip():
        raise ValidationError("Frequency (e.g. 'Twice daily') is required", field="frequency")

    try:
        duration_days = int(duration_days)
        if duration_days <= 0 or duration_days > 90:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValidationError("Duration must be between 1 and 90 days", field="duration_days")

    prescribed_date = prescribed_date or _now()[:10]

    conn = get_connection()
    try:
        # 1. Fetch patient and allergy info
        p = conn.execute("SELECT patient_id, full_name, allergies FROM patients WHERE patient_id = ?", (patient_id,)).fetchone()
        if not p:
            raise ValidationError(f"Patient #{patient_id} not found", field="patient_id")

        # 2. Fetch doctor
        d = conn.execute("SELECT doctor_id, full_name, department FROM doctors WHERE doctor_id = ?", (doctor_id,)).fetchone()
        if not d:
            raise ValidationError(f"Doctor #{doctor_id} not found", field="doctor_id")

        # 3. Fetch medicine
        m = conn.execute("SELECT * FROM medicines WHERE medicine_id = ?", (medicine_id,)).fetchone()
        if not m:
            raise ValidationError(f"Medicine #{medicine_id} not found", field="medicine_id")

        # 4. Clinical Poka-Yoke: Expiry Date Safeguard
        med_dict = dict(m)
        med_expiry = med_dict.get("expiry_date")
        if med_expiry:
            from datetime import date
            if med_expiry < date.today().isoformat():
                raise ValidationError(
                    f"CLINICAL SAFETY ALERT (Poka-Yoke): Cannot prescribe expired medicine '{m['name']}' "
                    f"(Batch: {med_dict.get('batch_no', 'N/A')}, Expired on: {med_expiry}). "
                    f"Dispensing expired medication is blocked.",
                    field="medicine_id"
                )

        # 5. Clinical Poka-Yoke Safety Contraindication Check
        patient_allergy = p["allergies"] or "None"
        contraindication = check_drug_allergy_contraindication(patient_allergy, m["name"], m["category"])
        if contraindication["contraindicated"]:
            raise ValidationError(
                f"CLINICAL SAFETY ALERT: Patient '{p['full_name']}' has documented allergy '{patient_allergy}'. "
                f"Contraindication detected with '{m['name']}': {contraindication['reason']}",
                field="medicine_id"
            )

        cursor = conn.cursor()
        now_ts = _now()
        cursor.execute(
            "INSERT INTO prescriptions "
            "(patient_id, doctor_id, appointment_id, medicine_id, dosage, frequency, duration_days, instructions, prescribed_date, status) "
            "VALUES (?,?,?,?,?,?,?,?,?,'Active')",
            (patient_id, doctor_id, appointment_id, medicine_id, dosage.strip(), frequency.strip(), duration_days, (instructions or "").strip(), prescribed_date)
        )
        rx_id = cursor.lastrowid

        log_audit(
            conn,
            "prescriptions",
            rx_id,
            "INSERT",
            f"Prescribed '{m['name']}' ({dosage}, {frequency}, {duration_days}d) for patient '{p['full_name']}' by Dr. '{d['full_name']}'",
            performed_by
        )
        conn.commit()
        return rx_id
    finally:
        conn.close()


def dispense_prescription(prescription_id: int, qty_dispensed: int = None, performed_by: str = "pharmacist_user"):
    """
    Dispenses an active prescription, deducting the medicine inventory stock.
    """
    conn = get_connection()
    try:
        rx = conn.execute(
            "SELECT rx.*, m.name as medicine_name, m.stock_qty, m.batch_no, m.expiry_date, p.full_name as patient_name "
            "FROM prescriptions rx "
            "JOIN medicines m ON rx.medicine_id = m.medicine_id "
            "JOIN patients p ON rx.patient_id = p.patient_id "
            "WHERE rx.prescription_id = ?",
            (prescription_id,)
        ).fetchone()

        if not rx:
            raise ValidationError(f"Prescription #{prescription_id} not found", field="prescription_id")
        if rx["status"] != "Active":
            raise ValidationError(f"Cannot dispense prescription with status '{rx['status']}' (only 'Active' prescriptions can be dispensed)", field="prescription_id")

        qty = qty_dispensed if qty_dispensed is not None else rx["duration_days"]
        try:
            qty = int(qty)
            if qty <= 0:
                raise ValueError()
        except (TypeError, ValueError):
            raise ValidationError("Dispensed quantity must be an integer >= 1", field="qty_dispensed")

        if "expiry_date" in rx.keys() and rx["expiry_date"]:
            from datetime import date
            if rx["expiry_date"] < date.today().isoformat():
                raise ValidationError(
                    f"CLINICAL SAFETY ALERT (Poka-Yoke): Medicine '{rx['medicine_name']}' in stock has expired on {rx['expiry_date']} (Batch: {rx['batch_no']}). Dispense blocked.",
                    field="medicine_id"
                )

        if rx["stock_qty"] < qty:
            raise ValidationError(f"Insufficient inventory for '{rx['medicine_name']}'. In stock: {rx['stock_qty']}, required: {qty}", field="stock_qty")

        cursor = conn.cursor()
        # Deduct inventory
        cursor.execute("UPDATE medicines SET stock_qty = stock_qty - ? WHERE medicine_id = ?", (qty, rx["medicine_id"]))
        # Update prescription status
        cursor.execute("UPDATE prescriptions SET status = 'Dispensed' WHERE prescription_id = ?", (prescription_id,))

        log_audit(
            conn,
            "prescriptions",
            prescription_id,
            "UPDATE",
            f"Dispensed prescription #{prescription_id} ({qty} units of '{rx['medicine_name']}') to patient '{rx['patient_name']}'",
            performed_by
        )
        conn.commit()
        return True
    finally:
        conn.close()


def list_prescriptions(patient_id: int = None, active_only: bool = False):
    conn = get_connection()
    try:
        query = (
            "SELECT rx.*, p.full_name as patient_name, p.allergies as patient_allergies, "
            "d.full_name as doctor_name, d.department, "
            "m.name as medicine_name, m.category as medicine_category, m.unit_price, m.stock_qty "
            "FROM prescriptions rx "
            "JOIN patients p ON rx.patient_id = p.patient_id "
            "JOIN doctors d ON rx.doctor_id = d.doctor_id "
            "JOIN medicines m ON rx.medicine_id = m.medicine_id "
        )
        params = []
        conditions = []
        if patient_id:
            conditions.append("rx.patient_id = ?")
            params.append(patient_id)
        if active_only:
            conditions.append("rx.status = 'Active'")

        if conditions:
            query += "WHERE " + " AND ".join(conditions) + " "
        query += "ORDER BY rx.prescription_id DESC"

        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
