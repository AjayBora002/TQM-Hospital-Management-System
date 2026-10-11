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

# ---- Fixed dropdown lists (Q07 Feature: Dropdown Lists) -------------------
GENDERS = ["Male", "Female", "Other"]
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
DEPARTMENTS = ["Cardiology", "Orthopedics", "Pediatrics", "General Medicine",
               "Neurology", "ENT", "Dermatology", "Gynecology"]
APPT_STATUS = ["Scheduled", "Completed", "Cancelled"]
ROOM_TYPES = ["General Ward", "Semi-Private", "Private", "ICU", "Operation Theatre"]
ROOM_STATUS = ["Available", "Occupied", "Under Maintenance", "Cleaning / Sanitizing"]
STAFF_ROLES = ["Nurse", "Receptionist", "Pharmacist", "Lab Technician",
               "Ward Boy", "Administrator"]
SHIFTS = ["Morning", "Evening", "Night"]
PAYMENT_METHODS = ["Cash", "Card", "UPI", "Insurance"]
PAYMENT_STATUS = ["Paid", "Pending", "Partially Paid"]
MEDICINE_CATEGORIES = ["Tablet", "Syrup", "Injection", "Ointment", "Surgical Item"]
DEFECT_CATEGORIES = ["Data Entry", "UI", "Validation", "Performance", "Other"]
DEFECT_SEVERITY = ["Low", "Medium", "High", "Critical"]
DEFECT_STATUS = ["Open", "Fixed"]

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

