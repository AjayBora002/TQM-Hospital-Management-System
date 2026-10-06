/**
 * Hospital Management System (HMS) - Client SPA Application Logic
 * Quality Goal: Q07 - Improve Data Accuracy
 */

let currentTab = 'dashboard';
let pendingModalAction = null;

// Toast notification handler
function showToast(msg, isError = false) {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toastMsg');
    const toastIcon = document.getElementById('toastIcon');
    toastMsg.innerText = msg;
    toastIcon.innerText = isError ? '✕' : '✓';
    toast.className = isError ? 'show toast-error' : 'show toast-success';
    setTimeout(() => { toast.className = ''; }, 3200);
}

// Q07 Modal Dialog Trigger
function openConfirmModal(title, message, onConfirm) {
    document.getElementById('modalTitle').innerText = title;
    document.getElementById('modalMessage').innerText = message;
    pendingModalAction = onConfirm;
    document.getElementById('confirmModal').classList.add('show');
}

function closeModal() {
    document.getElementById('confirmModal').classList.remove('show');
    pendingModalAction = null;
}

document.getElementById('modalConfirmBtn').addEventListener('click', () => {
    if (pendingModalAction) {
        pendingModalAction();
    }
    closeModal();
});

// Tab Switching
function switchTab(tabId) {
    currentTab = tabId;
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));

    const targetPanel = document.getElementById(`tab-${tabId}`);
    if (targetPanel) targetPanel.classList.add('active');

    const navTabs = document.querySelectorAll('.nav-tab');
    navTabs.forEach(b => {
        if (b.getAttribute('onclick').includes(tabId)) {
            b.classList.add('active');
        }
    });

    // Lazy data refreshes
    if (tabId === 'dashboard') loadDashboardData();
    if (tabId === 'patients') { loadPatients(); loadRoomChoices(); }
    if (tabId === 'doctors') loadDoctors();
    if (tabId === 'appointments') { loadAppointments(); loadDoctorChoices(); }
    if (tabId === 'rooms') loadRooms();
    if (tabId === 'staff') loadStaff();
    if (tabId === 'pharmacy') loadMedicines();
    if (tabId === 'billing') loadBills();
    if (tabId === 'audit') loadAuditLogs();
    if (tabId === 'defects') loadDefects();
}

// Q07 Feature: Input Masking for Phone (+91-XXXXX-XXXXX)
function setupPhoneMasking() {
    document.querySelectorAll('.phone-mask').forEach(input => {
        input.addEventListener('input', (e) => {
            let digits = e.target.value.replace(/\\D/g, '');
            if (digits.startsWith('91')) {
                digits = digits.substring(2);
            }
            digits = digits.substring(0, 10);
            if (digits.length === 0) {
                e.target.value = '';
            } else if (digits.length <= 5) {
                e.target.value = `+91-${digits}`;
            } else {
                e.target.value = `+91-${digits.substring(0, 5)}-${digits.substring(5)}`;
            }
        });
    });
}

// Q07 Feature: Auto-Complete helper
function setupAutocomplete(inputEl, boxEl, fetchUrl, onSelect) {
    inputEl.addEventListener('input', async (e) => {
        const val = e.target.value.trim();
        if (val.length < 1) {
            boxEl.style.display = 'none';
            return;
        }
        try {
            const res = await fetch(`${fetchUrl}?prefix=${encodeURIComponent(val)}`);
            const items = await res.json();
            if (!items || items.length === 0) {
                boxEl.style.display = 'none';
                return;
            }
            boxEl.innerHTML = '';
            items.forEach(it => {
                const div = document.createElement('div');
                div.className = 'autocomplete-item';
                div.innerText = it.label || it;
                div.addEventListener('click', () => {
                    inputEl.value = it.label || it;
                    boxEl.style.display = 'none';
                    onSelect(it);
                });
                boxEl.appendChild(div);
            });
            boxEl.style.display = 'block';
        } catch (err) {
            boxEl.style.display = 'none';
        }
    });

    document.addEventListener('click', (e) => {
        if (e.target !== inputEl && e.target !== boxEl) {
            boxEl.style.display = 'none';
        }
    });
}

