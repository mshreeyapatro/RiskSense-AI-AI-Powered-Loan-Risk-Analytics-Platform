/* ============================================================
   RiskSense AI — Portfolio Analyzer JavaScript
   Manual entries, CSV upload, Charts, Risk Aggregation
   ============================================================ */

let portfolioEntries = [];
let portfolioDonutChart = null;
let portfolioBarChart = null;

const SAMPLE_PORTFOLIO = [
    { loan_type:'Home Loan', loan_amount:4500000, tenure:240, interest:8.5, purpose:'Home Renovation', employment:'Salaried', income:120000, cibil:780, emis:5000, dti:0.22, age:38, gender:'Male', dependents:2, property:'Owned' },
    { loan_type:'Personal Loan', loan_amount:250000, tenure:24, interest:16.5, purpose:'Wedding', employment:'Unemployed', income:15000, cibil:480, emis:12000, dti:0.78, age:25, gender:'Female', dependents:0, property:'Rented' },
    { loan_type:'Business Loan', loan_amount:2000000, tenure:60, interest:14.0, purpose:'Business Expansion', employment:'Self-Employed', income:90000, cibil:650, emis:20000, dti:0.55, age:44, gender:'Male', dependents:3, property:'Owned' },
    { loan_type:'Car Loan', loan_amount:600000, tenure:48, interest:10.5, purpose:'Vehicle Purchase', employment:'Salaried', income:60000, cibil:710, emis:8000, dti:0.32, age:31, gender:'Male', dependents:1, property:'Rented' },
    { loan_type:'Education Loan', loan_amount:800000, tenure:84, interest:9.0, purpose:'Education', employment:'Student', income:0, cibil:0, emis:0, dti:0, age:22, gender:'Female', dependents:0, property:'Rented' },
    { loan_type:'Home Loan', loan_amount:6000000, tenure:300, interest:7.9, purpose:'Home Purchase', employment:'Business Owner', income:200000, cibil:820, emis:10000, dti:0.18, age:48, gender:'Male', dependents:4, property:'Jointly Owned' },
];

function fmtAmount(n) {
    if (n >= 10000000) return '$' + (n/10000000).toFixed(1) + 'Cr';
    if (n >= 100000) return '$' + (n/100000).toFixed(1) + 'L';
    if (n >= 1000) return '$' + (n/1000).toFixed(0) + 'K';
    return '$' + n;
}

function renderEntries() {
    const el = document.getElementById('portfolioEntries');
    const countEl = document.getElementById('entryCount');
    if (countEl) countEl.textContent = portfolioEntries.length;
    if (!el) return;

    if (portfolioEntries.length === 0) {
        el.innerHTML = '<div style="text-align:center;padding:var(--space-xl);color:var(--text-tertiary);font-size:0.82rem;">No entries yet</div>';
        return;
    }

    el.innerHTML = portfolioEntries.map((e, i) => `
        <div class="portfolio-entry">
            <div class="entry-info">
                <div class="entry-type">${e.loan_type}</div>
                <div class="entry-amount">${fmtAmount(e.loan_amount)} · CIBIL: ${e.cibil || '—'}</div>
            </div>
            <button class="entry-remove" onclick="removeEntry(${i})" aria-label="Remove entry">✕</button>
        </div>
    `).join('');
}

function removeEntry(idx) {
    portfolioEntries.splice(idx, 1);
    renderEntries();
}

async function analyzePortfolio() {
    if (portfolioEntries.length === 0) {
        if (window.showToast) showToast('Add at least one entry to analyze', 'warning');
        return;
    }

    const btn = document.getElementById('analyzePortfolioBtn');
    if (btn) { btn.disabled = true; btn.textContent = '⏳ Analyzing...'; }

    try {
        const response = await fetch('/api/batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ applications: portfolioEntries })
        });

        if (!response.ok) throw new Error('Server error');
        const data = await response.json();
        renderPortfolioResults(data);

        if (window.showToast) showToast(`Portfolio analyzed — ${data.fraud_count} high-risk loans identified`, data.fraud_count > 0 ? 'warning' : 'success');
    } catch(err) {
        if (window.showToast) showToast('Analysis failed: ' + err.message, 'danger');
    } finally {
        if (btn) { btn.disabled = false; btn.textContent = '🔍 Analyze Portfolio'; }
    }
}

