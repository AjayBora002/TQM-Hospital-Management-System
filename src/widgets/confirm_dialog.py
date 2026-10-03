"""
confirm_dialog.py -- Q07 Feature 4: Confirmation Modals
One shared helper so every destructive/critical action across every module
(Patients, Doctors, Appointments, Rooms, Staff, Medicines, Bills) asks the
same way -- no screen can accidentally skip the confirmation step.
"""
from tkinter import messagebox


def confirm(title, message):
    """Returns True only if the user explicitly clicks 'Yes'."""
    return messagebox.askyesno(title, message)


def confirm_delete(entity_name, record_id):
    return confirm("Confirm Delete", f"Delete {entity_name} #{record_id}? This cannot be undone.")


def confirm_update(entity_name, record_id):
    return confirm("Confirm Update", f"Update {entity_name} #{record_id}?")
