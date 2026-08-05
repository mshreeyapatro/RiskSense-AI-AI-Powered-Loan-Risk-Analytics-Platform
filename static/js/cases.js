/* ============================================================
   RiskSense AI — Case Management JavaScript
   localStorage-based CRUD, Search, Filter, Modal
   ============================================================ */

const CASES_KEY = 'risksense_cases';
let allCases = [];
let editingCaseId = null;
let searchQuery = '';
let statusFilter = 'all';

// ---- Data Persistence ----
function loadCases() {
    try { allCases = JSON.parse(localStorage.getItem(CASES_KEY) || '[]'); }
    catch(e) { allCases = []; }
}

function saveCases() {
    try { localStorage.setItem(CASES_KEY, JSON.stringify(allCases)); }
    catch(e) { console.warn('Could not save cases:', e); }
}

// ---- CRUD ----
function createCase(data = {}) {
    const id = 'CASE-' + String(Date.now()).slice(-6);
    const newCase = {
        id,
        loan_type: data.loan_type || 'Unknown',
        loan_amount: data.loan_amount || 0,
        risk_score: data.risk_score || 0,
        risk_level: data.risk_level || 'Unknown',
        probability: data.probability || 0,
        is_fraud: data.is_fraud || false,
        decision: data.decision || '',
        status: 'open',
        notes: '',
        created: new Date().toLocaleString(),
        updated: new Date().toLocaleString(),
    };
    allCases.unshift(newCase);
    saveCases();
    return newCase;
}

function updateCase(id, updates) {
    const idx = allCases.findIndex(c => c.id === id);
    if (idx === -1) return;
    allCases[idx] = { ...allCases[idx], ...updates, updated: new Date().toLocaleString() };
    saveCases();
}

function deleteCase(id) {
    allCases = allCases.filter(c => c.id !== id);
    saveCases();
}

// ---- Counts ----
function updateCounts() {
    document.getElementById('openCount').textContent = allCases.filter(c => c.status === 'open').length;
    document.getElementById('reviewCount').textContent = allCases.filter(c => c.status === 'reviewing').length;
    document.getElementById('resolvedCount').textContent = allCases.filter(c => c.status === 'resolved').length;
}

// ---- Render ----
function getFilteredCases() {
    return allCases.filter(c => {
        const matchesStatus = statusFilter === 'all' || c.status === statusFilter;
        const matchesSearch = !searchQuery ||
            c.id.toLowerCase().includes(searchQuery) ||
            (c.loan_type || '').toLowerCase().includes(searchQuery) ||
            (c.notes || '').toLowerCase().includes(searchQuery) ||
            String(c.loan_amount).includes(searchQuery);
        return matchesStatus && matchesSearch;
    });
}

