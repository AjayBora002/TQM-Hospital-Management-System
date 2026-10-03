"""doctors_view.py -- Doctors tab: CRUD UI with department dropdown, masking, confirm, audit."""
import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DEPARTMENTS
from models import doctor as doctor_model
from widgets.phone_mask_entry import PhoneMaskEntry
from widgets.confirm_dialog import confirm_delete, confirm_update
from utils.validators import not_empty


class DoctorsTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.selected_id = None
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="Doctor Details")
        form.pack(fill="x", padx=10, pady=8)

        ttk.Label(form, text="Full Name*").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var, width=28).grid(row=0, column=1, padx=5)

        ttk.Label(form, text="Department*").grid(row=0, column=2, sticky="w", padx=5)
        self.dept_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.dept_var, values=DEPARTMENTS,
                     state="readonly", width=18).grid(row=0, column=3, padx=5)

        ttk.Label(form, text="Phone*").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.phone_entry = PhoneMaskEntry(form, width=28)
        self.phone_entry.grid(row=1, column=1, padx=5)

        btns = ttk.Frame(form)
        btns.grid(row=2, column=0, columnspan=4, pady=8)
        ttk.Button(btns, text="Add", command=self.add_doctor).pack(side="left", padx=4)
        ttk.Button(btns, text="Update Selected", command=self.update_doctor).pack(side="left", padx=4)
        ttk.Button(btns, text="Delete Selected", command=self.delete_doctor).pack(side="left", padx=4)
        ttk.Button(btns, text="Clear Form", command=self.clear_form).pack(side="left", padx=4)

    def _build_table(self):
        cols = ("id", "name", "dept", "phone")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=16)
        for c, h, w in zip(cols, ["ID", "Name", "Department", "Phone"], [40, 200, 160, 160]):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w)
        self.tree.pack(fill="both", expand=True, padx=10, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in doctor_model.list_all():
            self.tree.insert("", "end", values=(r["doctor_id"], r["full_name"], r["department"], r["phone"]))

    def _on_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        self.selected_id = vals[0]
        self.name_var.set(vals[1])
        self.dept_var.set(vals[2])
        self.phone_entry.set(vals[3])

    def _validate(self):
        if not not_empty(self.name_var.get()):
            messagebox.showerror("Validation Error", "Full Name is required.")
            return False
        if self.dept_var.get() not in DEPARTMENTS:
            messagebox.showerror("Validation Error", "Please select a Department from the dropdown.")
            return False
        if len(self.phone_entry.get_digits()) != 10:
            messagebox.showerror("Validation Error", "Phone number must contain exactly 10 digits.")
            return False
        return True

    def clear_form(self):
        self.selected_id = None
        self.name_var.set("")
        self.dept_var.set("")
        self.phone_entry.set("")

    def add_doctor(self):
        if not self._validate():
            return
        doctor_model.add(self.name_var.get().strip(), self.dept_var.get(), self.phone_entry.get())
        messagebox.showinfo("Success", "Doctor added.")
        self.clear_form()
        self.refresh()

    def update_doctor(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a doctor row first.")
            return
        if not self._validate():
            return
        if not confirm_update("doctor", self.selected_id):
            return
        doctor_model.update(self.selected_id, self.name_var.get().strip(), self.dept_var.get(),
                             self.phone_entry.get())
        messagebox.showinfo("Success", "Doctor updated.")
        self.clear_form()
        self.refresh()

    def delete_doctor(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a doctor row first.")
            return
        if not confirm_delete("doctor", self.selected_id):
            return
        doctor_model.delete(self.selected_id)
        messagebox.showinfo("Deleted", "Doctor record deleted.")
        self.clear_form()
        self.refresh()
