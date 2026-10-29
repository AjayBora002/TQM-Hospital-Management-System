/**
 * auth.js -- Client-side Session State and Permission Evaluation
 */
import { api } from "./api.js";

class AuthManager {
  constructor() {
    this.user = null;
    this.role = null;
    this.permissions = {};
    this.authenticated = false;
    this.idleTimer = null;
    this.warningTimer = null;
    this.timeoutSeconds = 900; // 15 mins
  }

  async init() {
    try {
      const data = await api.get("/auth/me");
      if (data.authenticated && data.user) {
        this.user = data.user;
        this.role = data.role;
        this.permissions = data.permissions || {};
        this.authenticated = true;
        this.timeoutSeconds = data.idle_timeout_seconds || 900;
        this.resetIdleTimer();
        this.setupActivityListeners();
        return true;
      }
      this.authenticated = false;
      return false;
    } catch {
      this.authenticated = false;
      return false;
    }
  }

  async login(username, password) {
    const data = await api.post("/auth/login", { username, password });
    this.user = data.user;
    this.role = data.user.role;
    this.permissions = data.permissions || {};
    this.authenticated = true;
    this.timeoutSeconds = data.timeout_seconds || 900;
    this.resetIdleTimer();
    this.setupActivityListeners();
    return data;
  }

  async logout() {
    try {
      await api.post("/auth/logout", {});
    } finally {
      this.user = null;
      this.role = null;
      this.permissions = {};
      this.authenticated = false;
      if (this.idleTimer) clearTimeout(this.idleTimer);
      if (this.warningTimer) clearTimeout(this.warningTimer);
      window.location.href = "/login";
    }
  }

  async changePassword(currentPassword, newPassword) {
    return await api.post("/auth/change-password", {
      current_password: currentPassword,
      new_password: newPassword
    });
  }

  hasPermission(module, action = "view") {
    if (!this.role || !this.permissions) return false;
    // Hard restriction: Admin cannot edit clinical records
    if (this.role === "Admin" && module === "clinical" && ["create", "edit", "delete"].includes(action)) {
      return false;
    }
    const moduleActions = this.permissions[module] || [];
    return moduleActions.includes(action);
  }

  resetIdleTimer() {
    if (this.idleTimer) clearTimeout(this.idleTimer);
    if (this.warningTimer) clearTimeout(this.warningTimer);

    // Warning at 13 minutes (2 minutes before timeout)
    const warnMs = Math.max((this.timeoutSeconds - 120) * 1000, 30000);
    this.warningTimer = setTimeout(() => {
      window.dispatchEvent(new CustomEvent("hms:idle-warning", {
        detail: { minutesRemaining: 2 }
      }));
    }, warnMs);

    // Hard timeout at 15 minutes
    this.idleTimer = setTimeout(() => {
      this.logout();
    }, this.timeoutSeconds * 1000);
  }

  setupActivityListeners() {
    const events = ["mousedown", "keydown", "scroll", "touchstart"];
    const throttledReset = this.throttle(() => this.resetIdleTimer(), 10000);
    events.forEach(e => window.addEventListener(e, throttledReset, { passive: true }));
  }

  throttle(fn, limit) {
    let lastRan = 0;
    return function(...args) {
      const now = Date.now();
      if (now - lastRan >= limit) {
        fn.apply(this, args);
        lastRan = now;
      }
    };
  }
}

export const auth = new AuthManager();