// --- DASHBOARD API ---
async function loadDashboardData() {
    try {
        const res = await fetch('/api/dashboard/stats');
        const stats = await res.json();
        document.getElementById('stat-patients').innerText = stats.total_patients;
        document.getElementById('stat-doctors').innerText = stats.total_doctors;
        document.getElementById('stat-appointments').innerText = stats.scheduled_appts;
        document.getElementById('stat-rooms').innerText = stats.available_rooms;
        document.getElementById('stat-low-stock').innerText = stats.low_stock_meds;
        document.getElementById('stat-revenue').innerText = `₹${stats.total_revenue.toLocaleString('en-IN')}`;

        const tbody = document.getElementById('dashboard-audit-body');
        if (stats.recent_audit.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No audit records found</td></tr>';
        } else {
            tbody.innerHTML = stats.recent_audit.slice(0, 8).map(a => `
                <tr>
                    <td>#${a.log_id}</td>
                    <td>${a.timestamp}</td>
                    <td><code>${a.table_name}</code></td>
                    <td><span class="badge ${a.action === 'INSERT' ? 'badge-success' : a.action === 'UPDATE' ? 'badge-warning' : 'badge-danger'}">${a.action}</span></td>
                    <td>${a.details || '-'}</td>
                    <td>${a.performed_by}</td>
                </tr>
            `).join('');
        }
    } catch (err) {
        console.error(err);
    }
}

