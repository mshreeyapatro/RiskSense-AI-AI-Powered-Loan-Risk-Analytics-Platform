/* ============================================================
   RiskSense AI — Batch Screening JavaScript
   CSV Upload, PapaParse, Progress Bar, Results Table
   ============================================================ */

const BATCH_SAMPLE = [
    { loan_type:"Home Loan", loan_amount:4500000, tenure:240, interest:8.5, purpose:"Home Renovation", employment:"Salaried", income:120000, cibil:780, emis:5000, dti:0.22, age:38, gender:"Male", dependents:2, property:"Owned" },
    { loan_type:"Personal Loan", loan_amount:250000, tenure:24, interest:16.5, purpose:"Wedding", employment:"Unemployed", income:15000, cibil:480, emis:12000, dti:0.78, age:25, gender:"Female", dependents:0, property:"Rented" },
    { loan_type:"Business Loan", loan_amount:2000000, tenure:60, interest:14.0, purpose:"Business Expansion", employment:"Self-Employed", income:90000, cibil:650, emis:20000, dti:0.55, age:44, gender:"Male", dependents:3, property:"Owned" },
    { loan_type:"Car Loan", loan_amount:600000, tenure:48, interest:10.5, purpose:"Vehicle Purchase", employment:"Salaried", income:60000, cibil:710, emis:8000, dti:0.32, age:31, gender:"Male", dependents:1, property:"Rented" },
    { loan_type:"Education Loan", loan_amount:800000, tenure:84, interest:9.0, purpose:"Education", employment:"Student", income:0, cibil:0, emis:0, dti:0.0, age:22, gender:"Female", dependents:0, property:"Rented" },
    { loan_type:"Personal Loan", loan_amount:150000, tenure:12, interest:18.0, purpose:"Debt Consolidation", employment:"Salaried", income:30000, cibil:520, emis:10000, dti:0.67, age:34, gender:"Other", dependents:2, property:"Rented" },
    { loan_type:"Home Loan", loan_amount:6000000, tenure:300, interest:7.9, purpose:"Home Renovation", employment:"Business Owner", income:200000, cibil:820, emis:10000, dti:0.18, age:48, gender:"Male", dependents:4, property:"Jointly Owned" },
    { loan_type:"Business Loan", loan_amount:5000000, tenure:36, interest:15.0, purpose:"Medical Emergency", employment:"Unemployed", income:5000, cibil:350, emis:0, dti:0.95, age:55, gender:"Female", dependents:3, property:"Rented" },
    { loan_type:"Car Loan", loan_amount:900000, tenure:60, interest:11.0, purpose:"Vehicle Purchase", employment:"Retired", income:25000, cibil:700, emis:3000, dti:0.28, age:62, gender:"Male", dependents:2, property:"Owned" },
    { loan_type:"Personal Loan", loan_amount:500000, tenure:36, interest:13.5, purpose:"Business Expansion", employment:"Self-Employed", income:75000, cibil:680, emis:12000, dti:0.45, age:39, gender:"Male", dependents:1, property:"Owned" },
];

let allResults = [];
let displayedResults = [];
let currentFilter = 'all';

function initBatch() {
    // File Input
    const fileInput = document.getElementById('csvFileInput');
    const uploadZone = document.getElementById('uploadZone');

    if (fileInput) {
        fileInput.addEventListener('change', e => {
            const file = e.target.files[0];
            if (file) processCSVFile(file);
        });
    }

    // Drag & Drop
    if (uploadZone) {
        uploadZone.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
        uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
        uploadZone.addEventListener('drop', e => {
            e.preventDefault();
            uploadZone.classList.remove('drag-over');
            const file = e.dataTransfer.files[0];
            if (file && file.name.endsWith('.csv')) processCSVFile(file);
            else if (window.showToast) showToast('Please upload a .csv file', 'warning');
        });
    }

    // Load Sample
    document.getElementById('loadSampleBtn')?.addEventListener('click', () => {
        runBatch(BATCH_SAMPLE);
    });

    // Download Template
    document.getElementById('downloadTemplateBtn')?.addEventListener('click', downloadTemplate);

    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            renderResultsTable();
        });
    });

    // Export CSV
    document.getElementById('exportCsvBtn')?.addEventListener('click', exportResults);
}

