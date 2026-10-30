/**
 * pharmacy.js -- Pharmacy & Dispensary Domain Module
 * Prescription Dispensing with Allergy Poka-Yoke, Medicine Stock, Batch/Expiry Alerts,
 * Purchase Orders, and General Store Consumables.
 */
import { api } from "../core/api.js";
import { showToast, openModal, closeModal } from "../core/ui.js";

export async function loadPrescriptions() {
  try {
    const list = await api.get("/prescriptions");
    const tbody = document.getElementById("prescriptionsTableBody");
    if (!tbody) return;

    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:24px;color:#94a3b8;">No prescriptions recorded.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(rx => `
      <tr>
        <td>#RX-${String(rx.prescription_id).padStart(4, "0")}</td>
        <td><strong>${rx.patient_name || `Patient #${rx.patient_id}`}</strong></td>
        <td>${rx.doctor_name || `Doctor #${rx.doctor_id}`}</td>
        <td><strong>${rx.medicine_name}</strong></td>
        <td>${rx.dosage} (${rx.frequency})</td>
        <td>${rx.duration_days} days</td>
        <td><span class="badge ${rx.status === 'Dispensed' ? 'badge-success' : rx.status === 'Completed' ? 'badge-info' : 'badge-warning'}">${rx.status}</span></td>
        <td>
          ${rx.status === 'Active' ? `
            <button class="btn btn-sm btn-primary" onclick="window.hmsDispenseRxModal(${rx.prescription_id}, '${rx.medicine_name}', ${rx.patient_id})">Dispense</button>
          ` : `
            <span style="font-size:12px;color:#94a3b8;">Dispensed</span>
          `}
        </td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(`Failed to load prescriptions: ${err.message}`, "danger");
  }
}

export async function loadMedicines() {
  try {
    const list = await api.get("/medicines");
    const tbody = document.getElementById("medicinesTableBody");
    if (!tbody) return;

    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:24px;color:#94a3b8;">No medicines in inventory.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(m => {
      const isLowStock = m.stock_qty <= m.reorder_level;
      const isExpired = new Date(m.expiry_date) < new Date();

      return `
        <tr>
          <td><span style="font-family:monospace;font-weight:600;color:#0284c7;">${m.batch_no}</span></td>
          <td><strong>${m.name}</strong></td>
          <td>${m.category}</td>
          <td>
            <strong style="color:${isLowStock ? '#ef4444' : '#0f172a'};">${m.stock_qty}</strong>
            ${isLowStock ? '<span class="badge badge-danger" style="margin-left:4px;">LOW</span>' : ''}
          </td>
          <td>Rs. ${m.unit_price.toFixed(2)}</td>
          <td>
            <span style="${isExpired ? 'color:#ef4444;font-weight:bold;' : ''}">${m.expiry_date}</span>
            ${isExpired ? '<span class="badge badge-danger" style="margin-left:4px;">EXPIRED</span>' : ''}
          </td>
          <td>${m.reorder_level}</td>
          <td>
            <button class="btn btn-sm btn-secondary" onclick="window.hmsEditMedicineModal(${m.medicine_id})">Edit</button>
          </td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    showToast(`Failed to load medicines: ${err.message}`, "danger");
  }
}

export async function loadPurchaseOrders() {
  try {
    const list = await api.get("/purchase-orders");
    const tbody = document.getElementById("poTableBody");
    if (!tbody) return;

    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;padding:24px;color:#94a3b8;">No purchase orders.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(po => `
      <tr>
        <td>#PO-${String(po.po_id).padStart(4, "0")}</td>
        <td><strong>${po.medicine_name}</strong></td>
        <td>${po.supplier_name}</td>
        <td>${po.order_qty} units</td>
        <td>Rs. ${po.unit_cost.toFixed(2)}</td>
        <td><strong>Rs. ${po.total_cost.toFixed(2)}</strong></td>
        <td><span class="badge ${po.status === 'Received' ? 'badge-success' : 'badge-warning'}">${po.status}</span></td>
        <td>
          ${po.status === 'Pending' ? `
            <button class="btn btn-sm btn-success" onclick="window.hmsReceivePo(${po.po_id})">Receive</button>
          ` : `<span style="font-size:12px;color:#94a3b8;">Stocked</span>`}
        </td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(`Failed to load purchase orders: ${err.message}`, "danger");
  }
}