// --- PATIENTS API ---
async function loadPatients(query = '') {
    try {
        const res = await fetch(`/api/patients?q=${encodeURIComponent(query)}`);
        const data = await res.json();
        const tbody = document.getElementById('patients-table-body');
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No patients found.</td></tr>';
            return;
        }
        tbody.innerHTML = data.map(p => `
            <tr>
                <td><strong>#${p.patient_id}</strong></td>
                <td>${p.full_name}</td>
                <td>${p.gender}</td>
                <td>${p.dob}</td>
                <td><span class="badge badge-info">${p.blood_group}</span></td>
                <td>${p.phone}</td>
                <td>${p.room_id ? `<span class="badge badge-purple">Room ${p.room_number || p.room_id} (${p.room_type || 'Ward'})</span>` : '<span style="color:var(--text-muted); font-size:0.8rem;">Outpatient</span>'}</td>
                <td>
                    <div style="display:inline-flex; gap:4px; align-items:center;">
                        <button class="btn btn-secondary btn-sm" onclick='editPatient(${JSON.stringify(p)})'>Edit</button>
                        ${p.room_id ? `<button class="btn btn-warning btn-sm" onclick="openDischargeModal(${p.patient_id})" title="Discharge patient and clear room">🛏️ Discharge</button>` : ''}
                        <button class="btn btn-danger btn-sm" onclick="confirmDeletePatient(${p.patient_id}, '${p.full_name}')">Del</button>
                    </div>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        showToast('Failed to load patients', true);
    }
}

async function loadRoomChoices() {
    const res = await fetch('/api/rooms/choices?available_only=1');
    const choices = await res.json();
    const sel = document.getElementById('patient-room');
    sel.innerHTML = '<option value="">-- None / Outpatient --</option>' +
        choices.map(c => `<option value="${c.id}">${c.label}</option>`).join('');
}

async function savePatient(e) {
    e.preventDefault();
    const id = document.getElementById('patient-id').value;
    const payload = {
        full_name: document.getElementById('patient-name').value,
        gender: document.getElementById('patient-gender').value,
        dob: document.getElementById('patient-dob').value,
        blood_group: document.getElementById('patient-blood').value,
        phone: document.getElementById('patient-phone').value,
        address: document.getElementById('patient-address').value,
        room_id: document.getElementById('patient-room').value || null
    };

    const url = id ? `/api/patients/${id}` : '/api/patients';
    const method = id ? 'PUT' : 'POST';

    const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res.ok) {
        showToast(id ? 'Patient updated successfully' : 'Patient registered successfully');
        resetPatientForm();
        loadPatients();
        loadRooms();
        loadRoomChoices();
        loadDashboardData();
    } else {
        const err = await res.json();
        showToast(err.error || 'Validation error', true);
    }
}

function editPatient(p) {
    document.getElementById('patient-id').value = p.patient_id;
    document.getElementById('patient-name').value = p.full_name;
    document.getElementById('patient-gender').value = p.gender;
    document.getElementById('patient-dob').value = p.dob;
    document.getElementById('patient-blood').value = p.blood_group;
    document.getElementById('patient-phone').value = p.phone;
    document.getElementById('patient-address').value = p.address || '';
    document.getElementById('patient-room').value = p.room_id || '';
    document.getElementById('patient-form-title').innerText = `Edit Patient #${p.patient_id}`;
}

function resetPatientForm() {
    document.getElementById('patient-form').reset();
    document.getElementById('patient-id').value = '';
    document.getElementById('patient-form-title').innerText = 'Register Patient';
}

function confirmDeletePatient(id, name) {
    openConfirmModal('Delete Patient Record', `Are you sure you want to permanently remove patient '${name}'? Any allocated bed will be automatically cleared. This action is audited.`, async () => {
        const res = await fetch(`/api/patients/${id}`, { method: 'DELETE' });
        if (res.ok) {
            showToast('Patient deleted and allocated room cleared');
            loadPatients();
            loadRooms();
            loadRoomChoices();
            loadDashboardData();
        } else {
            showToast('Failed to delete patient', true);
        }
    });
}

// --- DOCTORS API ---
async function loadDoctors() {
    const res = await fetch('/api/doctors');
    const data = await res.json();
    const tbody = document.getElementById('doctors-table-body');
    tbody.innerHTML = data.map(d => `
        <tr>
            <td><strong>#${d.doctor_id}</strong></td>
            <td>${d.full_name}</td>
            <td><span class="badge badge-purple">${d.department}</span></td>
            <td>${d.phone}</td>
            <td>${d.created_at}</td>
            <td>
                <button class="btn btn-secondary btn-sm" onclick='editDoctor(${JSON.stringify(d)})'>Edit</button>
                <button class="btn btn-danger btn-sm" onclick="confirmDeleteDoctor(${d.doctor_id}, '${d.full_name}')">Del</button>
            </td>
        </tr>
    `).join('');
}

async function saveDoctor(e) {
    e.preventDefault();
    const id = document.getElementById('doctor-id').value;
    const payload = {
        full_name: document.getElementById('doctor-name').value,
        department: document.getElementById('doctor-department').value,
        phone: document.getElementById('doctor-phone').value
    };
    const url = id ? `/api/doctors/${id}` : '/api/doctors';
    const method = id ? 'PUT' : 'POST';
    const res = await fetch(url, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)});
    if (res.ok) {
        showToast(id ? 'Doctor record updated' : 'Doctor registered successfully');
        resetDoctorForm();
        loadDoctors();
        loadDashboardData();
    } else {
        showToast('Failed to save doctor', true);
    }
}

function editDoctor(d) {
    document.getElementById('doctor-id').value = d.doctor_id;
    document.getElementById('doctor-name').value = d.full_name;
    document.getElementById('doctor-department').value = d.department;
    document.getElementById('doctor-phone').value = d.phone;
    document.getElementById('doctor-form-title').innerText = `Edit Doctor #${d.doctor_id}`;
}

function resetDoctorForm() {
    document.getElementById('doctor-form').reset();
    document.getElementById('doctor-id').value = '';
    document.getElementById('doctor-form-title').innerText = 'Add Doctor';
}

function confirmDeleteDoctor(id, name) {
    openConfirmModal('Delete Doctor Record', `Are you sure you want to delete '${name}'?`, async () => {
        await fetch(`/api/doctors/${id}`, { method: 'DELETE' });
        showToast('Doctor deleted');
        loadDoctors();
        loadDashboardData();
    });
}

// --- APPOINTMENTS API ---
async function loadDoctorChoices() {
    const res = await fetch('/api/doctors/choices');
    const choices = await res.json();
    const sel = document.getElementById('appt-doctor-id');
    sel.innerHTML = '<option value="">-- Select Doctor --</option>' +
        choices.map(c => `<option value="${c.id}">${c.label}</option>`).join('');
}