function renderPortfolioResults(data) {
    document.getElementById('portfolioEmpty').style.display = 'none';
    document.getElementById('portfolioAnalysisResults').style.display = 'block';

    // KPIs
    document.getElementById('pkpiValue').textContent = fmtAmount(data.total_portfolio_value || 0);
    document.getElementById('pkpiExposure').textContent = fmtAmount(data.estimated_fraud_exposure || 0);
    document.getElementById('pkpiFraudRate').textContent = (data.fraud_rate || 0) + '%';
    const avgRisk = data.results?.length > 0 ? Math.round(data.results.reduce((s,r) => s + (r.risk_score||0), 0) / data.results.length) : 0;
    document.getElementById('pkpiAvgRisk').textContent = avgRisk + '/100';

    // Donut Chart
    const fraudCount = data.fraud_count || 0;
    const genuineCount = (data.total || 0) - fraudCount;

    if (portfolioDonutChart) portfolioDonutChart.destroy();
    const dCtx = document.getElementById('portfolioDonut')?.getContext('2d');
    if (dCtx) {
        portfolioDonutChart = new Chart(dCtx, {
            type: 'doughnut',
            data: {
                labels: ['Fraud', 'Genuine'],
                datasets: [{
                    data: [fraudCount, genuineCount],
                    backgroundColor: ['rgba(239,68,68,0.75)', 'rgba(16,185,129,0.75)'],
                    borderColor: 'transparent', borderWidth: 0, hoverOffset: 4,
                }]
            },
            options: {
                cutout: '70%', plugins: { legend: { display: false } },
                animation: { animateRotate: true, duration: 800 }
            }
        });
    }

    // Bar Chart by Loan Type
    const typeMap = {};
    (data.results || []).forEach(r => {
        if (r.loan_type) {
            if (!typeMap[r.loan_type]) typeMap[r.loan_type] = { total: 0, fraud: 0 };
            typeMap[r.loan_type].total++;
            if (r.is_fraud) typeMap[r.loan_type].fraud++;
        }
    });

    if (portfolioBarChart) portfolioBarChart.destroy();
    const bCtx = document.getElementById('portfolioTypeBar')?.getContext('2d');
    if (bCtx) {
        const labels = Object.keys(typeMap);
        portfolioBarChart = new Chart(bCtx, {
            type: 'bar',
            data: {
                labels: labels.map(l => l.split(' ')[0]),
                datasets: [
                    { label: 'Genuine', data: labels.map(l => typeMap[l].total - typeMap[l].fraud), backgroundColor: 'rgba(16,185,129,0.6)', borderRadius: 3 },
                    { label: 'Fraud', data: labels.map(l => typeMap[l].fraud), backgroundColor: 'rgba(239,68,68,0.6)', borderRadius: 3 },
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                scales: {
                    x: { stacked: true, grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.4)', font: { size: 9 } } },
                    y: { stacked: true, grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: 'rgba(255,255,255,0.4)', font: { size: 9 }, stepSize: 1 } }
                },
                plugins: { legend: { display: false } },
                animation: { duration: 700 }
            }
        });
    }

    // Breakdown Table
    const criticalAmt = (data.results||[]).filter(r => r.risk_level === 'Critical').reduce((s,r) => s + parseFloat(r.loan_amount||0), 0);
    const highAmt = (data.results||[]).filter(r => r.risk_level === 'High').reduce((s,r) => s + parseFloat(r.loan_amount||0), 0);
    const modAmt = (data.results||[]).filter(r => r.risk_level === 'Moderate').reduce((s,r) => s + parseFloat(r.loan_amount||0), 0);
    const lowAmt = (data.results||[]).filter(r => r.risk_level === 'Low').reduce((s,r) => s + parseFloat(r.loan_amount||0), 0);

    const segments = [
        { name: '🔴 Critical', count: (data.results||[]).filter(r=>r.risk_level==='Critical').length, amt: criticalAmt },
        { name: '🟠 High', count: (data.results||[]).filter(r=>r.risk_level==='High').length, amt: highAmt },
        { name: '🟡 Moderate', count: (data.results||[]).filter(r=>r.risk_level==='Moderate').length, amt: modAmt },
        { name: '🟢 Low', count: (data.results||[]).filter(r=>r.risk_level==='Low').length, amt: lowAmt },
    ];

    const tbody = document.getElementById('portfolioBreakdown');
    if (tbody) {
        tbody.innerHTML = segments.map(s => `
            <tr>
                <td style="font-size:0.82rem;">${s.name}</td>
                <td style="font-family:var(--font-mono);font-size:0.82rem;">${s.count}</td>
                <td style="color:var(--text-secondary);font-size:0.8rem;">${data.total > 0 ? Math.round(s.count/data.total*100) : 0}%</td>
                <td style="font-family:var(--font-mono);font-size:0.8rem;">${fmtAmount(s.amt)}</td>
            </tr>
        `).join('');
    }
}