function processCSVFile(file) {
    if (window.showToast) showToast('Parsing CSV...', 'info');
    Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        complete: results => {
            const data = results.data;
            if (data.length === 0) {
                if (window.showToast) showToast('CSV is empty or invalid', 'danger');
                return;
            }
            if (data.length > 500) {
                if (window.showToast) showToast('Batch limited to 500 rows. Truncating.', 'warning');
            }
            // Map CSV columns to API fields
            const applications = data.slice(0, 500).map(row => ({
                loan_type: row.loan_type || row.LoanType || 'Personal Loan',
                loan_amount: parseFloat(row.loan_amount || row.LoanAmount || 0),
                tenure: parseInt(row.tenure || row.Tenure || 36),
                interest: parseFloat(row.interest || row.Interest || 12),
                purpose: row.purpose || row.Purpose || 'Other',
                employment: row.employment || row.Employment || 'Salaried',
                income: parseFloat(row.income || row.Income || 0),
                cibil: parseInt(row.cibil || row.CIBIL || 600),
                emis: parseFloat(row.emis || row.EMIs || 0),
                dti: parseFloat(row.dti || row.DTI || 0.3),
                age: parseInt(row.age || row.Age || 30),
                gender: row.gender || row.Gender || 'Male',
                dependents: parseInt(row.dependents || row.Dependents || 0),
                property: row.property || row.Property || 'Rented',
            }));
            runBatch(applications);
        },
        error: err => {
            if (window.showToast) showToast('CSV parse error: ' + err.message, 'danger');
        }
    });
}

async function runBatch(applications) {
    const progressSection = document.getElementById('progressSection');
    const batchSummary = document.getElementById('batchSummary');
    const resultsSection = document.getElementById('resultsSection');
    const progressFill = document.getElementById('progressFill');
    const progressLabel = document.getElementById('progressLabel');
    const progressPct = document.getElementById('progressPct');
    const progressStatus = document.getElementById('progressStatus');

    // Show progress
    if (batchSummary) batchSummary.style.display = 'none';
    if (resultsSection) resultsSection.style.display = 'none';
    if (progressSection) progressSection.style.display = 'block';

    // Fake progress animation while API processes
    let fakeProgress = 0;
    const progressInterval = setInterval(() => {
        fakeProgress = Math.min(fakeProgress + (Math.random() * 8), 85);
        if (progressFill) progressFill.style.width = fakeProgress + '%';
        if (progressPct) progressPct.textContent = Math.round(fakeProgress) + '%';
        if (progressStatus) progressStatus.textContent = `Processing ${Math.round((fakeProgress/100) * applications.length)} / ${applications.length} applications...`;
    }, 200);

    if (progressLabel) progressLabel.textContent = `Screening ${applications.length} applications...`;

    try {
        const response = await fetch('/api/batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ applications })
        });

        clearInterval(progressInterval);
        if (progressFill) progressFill.style.width = '100%';
        if (progressPct) progressPct.textContent = '100%';
        if (progressStatus) progressStatus.textContent = 'Complete!';

        if (!response.ok) throw new Error('Server error: ' + response.status);

        const data = await response.json();
        allResults = data.results || [];

        setTimeout(() => {
            if (progressSection) progressSection.style.display = 'none';
            renderSummary(data);
            renderResultsTable();
            if (batchSummary) batchSummary.style.display = 'grid';
            if (resultsSection) resultsSection.style.display = 'block';
            if (window.showToast) showToast(`Screened ${data.total} applications — ${data.fraud_count} fraud flagged`, data.fraud_count > 0 ? 'warning' : 'success');

            // Fire alert if fraud found
            if (data.fraud_count > 0 && window.AlertSystem) {
                AlertSystem.addAlert(`Batch screening complete: ${data.fraud_count}/${data.total} applications flagged as fraud (${data.fraud_rate}%)`, 'fraud');
            }
        }, 500);

    } catch (err) {
        clearInterval(progressInterval);
        if (progressSection) progressSection.style.display = 'none';
        if (window.showToast) showToast('Batch failed: ' + err.message, 'danger');
    }
}

