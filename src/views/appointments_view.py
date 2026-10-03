"""appointments_view.py -- Appointments tab: links Patients+Doctors, dropdown status, confirm, audit."""
import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APPT_STATUS
from models import appointment as appt_model
from models import patient as patient_model
from models import doctor as doctor_model
from widgets.autocomplete_entry import AutocompleteEntry
from widgets.confirm_dialog import confirm_delete, confirm_update
from utils.validators import is_valid_date, is_valid_time


class AppointmentsTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.selected_id = None
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="Appointment Details")
        form.pack(fill="x", padx=10, pady=8)

        ttk.Label(form, text="Patient (name)*").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.patient_ac = AutocompleteEntry(form, fetch_candidates=patient_model.name_candidates, width=26)
        self.patient_ac.grid(row=0, column=1, padx=5)

        ttk.Label(form, text="Doctor*").grid(row=0, column=2, sticky="w", padx=5)
        self.doctor_var = tk.StringVar()
        self.doctor_combo = ttk.Combobox(form, textvariable=self.doctor_var, state="readonly", width=24)
        self.doctor_combo.grid(row=0, column=3, padx=5)
        self._load_doctor_choices()

        ttk.Label(form, text="Date (YYYY-MM-DD)*").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.date_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.date_var, width=28).grid(row=1, column=1, padx=5)

        ttk.Label(form, text="Time (HH:MM)*").grid(row=1, column=2, sticky="w", padx=5)
        self.time_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.time_var, width=24).grid(row=1, column=3, padx=5)

        ttk.Label(form, text="Status*").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.status_var = tk.StringVar(value="Scheduled")
        ttk.Combobox(form, textvariable=self.status_var, values=APPT_STATUS,
                     state="readonly", width=26).grid(row=2, column=1, padx=5)

        btns = ttk.Frame(form)
        btns.grid(row=3, column=0, columnspan=4, pady=8)
        ttk.Button(btns, text="Book", command=self.add_appt).pack(side="left", padx=4)
        ttk.Button(btns, text="Update Selected", command=self.update_appt).pack(side="left", padx=4)
        ttk.Button(btns, text="Cancel/Delete Selected", command=self.delete_appt).pack(side="left", padx=4)
        ttk.Button(btns, text="Clear Form", command=self.clear_form).pack(side="left", padx=4)
        ttk.Button(btns, text="Refresh Doctor List", command=self._load_doctor_choices).pack(side="left", padx=4)

    def _build_table(self):
        cols = ("id", "patient", "doctor", "date", "time", "status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=14)
        for c, h, w in zip(cols, ["ID", "Patient", "Doctor", "Date", "Time", "Status"],
                            [40, 160, 160, 100, 80, 100]):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w)
        self.tree.pack(fill="both", expand=True, padx=10, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _load_doctor_choices(self):
        self._doctor_map = doctor_model.choices_map()
        self.doctor_combo["values"] = list(self._doctor_map.keys())

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in appt_model.list_all():
            self.tree.insert("", "end", values=(r["appointment_id"], r["patient"], r["doctor"],
                                                  r["appt_date"], r["appt_time"], r["status"]))

    def _on_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        self.selected_id = vals[0]
        self.patient_ac.var.set(vals[1])
        for label in self._doctor_map:
            if label.startswith(vals[2]):
                self.doctor_var.set(label)
                break
        self.date_var.set(vals[3])
        self.time_var.set(vals[4])
        self.status_var.set(vals[5])

    def _validate(self):
        if patient_model.get_id_by_name(self.patient_ac.var.get().strip()) is None:
            messagebox.showerror("Validation Error",
                                  "Select a valid patient from the auto-complete suggestions.")
            return False
        if self.doctor_var.get() not in self._doctor_map:
            messagebox.showerror("Validation Error", "Please select a Doctor from the dropdown.")
            return False
        if not is_valid_date(self.date_var.get()):
            messagebox.showerror("Validation Error", "Date must be in YYYY-MM-DD format.")
            return False
        if not is_valid_time(self.time_var.get()):
            messagebox.showerror("Validation Error", "Time must be in HH:MM (24-hour) format.")
            return False
        if self.status_var.get() not in APPT_STATUS:
            messagebox.showerror("Validation Error", "Please select a Status from the dropdown.")
            return False
        return True

    def clear_form(self):
        self.selected_id = None
        self.patient_ac.var.set("")
        self.doctor_var.set("")
        self.date_var.set("")
        self.time_var.set("")
        self.status_var.set("Scheduled")

    def add_appt(self):
        if not self._validate():
            return
        pid = patient_model.get_id_by_name(self.patient_ac.var.get().strip())
        appt_model.add(pid, self._doctor_map[self.doctor_var.get()],
                        self.date_var.get().strip(), self.time_var.get().strip(), self.status_var.get())
        messagebox.showinfo("Success", "Appointment booked.")
        self.clear_form()
        self.refresh()

    def update_appt(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select an appointment row first.")
            return
        if not self._validate():
            return
        if not confirm_update("appointment", self.selected_id):
            return
        pid = patient_model.get_id_by_name(self.patient_ac.var.get().strip())
        appt_model.update(self.selected_id, pid, self._doctor_map[self.doctor_var.get()],
                           self.date_var.get().strip(), self.time_var.get().strip(), self.status_var.get())
        messagebox.showinfo("Success", "Appointment updated.")
        self.clear_form()
        self.refresh()

    def delete_appt(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select an appointment row first.")
            return
        if not confirm_delete("appointment", self.selected_id):
            return
        appt_model.delete(self.selected_id)
        messagebox.showinfo("Deleted", "Appointment deleted.")
        self.clear_form()
        self.refresh()
