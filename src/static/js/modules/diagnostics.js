/**
 * diagnostics.js -- Diagnostics Domain Module
 * Laboratory Information System (LIS), Radiology & DICOM Reports, and Blood Bank Inventory.
 */
import { api } from "../core/api.js";
import { showToast, openModal, closeModal } from "../core/ui.js";

export async function loadLabTests() {
  try {
    const tests = await api.get("/lab-tests");
    const tbody = document.getElementById("labTestsTableBody");
    if (!tbody) return;

    if (!tests || tests.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:24px;color:#94a3b8;">No laboratory orders recorded.</td></tr>`;
      return;
    }

    tbody.innerHTML = tests.map(t => {
      const isAbnormal = Boolean(t.abnormal_flag);
      return `
        <tr>
          <td>#LAB-${String(t.test_id).padStart(4, "0")}</td>
          <td><strong>${t.patient_name || `Patient #${t.patient_id}`}</strong></td>
          <td>${t.doctor_name || `Doctor #${t.doctor_id}`}</td>
          <td><strong>${t.test_name}</strong> <span style="font-size:11px;color:#64748b;">(${t.category})</span></td>
          <td>
            ${t.result_value !== null ? `<strong>${t.result_value}</strong> ${t.unit}` : '<span style="color:#94a3b8;">Pending</span>'}
          </td>
          <td><span style="font-size:12px;color:#64748b;">${t.ref_min} - ${t.ref_max} ${t.unit}</span></td>
          <td>
            ${isAbnormal ? '<span class="badge badge-danger">ABNORMAL</span>' : `<span class="badge ${t.status === 'Completed' || t.status === 'Verified' ? 'badge-success' : 'badge-warning'}">${t.status}</span>`}
          </td>
          <td>
            <div style="display:flex;gap:4px;">
              ${t.status === 'Pending' ? `
                <button class="btn btn-sm btn-primary" onclick="window.hmsOpenLabResultModal(${t.test_id}, '${t.test_name}', ${t.ref_min}, ${t.ref_max}, '${t.unit}')">Enter Result</button>
              ` : `
                <button class="btn btn-sm btn-secondary" onclick="window.hmsPrintLabReport(${t.test_id})">Print Report</button>
              `}
            </div>
          </td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    showToast(`Failed to load lab tests: ${err.message}`, "danger");
  }
}

export async function loadRadiologyOrders() {
  try {
    const orders = await api.get("/radiology/orders");
    const tbody = document.getElementById("radiologyTableBody");
    if (!tbody) return;

    if (!orders || orders.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:#94a3b8;">No radiology imaging orders.</td></tr>`;
      return;
    }

    tbody.innerHTML = orders.map(r => `
      <tr>
        <td>#RAD-${String(r.order_id).padStart(4, "0")}</td>
        <td><strong>${r.patient_name}</strong></td>
        <td><span class="badge badge-info">${r.modality}</span> <strong>${r.body_part}</strong></td>
        <td>${r.ordering_doctor_name}</td>
        <td><span class="badge ${r.urgency === 'STAT' ? 'badge-danger' : r.urgency === 'Urgent' ? 'badge-warning' : 'badge-neutral'}">${r.urgency}</span></td>
        <td><span class="badge ${r.status === 'Verified' || r.status === 'Reported' ? 'badge-success' : 'badge-warning'}">${r.status}</span></td>
        <td>
          <div style="display:flex;gap:4px;">
            ${r.status === 'Ordered' || r.status === 'Scheduled' ? `
              <button class="btn btn-sm btn-primary" onclick="window.hmsOpenRadiologyReportModal(${r.order_id})">File Report</button>
            ` : `
              <button class="btn btn-sm btn-secondary" onclick="window.hmsViewRadiologyReport(${r.order_id})">View Findings</button>
            `}
          </div>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(`Failed to load radiology orders: ${err.message}`, "danger");
  }
}

export async function loadBloodBank() {
  try {
    const units = await api.get("/blood-bank/inventory");
    const tbody = document.getElementById("bloodBankTableBody");
    if (!tbody) return;

    if (!units || units.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:#94a3b8;">No blood units in inventory.</td></tr>`;
      return;
    }

    tbody.innerHTML = units.map(u => {
      const isExpiring = new Date(u.expiry_date) < new Date();
      return `
        <tr>
          <td><span style="font-family:monospace;font-weight:600;color:#0284c7;">${u.bag_number}</span></td>
          <td><span class="badge badge-danger" style="font-size:14px;font-weight:bold;">${u.blood_group}</span></td>
          <td><strong>${u.component_type}</strong></td>
          <td>${u.collection_date}</td>
          <td>
            <span style="${isExpiring ? 'color:#ef4444;font-weight:bold;' : ''}">${u.expiry_date}</span>
            ${isExpiring ? '<span class="badge badge-danger" style="margin-left:4px;">EXPIRED</span>' : ''}
          </td>
          <td><span style="font-size:12px;color:#64748b;">${u.storage_location}</span></td>
          <td><span class="badge ${u.status === 'Available' ? 'badge-success' : 'badge-warning'}">${u.status}</span></td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    showToast(`Failed to load blood bank inventory: ${err.message}`, "danger");
  }
}

