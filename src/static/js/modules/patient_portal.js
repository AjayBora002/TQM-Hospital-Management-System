/**
 * patient_portal.js -- Patient Self-Service Portal Module
 * Strict row-level isolation: Views only the authenticated patient's records.
 */
import { api } from "../core/api.js";
import { showToast, printDocument } from "../core/ui.js";

export async function loadPatientPortalDashboard() {
  try {
    const profile = await api.get("/patient-portal/profile");
    const container = document.getElementById("patientPortalContainer");
    if (!container) return;

    const [appts, rxs, bills, labs] = await Promise.all([
      api.get("/patient-portal/appointments"),
      api.get("/patient-portal/prescriptions"),
      api.get("/patient-portal/bills"),
      api.get("/patient-portal/lab-reports")
    ]);

    container.innerHTML = `
      <div style="background:#f0f9ff;border:1px solid #bae6fd;padding:20px;border-radius:10px;margin-bottom:24px;">
        <h2 style="margin:0 0 6px 0;color:#0369a1;">Welcome, ${profile.full_name}</h2>
        <div style="font-size:14px;color:#0284c7;">
          UHID: <strong>UHID-2026-${String(profile.patient_id).padStart(4, "0")}</strong> | 
          Blood Group: <strong>${profile.blood_group}</strong> | 
          Phone: ${profile.phone}
        </div>
      </div>

      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(320px, 1fr));gap:20px;">
        <!-- My Appointments -->
        <div class="card">
          <h3 class="card-title">My Appointments (${appts.length})</h3>
          ${appts.length === 0 ? '<p style="color:#94a3b8;font-size:13px;">No scheduled appointments.</p>' : appts.map(a => `
            <div style="padding:10px 0;border-bottom:1px solid #e2e8f0;display:flex;justify-content:space-between;align-items:center;">
              <div>
                <strong>${a.doctor_name}</strong> (${a.department})
                <div style="font-size:12px;color:#64748b;">${a.appt_date} at ${a.appt_time}</div>
              </div>
              <span class="badge ${a.status === 'Completed' ? 'badge-success' : 'badge-info'}">${a.status}</span>
            </div>
          `).join("")}
        </div>

        <!-- My Prescriptions -->
        <div class="card">
          <h3 class="card-title">My Prescriptions (${rxs.length})</h3>
          ${rxs.length === 0 ? '<p style="color:#94a3b8;font-size:13px;">No active prescriptions.</p>' : rxs.map(rx => `
            <div style="padding:10px 0;border-bottom:1px solid #e2e8f0;">
              <div style="display:flex;justify-content:space-between;">
                <strong>${rx.medicine_name}</strong>
                <span class="badge ${rx.status === 'Dispensed' ? 'badge-success' : 'badge-warning'}">${rx.status}</span>
              </div>
              <div style="font-size:13px;color:#475569;margin-top:2px;">Dosage: ${rx.dosage} (${rx.frequency}) for ${rx.duration_days} days</div>
              <div style="font-size:12px;color:#94a3b8;">Prescribed by ${rx.doctor_name} on ${rx.prescribed_date}</div>
            </div>
          `).join("")}
        </div>

        <!-- My Invoices & Bills -->
        <div class="card">
          <h3 class="card-title">My Bills & Receipts (${bills.length})</h3>
          ${bills.length === 0 ? '<p style="color:#94a3b8;font-size:13px;">No invoices found.</p>' : bills.map(b => `
            <div style="padding:10px 0;border-bottom:1px solid #e2e8f0;display:flex;justify-content:space-between;align-items:center;">
              <div>
                <strong>Invoice #INV-${String(b.bill_id).padStart(4, "0")}</strong>
                <div style="font-size:12px;color:#64748b;">Date: ${b.created_at}</div>
              </div>
              <div style="text-align:right;">
                <div style="font-weight:bold;color:#0284c7;">Rs. ${b.total_amount.toFixed(2)}</div>
                <span class="badge ${b.payment_status === 'Paid' ? 'badge-success' : 'badge-danger'}">${b.payment_status}</span>
              </div>
            </div>
          `).join("")}
        </div>

        <!-- My Diagnostic Lab Reports -->
        <div class="card">
          <h3 class="card-title">My Lab Reports (${labs.length})</h3>
          ${labs.length === 0 ? '<p style="color:#94a3b8;font-size:13px;">No released lab reports.</p>' : labs.map(l => `
            <div style="padding:10px 0;border-bottom:1px solid #e2e8f0;display:flex;justify-content:space-between;align-items:center;">
              <div>
                <strong>${l.test_name}</strong> (${l.category})
                <div style="font-size:13px;color:#0284c7;font-weight:600;">Result: ${l.result_value} ${l.unit}</div>
                <div style="font-size:11px;color:#64748b;">Ref range: ${l.ref_min} - ${l.ref_max} ${l.unit}</div>
              </div>
              <span class="badge ${l.abnormal_flag ? 'badge-danger' : 'badge-success'}">${l.abnormal_flag ? 'ABNORMAL' : 'NORMAL'}</span>
            </div>
          `).join("")}
        </div>
      </div>
    `;
  } catch (err) {
    showToast(`Failed to load patient portal: ${err.message}`, "danger");
  }
}

