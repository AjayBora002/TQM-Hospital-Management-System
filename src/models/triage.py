"""
triage.py -- Model and clinical logic for Emergency Priority Triage Queue.
Implements automated Manchester/ESI triage scoring to rank incoming walk-in
and emergency patients by physiological severity (Code Red, Yellow, Green).
"""
from datetime import datetime
from database.db_manager import get_connection


def evaluate_triage_tier(systolic=None, diastolic=None, pulse=None, temperature=None, spo2=None):
    """
    Computes clinical emergency priority tier based on vital parameters:
    - Code Red (Resuscitation) -> Priority 1: Imminent life threat (SpO2 < 90, severe arrhythmia, crisis BP, hyper/hypothermia)
    - Code Yellow (Urgent)     -> Priority 2: Serious illness requiring prompt intervention
    - Code Green (Stable)      -> Priority 3: Non-urgent stable patient
    """
    def _to_num(val, cast=float):
        if val is None or str(val).strip() == "":
            return None
        try:
            return cast(val)
        except (ValueError, TypeError):
            return None

    systolic = _to_num(systolic, int)
    diastolic = _to_num(diastolic, int)
    pulse = _to_num(pulse, int)
    temperature = _to_num(temperature, float)
    spo2 = _to_num(spo2, int)

    reasons = []

    # Check Code Red criteria
    if spo2 is not None and spo2 < 90:
        reasons.append(f"Severe Hypoxemia (SpO2: {spo2}%)")
    if pulse is not None and (pulse > 130 or pulse < 45):
        reasons.append(f"Critical Arrhythmia (Pulse: {pulse} bpm)")
    if systolic is not None and (systolic > 180 or systolic < 80):
        reasons.append(f"Hypertensive Crisis / Shock (BP: {systolic}/{diastolic or '-'} mmHg)")
    elif diastolic is not None and (diastolic >= 120 or diastolic < 50):
        reasons.append(f"Crisis Diastolic BP ({diastolic} mmHg)")
    if temperature is not None and (temperature >= 104.0 or temperature < 95.0):
        reasons.append(f"Critical Temperature / Hypothermia (Temp: {temperature}°F)")

    if reasons:
        return {
            "tier": "Code Red",
            "priority": 1,
            "badge_color": "#dc3545",
            "action_urgency": "Immediate Resuscitation (< 5 mins)",
            "reasons": reasons
        }

    # Check Code Yellow criteria
    if spo2 is not None and spo2 < 95:
        reasons.append(f"Sub-optimal Oxygen (SpO2: {spo2}%)")
    if pulse is not None and (pulse > 105 or pulse < 55):
        reasons.append(f"Abnormal Heart Rate (Pulse: {pulse} bpm)")
    if systolic is not None and (systolic >= 140 or systolic <= 90):
        reasons.append(f"Elevated / Low BP ({systolic}/{diastolic or '-'} mmHg)")
    elif diastolic is not None and (diastolic >= 90 or diastolic <= 60):
        reasons.append(f"Abnormal Diastolic BP ({diastolic} mmHg)")
    if temperature is not None and (temperature >= 101.0 or temperature < 97.0):
        reasons.append(f"Significant Pyrexia / Low Temp (Temp: {temperature}°F)")

    if reasons:
        return {
            "tier": "Code Yellow",
            "priority": 2,
            "badge_color": "#ffc107",
            "action_urgency": "Urgent Care (< 30 mins)",
            "reasons": reasons
        }

    # Default to Code Green
    return {
        "tier": "Code Green",
        "priority": 3,
        "badge_color": "#28a745",
        "action_urgency": "Standard Outpatient Care (< 120 mins)",
        "reasons": ["Vital signs within acceptable physiological boundaries"]
    }


def get_emergency_queue():
    """
    Retrieves latest recorded vitals for patients who have vitals recorded in the system,
    evaluates clinical triage tier for each, and returns queue sorted by:
    1. Priority level (Code Red first, then Yellow, then Green)
    2. Waiting time (earliest recorded first)
    """
    conn = get_connection()
    try:
        # Get each patient's latest vital log
        rows = conn.execute("""
            SELECT v.*, p.full_name as patient_name, p.phone as patient_phone,
                   p.gender as patient_gender, p.dob as patient_dob, p.blood_group,
                   p.allergies
            FROM vitals_log v
            JOIN patients p ON v.patient_id = p.patient_id
            WHERE v.vital_id IN (
                SELECT MAX(vital_id) FROM vitals_log GROUP BY patient_id
            )
            ORDER BY v.vital_id DESC
        """).fetchall()

        queue = []
        for r in rows:
            r_dict = dict(r)
            eval_res = evaluate_triage_tier(
                systolic=r_dict.get("systolic"),
                diastolic=r_dict.get("diastolic"),
                pulse=r_dict.get("pulse"),
                temperature=r_dict.get("temperature"),
                spo2=r_dict.get("spo2")
            )
            queue_item = {
                "vital_id": r_dict["vital_id"],
                "patient_id": r_dict["patient_id"],
                "patient_name": r_dict["patient_name"],
                "patient_phone": r_dict["patient_phone"],
                "gender": r_dict["patient_gender"],
                "dob": r_dict["patient_dob"],
                "blood_group": r_dict["blood_group"],
                "allergies": r_dict["allergies"],
                "vitals": {
                    "systolic": r_dict.get("systolic"),
                    "diastolic": r_dict.get("diastolic"),
                    "pulse": r_dict.get("pulse"),
                    "temperature": r_dict.get("temperature"),
                    "spo2": r_dict.get("spo2")
                },
                "recorded_at": r_dict["recorded_at"],
                "tier": eval_res["tier"],
                "priority": eval_res["priority"],
                "badge_color": eval_res["badge_color"],
                "action_urgency": eval_res["action_urgency"],
                "reasons": eval_res["reasons"]
            }
            queue.append(queue_item)

        # Sort by priority (1 -> 2 -> 3) and then recorded_at ASC
        queue.sort(key=lambda x: (x["priority"], x["recorded_at"]))
        return queue
    finally:
        conn.close()
