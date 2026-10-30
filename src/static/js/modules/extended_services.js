/**
 * extended_services.js -- Frontend Handlers for Extended Hospital Departments & Modules
 * Covers 17 specialized services:
 *  1. Health Packages
 *  2. Referrals Desk
 *  3. Telemedicine Consults
 *  4. Dialysis Unit
 *  5. Maternity & Nursery
 *  6. Physiotherapy
 *  7. Vaccination / Immunization
 *  8. Medical Records (MRD)
 *  9. Pharmacy Returns
 * 10. CSSD Sterilization
 * 11. Linen & Laundry
 * 12. Mortuary Register
 * 13. Security Gate Log
 * 14. Facility Safety Checklists
 * 15. Infection Control Surveillance
 * 16. Patient Feedback
 * 17. Morbidity & Mortality (M&M) Reviews
 */

const esc = (s) => (window.escapeHtml ? window.escapeHtml(s || '') : (s || ''));

// Helper for status PUT
async function updateModuleStatus(url, payload, reloadFn, successMsg = 'Status updated successfully') {
    try {
        const res = await fetch(url, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            if (window.showToast) window.showToast(successMsg);
            if (reloadFn) reloadFn();
        } else {
            const err = await res.json();
            if (window.showToast) window.showToast(err.error || 'Failed to update status', 'error');
        }
    } catch (e) {
        if (window.showToast) window.showToast('Network error while updating status', 'error');
    }
}

// -------------------------------------------------------------
// 1. HEALTH PACKAGES
// -------------------------------------------------------------
window.hmsLoadHealthPackages = async function() {
    try {
        const res = await fetch('/api/health-packages');
        if (!res.ok) return;
        const list = await res.json();
        const tbody = document.getElementById('healthPackagesTableBody');
        if (!tbody) return;
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No health checkup packages found.</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(p => `
            <tr>
                <td><code>${esc(p.code)}</code></td>
                <td><strong>${esc(p.package_name)}</strong><br><small style="color:var(--text-muted);">${esc(p.description)}</small></td>
                <td><strong style="color:var(--color-primary);">₹${Number(p.price).toFixed(2)}</strong></td>
                <td><small>${esc(p.tests_included)}</small></td>
                <td><span class="badge ${p.active ? 'badge-success' : 'badge-secondary'}">${p.active ? 'Active' : 'Archived'}</span></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="window.hmsToggleHealthPackage(${p.package_id}, ${p.active ? 0 : 1})">
                        ${p.active ? 'Archive' : 'Activate'}
                    </button>
                </td>
            </tr>
        `).join('');
    } catch(e) {}
};

window.hmsSaveHealthPackage = async function(e) {
    e.preventDefault();
    const payload = {
        package_name: document.getElementById('hp-name').value.trim(),
        code: document.getElementById('hp-code').value.trim().toUpperCase(),
        price: parseFloat(document.getElementById('hp-price').value),
        tests_included: document.getElementById('hp-tests').value.trim(),
        description: document.getElementById('hp-desc').value.trim()
    };
    try {
        const res = await fetch('/api/health-packages', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            if (window.showToast) window.showToast('Health package registered successfully!');
            document.getElementById('healthPackageForm').reset();
            window.hmsLoadHealthPackages();
        } else {
            const err = await res.json();
            if (window.showToast) window.showToast(err.error || 'Failed to create package', 'error');
        }
    } catch(e) {}
};

window.hmsToggleHealthPackage = function(pkgId, newActive) {
    updateModuleStatus(`/api/health-packages/${pkgId}/status`, { active: newActive }, window.hmsLoadHealthPackages);
};

