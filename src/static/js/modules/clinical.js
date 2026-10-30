/**
 * clinical.js -- Clinical Domain Module
 * Triage Vitals, EMR Encounters & Timeline, Doctor Clinical Orders,
 * Emergency/Casualty Board, ICU Monitoring, and OT Schedules.
 */
import { api } from "../core/api.js";
import { store } from "../core/store.js";
import { showToast, openModal, closeModal } from "../core/ui.js";

export async function loadPatientTimeline(patientId) {
  try {
    const data = await api.get(`/patients/${patientId}/timeline`);
    const container = document.getElementById("emrTimelineContainer");
    if (!container) return;

    const pat = data.patient;
    const encounters = data.encounters || [];
    const prescriptions = data.prescriptions || [];
    const labs = data.lab_tests || [];
    const vitals = data.vitals || [];

    container.innerHTML = `
      <div style="background:#f8fafc;padding:16px;border-radius:8px;margin-bottom:20px;border:1px solid #e2e8f0;display:flex;justify-content:space-between;align-items:center;">
        <div>
          <h3 style="margin:0 0 4px 0;color:#0f172a;">${pat.full_name} (${pat.gender}, ${pat.dob || 'DOB N/A'})</h3>
          <div style="font-size:13px;color:#64748b;">UHID: UHID-2026-${String(pat.patient_id).padStart(4, "0")} | Blood: <strong>${pat.blood_group}</strong> | Allergies: <strong style="color:${pat.allergies !== 'None' ? '#ef4444' : '#10b981'};">${pat.allergies}</strong></div>
        </div>
        <div style="display:flex;gap:8px;">
          <button class="btn btn-sm btn-primary" onclick="window.hmsOpenConsultationModal(${pat.patient_id})">New SOAP Consultation</button>
          <button class="btn btn-sm btn-secondary" onclick="window.hmsOpenOrderModal(${pat.patient_id})">Clinical Order</button>
        </div>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
        <!-- Encounters / SOAP Notes -->
        <div class="card">
          <h4 style="margin-top:0;border-bottom:1px solid #e2e8f0;padding-bottom:8px;">Doctor Consultations (SOAP)</h4>
          ${encounters.length === 0 ? '<p style="color:#94a3b8;font-size:13px;">No consultation records yet.</p>' : encounters.map(e => `
            <div style="background:#f1f5f9;padding:12px;border-radius:6px;margin-bottom:10px;">
              <div style="display:flex;justify-content:space-between;font-size:12px;color:#64748b;margin-bottom:4px;">
                <span>${e.encounter_date}</span>
                <span>${e.doctor_name || 'Attending Physician'}</span>
              </div>
              <div style="font-weight:600;color:#0284c7;">Diagnosis: ${e.diagnosis}</div>
              <div style="font-size:13px;margin-top:4px;"><strong>Chief Complaint:</strong> ${e.chief_complaint}</div>
              ${e.history_illness ? `<div style="font-size:12px;color:#475569;">History: ${e.history_illness}</div>` : ''}
              ${e.plan ? `<div style="font-size:12px;color:#059669;margin-top:2px;">Plan: ${e.plan}</div>` : ''}
            </div>
          `).join("")}
        </div>

        <!-- Prescriptions & Labs -->
        <div class="card">
          <h4 style="margin-top:0;border-bottom:1px solid #e2e8f0;padding-bottom:8px;">Active Medications & Diagnostics</h4>
          <h5 style="margin:10px 0 6px 0;color:#475569;">Prescriptions</h5>
          ${prescriptions.length === 0 ? '<p style="color:#94a3b8;font-size:13px;">No prescriptions.</p>' : prescriptions.map(rx => `
            <div style="padding:8px;border-bottom:1px solid #e2e8f0;font-size:13px;display:flex;justify-content:space-between;">
              <div>
                <strong>${rx.medicine_name}</strong> - ${rx.dosage} (${rx.frequency})
                <div style="font-size:11px;color:#64748b;">${rx.instructions || 'Standard course'} | ${rx.duration_days} days</div>
              </div>
              <span class="badge ${rx.status === 'Dispensed' ? 'badge-success' : 'badge-warning'}">${rx.status}</span>
            </div>
          `).join("")}

          <h5 style="margin:14px 0 6px 0;color:#475569;">Diagnostic Lab Results</h5>
          ${labs.length === 0 ? '<p style="color:#94a3b8;font-size:13px;">No lab orders.</p>' : labs.map(l => `
            <div style="padding:8px;border-bottom:1px solid #e2e8f0;font-size:13px;display:flex;justify-content:space-between;">
              <div>
                <strong>${l.test_name}</strong>: ${l.result_value !== null ? `${l.result_value} ${l.unit}` : 'Result Pending'}
                <div style="font-size:11px;color:#64748b;">Ref: ${l.ref_min} - ${l.ref_max} ${l.unit}</div>
              </div>
              <span class="badge ${l.abnormal_flag ? 'badge-danger' : 'badge-success'}">${l.abnormal_flag ? 'ABNORMAL' : l.status}</span>
            </div>
          `).join("")}
        </div>
      </div>
    `;
  } catch (err) {
    showToast(`Failed to load patient timeline: ${err.message}`, "danger");
  }
}