function renderCases() {
    const grid = document.getElementById('casesGrid');
    if (!grid) return;
    updateCounts();

    const filtered = getFilteredCases();
    if (filtered.length === 0) {
        grid.innerHTML = `
            <div class="empty-cases">
                <div class="icon">📂</div>
                <h3>${allCases.length === 0 ? 'No Cases Yet' : 'No Cases Match Filter'}</h3>
                <p>${allCases.length === 0 ? 'Cases are automatically created when you run a fraud analysis. You can also create them manually.' : 'Try changing the search or status filter.'}</p>
                ${allCases.length === 0 ? '<a href="/prediction" class="btn btn-primary btn-sm" style="margin-top:1rem;">Run Analysis →</a>' : ''}
            </div>`;
        return;
    }

    const riskColor = level => level === 'Critical' ? 'var(--color-danger)' : level === 'High' ? 'var(--color-warning)' : level === 'Moderate' ? 'var(--color-warning)' : 'var(--color-success)';

    grid.innerHTML = filtered.map(c => `
        <div class="glass-card case-card reveal" data-case-id="${c.id}">
            <div class="case-header">
                <div>
                    <div class="case-id">${c.id}</div>
                    <div class="case-title">${c.loan_type || 'Unknown'} — $${Number(c.loan_amount||0).toLocaleString()}</div>
                </div>
                <span class="case-status ${c.status}">${c.status === 'open' ? '🔴 Open' : c.status === 'reviewing' ? '🟡 Under Review' : '🟢 Resolved'}</span>
            </div>
            <div class="case-meta">Created: ${c.created}</div>
            <div class="case-tags">
                <span class="case-tag">${c.is_fraud ? '🚨 Fraud' : '✅ Genuine'}</span>
                <span class="case-tag" style="color:${riskColor(c.risk_level)};">Risk: ${c.risk_score || 0}/100</span>
                <span class="case-tag">${c.risk_level || 'Unknown'}</span>
                ${c.probability ? `<span class="case-tag">${(c.probability*100).toFixed(1)}% prob.</span>` : ''}
            </div>
            ${c.notes ? `<div class="case-note">${c.notes.substring(0, 120)}${c.notes.length > 120 ? '…' : ''}</div>` : ''}
            <div class="case-actions">
                <button class="btn btn-sm btn-outline open-case-btn" data-id="${c.id}">📝 Details</button>
                <button class="btn btn-sm btn-outline" onclick="quickStatus('${c.id}', '${c.status === 'open' ? 'reviewing' : c.status === 'reviewing' ? 'resolved' : 'open'}')" style="font-size:0.72rem;">
                    ${c.status === 'open' ? '→ Review' : c.status === 'reviewing' ? '→ Resolve' : '→ Reopen'}
                </button>
                <button class="btn btn-sm btn-outline" onclick="confirmDelete('${c.id}')" style="color:var(--color-danger);border-color:var(--color-danger-bg);margin-left:auto;">🗑</button>
            </div>
        </div>
    `).join('');

    // Attach open buttons
    grid.querySelectorAll('.open-case-btn').forEach(btn => {
        btn.addEventListener('click', () => openCaseModal(btn.dataset.id));
    });
}

function quickStatus(id, newStatus) {
    updateCase(id, { status: newStatus });
    renderCases();
    const labels = { open: 'Open', reviewing: 'Under Review', resolved: 'Resolved' };
    if (window.showToast) showToast(`Case moved to ${labels[newStatus]}`, 'success');
}

function confirmDelete(id) {
    if (confirm('Delete this case? This cannot be undone.')) {
        deleteCase(id);
        renderCases();
        if (window.showToast) showToast('Case deleted', 'info');
    }
}

// ---- Modal ----
function openCaseModal(id) {
    const c = allCases.find(c => c.id === id);
    if (!c) return;
    editingCaseId = id;

    document.getElementById('modalCaseTitle').textContent = `${c.id} — ${c.loan_type}`;
    document.getElementById('modalNotes').value = c.notes || '';

    // Highlight current status
    document.querySelectorAll('.modal-status-btn').forEach(btn => {
        btn.className = 'modal-status-btn';
        if (btn.dataset.statusSet === c.status) {
            btn.classList.add(`active-${c.status}`);
        }
    });

    // Details
    document.getElementById('modalDetails').innerHTML = `
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:var(--space-sm);margin-bottom:var(--space-md);">
            ${[
                ['Loan Type', c.loan_type],
                ['Amount', '$' + Number(c.loan_amount||0).toLocaleString()],
                ['Risk Score', (c.risk_score || 0) + '/100'],
                ['Risk Level', c.risk_level || '—'],
                ['Probability', c.probability ? (c.probability*100).toFixed(1)+'%' : '—'],
                ['Decision', c.decision || '—'],
            ].map(([k, v]) => `
                <div style="padding:var(--space-sm);background:var(--glass-bg);border-radius:var(--radius-sm);">
                    <div style="font-size:0.68rem;color:var(--text-tertiary);font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:2px;">${k}</div>
                    <div style="font-size:0.85rem;font-weight:600;">${v}</div>
                </div>
            `).join('')}
        </div>
    `;

    const modal = document.getElementById('caseModal');
    if (modal) { modal.style.display = 'flex'; requestAnimationFrame(() => modal.classList.add('open')); }
    document.body.style.overflow = 'hidden';
}

function closeCaseModal() {
    const modal = document.getElementById('caseModal');
    if (modal) { modal.classList.remove('open'); setTimeout(() => modal.style.display = 'none', 300); }
    document.body.style.overflow = '';
    editingCaseId = null;
}

