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
    """Validates billing calculations and status."""
    if not data.get("patient_id"):
        raise ValidationError("Billing must be associated with a valid patient ID.", field="patient_id")
    for charge_field in ["room_charges", "consultation_charges", "medicine_charges"]:
        val = data.get(charge_field, 0)
        try:
            num = float(val)
            if num < 0:
                raise ValidationError(f"{charge_field} cannot be negative.", field=charge_field)
        except (ValueError, TypeError):
            raise ValidationError(f"{charge_field} must be a valid numeric amount.", field=charge_field)
    return True