async function loadAppointments() {
    const res = await fetch('/api/appointments');
    const data = await res.json();
    const tbody = document.getElementById('appts-table-body');
    tbody.innerHTML = data.map(a => `
        <tr>
            <td><strong>#${a.appointment_id}</strong></td>
            <td>${a.patient}</td>
            <td>${a.doctor}</td>
            <td>${a.appt_date}</td>
            <td>${a.appt_time}</td>
            <td><span class="badge ${a.status === 'Completed' ? 'badge-success' : a.status === 'Cancelled' ? 'badge-danger' : 'badge-warning'}">${a.status}</span></td>
            <td>
                <button class="btn btn-secondary btn-sm" onclick='editAppt(${JSON.stringify(a)})'>Edit</button>
                <button class="btn btn-danger btn-sm" onclick="confirmDeleteAppt(${a.appointment_id})">Del</button>
            </td>
        </tr>
    `).join('');
}

async function saveAppointment(e) {
    e.preventDefault();
    const id = document.getElementById('appt-id').value;
    const patientId = document.getElementById('appt-patient-id').value;
    if (!patientId) {
        showToast('Please select a valid patient using auto-complete suggestions', true);
        return;
    }
    const payload = {
        patient_id: patientId,
        doctor_id: document.getElementById('appt-doctor-id').value,
        appt_date: document.getElementById('appt-date').value,
        appt_time: document.getElementById('appt-time').value,
        status: document.getElementById('appt-status').value
    };
    const url = id ? `/api/appointments/${id}` : '/api/appointments';
    const method = id ? 'PUT' : 'POST';
    const res = await fetch(url, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)});
    if (res.ok) {
        showToast('Appointment saved');
        resetApptForm();
        loadAppointments();
        loadDashboardData();
    } else {
        showToast('Error booking appointment', true);
    }
}

function editAppt(a) {
    document.getElementById('appt-id').value = a.appointment_id;
    document.getElementById('appt-patient-name').value = a.patient;
    document.getElementById('appt-date').value = a.appt_date;
    document.getElementById('appt-time').value = a.appt_time;
    document.getElementById('appt-status').value = a.status;
    document.getElementById('appt-form-title').innerText = `Edit Appointment #${a.appointment_id}`;
}

function resetApptForm() {
    document.getElementById('appt-form').reset();
    document.getElementById('appt-id').value = '';
    document.getElementById('appt-patient-id').value = '';
    document.getElementById('appt-form-title').innerText = 'Schedule Appointment';
}

function confirmDeleteAppt(id) {
    openConfirmModal('Cancel Appointment', `Delete appointment #${id}?`, async () => {
        await fetch(`/api/appointments/${id}`, { method: 'DELETE' });
        showToast('Appointment deleted');
        loadAppointments();
        loadDashboardData();
    });
}

// --- ROOMS API ---
async function loadRooms() {
    const res = await fetch('/api/rooms');
    const data = await res.json();
    const tbody = document.getElementById('rooms-table-body');
    tbody.innerHTML = data.map(r => `
        <tr>
            <td><strong>#${r.room_id}</strong></td>
            <td>Room ${r.room_number}</td>
            <td>${r.room_type}</td>
            <td><span class="badge ${r.status === 'Available' ? 'badge-success' : r.status === 'Occupied' ? 'badge-danger' : 'badge-warning'}">${r.status}</span></td>
            <td>₹${parseFloat(r.rate_per_day).toFixed(2)}</td>
            <td>
                <button class="btn btn-secondary btn-sm" onclick='editRoom(${JSON.stringify(r)})'>Edit</button>
                <button class="btn btn-danger btn-sm" onclick="confirmDeleteRoom(${r.room_id})">Del</button>
            </td>
        </tr>
    `).join('');
}

