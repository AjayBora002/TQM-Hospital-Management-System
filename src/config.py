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
