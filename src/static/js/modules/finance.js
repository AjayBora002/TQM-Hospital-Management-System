/**
 * finance.js -- Finance & Revenue Cycle Domain Module
 * Invoicing & Billing, Advance Deposits, and Insurance/TPA Claims Desk.
 */
import { api } from "../core/api.js";
import { showToast, openModal, closeModal, printDocument } from "../core/ui.js";

export async function loadBills() {
  try {
    const list = await api.get("/bills");
    const tbody = document.getElementById("billsTableBody");
    if (!tbody) return;

    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:24px;color:#94a3b8;">No invoices found.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(b => `
      <tr>
        <td>#INV-${String(b.bill_id).padStart(4, "0")}</td>
        <td><strong>${b.patient_name || `Patient #${b.patient_id}`}</strong></td>
        <td>Rs. ${b.room_charges.toFixed(2)}</td>
        <td>Rs. ${b.consultation_charges.toFixed(2)}</td>
        <td>Rs. ${b.medicine_charges.toFixed(2)}</td>
        <td><strong style="color:#0284c7;font-size:15px;">Rs. ${b.total_amount.toFixed(2)}</strong></td>
        <td><span class="badge ${b.payment_status === 'Paid' ? 'badge-success' : 'badge-danger'}">${b.payment_status}</span></td>
        <td>
          <div style="display:flex;gap:4px;">
            <button class="btn btn-sm btn-secondary" onclick="window.hmsPrintReceipt(${b.bill_id})">Receipt</button>
            ${b.payment_status !== 'Paid' ? `
              <button class="btn btn-sm btn-success" onclick="window.hmsMarkPaid(${b.bill_id})">Pay</button>
            ` : ''}
          </div>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(`Failed to load bills: ${err.message}`, "danger");
  }
}

export async function loadInsuranceClaims() {
  try {
    const list = await api.get("/finance/insurance-claims");
    const tbody = document.getElementById("insuranceTableBody");
    if (!tbody) return;

    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:24px;color:#94a3b8;">No insurance claims filed.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(c => `
      <tr>
        <td>#CLM-${String(c.claim_id).padStart(4, "0")}</td>
        <td><strong>${c.patient_name}</strong></td>
        <td><strong>${c.tpa_name}</strong></td>
        <td><span style="font-family:monospace;font-size:12px;">${c.policy_number}</span></td>
        <td>Rs. ${c.claim_amount.toFixed(2)}</td>
        <td><strong>Rs. ${c.approved_amount ? c.approved_amount.toFixed(2) : '0.00'}</strong></td>
        <td><span class="badge ${c.pre_auth_status === 'Approved' ? 'badge-success' : 'badge-warning'}">${c.pre_auth_status}</span></td>
        <td><span class="badge ${c.claim_status === 'Settled' ? 'badge-success' : 'badge-info'}">${c.claim_status}</span></td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(`Failed to load insurance claims: ${err.message}`, "danger");
  }
}
