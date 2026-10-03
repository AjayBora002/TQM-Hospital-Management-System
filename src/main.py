"""
main.py -- Hospital Management System (HMS) | Entry point
BBAT104 Course Project | Session 2026-27
Student: Ajay Bora | Branch: CSE | Section: B
Baseline System: Hospital Management System
Quality Goal: Q07 - Improve Data Accuracy

Modules: Dashboard, Patients, Doctors, Appointments, Rooms/Wards, Staff,
         Pharmacy/Inventory, Billing, Audit Log, Defect Checksheet.

Q07 features (implemented once in src/widgets/, reused across every module):
  1. Input Masking      -> widgets/phone_mask_entry.py
  2. Dropdown Lists      -> config.py fixed lists + ttk.Combobox(state="readonly")
  3. Auto-Complete       -> widgets/autocomplete_entry.py
  4. Confirmation Modals -> widgets/confirm_dialog.py
  5. Audit Logs          -> database/db_manager.log_audit(), views/audit_view.py

Run:  python src/main.py   (first run auto-creates src/database/hms.db)
"""
import sys
import os
import tkinter as tk
from tkinter import ttk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import APP_TITLE, WINDOW_SIZE
from database.db_manager import init_db

from views.dashboard_view import DashboardTab
from views.patients_view import PatientsTab
from views.doctors_view import DoctorsTab
from views.appointments_view import AppointmentsTab
from views.rooms_view import RoomsTab
from views.staff_view import StaffTab
from views.medicines_view import MedicinesTab
from views.billing_view import BillingTab
from views.audit_view import AuditLogTab
from views.defects_view import DefectLogTab


class HMSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        init_db()

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.dashboard_tab = DashboardTab(notebook)
        self.patients_tab = PatientsTab(notebook)
        self.doctors_tab = DoctorsTab(notebook)
        self.appointments_tab = AppointmentsTab(notebook)
        self.rooms_tab = RoomsTab(notebook)
        self.staff_tab = StaffTab(notebook)
        self.medicines_tab = MedicinesTab(notebook)
        self.billing_tab = BillingTab(notebook)
        self.audit_tab = AuditLogTab(notebook)
        self.defect_tab = DefectLogTab(notebook)

        notebook.add(self.dashboard_tab, text="Dashboard")
        notebook.add(self.patients_tab, text="Patients")
        notebook.add(self.doctors_tab, text="Doctors")
        notebook.add(self.appointments_tab, text="Appointments")
        notebook.add(self.rooms_tab, text="Rooms / Wards")
        notebook.add(self.staff_tab, text="Staff")
        notebook.add(self.medicines_tab, text="Pharmacy")
        notebook.add(self.billing_tab, text="Billing")
        notebook.add(self.audit_tab, text="Audit Log")
        notebook.add(self.defect_tab, text="Defect Checksheet")

        # Refresh dependent tabs whenever the user switches to them
        def on_tab_change(_event):
            current = notebook.select()
            widget = notebook.nametowidget(current)
            if widget is self.audit_tab:
                self.audit_tab.refresh()
            elif widget is self.dashboard_tab:
                self.dashboard_tab.refresh()
            elif widget is self.appointments_tab:
                self.appointments_tab._load_doctor_choices()
            elif widget is self.patients_tab:
                self.patients_tab._load_room_choices()

        notebook.bind("<<NotebookTabChanged>>", on_tab_change)


if __name__ == "__main__":
    app = HMSApp()
    app.mainloop()