export async function loadEmergencyCases() {
  try {
    const cases = await api.get("/emergency");
    const tbody = document.getElementById("emergencyTableBody");
    if (!tbody) return;

    if (!cases || cases.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:#94a3b8;">No active emergency cases.</td></tr>`;
      return;
    }

    tbody.innerHTML = cases.map(c => {
      const colorBadge = c.triage_color === "Red" 
        ? "background:#ef4444;color:#fff;" 
        : c.triage_color === "Yellow" 
          ? "background:#f59e0b;color:#fff;" 
          : "background:#10b981;color:#fff;";

      return `
        <tr>
          <td><span style="display:inline-block;padding:3px 10px;border-radius:12px;font-weight:bold;${colorBadge}">${c.triage_color}</span></td>
          <td><strong>${c.patient_name}</strong></td>
          <td>${c.chief_complaint}</td>
          <td><span style="font-family:monospace;font-size:12px;">${c.vitals_summary || 'Pending'}</span></td>
          <td>${c.attending_doctor_name || 'ER Attending'}</td>
          <td><span class="badge badge-info">${c.status}</span></td>
          <td>
            <button class="btn btn-sm btn-secondary" onclick="window.hmsUpdateEmergencyModal(${c.emergency_id})">Disposition</button>
          </td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    showToast(`Failed to load emergency cases: ${err.message}`, "danger");
  }
}

export async function loadOtSchedules() {
  try {
    const list = await api.get("/ot/schedules");
    const tbody = document.getElementById("otTableBody");
    if (!tbody) return;

    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:24px;color:#94a3b8;">No scheduled surgical procedures.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(o => `
      <tr>
        <td><strong>${o.ot_room}</strong></td>
        <td><strong>${o.procedure_name}</strong></td>
        <td>${o.patient_name}</td>
        <td>${o.surgeon_name}</td>
        <td>${o.anesthetist_name} (${o.anesthesia_type})</td>
        <td>${o.scheduled_start.replace("T", " ")}</td>
        <td>
          <span class="badge ${o.pre_op_checklist_ok ? 'badge-success' : 'badge-warning'}">Pre-Op: ${o.pre_op_checklist_ok ? 'PASS' : 'PENDING'}</span>
          <span class="badge ${o.post_op_checklist_ok ? 'badge-success' : 'badge-warning'}">Post-Op: ${o.post_op_checklist_ok ? 'PASS' : 'PENDING'}</span>
        </td>
        <td>
          <button class="btn btn-sm btn-secondary" onclick="window.hmsOtChecklistModal(${o.ot_id})">Checklist</button>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(`Failed to load OT schedules: ${err.message}`, "danger");
  }
}