async function saveRoom(e) {
    e.preventDefault();
    const id = document.getElementById('room-id').value;
    const payload = {
        room_number: document.getElementById('room-number').value,
        room_type: document.getElementById('room-type').value,
        status: document.getElementById('room-status').value,
        rate_per_day: parseFloat(document.getElementById('room-rate').value)
    };
    const url = id ? `/api/rooms/${id}` : '/api/rooms';
    const method = id ? 'PUT' : 'POST';
    const res = await fetch(url, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)});
    if (res.ok) {
        showToast('Room saved');
        resetRoomForm();
        loadRooms();
        loadDashboardData();
    } else {
        showToast('Failed to save room', true);
    }
}

function editRoom(r) {
    document.getElementById('room-id').value = r.room_id;
    document.getElementById('room-number').value = r.room_number;
    document.getElementById('room-type').value = r.room_type;
    document.getElementById('room-status').value = r.status;
    document.getElementById('room-rate').value = r.rate_per_day;
    document.getElementById('room-form-title').innerText = `Edit Room #${r.room_number}`;
}

function resetRoomForm() {
    document.getElementById('room-form').reset();
    document.getElementById('room-id').value = '';
    document.getElementById('room-form-title').innerText = 'Add Room / Ward';
}

function confirmDeleteRoom(id) {
    openConfirmModal('Delete Room', `Delete room #${id}?`, async () => {
        await fetch(`/api/rooms/${id}`, { method: 'DELETE' });
        showToast('Room deleted');
        loadRooms();
        loadDashboardData();
    });
}

// --- STAFF API ---
async function loadStaff() {
    const res = await fetch('/api/staff');
    const data = await res.json();
    const tbody = document.getElementById('staff-table-body');
    tbody.innerHTML = data.map(s => `
        <tr>
            <td><strong>#${s.staff_id}</strong></td>
            <td>${s.full_name}</td>
            <td><span class="badge badge-info">${s.role}</span></td>
            <td>${s.shift}</td>
            <td>${s.phone}</td>
            <td>
                <button class="btn btn-secondary btn-sm" onclick='editStaff(${JSON.stringify(s)})'>Edit</button>
                <button class="btn btn-danger btn-sm" onclick="confirmDeleteStaff(${s.staff_id})">Del</button>
            </td>
        </tr>
    `).join('');
}

async function saveStaff(e) {
    e.preventDefault();
    const id = document.getElementById('staff-id').value;
    const payload = {
        full_name: document.getElementById('staff-name').value,
        role: document.getElementById('staff-role').value,
        shift: document.getElementById('staff-shift').value,
        phone: document.getElementById('staff-phone').value
    };
    const url = id ? `/api/staff/${id}` : '/api/staff';
    const method = id ? 'PUT' : 'POST';
    const res = await fetch(url, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)});
    if (res.ok) {
        showToast('Staff saved');
        resetStaffForm();
        loadStaff();
    } else {
        showToast('Failed to save staff', true);
    }
}

function editStaff(s) {
    document.getElementById('staff-id').value = s.staff_id;
    document.getElementById('staff-name').value = s.full_name;
    document.getElementById('staff-role').value = s.role;
    document.getElementById('staff-shift').value = s.shift;
    document.getElementById('staff-phone').value = s.phone;
    document.getElementById('staff-form-title').innerText = `Edit Staff #${s.staff_id}`;
}

function resetStaffForm() {
    document.getElementById('staff-form').reset();
    document.getElementById('staff-id').value = '';
    document.getElementById('staff-form-title').innerText = 'Add Staff Member';
}

function confirmDeleteStaff(id) {
    openConfirmModal('Delete Staff Record', `Delete staff member #${id}?`, async () => {
        await fetch(`/api/staff/${id}`, { method: 'DELETE' });
        showToast('Staff member deleted');
        loadStaff();
    });
}

// --- PHARMACY API ---
let lowStockOnly = false;
async function loadMedicines() {
    const url = lowStockOnly ? '/api/medicines?low_stock=1' : '/api/medicines';
    const res = await fetch(url);
    const data = await res.json();
    const tbody = document.getElementById('meds-table-body');
    tbody.innerHTML = data.map(m => {
        const isLow = m.stock_qty <= m.reorder_level;
        return `
            <tr style="${isLow ? 'background-color: #fff1f2;' : ''}">
                <td><strong>#${m.medicine_id}</strong></td>
                <td>${m.name}</td>
                <td><span class="badge badge-purple">${m.category}</span></td>
                <td><strong>${m.stock_qty}</strong></td>
                <td>₹${parseFloat(m.unit_price).toFixed(2)}</td>
                <td>${m.reorder_level}</td>
                <td><span class="badge ${isLow ? 'badge-danger' : 'badge-success'}">${isLow ? 'LOW STOCK' : 'Adequate'}</span></td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick='editMed(${JSON.stringify(m)})'>Edit</button>
                    <button class="btn btn-danger btn-sm" onclick="confirmDeleteMed(${m.medicine_id})">Del</button>
                </td>
            </tr>
        `;
    }).join('');
}

