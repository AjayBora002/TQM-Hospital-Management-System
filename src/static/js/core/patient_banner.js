/**
 * patient_banner.js -- Persistent Patient Context Banner Manager
 * Stays visible across modules when a patient is active.
 */
import { store } from "./store.js";

export function initPatientBanner() {
  const bannerEl = document.getElementById("patientContextBanner");
  if (!bannerEl) return;

  store.subscribe((key, val) => {
    if (key === "patient") {
      renderPatientBanner(bannerEl, val);
    }
  });

  // Attach quick action handlers
  bannerEl.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-banner-action]");
    if (!btn) return;
    const action = btn.dataset.bannerAction;
    const patient = store.currentPatient;
    if (!patient) return;

    if (action === "clear") {
      store.clearCurrentPatient();
      return;
    }

    window.dispatchEvent(new CustomEvent("hms:patient-quick-action", {
      detail: { action, patient }
    }));
  });
}

function renderPatientBanner(bannerEl, patient) {
  if (!patient) {
    bannerEl.classList.add("hidden");
    return;
  }

  bannerEl.classList.remove("hidden");

  const initials = (patient.full_name || "P")
    .split(" ")
    .map(n => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  const dobYear = patient.dob ? new Date(patient.dob).getFullYear() : 1995;
  const age = new Date().getFullYear() - dobYear;
  const uhid = patient.uhid || `UHID-2026-${String(patient.patient_id).padStart(4, "0")}`;
  const allergies = (patient.allergies || "None").trim();
  const hasAllergy = allergies.toLowerCase() !== "none" && allergies.length > 0;
  const location = patient.room_number ? `Bed: ${patient.room_number}` : "Outpatient";

  bannerEl.innerHTML = `
    <div class="patient-banner-info">
      <div class="patient-avatar-mini">${initials}</div>
      <div class="patient-name-uhid">
        <span class="patient-banner-name">${escapeHtml(patient.full_name)}</span>
        <span class="patient-banner-uhid">${uhid}</span>
      </div>
      <div class="patient-banner-demographics">
        <span>${age}y / ${patient.gender || 'Unknown'}</span>
        <span class="badge badge-neutral">${patient.blood_group || 'O+'}</span>
        <span class="patient-banner-location">${location}</span>
        ${hasAllergy ? `
          <span class="allergy-alert-pill" title="Known Drug/Latex Allergies">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"></polygon><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
            ALLERGY: ${escapeHtml(allergies)}
          </span>
        ` : ''}
      </div>
    </div>
    <div class="patient-banner-actions">
      <button class="banner-action-btn" data-banner-action="consultation">Consultation</button>
      <button class="banner-action-btn" data-banner-action="prescribe">Prescribe</button>
      <button class="banner-action-btn" data-banner-action="order-lab">Order Lab</button>
      <button class="banner-action-btn" data-banner-action="admit">Admit</button>
      <button class="banner-action-btn" data-banner-action="bill">Bill</button>
      <button class="banner-action-btn" data-banner-action="timeline">360° EMR</button>
      <button class="banner-clear-btn" data-banner-action="clear" title="Clear Patient Context">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>
    </div>
  `;
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str).replace(/[&<>"']/g, m => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));
}
