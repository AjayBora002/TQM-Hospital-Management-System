"""patients_view.py -- Patients tab: CRUD UI using masking, dropdowns, auto-complete, confirm, audit."""
import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import GENDERS, BLOOD_GROUPS
from models import patient as patient_model
from models import room as room_model
from widgets.phone_mask_entry import PhoneMaskEntry
from widgets.autocomplete_entry import AutocompleteEntry
from widgets.confirm_dialog import confirm_delete, confirm_update
from utils.validators import is_valid_date, not_empty


class PatientsTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.selected_id = None
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="Patient Details")
        form.pack(fill="x", padx=10, pady=8)

        ttk.Label(form, text="Full Name*").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var, width=28).grid(row=0, column=1, padx=5)

        ttk.Label(form, text="Gender*").grid(row=0, column=2, sticky="w", padx=5)
        self.gender_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.gender_var, values=GENDERS,
                     state="readonly", width=12).grid(row=0, column=3, padx=5)

        ttk.Label(form, text="DOB (YYYY-MM-DD)*").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.dob_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.dob_var, width=28).grid(row=1, column=1, padx=5)

        ttk.Label(form, text="Blood Group*").grid(row=1, column=2, sticky="w", padx=5)
        self.blood_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.blood_var, values=BLOOD_GROUPS,
                     state="readonly", width=12).grid(row=1, column=3, padx=5)

        ttk.Label(form, text="Phone*").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.phone_entry = PhoneMaskEntry(form, width=28)
        self.phone_entry.grid(row=2, column=1, padx=5)

        ttk.Label(form, text="Room").grid(row=2, column=2, sticky="w", padx=5)
        self.room_var = tk.StringVar()
        self.room_combo = ttk.Combobox(form, textvariable=self.room_var, state="readonly", width=18)
        self.room_combo.grid(row=2, column=3, padx=5)
        self._load_room_choices()

        ttk.Label(form, text="Address").grid(row=3, column=0, sticky="w", padx=5, pady=4)
        self.address_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.address_var, width=28).grid(row=3, column=1, padx=5)

        btns = ttk.Frame(form)
        btns.grid(row=4, column=0, columnspan=4, pady=8)
        ttk.Button(btns, text="Add", command=self.add_patient).pack(side="left", padx=4)
        ttk.Button(btns, text="Update Selected", command=self.update_patient).pack(side="left", padx=4)
        ttk.Button(btns, text="Delete Selected", command=self.delete_patient).pack(side="left", padx=4)
        ttk.Button(btns, text="Clear Form", command=self.clear_form).pack(side="left", padx=4)
        ttk.Button(btns, text="Refresh Rooms", command=self._load_room_choices).pack(side="left", padx=4)

    def _build_table(self):
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=10)
        ttk.Label(search_frame, text="Search (auto-complete by name): ").pack(side="left")
        self.search_entry = AutocompleteEntry(
            search_frame, fetch_candidates=lambda p: patient_model.name_candidates(p), width=30
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.var.trace_add("write", lambda *_: self.refresh(self.search_entry.var.get()))

        cols = ("id", "name", "gender", "dob", "blood", "phone", "room", "address")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=13)
        headers = ["ID", "Name", "Gender", "DOB", "Blood Grp", "Phone", "Room", "Address"]
        widths = [40, 150, 70, 90, 70, 130, 80, 170]
        for c, h, w in zip(cols, headers, widths):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w)
        self.tree.pack(fill="both", expand=True, padx=10, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _load_room_choices(self):
        self._room_map = room_model.choices_map()
        self.room_combo["values"] = [""] + list(self._room_map.keys())

    def refresh(self, name_filter=""):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in patient_model.list_all(name_filter):
            room_label = next((k for k, v in getattr(self, "_room_map", {}).items()
                                if v == r["room_id"]), "")
            self.tree.insert("", "end", values=(r["patient_id"], r["full_name"], r["gender"],
                                                  r["dob"], r["blood_group"], r["phone"],
                                                  room_label, r["address"]))

    def _on_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        self.selected_id = vals[0]
        self.name_var.set(vals[1])
        self.gender_var.set(vals[2])
        self.dob_var.set(vals[3])
        self.blood_var.set(vals[4])
        self.phone_entry.set(vals[5])
        self.room_var.set(vals[6])
        self.address_var.set(vals[7])

    def _validate(self):
        if not not_empty(self.name_var.get()):
            messagebox.showerror("Validation Error", "Full Name is required.")
            return False
        if self.gender_var.get() not in GENDERS:
            messagebox.showerror("Validation Error", "Please select a Gender from the dropdown.")
            return False
        if not is_valid_date(self.dob_var.get()):
            messagebox.showerror("Validation Error", "DOB must be in YYYY-MM-DD format.")
            return False
        if self.blood_var.get() not in BLOOD_GROUPS:
            messagebox.showerror("Validation Error", "Please select a Blood Group from the dropdown.")
            return False
        if len(self.phone_entry.get_digits()) != 10:
            messagebox.showerror("Validation Error", "Phone number must contain exactly 10 digits.")
            return False
        return True

    def _room_id(self):
        return self._room_map.get(self.room_var.get()) if self.room_var.get() else None

    def clear_form(self):
        self.selected_id = None
        self.name_var.set("")
        self.gender_var.set("")
        self.dob_var.set("")
        self.blood_var.set("")
        self.phone_entry.set("")
        self.room_var.set("")
        self.address_var.set("")

    def add_patient(self):
        if not self._validate():
            return
        patient_model.add(self.name_var.get().strip(), self.gender_var.get(), self.dob_var.get().strip(),
                           self.blood_var.get(), self.phone_entry.get(), self.address_var.get().strip(),
                           self._room_id())
        messagebox.showinfo("Success", "Patient added.")
        self.clear_form()
        self.refresh()

    def update_patient(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a patient row first.")
            return
        if not self._validate():
            return
        if not confirm_update("patient", self.selected_id):
            return
        patient_model.update(self.selected_id, self.name_var.get().strip(), self.gender_var.get(),
                              self.dob_var.get().strip(), self.blood_var.get(), self.phone_entry.get(),
                              self.address_var.get().strip(), self._room_id())
        messagebox.showinfo("Success", "Patient updated.")
        self.clear_form()
        self.refresh()

    def delete_patient(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a patient row first.")
            return
        if not confirm_delete("patient", self.selected_id):
            return
        patient_model.delete(self.selected_id)
        messagebox.showinfo("Deleted", "Patient record deleted.")
        self.clear_form()
        self.refresh()