// -------------------------------------------------------------
// 2. REFERRALS DESK
// -------------------------------------------------------------
window.hmsLoadReferrals = async function() {
    try {
        const res = await fetch('/api/referrals');
        if (!res.ok) return;
        const list = await res.json();
        const tbody = document.getElementById('referralsTableBody');
        if (!tbody) return;
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:var(--text-muted);">No referrals found.</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(r => `
            <tr>
                <td>#REF-${r.referral_id}</td>
                <td><code>${esc(r.uhid)}</code></td>
                <td><strong>${esc(r.patient_name)}</strong></td>
                <td><span class="badge ${r.referral_type === 'Inbound' ? 'badge-primary' : 'badge-warning'}">${esc(r.referral_type)}</span></td>
                <td>${esc(r.referring_center)}</td>
                <td>${esc(r.specialty)}</td>
                <td><span class="badge ${r.status === 'Accepted' ? 'badge-success' : 'badge-secondary'}">${esc(r.status)}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="window.hmsUpdateReferralStatus(${r.referral_id}, 'Accepted')">Accept</button>
                    <button class="btn btn-sm btn-secondary" onclick="window.hmsUpdateReferralStatus(${r.referral_id}, 'Completed')">Close</button>
                </td>
            </tr>
        `).join('');
    } catch(e) {}
};

window.hmsSaveReferral = async function(e) {
    e.preventDefault();
    const payload = {
        uhid: document.getElementById('ref-uhid').value.trim(),
        patient_name: document.getElementById('ref-patient').value.trim(),
        referral_type: document.getElementById('ref-type').value,
        referring_center: document.getElementById('ref-center').value.trim(),
        specialty: document.getElementById('ref-dept').value.trim(),
        clinical_reason: document.getElementById('ref-reason').value.trim()
    };
    try {
        const res = await fetch('/api/referrals', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            if (window.showToast) window.showToast('Referral registered successfully!');
            document.getElementById('referralForm').reset();
            window.hmsLoadReferrals();
        } else {
            const err = await res.json();
            if (window.showToast) window.showToast(err.error || 'Failed to save referral', 'error');
        }
    } catch(e) {}
};

window.hmsUpdateReferralStatus = function(refId, status) {
    updateModuleStatus(`/api/referrals/${refId}/status`, { status }, window.hmsLoadReferrals);
};

// -------------------------------------------------------------
// 3. TELEMEDICINE
// -------------------------------------------------------------
window.hmsLoadTelemedicine = async function() {
    try {
        const res = await fetch('/api/telemedicine');
        if (!res.ok) return;
        const list = await res.json();
        const tbody = document.getElementById('telemedicineTableBody');
        if (!tbody) return;
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; color:var(--text-muted);">No telemedicine appointments found.</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(t => `
            <tr>
                <td>#TEL-${t.tele_id}</td>
                <td><code>${esc(t.uhid)}</code></td>
                <td><strong>${esc(t.patient_name)}</strong></td>
                <td>${esc(t.doctor_name)}</td>
                <td>${esc(t.scheduled_time)}</td>
                <td>${esc(t.platform)}</td>
                <td><span class="badge ${t.status === 'Completed' ? 'badge-success' : 'badge-primary'}">${esc(t.status)}</span></td>
                <td><a href="${esc(t.meeting_link)}" target="_blank" class="btn btn-sm btn-primary">Join Room</a></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="window.hmsUpdateTelemedicineStatus(${t.tele_id}, 'Completed')">Mark Done</button>
                </td>
            </tr>
        `).join('');
    } catch(e) {}
};

window.hmsSaveTelemedicine = async function(e) {
    e.preventDefault();
    const payload = {
        uhid: document.getElementById('tele-uhid').value.trim(),
        patient_name: document.getElementById('tele-patient').value.trim(),
        doctor_name: document.getElementById('tele-doctor').value.trim(),
        scheduled_time: document.getElementById('tele-time').value,
        platform: document.getElementById('tele-platform').value
    };
    try {
        const res = await fetch('/api/telemedicine', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            if (window.showToast) window.showToast('Virtual consult booked!');
            document.getElementById('telemedicineForm').reset();
            window.hmsLoadTelemedicine();
        } else {
            const err = await res.json();
            if (window.showToast) window.showToast(err.error || 'Failed to book consult', 'error');
        }
    } catch(e) {}
};

window.hmsUpdateTelemedicineStatus = function(teleId, status) {
    updateModuleStatus(`/api/telemedicine/${teleId}/status`, { status }, window.hmsLoadTelemedicine);
};

// -------------------------------------------------------------
// 4. DIALYSIS
// -------------------------------------------------------------
window.hmsLoadDialysis = async function() {
    try {
        const res = await fetch('/api/dialysis');
        if (!res.ok) return;
        const list = await res.json();
        const tbody = document.getElementById('dialysisTableBody');
        if (!tbody) return;
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; color:var(--text-muted);">No dialysis sessions found.</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(d => `
            <tr>
                <td>#DIA-${d.session_id}</td>
                <td><code>${esc(d.uhid)}</code></td>
                <td><strong>${esc(d.patient_name)}</strong></td>
                <td>${esc(d.machine_no)}</td>
                <td>${esc(d.session_type)}</td>
                <td>${d.pre_weight ? d.pre_weight + ' kg' : '--'}</td>
                <td>${d.post_weight ? d.post_weight + ' kg' : '--'}</td>
                <td><span class="badge ${d.status === 'Completed' ? 'badge-success' : 'badge-warning'}">${esc(d.status)}</span></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="window.hmsUpdateDialysisStatus(${d.session_id}, 'Completed')">Complete</button>
                </td>
            </tr>
        `).join('');
    } catch(e) {}
};

window.hmsSaveDialysis = async function(e) {
    e.preventDefault();
    const payload = {
        uhid: document.getElementById('dia-uhid').value.trim(),
        patient_name: document.getElementById('dia-patient').value.trim(),
        machine_no: document.getElementById('dia-machine').value.trim(),
        session_type: document.getElementById('dia-type').value,
        pre_weight: parseFloat(document.getElementById('dia-pre-weight').value) || null
    };
    try {
        const res = await fetch('/api/dialysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            if (window.showToast) window.showToast('Dialysis session scheduled!');
            document.getElementById('dialysisForm').reset();
            window.hmsLoadDialysis();
        } else {
            const err = await res.json();
            if (window.showToast) window.showToast(err.error || 'Failed to schedule dialysis', 'error');
        }
    } catch(e) {}
};

window.hmsUpdateDialysisStatus = function(sessionId, status) {
    updateModuleStatus(`/api/dialysis/${sessionId}/status`, { status, post_weight: 66.8 }, window.hmsLoadDialysis);
};

// -------------------------------------------------------------
// 5. MATERNITY & NURSERY
// -------------------------------------------------------------
window.hmsLoadMaternity = async function() {
    try {
        const res = await fetch('/api/maternity');
        if (!res.ok) return;
        const list = await res.json();
        const tbody = document.getElementById('maternityTableBody');
        if (!tbody) return;
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; color:var(--text-muted);">No delivery records found.</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(m => `
            <tr>
                <td>#MAT-${m.record_id}</td>
                <td><code>${esc(m.mother_uhid)}</code></td>
                <td><strong>${esc(m.mother_name)}</strong></td>
                <td>${esc(m.delivery_type)}</td>
                <td><span class="badge ${m.baby_gender === 'Female' ? 'badge-primary' : 'badge-secondary'}">${esc(m.baby_gender)}</span></td>
                <td><strong>${m.birth_weight_kg} kg</strong></td>
                <td>${m.apgar_1min} / ${m.apgar_5min}</td>
                <td>${esc(m.nursery_crib_no || 'Rooming In')}</td>
                <td><small>${esc(m.delivery_time)}</small></td>
            </tr>
        `).join('');
    } catch(e) {}
};

window.hmsSaveMaternity = async function(e) {
    e.preventDefault();
    const payload = {
        mother_uhid: document.getElementById('mat-mother-uhid').value.trim(),
        mother_name: document.getElementById('mat-mother-name').value.trim(),
        delivery_type: document.getElementById('mat-delivery-type').value,
        baby_gender: document.getElementById('mat-baby-gender').value,
        birth_weight_kg: parseFloat(document.getElementById('mat-birth-weight').value),
        apgar_1min: parseInt(document.getElementById('mat-apgar1').value) || 8,
        apgar_5min: parseInt(document.getElementById('mat-apgar5').value) || 9,
        nursery_crib_no: document.getElementById('mat-crib').value.trim()
    };
    try {
        const res = await fetch('/api/maternity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            if (window.showToast) window.showToast('Birth record created successfully!');
            document.getElementById('maternityForm').reset();
            window.hmsLoadMaternity();
        } else {
            const err = await res.json();
            if (window.showToast) window.showToast(err.error || 'Failed to save birth record', 'error');
        }
    } catch(e) {}
};

// -------------------------------------------------------------
// 6. PHYSIOTHERAPY
// -------------------------------------------------------------
window.hmsLoadPhysiotherapy = async function() {
    try {
        const res = await fetch('/api/physiotherapy');
        if (!res.ok) return;
        const list = await res.json();
        const tbody = document.getElementById('physiotherapyTableBody');
        if (!tbody) return;
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:var(--text-muted);">No physiotherapy sessions found.</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(p => `
            <tr>
                <td>#PT-${p.session_id}</td>
                <td><code>${esc(p.uhid)}</code></td>
                <td><strong>${esc(p.patient_name)}</strong></td>
                <td>${esc(p.diagnosis)}</td>
                <td><small>${esc(p.protocol)}</small></td>
                <td>Session #${p.session_number}</td>
                <td><span class="badge ${p.status === 'Completed' ? 'badge-success' : 'badge-warning'}">${esc(p.status)}</span></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="window.hmsUpdatePhysioStatus(${p.session_id}, 'Completed')">Complete</button>
                </td>
            </tr>
        `).join('');
    } catch(e) {}
};

window.hmsSavePhysiotherapy = async function(e) {
    e.preventDefault();
    const payload = {
        uhid: document.getElementById('pt-uhid').value.trim(),
        patient_name: document.getElementById('pt-patient').value.trim(),
        diagnosis: document.getElementById('pt-diagnosis').value.trim(),
        protocol: document.getElementById('pt-protocol').value.trim()
    };
    try {
        const res = await fetch('/api/physiotherapy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            if (window.showToast) window.showToast('Physiotherapy session scheduled!');
            document.getElementById('physioForm').reset();
            window.hmsLoadPhysiotherapy();
        } else {
            const err = await res.json();
            if (window.showToast) window.showToast(err.error || 'Failed to schedule session', 'error');
        }
    } catch(e) {}
};

window.hmsUpdatePhysioStatus = function(sessId, status) {
    updateModuleStatus(`/api/physiotherapy/${sessId}/status`, { status }, window.hmsLoadPhysiotherapy);
};

// -------------------------------------------------------------
// 7. VACCINATION / IMMUNIZATION
// -------------------------------------------------------------
window.hmsLoadVaccination = async function() {
    try {
        const res = await fetch('/api/vaccination');
        if (!res.ok) return;
        const list = await res.json();
        const tbody = document.getElementById('vaccinationTableBody');
        if (!tbody) return;
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; color:var(--text-muted);">No vaccination records found.</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(v => `
            <tr>
                <td>#VAC-${v.entry_id}</td>
                <td><code>${esc(v.uhid)}</code></td>
                <td><strong>${esc(v.patient_name)}</strong></td>
                <td>${esc(v.vaccine_name)}</td>
                <td>Dose ${v.dose_number}</td>
                <td><code>${esc(v.batch_no || '--')}</code></td>
                <td>${esc(v.expiry_date || '--')}</td>
                <td><span class="badge ${v.status === 'Administered' ? 'badge-success' : 'badge-secondary'}">${esc(v.status)}</span></td>
                <td><small>${esc(v.administered_date)}</small></td>
            </tr>
        `).join('');
    } catch(e) {}
};

window.hmsSaveVaccination = async function(e) {
    e.preventDefault();
    const payload = {
        uhid: document.getElementById('vac-uhid').value.trim(),
        patient_name: document.getElementById('vac-patient').value.trim(),
        vaccine_name: document.getElementById('vac-name').value,
        dose_number: parseInt(document.getElementById('vac-dose').value) || 1,
        batch_no: document.getElementById('vac-batch').value.trim()
    };
    try {
        const res = await fetch('/api/vaccination', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            if (window.showToast) window.showToast('Vaccination recorded successfully!');
            document.getElementById('vaccinationForm').reset();
            window.hmsLoadVaccination();
        } else {
            const err = await res.json();
            if (window.showToast) window.showToast(err.error || 'Failed to record vaccine', 'error');
        }
    } catch(e) {}
};

// -------------------------------------------------------------
// 8. MEDICAL RECORDS (MRD)
// -------------------------------------------------------------
window.hmsLoadMrd = async function() {
    try {
        const res = await fetch('/api/medical-records');
        if (!res.ok) return;
        const list = await res.json();
        const tbody = document.getElementById('mrdTableBody');
        if (!tbody) return;
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:var(--text-muted);">No MRD files found.</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(m => `
            <tr>
                <td>#MRD-${m.record_id}</td>
                <td><code>${esc(m.uhid)}</code></td>
                <td><strong>${esc(m.patient_name)}</strong></td>
                <td><code>${esc(m.icd_code)}</code> - ${esc(m.icd_description)}</td>
                <td><strong>${esc(m.physical_shelf_bay)}</strong></td>
                <td><span class="badge ${m.record_status === 'Archived' ? 'badge-success' : 'badge-warning'}">${esc(m.record_status)}</span></td>
                <td>${esc(m.borrowed_by || 'On Shelf')}</td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="window.hmsUpdateMrdStatus(${m.record_id}, 'Issued', 'Dr. Rajesh Sharma')">Issue</button>
                    <button class="btn btn-sm btn-secondary" onclick="window.hmsUpdateMrdStatus(${m.record_id}, 'Archived')">Return</button>
                </td>
            </tr>
        `).join('');
    } catch(e) {}
};

window.hmsSaveMrd = async function(e) {
    e.preventDefault();
    const payload = {
        uhid: document.getElementById('mrd-uhid').value.trim(),
        patient_name: document.getElementById('mrd-patient').value.trim(),
        icd_code: document.getElementById('mrd-icd').value.trim().toUpperCase(),
        icd_description: document.getElementById('mrd-desc').value.trim(),
        physical_shelf_bay: document.getElementById('mrd-location').value.trim()
    };
    try {
        const res = await fetch('/api/medical-records', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            if (window.showToast) window.showToast('MRD record archived!');
            document.getElementById('mrdForm').reset();
            window.hmsLoadMrd();
        } else {
            const err = await res.json();
            if (window.showToast) window.showToast(err.error || 'Failed to archive record', 'error');
        }
    } catch(e) {}
};

window.hmsUpdateMrdStatus = function(recId, status, borrowedBy = null) {
    updateModuleStatus(`/api/medical-records/${recId}/status`, { status, borrowed_by: borrowedBy }, window.hmsLoadMrd);
};

// -------------------------------------------------------------
// 9. PHARMACY RETURNS
// -------------------------------------------------------------
window.hmsLoadPharmacyReturns = async function() {
    try {
        const res = await fetch('/api/pharmacy-returns');
        if (!res.ok) return;
        const list = await res.json();
        const tbody = document.getElementById('pharmacyReturnsTableBody');
        if (!tbody) return;
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; color:var(--text-muted);">No pharmacy returns recorded.</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(r => `
            <tr>
                <td>#RET-${r.return_id}</td>
                <td><code>${esc(r.uhid)}</code></td>
                <td><strong>${esc(r.medicine_name)}</strong></td>
                <td>${esc(r.batch_no || '--')}</td>
                <td>${r.qty_returned}</td>
                <td><strong>₹${Number(r.refund_amount).toFixed(2)}</strong></td>
                <td><small>${esc(r.reason)}</small></td>
                <td><span class="badge ${r.status === 'Approved' ? 'badge-success' : 'badge-warning'}">${esc(r.status)}</span></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="window.hmsUpdateReturnStatus(${r.return_id}, 'Approved')">Approve Credit</button>
                </td>
            </tr>
        `).join('');
    } catch(e) {}
};

window.hmsSavePharmacyReturn = async function(e) {
    e.preventDefault();
    const payload = {
        uhid: document.getElementById('ret-uhid').value.trim(),
        medicine_name: document.getElementById('ret-medicine').value.trim(),
        batch_no: document.getElementById('ret-batch').value.trim(),
        qty_returned: parseInt(document.getElementById('ret-qty').value) || 1,
        refund_amount: parseFloat(document.getElementById('ret-refund').value) || 0.0,
        reason: document.getElementById('ret-reason').value
    };
    try {
        const res = await fetch('/api/pharmacy-returns', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            if (window.showToast) window.showToast('Pharmacy return processed!');
            document.getElementById('pharmacyReturnForm').reset();
            window.hmsLoadPharmacyReturns();
        } else {
            const err = await res.json();
            if (window.showToast) window.showToast(err.error || 'Failed to process return', 'error');
        }
    } catch(e) {}
};

window.hmsUpdateReturnStatus = function(retId, status) {
    updateModuleStatus(`/api/pharmacy-returns/${retId}/status`, { status }, window.hmsLoadPharmacyReturns);
};

// -------------------------------------------------------------
// 10. CSSD STERILIZATION
// -------------------------------------------------------------
window.hmsLoadCssd = async function() {
    try {
        const res = await fetch('/api/cssd');
        if (!res.ok) return;
        const list = await res.json();
        const tbody = document.getElementById('cssdTableBody');
        if (!tbody) return;
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:var(--text-muted);">No sterilization cycles found.</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(c => `
            <tr>
                <td>#CYCLE-${c.cycle_id}</td>
                <td><strong>${esc(c.autoclave_id)}</strong></td>
                <td>${esc(c.cycle_type)}</td>
                <td>${c.items_count} packs</td>
                <td><span class="badge ${c.chemical_indicator_passed ? 'badge-success' : 'badge-danger'}">${c.chemical_indicator_passed ? 'Passed (Class 5)' : 'Failed (Reject)'}</span></td>
                <td><small>${esc(c.started_at)}</small></td>
                <td><span class="badge ${c.status === 'Released' ? 'badge-success' : 'badge-primary'}">${esc(c.status)}</span></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="window.hmsUpdateCssdStatus(${c.cycle_id}, 'Released')">Release Packs</button>
                </td>
            </tr>
        `).join('');
    } catch(e) {}
};

window.hmsSaveCssd = async function(e) {
    e.preventDefault();
    const payload = {
        autoclave_id: document.getElementById('cssd-autoclave').value.trim(),
        cycle_type: document.getElementById('cssd-type').value,
        items_count: parseInt(document.getElementById('cssd-items').value) || 10,
        chemical_indicator_passed: parseInt(document.getElementById('cssd-indicator').value)
    };
    try {
        const res = await fetch('/api/cssd', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            if (window.showToast) window.showToast('Autoclave cycle recorded!');
            document.getElementById('cssdForm').reset();
            window.hmsLoadCssd();
        } else {
            const err = await res.json();
            if (window.showToast) window.showToast(err.error || 'Failed to record cycle', 'error');
        }
    } catch(e) {}
};

window.hmsUpdateCssdStatus = function(cycleId, status) {
    updateModuleStatus(`/api/cssd/${cycleId}/status`, { status }, window.hmsLoadCssd);
};

// -------------------------------------------------------------
// 11. LAUNDRY & LINEN
// -------------------------------------------------------------
window.hmsLoadLaundry = async function() {
    try {
        const res = await fetch('/api/laundry');
        if (!res.ok) return;
        const list = await res.json();
        const tbody = document.getElementById('laundryTableBody');
        if (!tbody) return;
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:var(--text-muted);">No laundry batches found.</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(l => `
            <tr>
                <td>#LIN-${l.batch_id}</td>
                <td><strong>${esc(l.ward_name)}</strong></td>
                <td>${esc(l.linen_type)}</td>
                <td><strong style="color:var(--color-primary);">${l.clean_qty}</strong></td>
                <td><strong style="color:var(--color-danger);">${l.soiled_qty}</strong></td>
                <td><span class="badge ${l.status === 'Dispatched' ? 'badge-success' : 'badge-warning'}">${esc(l.status)}</span></td>
                <td><small>${esc(l.last_updated)}</small></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="window.hmsUpdateLaundryStatus(${l.batch_id}, 'Dispatched')">Dispatch</button>
                </td>
            </tr>
        `).join('');
    } catch(e) {}
};

window.hmsSaveLaundry = async function(e) {
    e.preventDefault();
    const payload = {
        ward_name: document.getElementById('ln-ward').value.trim(),
        linen_type: document.getElementById('ln-type').value,
        clean_qty: parseInt(document.getElementById('ln-clean').value) || 0,
        soiled_qty: parseInt(document.getElementById('ln-soiled').value) || 0
    };
    try {
        const res = await fetch('/api/laundry', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            if (window.showToast) window.showToast('Linen batch logged!');
            document.getElementById('laundryForm').reset();
            window.hmsLoadLaundry();
        } else {
            const err = await res.json();
            if (window.showToast) window.showToast(err.error || 'Failed to save laundry batch', 'error');
        }
    } catch(e) {}
};

window.hmsUpdateLaundryStatus = function(batchId, status) {
    updateModuleStatus(`/api/laundry/${batchId}/status`, { status }, window.hmsLoadLaundry);
};

// -------------------------------------------------------------
// 12. MORTUARY REGISTER
// -------------------------------------------------------------
window.hmsLoadMortuary = async function() {
    try {
        const res = await fetch('/api/mortuary');
        if (!res.ok) return;
        const list = await res.json();
        const tbody = document.getElementById('mortuaryTableBody');
        if (!tbody) return;
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; color:var(--text-muted);">No mortuary entries found.</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(m => `
            <tr>
                <td>#MOR-${m.entry_id}</td>
                <td><code>${esc(m.deceased_uhid)}</code></td>
                <td><strong>${esc(m.deceased_name)}</strong></td>
                <td><small>${esc(m.cause_of_death)}</small></td>
                <td><strong>${esc(m.cold_chamber_no)}</strong></td>
                <td><small>${esc(m.received_at)}</small></td>
                <td><span class="badge ${m.status === 'Released' ? 'badge-secondary' : 'badge-danger'}">${esc(m.status)}</span></td>
                <td>${esc(m.released_to || 'In Chamber')}</td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="window.hmsUpdateMortuaryStatus(${m.entry_id}, 'Released', 'Next of Kin / Police Clearance')">Release</button>
                </td>
            </tr>
        `).join('');
    } catch(e) {}
};

window.hmsSaveMortuary = async function(e) {
    e.preventDefault();
    const payload = {
        deceased_uhid: document.getElementById('mor-uhid').value.trim(),
        deceased_name: document.getElementById('mor-name').value.trim(),
        cause_of_death: document.getElementById('mor-cause').value.trim(),
        cold_chamber_no: document.getElementById('mor-chamber').value.trim()
    };
    try {
        const res = await fetch('/api/mortuary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            if (window.showToast) window.showToast('Decedent intake recorded!');
            document.getElementById('mortuaryForm').reset();
            window.hmsLoadMortuary();
        } else {
            const err = await res.json();
            if (window.showToast) window.showToast(err.error || 'Failed to record mortuary intake', 'error');
        }
    } catch(e) {}
};

window.hmsUpdateMortuaryStatus = function(entryId, status, releasedTo = null) {
    updateModuleStatus(`/api/mortuary/${entryId}/status`, { status, released_to: releasedTo }, window.hmsLoadMortuary);
};

// -------------------------------------------------------------
// 13. SECURITY & GATE LOG
// -------------------------------------------------------------
window.hmsLoadSecurity = async function() {
    try {
        const res = await fetch('/api/security-log');
        if (!res.ok) return;
        const list = await res.json();
        const tbody = document.getElementById('securityLogTableBody');
        if (!tbody) return;
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; color:var(--text-muted);">No security log entries found.</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(s => `
            <tr>
                <td>#SEC-${s.log_id}</td>
                <td>${esc(s.gate_number)}</td>
                <td><strong>${esc(s.visitor_name)}</strong></td>
                <td><code>${esc(s.badge_number)}</code></td>
                <td>${esc(s.purpose)}</td>
                <td>${esc(s.vehicle_number || '--')}</td>
                <td><small>${esc(s.entry_time)}</small></td>
                <td><span class="badge ${s.status === 'Inside Campus' ? 'badge-primary' : 'badge-secondary'}">${esc(s.status)}</span></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="window.hmsUpdateSecurityStatus(${s.log_id}, 'Exited')">Log Exit</button>
                </td>
            </tr>
        `).join('');
    } catch(e) {}
};

window.hmsSaveSecurity = async function(e) {
    e.preventDefault();
    const payload = {
        gate_number: document.getElementById('sec-gate').value,
        visitor_name: document.getElementById('sec-visitor').value.trim(),
        badge_number: document.getElementById('sec-badge').value.trim(),
        purpose: document.getElementById('sec-purpose').value.trim(),
        vehicle_number: document.getElementById('sec-vehicle').value.trim()
    };
    try {
        const res = await fetch('/api/security-log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            if (window.showToast) window.showToast('Security badge checked in!');
            document.getElementById('securityForm').reset();
            window.hmsLoadSecurity();
        } else {
            const err = await res.json();
            if (window.showToast) window.showToast(err.error || 'Failed to log gate entry', 'error');
        }
    } catch(e) {}
};

window.hmsUpdateSecurityStatus = function(logId, status) {
    updateModuleStatus(`/api/security-log/${logId}/status`, { status }, window.hmsLoadSecurity);
};

// -------------------------------------------------------------
// 14. FACILITY SAFETY CHECKLISTS
// -------------------------------------------------------------
window.hmsLoadSafetyChecklists = async function() {
    try {
        const res = await fetch('/api/safety-checklists');
        if (!res.ok) return;
        const list = await res.json();
        const tbody = document.getElementById('safetyChecklistsTableBody');
        if (!tbody) return;
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; color:var(--text-muted);">No safety rounds recorded.</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(c => `
            <tr>
                <td>#SFT-${c.checklist_id}</td>
                <td><strong>${c.o2_manifold_psi} PSI</strong></td>
                <td>${c.vacuum_psi} PSI</td>
                <td><span class="badge ${c.fire_alarm_ok ? 'badge-success' : 'badge-danger'}">${c.fire_alarm_ok ? 'Normal' : 'Fault'}</span></td>
                <td>${c.dg_set_fuel_pct}%</td>
                <td>${esc(c.inspected_by)}</td>
                <td><small>${esc(c.created_at)}</small></td>
                <td><span class="badge ${c.status === 'Verified' ? 'badge-success' : 'badge-warning'}">${esc(c.status)}</span></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="window.hmsUpdateSafetyStatus(${c.checklist_id}, 'Verified')">Verify</button>
                </td>
            </tr>
        `).join('');
    } catch(e) {}
};

window.hmsSaveSafetyChecklist = async function(e) {
    e.preventDefault();
    const payload = {
        o2_manifold_psi: parseFloat(document.getElementById('sft-o2').value),
        vacuum_psi: parseFloat(document.getElementById('sft-vacuum').value),
        fire_alarm_ok: parseInt(document.getElementById('sft-fire').value),
        dg_set_fuel_pct: parseFloat(document.getElementById('sft-fuel').value),
        notes: document.getElementById('sft-notes').value.trim()
    };
    try {
        const res = await fetch('/api/safety-checklists', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            if (window.showToast) window.showToast('Life-safety audit round submitted!');
            document.getElementById('safetyChecklistForm').reset();
            window.hmsLoadSafetyChecklists();
        } else {
            const err = await res.json();
            if (window.showToast) window.showToast(err.error || 'Failed to submit checklist', 'error');
        }
    } catch(e) {}
};

window.hmsUpdateSafetyStatus = function(chkId, status) {
    updateModuleStatus(`/api/safety-checklists/${chkId}/status`, { status }, window.hmsLoadSafetyChecklists);
};

// -------------------------------------------------------------
// 15. INFECTION CONTROL
// -------------------------------------------------------------
window.hmsLoadInfectionControl = async function() {
    try {
        const res = await fetch('/api/infection-control');
        if (!res.ok) return;
        const list = await res.json();
        const tbody = document.getElementById('infectionControlTableBody');
        if (!tbody) return;
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="10" style="text-align:center; color:var(--text-muted);">No active HAI surveillance cases found.</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(i => `
            <tr>
                <td>#HAI-${i.case_id}</td>
                <td><code>${esc(i.uhid)}</code></td>
                <td><strong>${esc(i.patient_name)}</strong></td>
                <td>${esc(i.ward_name)}</td>
                <td><span class="badge badge-warning">${esc(i.infection_type)}</span></td>
                <td><em>${esc(i.organism_isolated || 'Pending Culture')}</em></td>
                <td><span class="badge ${i.isolation_required ? 'badge-danger' : 'badge-secondary'}">${i.isolation_required ? 'Isolation Active' : 'Standard'}</span></td>
                <td><span class="badge ${i.alert_level === 'High' ? 'badge-danger' : 'badge-warning'}">${esc(i.alert_level)}</span></td>
                <td><small>${esc(i.reported_at)}</small></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="window.hmsUpdateInfectionStatus(${i.case_id}, 'Resolved')">Resolve</button>
                </td>
            </tr>
        `).join('');
    } catch(e) {}
};

window.hmsSaveInfectionControl = async function(e) {
    e.preventDefault();
    const payload = {
        uhid: document.getElementById('inf-uhid').value.trim(),
        patient_name: document.getElementById('inf-patient').value.trim(),
        ward_name: document.getElementById('inf-ward').value.trim(),
        infection_type: document.getElementById('inf-type').value,
        organism_isolated: document.getElementById('inf-organism').value.trim(),
        isolation_required: parseInt(document.getElementById('inf-isolation').value)
    };
    try {
        const res = await fetch('/api/infection-control', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            if (window.showToast) window.showToast('HAI surveillance case logged!');
            document.getElementById('infectionForm').reset();
            window.hmsLoadInfectionControl();
        } else {
            const err = await res.json();
            if (window.showToast) window.showToast(err.error || 'Failed to log infection', 'error');
        }
    } catch(e) {}
};

window.hmsUpdateInfectionStatus = function(caseId, status) {
    updateModuleStatus(`/api/infection-control/${caseId}/status`, { status }, window.hmsLoadInfectionControl);
};

// -------------------------------------------------------------
// 16. PATIENT FEEDBACK & CSAT
// -------------------------------------------------------------
window.hmsLoadFeedback = async function() {
    try {
        const res = await fetch('/api/feedback');
        if (!res.ok) return;
        const list = await res.json();
        const tbody = document.getElementById('feedbackTableBody');
        if (!tbody) return;
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:var(--text-muted);">No patient feedback records found.</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(f => `
            <tr>
                <td>#CSAT-${f.feedback_id}</td>
                <td><code>${esc(f.uhid || 'Anonymous')}</code></td>
                <td><strong>${esc(f.department)}</strong></td>
                <td><strong style="color:#eab308;">${'★'.repeat(f.rating)}${'☆'.repeat(5 - f.rating)}</strong> (${f.rating}/5)</td>
                <td><small>${esc(f.comments)}</small></td>
                <td><span class="badge ${f.status === 'Resolved' ? 'badge-success' : 'badge-warning'}">${esc(f.status)}</span></td>
                <td><small>${esc(f.resolution_notes || '--')}</small></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="window.hmsUpdateFeedbackStatus(${f.feedback_id}, 'Resolved')">Resolve</button>
                </td>
            </tr>
        `).join('');
    } catch(e) {}
};

window.hmsSaveFeedback = async function(e) {
    e.preventDefault();
    const payload = {
        uhid: document.getElementById('fb-uhid').value.trim() || null,
        department: document.getElementById('fb-dept').value,
        rating: parseInt(document.getElementById('fb-rating').value) || 5,
        comments: document.getElementById('fb-comments').value.trim()
    };
    try {
        const res = await fetch('/api/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            if (window.showToast) window.showToast('Patient feedback recorded! Thank you.');
            document.getElementById('feedbackForm').reset();
            window.hmsLoadFeedback();
        } else {
            const err = await res.json();
            if (window.showToast) window.showToast(err.error || 'Failed to submit feedback', 'error');
        }
    } catch(e) {}
};

window.hmsUpdateFeedbackStatus = function(fbId, status) {
    updateModuleStatus(`/api/feedback/${fbId}/status`, { status, resolution_notes: 'Reviewed in monthly quality committee.' }, window.hmsLoadFeedback);
};

// -------------------------------------------------------------
// 17. MORBIDITY & MORTALITY (M&M) REVIEWS
// -------------------------------------------------------------
window.hmsLoadMmReviews = async function() {
    try {
        const res = await fetch('/api/mm-reviews');
        if (!res.ok) return;
        const list = await res.json();
        const tbody = document.getElementById('mmReviewsTableBody');
        if (!tbody) return;
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; color:var(--text-muted);">No M&M reviews found.</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(m => `
            <tr>
                <td>#MM-${m.review_id}</td>
                <td><code>${esc(m.uhid)}</code></td>
                <td><strong>${esc(m.patient_name)}</strong></td>
                <td>${esc(m.primary_diagnosis)}</td>
                <td>${esc(m.reviewer_doctor)}</td>
                <td><span class="badge badge-warning">${esc(m.root_cause_category)}</span></td>
                <td><span class="badge ${m.status === 'Closed' ? 'badge-success' : 'badge-primary'}">${esc(m.status)}</span></td>
                <td><small>${esc(m.review_date)}</small></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="window.hmsUpdateMmReviewStatus(${m.review_id}, 'Closed')">Close Review</button>
                </td>
            </tr>
        `).join('');
    } catch(e) {}
};

window.hmsSaveMmReview = async function(e) {
    e.preventDefault();
    const payload = {
        uhid: document.getElementById('mm-uhid').value.trim(),
        patient_name: document.getElementById('mm-patient').value.trim(),
        primary_diagnosis: document.getElementById('mm-diagnosis').value.trim(),
        reviewer_doctor: document.getElementById('mm-reviewer').value.trim(),
        root_cause_category: document.getElementById('mm-rca').value,
        findings: document.getElementById('mm-findings').value.trim()
    };
    try {
        const res = await fetch('/api/mm-reviews', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            if (window.showToast) window.showToast('M&M Case Review filed successfully!');
            document.getElementById('mmReviewForm').reset();
            window.hmsLoadMmReviews();
        } else {
            const err = await res.json();
            if (window.showToast) window.showToast(err.error || 'Failed to file review', 'error');
        }
    } catch(e) {}
};

window.hmsUpdateMmReviewStatus = function(revId, status) {
    updateModuleStatus(`/api/mm-reviews/${revId}/status`, { status }, window.hmsLoadMmReviews);
};
