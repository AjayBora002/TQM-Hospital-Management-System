"""staff_view.py -- Staff tab: role/shift dropdowns, phone masking, confirm, audit."""
import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import STAFF_ROLES, SHIFTS
from models import staff as staff_model
from widgets.phone_mask_entry import PhoneMaskEntry
from widgets.confirm_dialog import confirm_delete, confirm_update
from utils.validators import not_empty


class StaffTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.selected_id = None
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="Staff Details")
        form.pack(fill="x", padx=10, pady=8)

        ttk.Label(form, text="Full Name*").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var, width=28).grid(row=0, column=1, padx=5)

        ttk.Label(form, text="Role*").grid(row=0, column=2, sticky="w", padx=5)
        self.role_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.role_var, values=STAFF_ROLES,
                     state="readonly", width=18).grid(row=0, column=3, padx=5)

        ttk.Label(form, text="Shift*").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.shift_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.shift_var, values=SHIFTS,
                     state="readonly", width=26).grid(row=1, column=1, padx=5)

        ttk.Label(form, text="Phone*").grid(row=1, column=2, sticky="w", padx=5)
        self.phone_entry = PhoneMaskEntry(form, width=20)
        self.phone_entry.grid(row=1, column=3, padx=5)

        btns = ttk.Frame(form)
        btns.grid(row=2, column=0, columnspan=4, pady=8)
        ttk.Button(btns, text="Add", command=self.add_staff).pack(side="left", padx=4)
        ttk.Button(btns, text="Update Selected", command=self.update_staff).pack(side="left", padx=4)
        ttk.Button(btns, text="Delete Selected", command=self.delete_staff).pack(side="left", padx=4)
        ttk.Button(btns, text="Clear Form", command=self.clear_form).pack(side="left", padx=4)

    def _build_table(self):
        cols = ("id", "name", "role", "shift", "phone")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=16)
        for c, h, w in zip(cols, ["ID", "Name", "Role", "Shift", "Phone"], [40, 180, 140, 100, 150]):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w)
        self.tree.pack(fill="both", expand=True, padx=10, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in staff_model.list_all():
            self.tree.insert("", "end", values=(r["staff_id"], r["full_name"], r["role"],
                                                  r["shift"], r["phone"]))

    def _on_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        self.selected_id = vals[0]
        self.name_var.set(vals[1])
        self.role_var.set(vals[2])
        self.shift_var.set(vals[3])
        self.phone_entry.set(vals[4])

    def _validate(self):
        if not not_empty(self.name_var.get()):
            messagebox.showerror("Validation Error", "Full Name is required.")
            return False
        if self.role_var.get() not in STAFF_ROLES:
            messagebox.showerror("Validation Error", "Please select a Role from the dropdown.")
            return False
        if self.shift_var.get() not in SHIFTS:
            messagebox.showerror("Validation Error", "Please select a Shift from the dropdown.")
            return False
        if len(self.phone_entry.get_digits()) != 10:
            messagebox.showerror("Validation Error", "Phone number must contain exactly 10 digits.")
            return False
        return True

    def clear_form(self):
        self.selected_id = None
        self.name_var.set("")
        self.role_var.set("")
        self.shift_var.set("")
        self.phone_entry.set("")

    def add_staff(self):
        if not self._validate():
            return
        staff_model.add(self.name_var.get().strip(), self.role_var.get(), self.shift_var.get(),
                         self.phone_entry.get())
        messagebox.showinfo("Success", "Staff added.")
        self.clear_form()
        self.refresh()

    def update_staff(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a staff row first.")
            return
        if not self._validate():
            return
        if not confirm_update("staff", self.selected_id):
            return
        staff_model.update(self.selected_id, self.name_var.get().strip(), self.role_var.get(),
                            self.shift_var.get(), self.phone_entry.get())
        messagebox.showinfo("Success", "Staff updated.")
        self.clear_form()
        self.refresh()

    def delete_staff(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a staff row first.")
            return
        if not confirm_delete("staff", self.selected_id):
            return
        staff_model.delete(self.selected_id)
        messagebox.showinfo("Deleted", "Staff record deleted.")
        self.clear_form()
        self.refresh()
