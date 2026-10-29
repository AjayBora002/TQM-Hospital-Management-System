"""
config.py -- Single source of truth for app-wide constants and dropdown value lists.
Centralizing these here (instead of hardcoding in each view) is itself a Q07
data-accuracy control: every screen pulls from the exact same fixed lists.
"""
import os

APP_TITLE = "Hospital Management System | Q07: Improve Data Accuracy"
WINDOW_SIZE = "1150x680"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "src", "database", "hms.db")

# ---- Institutional Identity & ABDM Alignment -----------------------------
UHID_PREFIX = "UHID-2026-"

# ---- Fixed dropdown lists (Q07 Feature: Dropdown Lists) -------------------
GENDERS = ["Male", "Female", "Other"]
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
DEPARTMENTS = [
    "Cardiology", "Orthopedics", "Pediatrics", "General Medicine",
    "Neurology", "ENT", "Dermatology", "Gynecology",
    "Emergency & Trauma", "Intensive Care Unit (ICU)", "Operation Theatre",
    "Laboratory", "Radiology", "Pharmacy"
]
DOCTOR_SPECIALIZATIONS = [
    "Cardiologist", "Interventional Cardiologist", "Orthopedic Surgeon",
    "Joint Replacement Specialist", "Pediatrician", "Neonatologist",
    "General Physician", "Consultant Physician", "Neurologist", "Neurosurgeon",
    "ENT Specialist", "Head & Neck Surgeon", "Dermatologist",
    "Gynecologist", "Emergency Medicine Specialist",
    "Intensivist / Critical Care", "General Surgeon", "Pathologist", "Radiologist"
]
# Aligned with NABH & Base Project Guideline: Requested -> Confirmed -> Checked-in -> Waiting -> In consultation -> Completed / Cancelled / No-show
APPT_STATUS = ["Scheduled", "Confirmed", "Checked-in", "Waiting", "In consultation", "Completed", "Cancelled", "No-show"]
ROOM_TYPES = ["General Ward", "Semi-Private", "Private", "ICU", "Operation Theatre", "Emergency Observation"]
# Aligned with NABH & Base Project Guideline: Available -> Reserved -> Occupied -> Cleaning -> Maintenance / Blocked
ROOM_STATUS = ["Available", "Occupied", "Under Maintenance", "Cleaning / Sanitizing", "Reserved", "Blocked"]
LAB_ORDER_STATUS = ["Ordered", "Billing Pending", "Paid", "Sample Pending", "Collected", "Processing", "Verified", "Released", "Completed", "Cancelled"]
STAFF_ROLES = [
    "Nurse", "Head Nurse", "Ward Manager", "Receptionist", "Pharmacist",
    "Lab Technician", "Radiology Technician", "Cashier", "Ward Boy", "Administrator"
]
SHIFTS = ["Morning", "Evening", "Night"]
PAYMENT_METHODS = ["Cash", "Card", "UPI", "Insurance"]
PAYMENT_STATUS = ["Paid", "Pending", "Partially Paid"]
MEDICINE_CATEGORIES = ["Tablet", "Syrup", "Injection", "Ointment", "Surgical Item"]
DEFECT_CATEGORIES = ["Data Entry", "UI", "Validation", "Performance", "Other"]
DEFECT_SEVERITY = ["Low", "Medium", "High", "Critical"]
DEFECT_STATUS = ["Open", "Fixed"]

# ---- Clinical Orders & Doctor-Nurse Communication -------------------------
ORDER_TYPES = [
    "Medication", "Lab Test", "Nursing Care", "Vital Sign Monitoring",
    "Diet / Nutrition", "Physiotherapy", "Wound Care", "Discharge Clearance"
]
ORDER_URGENCIES = ["Routine", "Urgent", "STAT (Immediate)"]
ORDER_STATUSES = ["Ordered", "Acknowledged", "In Progress", "Completed", "Discontinued"]
TOKEN_STATUSES = ["Waiting", "Called", "In Consultation", "Completed", "Skipped"]
MESSAGE_URGENCIES = ["Normal", "Urgent", "Code Red"]