function filterLowStock() {
    lowStockOnly = !lowStockOnly;
    loadMedicines();
    showToast(lowStockOnly ? 'Showing LOW STOCK medicines only' : 'Showing all medicines');
}

async function saveMedicine(e) {
    e.preventDefault();
    const id = document.getElementById('med-id').value;
    const payload = {
        name: document.getElementById('med-name').value,
        category: document.getElementById('med-category').value,
        stock_qty: parseInt(document.getElementById('med-stock').value),
        unit_price: parseFloat(document.getElementById('med-price').value),
        reorder_level: parseInt(document.getElementById('med-reorder').value)
    };
    const url = id ? `/api/medicines/${id}` : '/api/medicines';
    const method = id ? 'PUT' : 'POST';
    const res = await fetch(url, { method, headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)});
    if (res.ok) {
        showToast('Medicine inventory updated');
        resetMedForm();
        loadMedicines();
        loadDashboardData();
    } else {
        showToast('Failed to save medicine', true);
    }
}

function editMed(m) {
    document.getElementById('med-id').value = m.medicine_id;
    document.getElementById('med-name').value = m.name;
    document.getElementById('med-category').value = m.category;
    document.getElementById('med-stock').value = m.stock_qty;
    document.getElementById('med-price').value = m.unit_price;
    document.getElementById('med-reorder').value = m.reorder_level;
    document.getElementById('med-form-title').innerText = `Edit Medicine #${m.medicine_id}`;
}

function resetMedForm() {
    document.getElementById('med-form').reset();
    document.getElementById('med-id').value = '';
    document.getElementById('med-reorder').value = '10';
    document.getElementById('med-form-title').innerText = 'Add Medicine';
}

function confirmDeleteMed(id) {
    openConfirmModal('Delete Medicine', `Delete medicine #${id} from pharmacy?`, async () => {
        await fetch(`/api/medicines/${id}`, { method: 'DELETE' });
        showToast('Medicine deleted');
        loadMedicines();
        loadDashboardData();
    });
}

// --- BILLING API ---
function updateBillCalculatedTotal() {
    const room = parseFloat(document.getElementById('bill-room').value) || 0;
    const consult = parseFloat(document.getElementById('bill-consult').value) || 0;
    const med = parseFloat(document.getElementById('bill-med').value) || 0;
    const total = room + consult + med;
    document.getElementById('bill-calculated-total').innerText = `₹${total.toFixed(2)}`;
}

document.querySelectorAll('.calc-total').forEach(input => {
    input.addEventListener('input', updateBillCalculatedTotal);
});

async function loadBills() {
    const res = await fetch('/api/bills');
    const data = await res.json();
    const tbody = document.getElementById('bills-table-body');
    tbody.innerHTML = data.map(b => `
        <tr>
            <td><strong>#${b.bill_id}</strong></td>
            <td>${b.patient_name}</td>
            <td>₹${parseFloat(b.room_charges).toFixed(2)}</td>
            <td>₹${parseFloat(b.consultation_charges).toFixed(2)}</td>
            <td>₹${parseFloat(b.medicine_charges).toFixed(2)}</td>
            <td><strong>₹${parseFloat(b.total_amount).toFixed(2)}</strong></td>
            <td><span class="badge badge-info">${b.payment_method}</span></td>
            <td><span class="badge ${b.payment_status === 'Paid' ? 'badge-success' : 'badge-warning'}">${b.payment_status}</span></td>
            <td>
                <div style="display:inline-flex; gap:4px; align-items:center;">
                    <button class="btn btn-secondary btn-sm" onclick="togglePaymentStatus(${b.bill_id}, '${b.payment_status}')">${b.payment_status === 'Paid' ? 'Mark Pending' : 'Mark Paid'}</button>
                    <button class="btn btn-warning btn-sm" onclick="openDischargeModal(${b.patient_id})" title="Discharge patient and verify bed release">🛏️ Discharge</button>
                    <button class="btn btn-danger btn-sm" onclick="confirmDeleteBill(${b.bill_id})">Del</button>
                </div>
            </td>
        </tr>
    `).join('');
}

