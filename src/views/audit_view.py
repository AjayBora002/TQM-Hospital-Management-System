"""audit_view.py -- Q07 Feature 5: Audit Logs (read-only viewer, every table)."""
from tkinter import ttk
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import audit as audit_model


class AuditLogTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        ttk.Label(self, text="Audit Log (read-only) -- every Insert/Update/Delete across every module",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=6)
        cols = ("id", "table", "record", "action", "details", "by", "time")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=20)
        for c, h, w in zip(cols, ["ID", "Table", "Record ID", "Action", "Details", "By", "Timestamp"],
                            [40, 100, 80, 80, 300, 110, 160]):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w)
        self.tree.pack(fill="both", expand=True, padx=10, pady=8)
        ttk.Button(self, text="Refresh", command=self.refresh).pack(pady=4)
        self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in audit_model.list_audit():
            self.tree.insert("", "end", values=(r["log_id"], r["table_name"], r["record_id"],
                                                  r["action"], r["details"], r["performed_by"],
                                                  r["timestamp"]))
