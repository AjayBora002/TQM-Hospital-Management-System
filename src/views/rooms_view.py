"""rooms_view.py -- Rooms/Wards tab: room inventory with type/status dropdowns, confirm, audit."""
import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ROOM_TYPES, ROOM_STATUS
from models import room as room_model
from widgets.confirm_dialog import confirm_delete, confirm_update
from utils.validators import not_empty


class RoomsTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.selected_id = None
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="Room / Ward Details")
        form.pack(fill="x", padx=10, pady=8)

        ttk.Label(form, text="Room Number*").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.number_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.number_var, width=20).grid(row=0, column=1, padx=5)

        ttk.Label(form, text="Room Type*").grid(row=0, column=2, sticky="w", padx=5)
        self.type_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.type_var, values=ROOM_TYPES,
                     state="readonly", width=20).grid(row=0, column=3, padx=5)

        ttk.Label(form, text="Status*").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.status_var = tk.StringVar(value="Available")
        ttk.Combobox(form, textvariable=self.status_var, values=ROOM_STATUS,
                     state="readonly", width=20).grid(row=1, column=1, padx=5)

        ttk.Label(form, text="Rate / Day (Rs)*").grid(row=1, column=2, sticky="w", padx=5)
        self.rate_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.rate_var, width=20).grid(row=1, column=3, padx=5)

        btns = ttk.Frame(form)
        btns.grid(row=2, column=0, columnspan=4, pady=8)
        ttk.Button(btns, text="Add", command=self.add_room).pack(side="left", padx=4)
        ttk.Button(btns, text="Update Selected", command=self.update_room).pack(side="left", padx=4)
        ttk.Button(btns, text="Delete Selected", command=self.delete_room).pack(side="left", padx=4)
        ttk.Button(btns, text="Clear Form", command=self.clear_form).pack(side="left", padx=4)

    def _build_table(self):
        cols = ("id", "number", "type", "status", "rate")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=16)
        for c, h, w in zip(cols, ["ID", "Room No.", "Type", "Status", "Rate/Day"],
                            [40, 100, 150, 130, 100]):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w)
        self.tree.pack(fill="both", expand=True, padx=10, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in room_model.list_all():
            self.tree.insert("", "end", values=(r["room_id"], r["room_number"], r["room_type"],
                                                  r["status"], r["rate_per_day"]))

    def _on_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        self.selected_id = vals[0]
        self.number_var.set(vals[1])
        self.type_var.set(vals[2])
        self.status_var.set(vals[3])
        self.rate_var.set(vals[4])

    def _validate(self):
        if not not_empty(self.number_var.get()):
            messagebox.showerror("Validation Error", "Room Number is required.")
            return False
        if self.type_var.get() not in ROOM_TYPES:
            messagebox.showerror("Validation Error", "Please select a Room Type from the dropdown.")
            return False
        if self.status_var.get() not in ROOM_STATUS:
            messagebox.showerror("Validation Error", "Please select a Status from the dropdown.")
            return False
        try:
            float(self.rate_var.get())
        except ValueError:
            messagebox.showerror("Validation Error", "Rate/Day must be a number.")
            return False
        return True

    def clear_form(self):
        self.selected_id = None
        self.number_var.set("")
        self.type_var.set("")
        self.status_var.set("Available")
        self.rate_var.set("")

    def add_room(self):
        if not self._validate():
            return
        room_model.add(self.number_var.get().strip(), self.type_var.get(),
                        self.status_var.get(), float(self.rate_var.get()))
        messagebox.showinfo("Success", "Room added.")
        self.clear_form()
        self.refresh()

    def update_room(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a room row first.")
            return
        if not self._validate():
            return
        if not confirm_update("room", self.selected_id):
            return
        room_model.update(self.selected_id, self.number_var.get().strip(), self.type_var.get(),
                           self.status_var.get(), float(self.rate_var.get()))
        messagebox.showinfo("Success", "Room updated.")
        self.clear_form()
        self.refresh()

    def delete_room(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a room row first.")
            return
        if not confirm_delete("room", self.selected_id):
            return
        room_model.delete(self.selected_id)
        messagebox.showinfo("Deleted", "Room deleted.")
        self.clear_form()
        self.refresh()
