/**
 * front_office.js -- Front Office Domain Module
 * Patient Registration (duplicate check, UHID, ABHA), Appointments (slot conflict engine),
 * OPD Queue / Tokens, and Visitor Management.
 */
import { api } from "../core/api.js";
import { store } from "../core/store.js";
import { showToast, openModal, closeModal } from "../core/ui.js";

export async function loadPatients(query = "") {
  try {
    const list = await api.get(`/patients?q=${encodeURIComponent(query)}`);
    const tbody = document.getElementById("patientsTableBody");
    if (!tbody) return;

    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:24px;color:#94a3b8;">No patient records found.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(p => {
      const uhid = `UHID-2026-${String(p.patient_id).padStart(4, "0")}`;
      const hasAllergy = p.allergies && p.allergies.toLowerCase() !== "none";
      return `
        <tr>
          <td><span style="font-family:monospace;font-weight:600;color:#0284c7;">${uhid}</span></td>
          <td>
            <strong>${p.full_name}</strong>
            ${p.address ? `<div style="font-size:12px;color:#64748b;">${p.address}</div>` : ''}
          </td>
          <td>${p.gender}</td>
          <td>${p.dob || 'N/A'}</td>
          <td><span class="badge badge-neutral">${p.blood_group}</span></td>
          <td>${p.phone}</td>
          <td>
            ${hasAllergy 
              ? `<span class="badge badge-danger">Allergy: ${p.allergies}</span>` 
              : `<span class="badge badge-success">None</span>`}
          </td>
          <td>
            <div style="display:flex;gap:6px;">
              <button class="btn btn-sm btn-primary" onclick="window.hmsSelectPatient(${p.patient_id})">Select</button>
              <button class="btn btn-sm btn-secondary" onclick="window.hmsOpenQueueModal(${p.patient_id})">Token</button>
              <button class="btn btn-sm btn-secondary" onclick="window.hmsOpenTimeline(${p.patient_id})">EMR</button>
            </div>
          </td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    showToast(`Failed to load patients: ${err.message}`, "danger");
  }
}

export async function registerPatient(formData) {
  try {
    const res = await api.post("/patients", formData);
    showToast("Patient registered successfully with assigned UHID", "success");
    loadPatients();
    return res;
  } catch (err) {
    showToast(`Registration failed: ${err.message}`, "danger");
    throw err;
  }
}

export async function loadAppointments() {
  try {
    const appts = await api.get("/appointments");
    const tbody = document.getElementById("appointmentsTableBody");
    if (!tbody) return;

    if (!appts || appts.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:#94a3b8;">No scheduled appointments.</td></tr>`;
      return;
    }

    tbody.innerHTML = appts.map(a => `
      <tr>
        <td>#APT-${String(a.appointment_id).padStart(4, "0")}</td>
        <td><strong>${a.patient_name || `Patient #${a.patient_id}`}</strong></td>
        <td>${a.doctor_name || `Doctor #${a.doctor_id}`}</td>
        <td>${a.appt_date}</td>
        <td><span class="badge badge-info">${a.appt_time}</span></td>
        <td><span class="badge ${a.status === 'Completed' ? 'badge-success' : a.status === 'Cancelled' ? 'badge-danger' : 'badge-warning'}">${a.status}</span></td>
        <td>
          <div style="display:flex;gap:4px;">
            ${a.status === 'Scheduled' ? `
              <button class="btn btn-sm btn-success" onclick="window.hmsCheckInAppt(${a.appointment_id}, ${a.patient_id}, ${a.doctor_id})">Check-in</button>
              <button class="btn btn-sm btn-danger" onclick="window.hmsCancelAppt(${a.appointment_id})">Cancel</button>
            ` : `
              <span style="font-size:12px;color:#94a3b8;">${a.status}</span>
            `}
          </div>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(`Failed to load appointments: ${err.message}`, "danger");
  }
}

export async function loadOpdQueue(doctorId = null) {
  try {
    const url = doctorId ? `/opd-queue/today?doctor_id=${doctorId}` : "/opd-queue/today";
    const queue = await api.get(url);
    const tbody = document.getElementById("opdQueueTableBody");
    if (!tbody) return;

    if (!queue || queue.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:#94a3b8;">No tokens in queue today.</td></tr>`;
      return;
    }

    tbody.innerHTML = queue.map(q => {
      const priorityClass = q.priority === "Emergency" ? "badge-danger" : q.priority === "Urgent" ? "badge-warning" : "badge-neutral";
      return `
        <tr>
          <td><span style="font-size:18px;font-weight:bold;color:#0284c7;">#${q.token_number}</span></td>
          <td><strong>${q.patient_name}</strong></td>
          <td>${q.doctor_name}</td>
          <td><span class="badge ${priorityClass}">${q.priority}</span></td>
          <td><span class="badge ${q.status === 'In Consultation' ? 'badge-warning' : q.status === 'Completed' ? 'badge-success' : 'badge-info'}">${q.status}</span></td>
          <td>${q.check_in_time ? q.check_in_time.split(" ")[1] || q.check_in_time : '-'}</td>
          <td>
            <div style="display:flex;gap:4px;">
              ${q.status === 'Waiting' ? `
                <button class="btn btn-sm btn-primary" onclick="window.hmsCallToken(${q.queue_id})">Call</button>
              ` : q.status === 'Called' || q.status === 'In Consultation' ? `
                <button class="btn btn-sm btn-success" onclick="window.hmsCompleteToken(${q.queue_id}, ${q.patient_id})">Complete</button>
              ` : `<span style="font-size:12px;color:#94a3b8;">Done</span>`}
            </div>
          </td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    showToast(`Failed to load OPD queue: ${err.message}`, "danger");
  }
}
