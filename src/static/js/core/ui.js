/**
 * ui.js -- UI Helpers, Toasts, Modals, Breadcrumbs, and Print Helpers
 */

export function showToast(message, type = "info", duration = 4000) {
  let container = document.getElementById("toastContainer");
  if (!container) {
    container = document.createElement("div");
    container.id = "toastContainer";
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <div style="flex:1;">${message}</div>
    <button style="background:transparent;border:none;cursor:pointer;color:#94a3b8;font-size:14px;">&times;</button>
  `;

  toast.querySelector("button").onclick = () => toast.remove();

  container.appendChild(toast);
  setTimeout(() => {
    if (toast.parentElement) toast.remove();
  }, duration);
}

export function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add("open");
    // Auto-focus first input
    const firstInput = modal.querySelector("input:not([type=hidden]), select, textarea");
    if (firstInput) firstInput.focus();
  }
}

export function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove("open");
  }
}

export function updateBreadcrumbs(section, subsection) {
  const container = document.getElementById("breadcrumbsContainer");
  if (!container) return;

  container.innerHTML = `
    <span class="breadcrumb-item">Hospital</span>
    <span class="breadcrumb-separator">/</span>
    <span class="breadcrumb-item">${section}</span>
    ${subsection ? `
      <span class="breadcrumb-separator">/</span>
      <span class="breadcrumb-active">${subsection}</span>
    ` : ""}
  `;
}

export function setupGlobalSearch(onSelectPatient) {
  const searchInput = document.getElementById("globalSearchInput");
  const searchModal = document.getElementById("globalSearchModal");
  const resultsContainer = document.getElementById("globalSearchResults");

  // Pressing '/' opens global search
  window.addEventListener("keydown", (e) => {
    if (e.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) {
      e.preventDefault();
      openModal("globalSearchModal");
      if (searchInput) searchInput.focus();
    } else if (e.key === "Escape") {
      closeModal("globalSearchModal");
    }
  });

  if (searchInput && resultsContainer) {
    let debounceTimer;
    searchInput.addEventListener("input", () => {
      clearTimeout(debounceTimer);
      const query = searchInput.value.trim();
      if (query.length < 1) {
        resultsContainer.innerHTML = '<div style="padding:16px;color:#94a3b8;text-align:center;">Type patient name, phone, or UHID to search</div>';
        return;
      }

      debounceTimer = setTimeout(async () => {
        try {
          const res = await fetch(`/api/patients?q=${encodeURIComponent(query)}`);
          const patients = await res.json();
          if (!patients || patients.length === 0) {
            resultsContainer.innerHTML = '<div style="padding:16px;color:#94a3b8;text-align:center;">No matching patients found.</div>';
            return;
          }

          resultsContainer.innerHTML = patients.slice(0, 6).map(p => `
            <div class="search-result-row" data-patient-id="${p.patient_id}" style="padding:10px 14px;border-bottom:1px solid #e2e8f0;cursor:pointer;display:flex;justify-content:space-between;align-items:center;">
              <div>
                <strong>${p.full_name}</strong> <span style="font-size:12px;color:#64748b;">(${p.gender}, ${p.blood_group})</span>
                <div style="font-size:12px;color:#94a3b8;">Phone: ${p.phone} | UHID-2026-${String(p.patient_id).padStart(4, "0")}</div>
              </div>
              <button class="btn btn-sm btn-secondary">Select</button>
            </div>
          `).join("");

          resultsContainer.querySelectorAll(".search-result-row").forEach(row => {
            row.onclick = () => {
              const pid = parseInt(row.dataset.patientId);
              const selected = patients.find(p => p.patient_id === pid);
              if (selected && onSelectPatient) {
                onSelectPatient(selected);
              }
              closeModal("globalSearchModal");
            };
          });
        } catch (err) {
          console.error("Search error", err);
        }
      }, 250);
    });
  }
}

export function printDocument(title, htmlContent) {
  const printWindow = window.open("", "_blank");
  printWindow.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>${title}</title>
      <link rel="stylesheet" href="/static/css/tokens.css">
      <link rel="stylesheet" href="/static/css/layout.css">
      <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; padding: 24px; color: #000; }
        .print-header { border-bottom: 2px solid #0284c7; padding-bottom: 12px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
        .print-title { font-size: 20px; font-weight: bold; color: #0284c7; }
        .meta-box { background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px; border-radius: 6px; margin-bottom: 16px; }
        table { width: 100%; border-collapse: collapse; margin-top: 16px; }
        th, td { border: 1px solid #cbd5e1; padding: 8px 12px; text-align: left; }
        th { background: #f1f5f9; }
        .footer-sign { margin-top: 40px; display: flex; justify-content: space-between; }
      </style>
    </head>
    <body onload="window.print();">
      ${htmlContent}
    </body>
    </html>
  `);
  printWindow.document.close();
}