function saveCaseModal() {
    if (!editingCaseId) return;
    const notes = document.getElementById('modalNotes').value;

    // Get selected status from active button
    let selectedStatus = null;
    document.querySelectorAll('.modal-status-btn').forEach(btn => {
        if (btn.className.includes('active-')) selectedStatus = btn.dataset.statusSet;
    });

    const updates = { notes };
    if (selectedStatus) updates.status = selectedStatus;

    updateCase(editingCaseId, updates);
    closeCaseModal();
    renderCases();
    if (window.showToast) showToast('Case updated successfully', 'success');
}

// ---- Create Demo Case ----
function createDemoCase() {
    const types = ['Home Loan','Personal Loan','Car Loan','Business Loan','Education Loan'];
    const levels = ['Low','Moderate','High','Critical'];
    const demo = {
        loan_type: types[Math.floor(Math.random()*types.length)],
        loan_amount: Math.floor(Math.random() * 4000000) + 100000,
        risk_score: Math.floor(Math.random() * 100),
        risk_level: levels[Math.floor(Math.random()*levels.length)],
        probability: Math.random(),
        is_fraud: Math.random() > 0.5,
        decision: Math.random() > 0.5 ? 'BLOCK & ESCALATE' : 'MANUAL REVIEW',
    };
    const c = createCase(demo);
    renderCases();
    if (window.showToast) showToast(`Case ${c.id} created`, 'success');
    if (demo.is_fraud && window.AlertSystem) {
        AlertSystem.addAlert(`New fraud case created: ${c.id} — ${c.loan_type} $${c.loan_amount.toLocaleString()}`, 'fraud');
    }
}

// ---- Auto-sync from prediction results (stored in localStorage) ----
function syncFromHistory() {
    try {
        const dash = JSON.parse(localStorage.getItem('risksense_dashboard') || '{"analyses":[]}');
        const analyses = dash.analyses || [];
        // Create cases for fraud predictions that don't already have corresponding cases
        const existingIds = new Set(allCases.map(c => c.sourceId).filter(Boolean));
        analyses.filter(a => a.is_fraud && !existingIds.has(a.id)).forEach(a => {
            createCase({
                loan_type: a.loan_type,
                loan_amount: a.loan_amount,
                risk_score: a.risk_score,
                probability: a.probability,
                is_fraud: true,
                decision: a.decision || 'BLOCK & ESCALATE',
                sourceId: a.id,
            });
        });
    } catch(e) {}
}

// ---- Init ----
document.addEventListener('DOMContentLoaded', () => {
    loadCases();
    syncFromHistory();
    renderCases();

    // Search
    document.getElementById('casesSearch')?.addEventListener('input', e => {
        searchQuery = e.target.value.toLowerCase().trim();
        renderCases();
    });

    // Status filter
    document.querySelectorAll('.status-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            document.querySelectorAll('.status-chip').forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            statusFilter = chip.dataset.status;
            renderCases();
        });
    });

    // New Case button
    document.getElementById('newCaseBtn')?.addEventListener('click', createDemoCase);

    // Clear All
    document.getElementById('clearCasesBtn')?.addEventListener('click', () => {
        if (confirm('Clear all cases? This cannot be undone.')) {
            allCases = [];
            saveCases();
            renderCases();
            if (window.showToast) showToast('All cases cleared', 'info');
        }
    });

    // Modal status buttons
    document.querySelectorAll('.modal-status-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.modal-status-btn').forEach(b => {
                b.className = 'modal-status-btn';
            });
            btn.classList.add(`active-${btn.dataset.statusSet}`);
        });
    });

    // Modal close / save
    document.getElementById('modalClose')?.addEventListener('click', closeCaseModal);
    document.getElementById('modalCancel')?.addEventListener('click', closeCaseModal);
    document.getElementById('modalSave')?.addEventListener('click', saveCaseModal);

    // Close on backdrop click
    document.getElementById('caseModal')?.addEventListener('click', e => {
        if (e.target === e.currentTarget) closeCaseModal();
    });
});
