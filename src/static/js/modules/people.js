/**
 * people.js -- Human Resources & Staff Rostering Domain Module
 * Staff Directory, Shift Rostering, and Leave Approvals.
 */
import { api } from "../core/api.js";
import { showToast, openModal, closeModal } from "../core/ui.js";

export async function loadStaff() {
  try {
    const list = await api.get("/staff");
    const tbody = document.getElementById("staffTableBody");
    if (!tbody) return;

    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:24px;color:#94a3b8;">No staff members listed.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(s => `
      <tr>
        <td>#STF-${String(s.staff_id).padStart(4, "0")}</td>
        <td><strong>${s.full_name}</strong></td>
        <td><span class="badge badge-info">${s.role}</span></td>
        <td><span class="badge badge-neutral">${s.shift}</span></td>
        <td>${s.phone}</td>
        <td>
          <button class="btn btn-sm btn-secondary" onclick="window.hmsEditStaffModal(${s.staff_id})">Edit</button>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(`Failed to load staff: ${err.message}`, "danger");
  }
}

export async function loadShifts() {
  try {
    const list = await api.get("/people/shifts");
    const tbody = document.getElementById("shiftsTableBody");
    if (!tbody) return;

    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:24px;color:#94a3b8;">No scheduled shifts.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(sh => `
      <tr>
        <td>#SHF-${String(sh.shift_id).padStart(4, "0")}</td>
        <td><strong>${sh.staff_name}</strong> <span style="font-size:12px;color:#64748b;">(${sh.staff_role})</span></td>
        <td>${sh.department}</td>
        <td>${sh.shift_date}</td>
        <td><span class="badge badge-info">${sh.shift_type}</span></td>
        <td>${sh.notes || '-'}</td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(`Failed to load shifts: ${err.message}`, "danger");
  }
}

export async function loadLeaves() {
  try {
    const list = await api.get("/people/leaves");
    const tbody = document.getElementById("leavesTableBody");
    if (!tbody) return;

    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:#94a3b8;">No pending leave requests.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(l => `
      <tr>
        <td>#LV-${String(l.leave_id).padStart(4, "0")}</td>
        <td><strong>${l.staff_name}</strong></td>
        <td><strong>${l.leave_type}</strong></td>
        <td>${l.start_date} to ${l.end_date}</td>
        <td>${l.reason}</td>
        <td><span class="badge ${l.status === 'Approved' ? 'badge-success' : l.status === 'Rejected' ? 'badge-danger' : 'badge-warning'}">${l.status}</span></td>
        <td>
          ${l.status === 'Pending' ? `
            <button class="btn btn-sm btn-success" onclick="window.hmsLeaveDecision(${l.leave_id}, 'Approved')">Approve</button>
            <button class="btn btn-sm btn-danger" onclick="window.hmsLeaveDecision(${l.leave_id}, 'Rejected')">Reject</button>
          ` : `<span style="font-size:12px;color:#94a3b8;">${l.approved_by || 'Processed'}</span>`}
        </td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(`Failed to load leaves: ${err.message}`, "danger");
  }
}

