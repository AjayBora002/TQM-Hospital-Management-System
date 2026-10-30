/**
 * quality.js -- Quality & Governance Domain Module
 * NABH/ISO Quality Audits, Incident Reporting & CAPA,
 * Defect Checksheet, Pareto Analysis, and Six Sigma Metrics.
 */
import { api } from "../core/api.js";
import { showToast, openModal, closeModal } from "../core/ui.js";

export async function loadQualityAudits() {
  try {
    const list = await api.get("/quality-audits");
    const tbody = document.getElementById("qualityAuditsTableBody");
    if (!tbody) return;

    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:#94a3b8;">No quality audits recorded.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(a => `
      <tr>
        <td><strong>${a.standard_code}</strong></td>
        <td><strong>${a.department}</strong></td>
        <td>${a.criterion}</td>
        <td><strong>${a.score}</strong> / ${a.max_score}</td>
        <td><span class="badge ${a.compliance_status === 'Compliant' ? 'badge-success' : 'badge-danger'}">${a.compliance_status}</span></td>
        <td>${a.audited_by} (${a.audit_date})</td>
        <td><span style="font-size:12px;color:#64748b;">${a.corrective_action || 'None required'}</span></td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(`Failed to load quality audits: ${err.message}`, "danger");
  }
}

export async function loadQualityIncidents() {
  try {
    const list = await api.get("/governance/incidents");
    const tbody = document.getElementById("incidentsTableBody");
    if (!tbody) return;

    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:#94a3b8;">No clinical quality incidents reported.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(i => `
      <tr>
        <td>#INC-${String(i.incident_id).padStart(4, "0")}</td>
        <td><strong>${i.incident_type}</strong></td>
        <td>${i.department}</td>
        <td><span class="badge ${i.severity === 'Sentinel Event' ? 'badge-danger' : i.severity === 'Near Miss' ? 'badge-warning' : 'badge-neutral'}">${i.severity}</span></td>
        <td>${i.description}</td>
        <td><span class="badge ${i.status === 'CAPA Initiated' || i.status === 'Closed' ? 'badge-success' : 'badge-danger'}">${i.status}</span></td>
        <td>
          ${!i.capa_id ? `
            <button class="btn btn-sm btn-primary" onclick="window.hmsOpenCapaModal(${i.incident_id})">Initiate CAPA</button>
          ` : `
            <span style="font-size:12px;color:#0284c7;font-weight:600;">CAPA Active</span>
          `}
        </td>
      </tr>
    `).join("");
  } catch (err) {
    showToast(`Failed to load quality incidents: ${err.message}`, "danger");
  }
}

export async function loadSixSigmaMetrics() {
  try {
    const data = await api.get("/tqm/six-sigma");
    const container = document.getElementById("sixSigmaWidgetContainer");
    if (!container) return;

    container.innerHTML = `
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon" style="background:#e0f2fe;color:#0284c7;">σ</div>
          <div class="stat-content">
            <div class="stat-value">${data.current_sigma_level || '4.2'} σ</div>
            <div class="stat-label">System Sigma Level</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background:#ecfdf5;color:#10b981;">%</div>
          <div class="stat-content">
            <div class="stat-value">${data.process_yield_percent || '99.2'}%</div>
            <div class="stat-label">Process Yield (Poka-Yoke)</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background:#fffbeb;color:#f59e0b;">!</div>
          <div class="stat-content">
            <div class="stat-value">${data.dpmo ? Math.round(data.dpmo) : 230}</div>
            <div class="stat-label">Defects Per Million (DPMO)</div>
          </div>
        </div>
      </div>
    `;
  } catch (err) {
    console.error("Six Sigma load error", err);
  }
}

