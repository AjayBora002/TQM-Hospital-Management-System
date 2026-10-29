/**
 * store.js -- Central Application State Store
 */

class Store {
  constructor() {
    this.currentPatient = null;
    this.activeModule = "dashboard";
    this.notifications = [];
    this.recentPatients = [];
    this.listeners = new Set();
  }

  setCurrentPatient(patient) {
    this.currentPatient = patient;
    if (patient) {
      this.addRecentPatient(patient);
    }
    this.notify("patient", this.currentPatient);
  }

  clearCurrentPatient() {
    this.currentPatient = null;
    this.notify("patient", null);
  }

  addRecentPatient(patient) {
    this.recentPatients = [
      patient,
      ...this.recentPatients.filter(p => p.patient_id !== patient.patient_id)
    ].slice(0, 8);
    this.notify("recentPatients", this.recentPatients);
  }

  setActiveModule(moduleName) {
    this.activeModule = moduleName;
    this.notify("module", this.activeModule);
  }

  setNotifications(notifications) {
    this.notifications = notifications;
    this.notify("notifications", this.notifications);
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  notify(key, value) {
    this.listeners.forEach(cb => {
      try {
        cb(key, value);
      } catch (err) {
        console.error("[Store listener error]", err);
      }
    });
  }
}

export const store = new Store();
