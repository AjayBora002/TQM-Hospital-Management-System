/**
 * main.js -- ES Module Bootstrap for HMS
 * Initialises the session/auth state from core/auth.js and exposes
 * the domain modules so app.js (which runs as a classic script in the
 * same page) can use their exports via window.hmsModules.
 *
 * Load order in index.html:
 *   1. <script type="module" src="js/main.js">  (this file)
 *   2. <script src="js/app.js">                 (classic, global)
 *
 * Because type="module" is deferred by default, app.js runs first.
 * We therefore attach the module exports to window.hmsModules so that
 * app.js tab-switch handlers can call into them at runtime (lazy).
 */

import { api } from "./core/api.js";
import { auth } from "./core/auth.js";
import { store } from "./core/store.js";
import { showToast, openModal, closeModal } from "./core/ui.js";
import { initPatientBanner } from "./core/patient_banner.js";

// Domain modules
import * as adminMod   from "./modules/admin.js";
import * as clinicalMod from "./modules/clinical.js";
import * as diagMod    from "./modules/diagnostics.js";
import * as financeMod from "./modules/finance.js";
import * as frontMod   from "./modules/front_office.js";
import * as inpatientMod from "./modules/inpatient.js";
import * as portalMod  from "./modules/patient_portal.js";
import * as peopleMod  from "./modules/people.js";
import * as pharmacyMod from "./modules/pharmacy.js";
import * as qualityMod from "./modules/quality.js";
import * as supportMod from "./modules/support.js";

// Expose to global scope so app.js classic script can access
window.hmsModules = {
  api,
  store,
  showToast,
  openModal,
  closeModal,
  initPatientBanner,
  admin:       adminMod,
  clinical:    clinicalMod,
  diagnostics: diagMod,
  finance:     financeMod,
  front_office: frontMod,
  inpatient:   inpatientMod,
  patient_portal: portalMod,
  people:      peopleMod,
  pharmacy:    pharmacyMod,
  quality:     qualityMod,
  support:     supportMod,
};

// Initialize auth manager (reads /api/auth/me, starts idle timer)
window.hmsAuth = auth;

// On DOMContentLoaded (or immediately if already loaded), hydrate the topbar
// with the live session data from /api/auth/me
async function hydrateTopbar() {
  try {
    const ok = await auth.init();
    if (!ok) {
      // Session is gone — redirect to login
      window.location.replace("/login");
      return;
    }

    // Update topbar user info using the authoritative server data
    const userNameEl  = document.getElementById("topbarUserName");
    const userRoleEl  = document.getElementById("topbarUserRole");
    const userAvatarEl = document.getElementById("topbarUserAvatar");

    if (auth.user) {
      const shortName = (auth.user.full_name || auth.user.username || "").split(" ").slice(0, 2).join(" ");
      if (userNameEl)   userNameEl.textContent  = shortName;
      if (userRoleEl)   userRoleEl.textContent  = auth.role || "";
      if (userAvatarEl) userAvatarEl.textContent = shortName.charAt(0).toUpperCase();
    }

    // Push permissions into a globally readable location for app.js
    window.hmsPermissions = auth.permissions;
    window.hmsRole        = auth.role;
    window.hmsUser        = auth.user;

    // Fire a custom event so app.js (classic) can react
    document.dispatchEvent(new CustomEvent("hms:auth:ready", {
      detail: { user: auth.user, role: auth.role, permissions: auth.permissions }
    }));
  } catch (err) {
    console.warn("[HMS main.js] Auth hydration error:", err);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", hydrateTopbar);
} else {
  hydrateTopbar();
}