function renderSummary(data) {
    const fmt = n => n >= 1000000 ? '$' + (n/1000000).toFixed(1) + 'M' : n >= 1000 ? '$' + (n/1000).toFixed(0) + 'K' : '$' + n;
    document.getElementById('bkpiTotal').textContent = data.total;
    document.getElementById('bkpiFraud').textContent = data.fraud_count;
    document.getElementById('bkpiRate').textContent = data.fraud_rate + '%';
    document.getElementById('bkpiExposure').textContent = fmt(data.estimated_fraud_exposure || 0);
}

function renderResultsTable() {
    const tbody = document.getElementById('resultsTbody');
    if (!tbody) return;

    let filtered = allResults;
    if (currentFilter === 'fraud') filtered = allResults.filter(r => r.is_fraud);
    else if (currentFilter === 'genuine') filtered = allResults.filter(r => !r.is_fraud);
    displayedResults = filtered;

    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:2rem;color:var(--text-tertiary);">No results match filter</td></tr>';
        return;
    }

    const riskClass = level => level === 'Critical' ? 'high' : level === 'High' ? 'high' : level === 'Moderate' ? 'medium' : 'low';

    tbody.innerHTML = filtered.map(r => `
        <tr class="${r.is_fraud ? 'fraud-row' : ''}">
            <td style="font-family:var(--font-mono);color:var(--text-tertiary);font-size:0.75rem;">#${r.index}</td>
            <td>${r.loan_type || '—'}</td>
            <td style="font-family:var(--font-mono);">$${Number(r.loan_amount||0).toLocaleString()}</td>
            <td><span class="badge ${r.is_fraud ? 'badge-danger' : 'badge-success'}">${r.is_fraud ? '🚨 FRAUD' : '✅ GENUINE'}</span></td>
            <td style="font-family:var(--font-mono);">${((r.probability||0)*100).toFixed(1)}%</td>
            <td><span class="risk-pill ${riskClass(r.risk_level || '')}">${r.risk_score || 0}/100</span></td>
            <td style="font-size:0.78rem;color:var(--text-secondary);">${r.decision || '—'}</td>
        </tr>
    `).join('');
}

function downloadTemplate() {
    const cols = ['loan_type','loan_amount','tenure','interest','purpose','employment','income','cibil','emis','dti','property','age','gender','dependents'];
    const sample = ['Home Loan','500000','60','12.5','Home Renovation','Salaried','60000','720','5000','0.28','Owned','35','Male','2'];
    const csv = cols.join(',') + '\n' + sample.join(',');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'risksense_batch_template.csv'; a.click();
    URL.revokeObjectURL(url);
    if (window.showToast) showToast('Template downloaded!', 'success');
}

function exportResults() {
    if (!allResults.length) { if (window.showToast) showToast('No results to export', 'warning'); return; }
    const cols = ['index','loan_type','loan_amount','is_fraud','probability','risk_score','risk_level','decision'];
    const rows = allResults.map(r => cols.map(c => JSON.stringify(r[c] ?? '')).join(','));
    const csv = cols.join(',') + '\n' + rows.join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'risksense_batch_results_' + Date.now() + '.csv'; a.click();
    URL.revokeObjectURL(url);
    if (window.showToast) showToast('Results exported!', 'success');
}

document.addEventListener('DOMContentLoaded', initBatch);
