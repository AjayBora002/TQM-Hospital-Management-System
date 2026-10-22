"""medicines_view.py -- Pharmacy/Inventory tab: category dropdown, stock tracking, confirm, audit."""
import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MEDICINE_CATEGORIES
from models import medicine as medicine_model
from widgets.confirm_dialog import confirm_delete, confirm_update
from utils.validators import not_empty


class MedicinesTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.selected_id = None
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="Medicine / Inventory Item")
        form.pack(fill="x", padx=10, pady=8)

        ttk.Label(form, text="Name*").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var, width=24).grid(row=0, column=1, padx=5)

        ttk.Label(form, text="Category*").grid(row=0, column=2, sticky="w", padx=5)
        self.cat_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.cat_var, values=MEDICINE_CATEGORIES,
                     state="readonly", width=18).grid(row=0, column=3, padx=5)

        ttk.Label(form, text="Stock Qty*").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.stock_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.stock_var, width=24).grid(row=1, column=1, padx=5)

        ttk.Label(form, text="Unit Price (Rs)*").grid(row=1, column=2, sticky="w", padx=5)
        self.price_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.price_var, width=18).grid(row=1, column=3, padx=5)

        ttk.Label(form, text="Reorder Level*").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.reorder_var = tk.StringVar(value="10")
        ttk.Entry(form, textvariable=self.reorder_var, width=24).grid(row=2, column=1, padx=5)

        ttk.Label(form, text="Batch No*").grid(row=2, column=2, sticky="w", padx=5)
        self.batch_var = tk.StringVar(value="BAT-2026-01")
        ttk.Entry(form, textvariable=self.batch_var, width=18).grid(row=2, column=3, padx=5)

        ttk.Label(form, text="Expiry (YYYY-MM-DD)*").grid(row=3, column=0, sticky="w", padx=5, pady=4)
        self.expiry_var = tk.StringVar(value="2027-12-31")
        ttk.Entry(form, textvariable=self.expiry_var, width=24).grid(row=3, column=1, padx=5)

        btns = ttk.Frame(form)
        btns.grid(row=4, column=0, columnspan=4, pady=8)
        ttk.Button(btns, text="Add", command=self.add_med).pack(side="left", padx=4)
        ttk.Button(btns, text="Update Selected", command=self.update_med).pack(side="left", padx=4)
        ttk.Button(btns, text="Delete Selected", command=self.delete_med).pack(side="left", padx=4)
        ttk.Button(btns, text="Clear Form", command=self.clear_form).pack(side="left", padx=4)

    def _build_table(self):
        cols = ("id", "name", "cat", "stock", "price", "reorder", "batch", "expiry")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=15)
        for c, h, w in zip(cols, ["ID", "Name", "Category", "Stock", "Unit Price", "Reorder Lvl", "Batch No", "Expiry Date"],
                            [40, 150, 110, 70, 80, 80, 95, 100]):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w)
        self.tree.pack(fill="both", expand=True, padx=10, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        ttk.Label(self, text="* Low Stock Alert | [EXPIRED] Poka-Yoke Blocked from dispensing",
                  font=("Segoe UI", 8, "italic")).pack(anchor="w", padx=10)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in medicine_model.list_all():
            r_dict = dict(r)
            is_low = r_dict["stock_qty"] <= r_dict["reorder_level"]
            is_exp = medicine_model.is_expired(r_dict.get("expiry_date", ""))
            flag = ""
            if is_exp:
                flag = " [EXPIRED]"
            elif is_low:
                flag = " *"
            self.tree.insert("", "end", values=(
                r_dict["medicine_id"],
                r_dict["name"] + flag,
                r_dict["category"],
                r_dict["stock_qty"],
                r_dict["unit_price"],
                r_dict["reorder_level"],
                r_dict.get("batch_no", "N/A"),
                r_dict.get("expiry_date", "N/A")
            ))

    def _on_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        self.selected_id = vals[0]
        name_clean = str(vals[1]).replace(" [EXPIRED]", "").replace(" *", "")
        self.name_var.set(name_clean)
        self.cat_var.set(vals[2])
        self.stock_var.set(vals[3])
        self.price_var.set(vals[4])
        self.reorder_var.set(vals[5])
        self.batch_var.set(vals[6])
        self.expiry_var.set(vals[7])

    def _validate(self):
        if not not_empty(self.name_var.get()):
            messagebox.showerror("Validation Error", "Name is required.")
            return False
        if self.cat_var.get() not in MEDICINE_CATEGORIES:
            messagebox.showerror("Validation Error", "Please select a Category from the dropdown.")
            return False
        try:
            s = int(self.stock_var.get())
            p = float(self.price_var.get())
            r = int(self.reorder_var.get())
            if s < 0 or p < 0 or r < 0:
                messagebox.showerror("Validation Error", "Stock, Price, and Reorder Level cannot be negative.")
                return False
        except ValueError:
            messagebox.showerror("Validation Error", "Stock/Reorder must be integers, Price a number.")
            return False
        from utils.validators import is_valid_date
        exp = self.expiry_var.get().strip()
        if exp and not is_valid_date(exp):
            messagebox.showerror("Validation Error", "Expiry Date must be in YYYY-MM-DD format.")
            return False
        return True

    def clear_form(self):
        self.selected_id = None
        self.name_var.set("")
        self.cat_var.set("")
        self.stock_var.set("")
        self.price_var.set("")
        self.reorder_var.set("10")
        self.batch_var.set("BAT-2026-01")
        self.expiry_var.set("2027-12-31")

    def add_med(self):
        if not self._validate():
            return
        medicine_model.add(
            self.name_var.get().strip(),
            self.cat_var.get(),
            int(self.stock_var.get()),
            float(self.price_var.get()),
            int(self.reorder_var.get()),
            batch_no=self.batch_var.get().strip() or "BAT-2026-01",
            expiry_date=self.expiry_var.get().strip() or "2027-12-31"
        )
        messagebox.showinfo("Success", "Medicine added.")
        self.clear_form()
        self.refresh()

    def update_med(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a medicine row first.")
            return
        if not self._validate():
            return
        if not confirm_update("medicine", self.selected_id):
            return
        medicine_model.update(
            self.selected_id,
            self.name_var.get().strip(),
            self.cat_var.get(),
            int(self.stock_var.get()),
            float(self.price_var.get()),
            int(self.reorder_var.get()),
            batch_no=self.batch_var.get().strip() or "BAT-2026-01",
            expiry_date=self.expiry_var.get().strip() or "2027-12-31"
        )
        messagebox.showinfo("Success", "Medicine updated.")
        self.clear_form()
        self.refresh()

    def delete_med(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a medicine row first.")
            return
        if not confirm_delete("medicine", self.selected_id):
            return
        medicine_model.delete(self.selected_id)
        messagebox.showinfo("Deleted", "Medicine deleted.")
        self.clear_form()
        self.refresh()
