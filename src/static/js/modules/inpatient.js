/**
 * inpatient.js -- Inpatient & Ward Management Domain Module
 * Interactive Bed Board, Admissions & Transfers, Nursing Tasks & MAR,
 * Shift Handover Protocol, and Printable Discharge Summary.
 */
import { api } from "../core/api.js";
import { showToast, openModal, closeModal, printDocument } from "../core/ui.js";

export async function loadBedBoard(wardId = null) {
  try {
    const url = wardId ? `/wards/bed-board?ward_id=${wardId}` : "/wards/bed-board";
    const data = await api.get(url);
    const container = document.getElementById("bedBoardContainer");
    if (!container) return;

    const beds = data.beds || [];
    const stats = data.stats || {};

    let statsHtml = `
      <div style="display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap;">
        <span class="badge badge-success" style="font-size:13px;padding:6px 12px;">Available: ${stats.available || 0}</span>
        <span class="badge badge-danger" style="font-size:13px;padding:6px 12px;">Occupied: ${stats.occupied || 0}</span>
        <span class="badge badge-warning" style="font-size:13px;padding:6px 12px;">Cleaning: ${stats.cleaning || 0}</span>
        <span class="badge badge-neutral" style="font-size:13px;padding:6px 12px;">Maintenance: ${stats.maintenance || 0}</span>
        <span class="badge badge-info" style="font-size:13px;padding:6px 12px;">Total Beds: ${stats.total || 0}</span>
      </div>
    `;

    let bedCardsHtml = beds.map(b => {
      let statusColor = "#10b981"; // green
      let statusBg = "#ecfdf5";
      if (b.status === "Occupied") { statusColor = "#ef4444"; statusBg = "#fef2f2"; }
      else if (b.status === "Cleaning / Sanitizing") { statusColor = "#f59e0b"; statusBg = "#fffbeb"; }
      else if (b.status === "Under Maintenance") { statusColor = "#64748b"; statusBg = "#f1f5f9"; }

      return `
        <div style="background:${statusBg};border:2px solid ${statusColor};border-radius:8px;padding:12px;display:flex;flex-direction:column;justify-content:space-between;min-height:120px;">
          <div>
            <div style="display:flex;justify-content:space-between;align-items:baseline;">
              <span style="font-weight:bold;font-size:16px;color:#0f172a;">${b.room_number}</span>
              <span style="font-size:11px;font-weight:600;color:${statusColor};text-transform:uppercase;">${b.status}</span>
            </div>
            <div style="font-size:12px;color:#64748b;margin-top:2px;">${b.room_type} | ${b.ward_name || 'General Ward'}</div>
            ${b.patient_name ? `
              <div style="margin-top:6px;font-size:13px;font-weight:600;color:#0f172a;">
                ${b.patient_name} <span style="font-size:11px;color:#64748b;">(Stay: ${b.stay_days || 1}d)</span>
              </div>
            ` : '<div style="font-size:12px;color:#94a3b8;margin-top:6px;">Ready for allocation</div>'}
          </div>
          <div style="margin-top:8px;display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:11px;color:#64748b;">Rs. ${b.rate_per_day}/day</span>
            <button class="btn btn-sm btn-secondary" style="padding:2px 6px;font-size:11px;" onclick="window.hmsEditBedStatusModal(${b.room_id}, '${b.room_number}', '${b.status}')">Status</button>
          </div>
        </div>
      `;
    }).join("");

    container.innerHTML = `
      ${statsHtml}
      <div style="display:grid;grid-template-columns:repeat(auto-fill, minmax(200px, 1fr));gap:12px;">
        ${bedCardsHtml}
      </div>
    `;
  } catch (err) {
    showToast(`Failed to load bed board: ${err.message}`, "danger");
  }
}

export async function loadAdmissions() {
  try {
    const list = await api.get("/admissions");
    const tbody = document.getElementById("admissionsTableBody");
    if (!tbody) return;

    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:#94a3b8;">No admission records found.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(a => `
      <tr>
        <td>#ADM-${String(a.admission_id).padStart(4, "0")}</td>
        <td><strong>${a.patient_name || `Patient #${a.patient_id}`}</strong></td>
        <td><strong>Room ${a.room_number}</strong> (${a.room_type})</td>
        <td>${a.admission_date}</td>
        <td>${a.diagnosis || 'Clinical Investigation'}</td>
        <td><span class="badge ${a.status === 'Admitted' ? 'badge-danger' : 'badge-success'}">${a.status}</span></td>
        <td>
          <div style="display:flex;gap:4px;">
            ${a.status === 'Admitted' ? `
              <button class="btn btn-sm btn-danger" onclick="window.hmsDischargeModal(${a.admission_id})">Discharge</button>
            ` : `
              <button class="btn btn-sm btn-secondary" onclick="window.hmsPrintDischargeSummary(${a.admission_id})">Summary</button>
            `}
          </div>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(`Failed to load admissions: ${err.message}`, "danger");
  }
}