function exportPortfolioReport() {
    if (window.showToast) showToast('Portfolio report export coming soon!', 'info');
}

document.addEventListener('DOMContentLoaded', () => {
    renderEntries();

    // Add Entry
    document.getElementById('addEntryBtn')?.addEventListener('click', () => {
        const lt = document.getElementById('pLoanType')?.value;
        const amt = parseFloat(document.getElementById('pLoanAmount')?.value || 0);
        const cibil = parseInt(document.getElementById('pCibil')?.value || 600);
        const dti = parseFloat(document.getElementById('pDti')?.value || 0.3);

        if (!amt || amt <= 0) { if (window.showToast) showToast('Enter a valid loan amount', 'warning'); return; }

        portfolioEntries.push({
            loan_type: lt, loan_amount: amt, tenure: 60, interest: 12,
            purpose: 'General', employment: 'Salaried', income: 50000,
            cibil, emis: 5000, dti, age: 35, gender: 'Male', dependents: 1, property: 'Rented'
        });
        document.getElementById('pLoanAmount').value = '';
        renderEntries();
        if (window.showToast) showToast('Entry added!', 'success');
    });

    // CSV Upload
    const csvInput = document.getElementById('portfolioCsvInput');
    const uploadZone = document.getElementById('portfolioUploadZone');
    if (csvInput) {
        csvInput.addEventListener('change', e => {
            const file = e.target.files[0];
            if (file) {
                Papa.parse(file, {
                    header: true, skipEmptyLines: true,
                    complete: r => {
                        portfolioEntries = r.data.slice(0, 500).map(row => ({
                            loan_type: row.loan_type || 'Personal Loan',
                            loan_amount: parseFloat(row.loan_amount || 0),
                            tenure: parseInt(row.tenure || 36),
                            interest: parseFloat(row.interest || 12),
                            purpose: row.purpose || 'Other',
                            employment: row.employment || 'Salaried',
                            income: parseFloat(row.income || 0),
                            cibil: parseInt(row.cibil || 600),
                            emis: parseFloat(row.emis || 0),
                            dti: parseFloat(row.dti || 0.3),
                            age: parseInt(row.age || 30),
                            gender: row.gender || 'Male',
                            dependents: parseInt(row.dependents || 0),
                            property: row.property || 'Rented',
                        }));
                        renderEntries();
                        if (window.showToast) showToast(`${portfolioEntries.length} entries loaded`, 'success');
                    }
                });
            }
        });
    }

    // Analyze
    document.getElementById('analyzePortfolioBtn')?.addEventListener('click', analyzePortfolio);

    // Load Sample
    document.getElementById('loadSamplePortfolioBtn')?.addEventListener('click', () => {
        portfolioEntries = [...SAMPLE_PORTFOLIO];
        renderEntries();
        if (window.showToast) showToast('Sample portfolio loaded! Click Analyze to run.', 'info');
    });

    // Export
    document.getElementById('exportPortfolioBtn')?.addEventListener('click', exportPortfolioReport);
});
