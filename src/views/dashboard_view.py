"""dashboard_view.py -- At-a-glance summary stats across all modules."""
from tkinter import ttk
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import get_connection


class DashboardTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        ttk.Label(self, text="Hospital Management System -- Dashboard",
                  font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        ttk.Label(self, text="Quality Goal Q07: Improve Data Accuracy",
                  font=("Segoe UI", 10, "italic")).pack(anchor="w", padx=15, pady=(0, 15))

        self.cards_frame = ttk.Frame(self)
        self.cards_frame.pack(fill="x", padx=15)
        ttk.Button(self, text="Refresh Dashboard", command=self.refresh).pack(anchor="w", padx=15, pady=10)
        self.refresh()

    def _stat(self, label, query):
        conn = get_connection()
        try:
            val = conn.execute(query).fetchone()[0]
        except Exception:
            val = 0
        conn.close()
        return val

    def refresh(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()

        stats = [
            ("Total Patients", "SELECT COUNT(*) FROM patients"),
            ("Total Doctors", "SELECT COUNT(*) FROM doctors"),
            ("Scheduled Appointments", "SELECT COUNT(*) FROM appointments WHERE status='Scheduled'"),
            ("Occupied Rooms", "SELECT COUNT(*) FROM rooms WHERE status='Occupied'"),
            ("Available Rooms", "SELECT COUNT(*) FROM rooms WHERE status='Available'"),
            ("Staff on Roll", "SELECT COUNT(*) FROM staff"),
            ("Low-Stock Medicines", "SELECT COUNT(*) FROM medicines WHERE stock_qty <= reorder_level"),
            ("Pending Bills", "SELECT COUNT(*) FROM bills WHERE payment_status != 'Paid'"),
            ("Open Defects", "SELECT COUNT(*) FROM defect_log WHERE status='Open'"),
            ("Audit Log Entries", "SELECT COUNT(*) FROM audit_log"),
        ]

        for i, (label, query) in enumerate(stats):
            val = self._stat(label, query)
            card = ttk.LabelFrame(self.cards_frame, text=label)
            card.grid(row=i // 3, column=i % 3, padx=8, pady=8, sticky="nsew")
            ttk.Label(card, text=str(val), font=("Segoe UI", 20, "bold")).pack(padx=20, pady=10)

        for c in range(3):
            self.cards_frame.columnconfigure(c, weight=1)
