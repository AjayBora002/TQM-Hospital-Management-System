"""billing_view.py -- Billing/Invoicing tab: patient auto-complete, payment dropdowns, confirm, audit."""
import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PAYMENT_METHODS, PAYMENT_STATUS
from models import bill as bill_model
from models import patient as patient_model
from widgets.autocomplete_entry import AutocompleteEntry
from widgets.confirm_dialog import confirm_delete, confirm


class BillingTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.selected_id = None
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="Generate Bill")
        form.pack(fill="x", padx=10, pady=8)

        ttk.Label(form, text="Patient (name)*").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.patient_ac = AutocompleteEntry(form, fetch_candidates=patient_model.name_candidates, width=26)
        self.patient_ac.grid(row=0, column=1, padx=5)

        ttk.Label(form, text="Room Charges (Rs)").grid(row=0, column=2, sticky="w", padx=5)
        self.room_var = tk.StringVar(value="0")
        ttk.Entry(form, textvariable=self.room_var, width=16).grid(row=0, column=3, padx=5)

        ttk.Label(form, text="Consultation Charges (Rs)").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.consult_var = tk.StringVar(value="0")
        ttk.Entry(form, textvariable=self.consult_var, width=26).grid(row=1, column=1, padx=5)

        ttk.Label(form, text="Medicine Charges (Rs)").grid(row=1, column=2, sticky="w", padx=5)
        self.med_var = tk.StringVar(value="0")
        ttk.Entry(form, textvariable=self.med_var, width=16).grid(row=1, column=3, padx=5)

        ttk.Label(form, text="Payment Method*").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.method_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.method_var, values=PAYMENT_METHODS,
                     state="readonly", width=24).grid(row=2, column=1, padx=5)

        ttk.Label(form, text="Payment Status*").grid(row=2, column=2, sticky="w", padx=5)
        self.pstatus_var = tk.StringVar(value="Pending")
        ttk.Combobox(form, textvariable=self.pstatus_var, values=PAYMENT_STATUS,
                     state="readonly", width=16).grid(row=2, column=3, padx=5)

        btns = ttk.Frame(form)
        btns.grid(row=3, column=0, columnspan=4, pady=8)
        ttk.Button(btns, text="Generate Bill", command=self.add_bill).pack(side="left", padx=4)
        ttk.Button(btns, text="Mark Paid (Selected)", command=self.mark_paid).pack(side="left", padx=4)
        ttk.Button(btns, text="Delete Selected", command=self.delete_bill).pack(side="left", padx=4)
        ttk.Button(btns, text="Clear Form", command=self.clear_form).pack(side="left", padx=4)

    def _build_table(self):
        cols = ("id", "patient", "room", "consult", "med", "total", "method", "status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=13)
        headers = ["ID", "Patient", "Room", "Consult", "Medicine", "Total", "Method", "Status"]
        widths = [40, 150, 70, 70, 80, 80, 80, 100]
        for c, h, w in zip(cols, headers, widths):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w)
        self.tree.pack(fill="both", expand=True, padx=10, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in bill_model.list_all():
            self.tree.insert("", "end", values=(r["bill_id"], r["patient_name"], r["room_charges"],
                                                  r["consultation_charges"], r["medicine_charges"],
                                                  r["total_amount"], r["payment_method"],
                                                  r["payment_status"]))

    def _on_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        self.selected_id = vals[0]

    def _validate(self):
        if patient_model.get_id_by_name(self.patient_ac.var.get().strip()) is None:
            messagebox.showerror("Validation Error",
                                  "Select a valid patient from the auto-complete suggestions.")
            return False
        try:
            float(self.room_var.get()); float(self.consult_var.get()); float(self.med_var.get())
        except ValueError:
            messagebox.showerror("Validation Error", "Charges must be numbers.")
            return False
        if self.method_var.get() not in PAYMENT_METHODS:
            messagebox.showerror("Validation Error", "Please select a Payment Method from the dropdown.")
            return False
        if self.pstatus_var.get() not in PAYMENT_STATUS:
            messagebox.showerror("Validation Error", "Please select a Payment Status from the dropdown.")
            return False
        return True

    def clear_form(self):
        self.selected_id = None
        self.patient_ac.var.set("")
        self.room_var.set("0")
        self.consult_var.set("0")
        self.med_var.set("0")
        self.method_var.set("")
        self.pstatus_var.set("Pending")

    def add_bill(self):
        if not self._validate():
            return
        pid = patient_model.get_id_by_name(self.patient_ac.var.get().strip())
        _, total = bill_model.add(pid, float(self.room_var.get()), float(self.consult_var.get()),
                                   float(self.med_var.get()), self.method_var.get(), self.pstatus_var.get())
        messagebox.showinfo("Success", f"Bill generated. Total: Rs {total}")
        self.clear_form()
        self.refresh()

    def mark_paid(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a bill row first.")
            return
        if not confirm("Confirm Update", f"Mark bill #{self.selected_id} as Paid?"):
            return
        bill_model.update_status(self.selected_id, "Paid")
        messagebox.showinfo("Success", "Bill marked as Paid.")
        self.refresh()

    def delete_bill(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select a bill row first.")
            return
        if not confirm_delete("bill", self.selected_id):
            return
        bill_model.delete(self.selected_id)
        messagebox.showinfo("Deleted", "Bill deleted.")
        self.clear_form()
        self.refresh()