async function togglePaymentStatus(id, currentStatus) {
    const newStatus = currentStatus === 'Paid' ? 'Pending' : 'Paid';
    await fetch(`/api/bills/${id}/status`, {
        method: 'PUT',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ payment_status: newStatus })
    });
    showToast(`Bill marked as ${newStatus}`);
    loadBills();
    loadDashboardData();
}

async function saveBill(e) {
    e.preventDefault();
    const patientId = document.getElementById('bill-patient-id').value;
    if (!patientId) {
        showToast('Please select a valid patient using auto-complete', true);
        return;
    }
    const payload = {
        patient_id: patientId,
        room_charges: parseFloat(document.getElementById('bill-room').value) || 0,
        consultation_charges: parseFloat(document.getElementById('bill-consult').value) || 0,
        medicine_charges: parseFloat(document.getElementById('bill-med').value) || 0,
        payment_method: document.getElementById('bill-method').value,
        payment_status: document.getElementById('bill-status').value
    };
    const res = await fetch('/api/bills', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(payload)
    });
    if (res.ok) {
        showToast('Invoice generated successfully');
        resetBillForm();
        loadBills();
        loadDashboardData();
    } else {
        showToast('Failed to generate invoice', true);
    }
}

function resetBillForm() {
    document.getElementById('bill-form').reset();
    document.getElementById('bill-patient-id').value = '';
    document.getElementById('bill-consult').value = '500';
    updateBillCalculatedTotal();
}

function confirmDeleteBill(id) {
    openConfirmModal('Delete Invoice', `Are you sure you want to delete invoice #${id}?`, async () => {
        await fetch(`/api/bills/${id}`, { method: 'DELETE' });
        showToast('Invoice deleted');
        loadBills();
        loadDashboardData();
    });
}

// --- AUDIT LOG API ---
async function loadAuditLogs() {
    const res = await fetch('/api/audit');
    const data = await res.json();
    const tbody = document.getElementById('audit-table-body');
    tbody.innerHTML = data.map(a => `
        <tr>
            <td><strong>#${a.log_id}</strong></td>
            <td>${a.timestamp}</td>
            <td><code>${a.table_name}</code></td>
            <td>${a.record_id || '-'}</td>
            <td><span class="badge ${a.action === 'INSERT' ? 'badge-success' : a.action === 'UPDATE' ? 'badge-warning' : 'badge-danger'}">${a.action}</span></td>
            <td>${a.details || '-'}</td>
            <td>${a.performed_by}</td>
        </tr>
    `).join('');
}

// --- DEFECT CHECKSHEET API ---
async function loadDefects() {
    const res = await fetch('/api/defects');
    const data = await res.json();
    const tbody = document.getElementById('defects-table-body');
    tbody.innerHTML = data.map(d => `
        <tr>
            <td><strong>#${d.defect_id}</strong></td>
            <td>${d.logged_at}</td>
            <td><span class="badge badge-purple">${d.category}</span></td>
            <td><span class="badge ${d.severity === 'Critical' ? 'badge-danger' : d.severity === 'High' ? 'badge-warning' : 'badge-info'}">${d.severity}</span></td>
            <td><span class="badge badge-warning">${d.status}</span></td>
            <td>${d.description}</td>
        </tr>
    `).join('');
}

async function saveDefect(e) {
    e.preventDefault();
    const payload = {
        category: document.getElementById('defect-category').value,
        severity: document.getElementById('defect-severity').value,
        description: document.getElementById('defect-desc').value
    };
    const res = await fetch('/api/defects', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(payload)
    });
    if (res.ok) {
        showToast('Defect logged on SQC checksheet');
        document.getElementById('defect-form').reset();
        loadDefects();
    } else {
        showToast('Failed to log defect', true);
    }
}