# ---- Clinical Poka-Yoke & Patient Safety Controls --------------------------
ALLERGIES = [
    "None",
    "Penicillin",
    "Sulfa Drugs",
    "Aspirin / NSAIDs",
    "Paracetamol",
    "Cephalosporins",
    "Latex",
    "Other"
]

DRUG_CONTRAINDICATION_MAP = {
    "Penicillin": ["amoxicillin", "ampicillin", "penicillin", "augmentin", "moxikind"],
    "Sulfa Drugs": ["bactrim", "sulfamethoxazole", "septra", "sulfa", "cotrimoxazole"],
    "Aspirin / NSAIDs": ["aspirin", "ibuprofen", "diclofenac", "naproxen", "combiflam", "brufen"],
    "Paracetamol": ["paracetamol", "crocin", "calpol", "acetaminophen", "dolo", "pacimol"],
    "Cephalosporins": ["cefixime", "ceftriaxone", "cephalexin", "cefuroxime", "taxim"]
}

STANDARD_APPOINTMENT_SLOTS = [
    "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "12:00", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00"
]

VITALS_RANGES = {
    "systolic": {"min": 60, "max": 250, "normal_min": 90, "normal_max": 130},
    "diastolic": {"min": 40, "max": 140, "normal_min": 60, "normal_max": 85},
    "pulse": {"min": 40, "max": 200, "normal_min": 60, "normal_max": 100},
    "temperature": {"min": 93.0, "max": 108.0, "normal_min": 97.0, "normal_max": 99.5},
    "spo2": {"min": 50, "max": 100, "normal_min": 95, "normal_max": 100}
}

# ---- Authentication & Role Management --------------------------------------
USER_ROLES = [
    "Admin",
    "Hospital Manager",
    "Doctor",
    "Nurse",
    "Ward Manager",
    "Receptionist",
    "Lab Technician",
    "Pharmacist",
    "Cashier",
    "Patient",
    "Quality Manager",
    "Radiologist",
    "OT Manager",
    "Blood Bank Technician",
    "Housekeeping Supervisor",
    "Biomedical Engineer",
    "HR Manager",
    "Store/Inventory Manager",
    "Insurance/TPA Desk",
    "Ambulance Dispatcher",
    "Dietitian"
]

# ---- Inpatient Admission & Stays -------------------------------------------
ADMISSION_STATUS = ["Admitted", "Discharged"]

# ---- Prescriptions & Pharmacy Clinical Workflow ----------------------------
DOSAGE_FREQUENCIES = [
    "Once daily (OD)",
    "Twice daily (BD)",
    "Thrice daily (TDS)",
    "Four times daily (QID)",
    "As needed (SOS)"
]
PRESCRIPTION_STATUS = ["Active", "Dispensed", "Completed", "Discontinued"]

# ---- Automated Database Backup ---------------------------------------------
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

# ---- Diagnostic Laboratory & Radiology Testing ----------------------------
LAB_CATEGORIES = ["Hematology", "Biochemistry", "Pathology", "Radiology", "Microbiology"]
LAB_TEST_TEMPLATES = {
    "Hemoglobin": {"category": "Hematology", "unit": "g/dL", "ref_min": 12.0, "ref_max": 17.5},
    "Fasting Blood Sugar": {"category": "Biochemistry", "unit": "mg/dL", "ref_min": 70.0, "ref_max": 99.0},
    "Serum Creatinine": {"category": "Biochemistry", "unit": "mg/dL", "ref_min": 0.6, "ref_max": 1.2},
    "Platelet Count": {"category": "Hematology", "unit": "10^3/uL", "ref_min": 150.0, "ref_max": 450.0},
    "Total Cholesterol": {"category": "Biochemistry", "unit": "mg/dL", "ref_min": 125.0, "ref_max": 200.0},
    "Serum Bilirubin": {"category": "Biochemistry", "unit": "mg/dL", "ref_min": 0.2, "ref_max": 1.2},
    "WBC Count": {"category": "Hematology", "unit": "/mcL", "ref_min": 4000.0, "ref_max": 11000.0},
}
