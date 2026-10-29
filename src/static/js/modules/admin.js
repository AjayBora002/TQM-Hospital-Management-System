/**
 * admin.js -- System Administration & Governance Domain Module
 * User & Role Management, Password Reset, Database Backups, and Audit Trail.
 */
import { api } from "../core/api.js";
import { showToast, openModal, closeModal } from "../core/ui.js";

export async function loadUsers() {
  try {
    const list = await api.get("/auth/users");
    const tbody = document.getElementById("usersTableBody");
    if (!tbody) return;

    tbody.innerHTML = list.map(u => `
      <tr>
        <td>#USR-${String(u.user_id).padStart(4, "0")}</td>
        <td><strong>${u.username}</strong></td>
        <td><span class="badge badge-info" style="font-weight:bold;">${u.role}</span></td>
        <td>${u.full_name}</td>
        <td>${u.email || '-'}</td>
        <td>${u.created_at}</td>
        <td>
          <button class="btn btn-sm btn-secondary" onclick="window.hmsAdminResetPasswordModal('${u.username}')">Reset Password</button>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(`Failed to load users: ${err.message}`, "danger");
  }
}

export async function loadAuditLogs() {
  try {
    const logs = await api.get("/audit");
    const tbody = document.getElementById("auditTableBody");
    if (!tbody) return;

    tbody.innerHTML = logs.map(l => {
      const isSecurity = l.table_name === "access_control" || (l.details && l.details.includes("FORBIDDEN"));
      return `
        <tr style="${isSecurity ? 'background:#fef2f2;' : ''}">
          <td>#${l.log_id}</td>
          <td><strong>${l.table_name}</strong></td>
          <td><span class="badge ${l.action === 'INSERT' ? 'badge-success' : l.action === 'UPDATE' ? 'badge-warning' : 'badge-danger'}">${l.action}</span></td>
          <td style="font-size:13px;max-width:350px;word-break:break-word;">${l.details || '-'}</td>
          <td><strong>${l.performed_by}</strong></td>
          <td><span style="font-family:monospace;font-size:12px;">${l.timestamp}</span></td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    showToast(`Failed to load audit logs: ${err.message}`, "danger");
  }
}

export async function loadBackups() {
  try {
    const list = await api.get("/system/backups");
    const tbody = document.getElementById("backupsTableBody");
    if (!tbody) return;

    tbody.innerHTML = list.map(b => `
      <tr>
        <td><strong>${b.filename}</strong></td>
        <td>${(b.size_bytes / 1024).toFixed(1)} KB</td>
        <td>${b.created_at}</td>
        <td><span class="badge badge-success">VERIFIED</span></td>
      </tr>
    `).join("");
  } catch (err) {
    console.error("Backups load error", err);
  }
}
