/**
 * support.js -- Hospital Support Services Domain Module
 * Housekeeping Sanitation, Clinical Dietetics, Ambulance Dispatch,
 * Biomedical Engineering, and Facility Tickets.
 */
import { api } from "../core/api.js";
import { showToast, openModal, closeModal } from "../core/ui.js";

export async function loadHousekeepingTasks() {
  try {
    const list = await api.get("/support/housekeeping");
    const tbody = document.getElementById("housekeepingTableBody");
    if (!tbody) return;

    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:24px;color:#94a3b8;">No pending housekeeping tasks.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(h => `
      <tr>
        <td>#HK-${String(h.task_id).padStart(4, "0")}</td>
        <td><strong>${h.area_name}</strong></td>
        <td>${h.task_type}</td>
        <td><span class="badge ${h.priority === 'Immediate' ? 'badge-danger' : h.priority === 'Urgent' ? 'badge-warning' : 'badge-neutral'}">${h.priority}</span></td>
        <td><span class="badge ${h.status === 'Completed' ? 'badge-success' : 'badge-warning'}">${h.status}</span></td>
        <td>${h.assigned_to || 'Sanitation Team'}</td>
        <td>${h.requested_at}</td>
        <td>
          ${h.status !== 'Completed' ? `
            <button class="btn btn-sm btn-success" onclick="window.hmsCompleteHousekeeping(${h.task_id})">Sanitize & Clear</button>
          ` : '<span style="font-size:12px;color:#10b981;font-weight:600;">Sanitized</span>'}
        </td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(`Failed to load housekeeping tasks: ${err.message}`, "danger");
  }
}

export async function loadDietOrders() {
  try {
    const list = await api.get("/support/diet-orders");
    const tbody = document.getElementById("dietOrdersTableBody");
    if (!tbody) return;

    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:#94a3b8;">No clinical diet orders.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(d => `
      <tr>
        <td>#DO-${String(d.order_id).padStart(4, "0")}</td>
        <td><strong>${d.patient_name}</strong></td>
        <td><strong>${d.diet_type}</strong></td>
        <td>${d.meal_type}</td>
        <td>${d.calories_kcal} kcal</td>
        <td><span class="badge ${d.status === 'Delivered' ? 'badge-success' : 'badge-info'}">${d.status}</span></td>
        <td><span style="font-size:12px;color:#64748b;">${d.dietitian_notes || 'Standard clinical nutrition'}</span></td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(`Failed to load diet orders: ${err.message}`, "danger");
  }
}

export async function loadAmbulanceFleet() {
  try {
    const list = await api.get("/support/ambulance-trips");
    const tbody = document.getElementById("ambulanceTableBody");
    if (!tbody) return;

    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:24px;color:#94a3b8;">No ambulance trips logged today.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(a => `
      <tr>
        <td>#EMS-${String(a.trip_id).padStart(4, "0")}</td>
        <td><strong>${a.vehicle_number}</strong></td>
        <td>${a.trip_type}</td>
        <td>${a.patient_name}</td>
        <td>${a.pickup_location}</td>
        <td>${a.drop_location}</td>
        <td><span class="badge ${a.status === 'Completed' ? 'badge-success' : 'badge-danger'}">${a.status}</span></td>
        <td>${a.dispatch_time}</td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(`Failed to load ambulance trips: ${err.message}`, "danger");
  }
}

export async function loadBiomedicalEquipment() {
  try {
    const list = await api.get("/support/biomedical");
    const tbody = document.getElementById("biomedTableBody");
    if (!tbody) return;

    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:24px;color:#94a3b8;">No biomedical equipment records.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(b => `
      <tr>
        <td>#BME-${String(b.equip_id).padStart(4, "0")}</td>
        <td><strong>${b.equipment_name}</strong> <span style="font-size:11px;color:#64748b;">(${b.model})</span></td>
        <td><span style="font-family:monospace;font-size:12px;">${b.serial_number}</span></td>
        <td>${b.location}</td>
        <td><span class="badge ${b.status === 'Operational' ? 'badge-success' : 'badge-danger'}">${b.status}</span></td>
        <td>${b.next_service_date || 'N/A'}</td>
        <td>${b.calibration_due || 'N/A'}</td>
        <td><span style="font-size:12px;color:#64748b;">${b.vendor_contact || 'In-House'}</span></td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(`Failed to load biomedical assets: ${err.message}`, "danger");
  }
}