// --- DISCHARGE & BED CLEARANCE MODAL LOGIC ---
async function openDischargeModal(patientId) {
    try {
        const res = await fetch(`/api/patients/${patientId}/discharge-summary`);
        if (!res.ok) {
            showToast('Unable to fetch discharge summary', true);
            return;
        }
        const data = await res.json();

        document.getElementById('ds-patient-id').value = data.patient_id;
        document.getElementById('ds-patient-name').innerText = data.full_name;
        document.getElementById('ds-patient-badge').innerText = `ID #${data.patient_id}`;
        document.getElementById('ds-patient-phone').innerText = data.phone || '-';
        document.getElementById('ds-patient-blood').innerText = data.blood_group || '-';
        document.getElementById('ds-admit-date').innerText = (data.admission_date || '').replace('T', ' ');

        const roomLabel = data.room_number ? `Room ${data.room_number} (${data.room_type || 'Ward'})` : 'No Bed Currently Assigned';
        document.getElementById('ds-room-info').innerText = roomLabel;

        document.getElementById('ds-total-billed').innerText = `₹${data.total_billed.toFixed(2)}`;
        document.getElementById('ds-total-paid').innerText = `₹${data.total_paid.toFixed(2)}`;
        document.getElementById('ds-balance-due').innerText = `₹${data.balance_due.toFixed(2)}`;

        const billingBadge = document.getElementById('ds-billing-badge');
        if (data.has_unpaid_bills || data.balance_due > 0) {
            billingBadge.className = 'badge badge-warning';
            billingBadge.innerText = `⚠️ Outstanding Balance: ₹${data.balance_due.toFixed(2)}`;
        } else {
            billingBadge.className = 'badge badge-success';
            billingBadge.innerText = '✓ Billing Cleared (Zero Balance)';
        }

        document.getElementById('ds-room-status').value = 'Available';
        document.getElementById('ds-notes').value = '';
        document.getElementById('dischargeModal').classList.add('show');
    } catch (err) {
        console.error(err);
        showToast('Error opening discharge summary', true);
    }
}

function closeDischargeModal() {
    document.getElementById('dischargeModal').classList.remove('show');
}

async function executeDischarge() {
    const patientId = document.getElementById('ds-patient-id').value;
    if (!patientId) return;

    const notes = document.getElementById('ds-notes').value.trim();
    const roomStatus = document.getElementById('ds-room-status').value;

    try {
        const res = await fetch(`/api/patients/${patientId}/discharge`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                discharge_notes: notes,
                room_status: roomStatus
            })
        });

        if (res.ok) {
            const data = await res.json();
            const roomMsg = data.details.freed_room_number
                ? ` Room #${data.details.freed_room_number} cleared and set to ${roomStatus}.`
                : '';
            showToast(`Patient discharged successfully!${roomMsg}`);
            closeDischargeModal();
            loadPatients();
            loadRooms();
            loadRoomChoices();
            loadBills();
            loadDashboardData();
        } else {
            const err = await res.json();
            showToast(err.error || 'Failed to discharge patient', true);
        }
    } catch (err) {
        console.error(err);
        showToast('Error executing discharge', true);
    }
}

// Initial setup on window load
window.addEventListener('DOMContentLoaded', () => {
    setupPhoneMasking();

    // Setup patient auto-complete for appointment tab
    setupAutocomplete(
        document.getElementById('appt-patient-name'),
        document.getElementById('patient-autocomplete-box'),
        '/api/patients/autocomplete',
        (item) => {
            document.getElementById('appt-patient-id').value = item.id;
        }
    );

    // Setup patient auto-complete for billing tab
    setupAutocomplete(
        document.getElementById('bill-patient-name'),
        document.getElementById('bill-patient-autocomplete'),
        '/api/patients/autocomplete',
        (item) => {
            document.getElementById('bill-patient-id').value = item.id;
        }
    );

    // Load initial view
    loadDashboardData();
});
