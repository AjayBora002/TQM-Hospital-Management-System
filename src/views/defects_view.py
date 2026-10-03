"""defects_view.py -- Defect Checksheet tab (Step 6): feeds the Pareto chart in sqc/."""
import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DEFECT_CATEGORIES, DEFECT_SEVERITY
from models import audit as audit_model


class DefectLogTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        form = ttk.LabelFrame(self, text="Log a Defect / Bug (Checksheet entry)")
        form.pack(fill="x", padx=10, pady=8)

        ttk.Label(form, text="Category*").grid(row=0, column=0, padx=5, pady=4, sticky="w")
        self.cat_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.cat_var, values=DEFECT_CATEGORIES,
                     state="readonly", width=18).grid(row=0, column=1, padx=5)

        ttk.Label(form, text="Severity*").grid(row=0, column=2, padx=5, sticky="w")
        self.sev_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.sev_var, values=DEFECT_SEVERITY,
                     state="readonly", width=14).grid(row=0, column=3, padx=5)

        ttk.Label(form, text="Description*").grid(row=1, column=0, padx=5, pady=4, sticky="w")
        self.desc_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.desc_var, width=60).grid(row=1, column=1, columnspan=3,
                                                                     padx=5, sticky="w")

        ttk.Button(form, text="Log Defect", command=self.add_defect).grid(row=2, column=0, pady=8)

        cols = ("id", "category", "severity", "status", "desc", "time")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=14)
        for c, h, w in zip(cols, ["ID", "Category", "Severity", "Status", "Description", "Logged At"],
                            [40, 100, 80, 70, 320, 150]):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w)
        self.tree.pack(fill="both", expand=True, padx=10, pady=8)
        self.refresh()

    def add_defect(self):
        if not self.cat_var.get() or not self.sev_var.get() or not self.desc_var.get().strip():
            messagebox.showerror("Validation Error", "Category, Severity and Description are required.")
            return
        audit_model.add_defect(self.cat_var.get(), self.desc_var.get().strip(), self.sev_var.get())
        self.cat_var.set("")
        self.sev_var.set("")
        self.desc_var.set("")
        self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in audit_model.list_defects():
            self.tree.insert("", "end", values=(r["defect_id"], r["category"], r["severity"],
                                                  r["status"], r["description"], r["logged_at"]))
