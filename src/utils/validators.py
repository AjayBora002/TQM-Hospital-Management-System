"""
validators.py -- Shared validation rules (Q07 Data Accuracy support).
Centralizing validation prevents each view from re-implementing (and
potentially mis-implementing) the same accuracy rules.
"""
import re
from datetime import datetime
from .exception_handler import ValidationError


# Low-level predicate helpers
def is_valid_date(value: str) -> bool:
    if not value or not re.match(r"^\d{4}-\d{2}-\d{2}$", value.strip()):
        return False
    try:
        datetime.strptime(value.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_time(value: str) -> bool:
    if not value:
        return False
    return bool(re.match(r"^([01]\d|2[0-3]):[0-5]\d$", value.strip()))


def is_valid_phone_digits(digits: str) -> bool:
    clean = re.sub(r"\D", "", digits or "")
    if len(clean) == 12 and clean.startswith("91"):
        return True
    return len(clean) == 10



def not_empty(value: str) -> bool:
    return bool(value and str(value).strip())


def in_fixed_set(value: str, allowed: set) -> bool:
    return value in allowed


# Strict Q07 Validators (Raise ValidationError on failure)
def validate_patient_payload(data: dict):
    """Validates patient creation or update payload against Q07 rules."""
    name = (data.get("full_name") or "").strip()
    if not name or len(name) < 2:
        raise ValidationError("Patient full name must be at least 2 characters.", field="full_name")
    
    gender = data.get("gender")
    if gender not in {"Male", "Female", "Other"}:
        raise ValidationError("Gender must be 'Male', 'Female', or 'Other'.", field="gender")
    
    dob = data.get("dob")
    if not is_valid_date(dob):
        raise ValidationError("Date of birth must be a valid YYYY-MM-DD date.", field="dob")
        
    blood = data.get("blood_group")
    valid_blood = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
    if blood not in valid_blood:
        raise ValidationError(f"Blood group must be one of {', '.join(valid_blood)}.", field="blood_group")
        
    phone = data.get("phone", "")
    if not is_valid_phone_digits(phone):
        raise ValidationError("Phone number must contain exactly 10 digits.", field="phone")
    return True


def validate_appointment_payload(data: dict):
    """Validates appointment booking payload."""
    if not data.get("patient_id"):
        raise ValidationError("Patient selection is mandatory.", field="patient_id")
    if not data.get("doctor_id"):
        raise ValidationError("Doctor selection is mandatory.", field="doctor_id")
    if not is_valid_date(data.get("appt_date", "")):
        raise ValidationError("Appointment date must be a valid YYYY-MM-DD date.", field="appt_date")
    if not is_valid_time(data.get("appt_time", "")):
        raise ValidationError("Appointment time must be in HH:MM (24-hour) format.", field="appt_time")
    return True


def validate_billing_payload(data: dict):
    """Validates billing calculations, charges, and payment status against Q07 rules."""
    if not data.get("patient_id"):
        raise ValidationError("Billing must be associated with a valid patient ID.", field="patient_id")
    try:
        pid = int(data.get("patient_id"))
        if pid <= 0:
            raise ValidationError("Patient ID must be a positive integer.", field="patient_id")
    except (ValueError, TypeError):
        raise ValidationError("Patient ID must be an integer.", field="patient_id")

    for charge_field in ["room_charges", "consultation_charges", "medicine_charges"]:
        val = data.get(charge_field, 0)
        try:
            num = float(val)
            if num < 0:
                raise ValidationError(f"{charge_field.replace('_', ' ').capitalize()} cannot be negative.", field=charge_field)
        except (ValueError, TypeError):
            raise ValidationError(f"{charge_field.replace('_', ' ').capitalize()} must be a valid numeric amount.", field=charge_field)

    pm = data.get("payment_method")
    if pm:
        from config import PAYMENT_METHODS
        if pm not in PAYMENT_METHODS:
            raise ValidationError(f"Payment method must be one of {', '.join(PAYMENT_METHODS)}.", field="payment_method")

    ps = data.get("payment_status")
    if ps:
        from config import PAYMENT_STATUS
        allowed_statuses = set(PAYMENT_STATUS) | {"Unpaid", "Partial"}
        if ps not in allowed_statuses:
            raise ValidationError(f"Payment status must be one of {', '.join(sorted(allowed_statuses))}.", field="payment_status")
    return True



# Clinical Poka-Yoke: Triage Vitals & Boundary Validators
def validate_vital_signs(data: dict) -> dict:
    """Validates patient vital signs against physiological limits and computes triage severity."""
    from config import VITALS_RANGES

    parsed = {}
    is_warning = False
    is_critical = False
    alerts = []

    # Systolic
    if "systolic" in data and data["systolic"] not in (None, ""):
        try:
            sys_val = int(data["systolic"])
            cfg = VITALS_RANGES["systolic"]
            if sys_val < cfg["min"] or sys_val > cfg["max"]:
                raise ValidationError(f"Systolic BP ({sys_val}) is outside survivable physiological range [{cfg['min']}-{cfg['max']}].", field="systolic")
            if sys_val < cfg["normal_min"] or sys_val > cfg["normal_max"]:
                is_warning = True
                alerts.append(f"Abnormal Systolic BP: {sys_val} mmHg")
            if sys_val >= 180 or sys_val < 85:
                is_critical = True
            parsed["systolic"] = sys_val
        except (ValueError, TypeError):
            raise ValidationError("Systolic BP must be an integer.", field="systolic")

    # Diastolic
    if "diastolic" in data and data["diastolic"] not in (None, ""):
        try:
            dia_val = int(data["diastolic"])
            cfg = VITALS_RANGES["diastolic"]
            if dia_val < cfg["min"] or dia_val > cfg["max"]:
                raise ValidationError(f"Diastolic BP ({dia_val}) is outside survivable physiological range [{cfg['min']}-{cfg['max']}].", field="diastolic")
            if dia_val < cfg["normal_min"] or dia_val > cfg["normal_max"]:
                is_warning = True
                alerts.append(f"Abnormal Diastolic BP: {dia_val} mmHg")
            if dia_val >= 120 or dia_val < 50:
                is_critical = True
            parsed["diastolic"] = dia_val
        except (ValueError, TypeError):
            raise ValidationError("Diastolic BP must be an integer.", field="diastolic")

    # Pulse
    if "pulse" in data and data["pulse"] not in (None, ""):
        try:
            pulse_val = int(data["pulse"])
            cfg = VITALS_RANGES["pulse"]
            if pulse_val < cfg["min"] or pulse_val > cfg["max"]:
                raise ValidationError(f"Heart rate ({pulse_val}) is outside allowable range [{cfg['min']}-{cfg['max']}].", field="pulse")
            if pulse_val < cfg["normal_min"] or pulse_val > cfg["normal_max"]:
                is_warning = True
                alerts.append(f"Abnormal Heart Rate: {pulse_val} bpm")
            if pulse_val > 140 or pulse_val < 45:
                is_critical = True
            parsed["pulse"] = pulse_val
        except (ValueError, TypeError):
            raise ValidationError("Heart rate must be an integer.", field="pulse")

    # Temperature
    if "temperature" in data and data["temperature"] not in (None, ""):
        try:
            temp_val = float(data["temperature"])
            cfg = VITALS_RANGES["temperature"]
            if temp_val < cfg["min"] or temp_val > cfg["max"]:
                raise ValidationError(f"Temperature ({temp_val} F) is outside allowable range [{cfg['min']}-{cfg['max']}].", field="temperature")
            if temp_val < cfg["normal_min"] or temp_val > cfg["normal_max"]:
                is_warning = True
                alerts.append(f"Abnormal Temperature: {temp_val} F")
            if temp_val >= 104.0 or temp_val < 95.0:
                is_critical = True
            parsed["temperature"] = temp_val
        except (ValueError, TypeError):
            raise ValidationError("Temperature must be a numeric value.", field="temperature")

    # SpO2
    if "spo2" in data and data["spo2"] not in (None, ""):
        try:
            spo2_val = int(data["spo2"])
            cfg = VITALS_RANGES["spo2"]
            if spo2_val < cfg["min"] or spo2_val > cfg["max"]:
                raise ValidationError(f"SpO2 saturation ({spo2_val}%) is outside allowable range [{cfg['min']}-{cfg['max']}].", field="spo2")
            if spo2_val < cfg["normal_min"]:
                is_warning = True
                alerts.append(f"Low Oxygen Saturation (SpO2): {spo2_val}%")
            if spo2_val < 90:
                is_critical = True
            parsed["spo2"] = spo2_val
        except (ValueError, TypeError):
            raise ValidationError("SpO2 must be an integer percentage (0-100).", field="spo2")

    triage_status = "Critical" if is_critical else ("Warning" if is_warning else "Normal")
    parsed["triage_status"] = triage_status
    parsed["alerts"] = alerts
    return parsed


# Clinical Poka-Yoke: Drug Allergy & Adverse Reaction Checker
def check_drug_allergy_contraindication(patient_allergies: str, medicine_name: str, medicine_category: str = "") -> dict:
    """Evaluates whether prescribing a medicine triggers a documented patient allergy."""
    from config import DRUG_CONTRAINDICATION_MAP

    if not patient_allergies or patient_allergies.strip().lower() in ("none", ""):
        return {"contraindicated": False, "reason": "No documented patient allergies."}

    med_lower = (medicine_name or "").lower()
    cat_lower = (medicine_category or "").lower()
    allergies_list = [a.strip() for a in patient_allergies.split(",") if a.strip()]

    for allergy in allergies_list:
        keywords = DRUG_CONTRAINDICATION_MAP.get(allergy, [])
        for kw in keywords:
            if kw in med_lower or kw in cat_lower:
                return {
                    "contraindicated": True,
                    "allergy": allergy,
                    "matched_trigger": kw,
                    "medicine": medicine_name,
                    "severity": "CRITICAL",
                    "reason": f"POTENTIAL ADVERSE DRUG REACTION: Patient has recorded '{allergy}' allergy. '{medicine_name}' contains or belongs to '{kw}' class."
                }

    return {"contraindicated": False, "reason": "Medication does not trigger documented patient allergies."}

