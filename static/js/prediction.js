/* ============================================================
   RiskSense AI — Prediction Page JavaScript
   Multi-step wizard, live risk meter, presets, share link,
   history drawer, PDF export, Chart.js
   ============================================================ */

// ============================================================
// MULTI-STEP FORM WIZARD
// ============================================================
const FormWizard = {
  currentStep: 1,
  totalSteps: 3,

  init() {
    this.updateStep(1);
    this.bindButtons();
    // If random_data was filled by server, auto-advance awareness
    if (document.querySelector('.form-step.active #loan_type option[selected]')) {
      // form was pre-filled — stay on step 1
    }
  },

  bindButtons() {
    document.querySelectorAll('[data-step-next]').forEach(btn => {
      btn.addEventListener('click', () => this.next());
    });
    document.querySelectorAll('[data-step-prev]').forEach(btn => {
      btn.addEventListener('click', () => this.prev());
    });
  },

  next() {
    if (this.currentStep < this.totalSteps) {
      this.updateStep(this.currentStep + 1);
    }
  },

  prev() {
    if (this.currentStep > 1) {
      this.updateStep(this.currentStep - 1);
    }
  },

  goTo(step) { this.updateStep(step); },

  updateStep(step) {
    this.currentStep = step;

    document.querySelectorAll('.step-dot').forEach((dot, i) => {
      dot.classList.remove('active', 'completed');
      if (i + 1 < step) dot.classList.add('completed');
      if (i + 1 === step) dot.classList.add('active');
    });

    document.querySelectorAll('.step-line').forEach((line, i) => {
      line.classList.toggle('active', i + 1 < step);
    });

    document.querySelectorAll('.form-step').forEach((panel, i) => {
      panel.classList.toggle('active', i + 1 === step);
    });

    if (step === 3) this.populateReview();
  },

  populateReview() {
    const form = document.getElementById('predictionForm');
    if (!form) return;
    const data = new FormData(form);
    const reviewEl = document.getElementById('reviewSummary');
    if (!reviewEl) return;

    const labels = {
      loan_type: 'Loan Type', loan_amount: 'Loan Amount ($)', tenure: 'Tenure (months)',
      interest: 'Interest Rate (%)', purpose: 'Purpose', employment: 'Employment',
      income: 'Monthly Income ($)', cibil: 'CIBIL Score', emis: 'Existing EMIs ($)',
      dti: 'Debt-to-Income', property: 'Property', age: 'Age',
      gender: 'Gender', dependents: 'Dependents'
    };

    let html = '<div class="grid grid-2 gap-md">';
    for (const [key, label] of Object.entries(labels)) {
      const val = data.get(key) || '—';
      html += `<div class="review-item"><span class="text-xs text-secondary">${label}</span><span class="font-semibold">${val}</span></div>`;
    }
    html += '</div>';
    reviewEl.innerHTML = html;
  }
};

// ============================================================
// LIVE RISK METER (Pure JS heuristic, instant feedback)
// ============================================================
const RiskMeter = {
  score: 0,
  panel: null,

  init() {
    this.panel = document.getElementById('liveRiskPanel');
    if (!this.panel) return;

    const fields = ['loan_amount', 'tenure', 'interest', 'income', 'cibil', 'emis', 'dti', 'age',
                    'dependents', 'loan_type', 'employment', 'property', 'purpose', 'gender'];

    fields.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('input', () => this.calculate());
        el.addEventListener('change', () => this.calculate());
      }
    });

    this.calculate();
  },

  calculate() {
    let score = 0;
    const get = id => {
      const el = document.getElementById(id);
      return el ? el.value : '';
    };

    const cibil = parseInt(get('cibil')) || 0;
    const dti = parseFloat(get('dti')) || 0;
    const income = parseFloat(get('income')) || 1;
    const loanAmount = parseFloat(get('loan_amount')) || 0;
    const tenure = parseInt(get('tenure')) || 1;
    const interest = parseFloat(get('interest')) || 0;
    const age = parseInt(get('age')) || 30;
    const emis = parseFloat(get('emis')) || 0;
    const dependents = parseInt(get('dependents')) || 0;
    const employment = get('employment');
    const property = get('property');
    const loanType = get('loan_type');

    // CIBIL Score risk (max 25 pts)
    if (cibil < 500) score += 25;
    else if (cibil < 600) score += 18;
    else if (cibil < 700) score += 10;
    else if (cibil < 750) score += 4;
    else score += 0;

    // DTI risk (max 20 pts)
    if (dti > 0.7) score += 20;
    else if (dti > 0.5) score += 14;
    else if (dti > 0.35) score += 7;

    // Loan-to-income ratio (max 20 pts)
    const loanToIncome = loanAmount / (income * 12 || 1);
    if (loanToIncome > 15) score += 20;
    else if (loanToIncome > 8) score += 12;
    else if (loanToIncome > 4) score += 5;

    // Employment risk (max 15 pts)
    const empRisk = { 'Unemployed': 15, 'Student': 10, 'Retired': 5, 'Self-Employed': 5 };
    score += empRisk[employment] || 0;

    // Interest rate risk (max 8 pts)
    if (interest > 16) score += 8;
    else if (interest > 13) score += 4;

    // EMI burden (max 7 pts)
    const emiToIncome = emis / (income || 1);
    if (emiToIncome > 0.5) score += 7;
    else if (emiToIncome > 0.3) score += 3;

    // Property risk (max 5 pts)
    if (property === 'Rented') score += 3;

    // Dependents risk
    if (dependents >= 4) score += 4;
    else if (dependents >= 2) score += 2;

    // Age extremes
    if (age < 22 || age > 60) score += 3;

    this.score = Math.min(score, 100);
    this.render();
  },

  render() {
    const panel = this.panel;
    if (!panel) return;

    const s = this.score;
    let level, color, emoji;
    if (s >= 70) { level = 'HIGH RISK'; color = '#ef4444'; emoji = '🔴'; }
    else if (s >= 45) { level = 'MEDIUM RISK'; color = '#f59e0b'; emoji = '🟡'; }
    else if (s >= 20) { level = 'LOW RISK'; color = '#10b981'; emoji = '🟢'; }
    else { level = 'MINIMAL RISK'; color = '#10b981'; emoji = '✅'; }

    panel.style.display = 'flex';

    const fill = panel.querySelector('.risk-meter-fill');
    const label = panel.querySelector('.risk-meter-label');
    const scoreEl = panel.querySelector('.risk-meter-score');
    const levelEl = panel.querySelector('.risk-meter-level');

    if (fill) {
      fill.style.width = s + '%';
      fill.style.background = s >= 70 ? 'linear-gradient(90deg, #ef4444, #b91c1c)' :
                               s >= 45 ? 'linear-gradient(90deg, #f59e0b, #d97706)' :
                               'linear-gradient(90deg, #10b981, #059669)';
    }
    if (scoreEl) scoreEl.textContent = s + '/100';
    if (levelEl) { levelEl.textContent = emoji + ' ' + level; levelEl.style.color = color; }
    if (label) label.textContent = 'Live Risk Estimate';
  }
};

// ============================================================
// SMART PRESETS
// ============================================================
const Presets = {
  HIGH_RISK: {
    loan_type: 'Personal Loan', loan_amount: '4500000', tenure: '360',
    interest: '17.5', purpose: 'Debt Consolidation', employment: 'Unemployed',
    income: '18000', cibil: '420', emis: '45000', dti: '0.82',
    property: 'Rented', age: '58', gender: 'Male', dependents: '4'
  },
  LOW_RISK: {
    loan_type: 'Home Loan', loan_amount: '2500000', tenure: '120',
    interest: '8.5', purpose: 'Home Renovation', employment: 'Salaried',
    income: '120000', cibil: '810', emis: '8000', dti: '0.18',
    property: 'Owned', age: '35', gender: 'Female', dependents: '1'
  },

  fill(preset) {
    const data = this[preset];
    if (!data) return;
    for (const [key, value] of Object.entries(data)) {
      const el = document.getElementById(key);
      if (!el) continue;
      el.value = value;
      el.dispatchEvent(new Event('change'));
      el.dispatchEvent(new Event('input'));
    }
    RiskMeter.calculate();
    if (window.showToast) showToast(`${preset === 'HIGH_RISK' ? '🔴 High-Risk' : '🟢 Low-Risk'} scenario loaded`, preset === 'HIGH_RISK' ? 'warning' : 'success');
    // Jump back to step 1 to show filled form
    FormWizard.goTo(1);
  },

  random() {
    const data = {
      loan_type: ['Home Loan', 'Personal Loan', 'Car Loan', 'Education Loan', 'Business Loan'][Math.floor(Math.random()*5)],
      loan_amount: Math.floor(Math.random() * 4900000 + 100000).toString(),
      tenure: Math.floor(Math.random() * 348 + 12).toString(),
      interest: (Math.random() * 11 + 7).toFixed(2),
      purpose: ['Business Expansion', 'Debt Consolidation', 'Education', 'Home Renovation', 'Medical Emergency', 'Vehicle Purchase', 'Wedding'][Math.floor(Math.random()*7)],
      employment: ['Salaried', 'Self-Employed', 'Business Owner', 'Student', 'Unemployed', 'Retired'][Math.floor(Math.random()*6)],
      income: Math.floor(Math.random() * 185000 + 15000).toString(),
      cibil: Math.floor(Math.random() * 600 + 300).toString(),
      emis: Math.floor(Math.random() * 50000).toString(),
      dti: (Math.random() * 0.8 + 0.1).toFixed(2),
      property: ['Owned', 'Rented', 'Jointly Owned'][Math.floor(Math.random()*3)],
      age: Math.floor(Math.random() * 52 + 18).toString(),
      gender: ['Male', 'Female', 'Other'][Math.floor(Math.random()*3)],
      dependents: Math.floor(Math.random() * 6).toString()
    };
    
    for (const [key, value] of Object.entries(data)) {
      const el = document.getElementById(key);
      if (el) { el.value = value; el.dispatchEvent(new Event('change')); el.dispatchEvent(new Event('input')); }
    }
    RiskMeter.calculate();
    if (window.showToast) showToast(`🎲 Random scenario loaded`, 'info');
    FormWizard.goTo(1);
  },

  async dataset() {
    try {
      if (window.showToast) showToast('📂 Loading random dataset record...', 'info');
      const res = await fetch('/api/dataset/random');
      if (!res.ok) throw new Error('API error');
      const { form_data } = await res.json();
      
      for (const [key, value] of Object.entries(form_data)) {
        const el = document.getElementById(key);
        if (el) { el.value = value; el.dispatchEvent(new Event('change')); el.dispatchEvent(new Event('input')); }
      }
      RiskMeter.calculate();
      if (window.showToast) showToast(`📂 Dataset record loaded successfully`, 'success');
      FormWizard.goTo(1);
    } catch(e) {
      if (window.showToast) showToast('Could not load dataset record', 'danger');
    }
  }
};

// ============================================================
// SHARE LINK (encode report data in URL hash)
// ============================================================
const ShareLink = {
  generate(reportData) {
    try {
      const encoded = btoa(encodeURIComponent(JSON.stringify(reportData)));
      return window.location.origin + '/prediction#report=' + encoded;
    } catch { return null; }
  },

  copyToClipboard(url) {
    navigator.clipboard.writeText(url).then(() => {
      if (window.showToast) showToast('Share link copied to clipboard!', 'success');
    });
  },

  // Check on load if URL has shared report
  checkHash() {
    const hash = window.location.hash;
    if (!hash.startsWith('#report=')) return;
    try {
      const encoded = hash.slice(8);
      const data = JSON.parse(decodeURIComponent(atob(encoded)));
      this._renderSharedBanner(data);
    } catch { /* invalid hash */ }
  },

  _renderSharedBanner(data) {
    const container = document.getElementById('sharedReportBanner');
    if (!container) return;
    container.style.display = 'block';
    container.innerHTML = `
      <div class="glass-card no-hover" style="padding: var(--space-lg); border: 1px solid rgba(124,58,237,0.2); margin-bottom: var(--space-lg);">
        <div class="flex items-center gap-md">
          <span style="font-size: 1.2rem;">🔗</span>
          <div>
            <div style="font-weight: 700; font-size: 0.9rem;">Shared Analysis Preview</div>
            <div style="font-size: 0.8rem; color: var(--text-secondary);">
              ${data.label || '—'} · ${data.probability || '—'} · Risk: ${data.risk_score || '—'}/100
            </div>
          </div>
          <button class="btn btn-primary btn-sm" style="margin-left:auto;" onclick="window.location.hash=''">Dismiss</button>
        </div>
      </div>
    `;
  }
};

// ============================================================
// HISTORY DRAWER
// ============================================================
const HistoryDrawer = {
  STORAGE_KEY: 'risksense_dashboard',

  init() {
    const btn = document.getElementById('historyDrawerBtn');
    const drawer = document.getElementById('historyDrawer');
    const overlay = document.getElementById('historyOverlay');
    const closeBtn = document.getElementById('historyCloseBtn');

    if (btn) btn.addEventListener('click', () => this.open());
    if (closeBtn) closeBtn.addEventListener('click', () => this.close());
    if (overlay) overlay.addEventListener('click', () => this.close());

    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') this.close();
    });
  },

  open() {
    this.render();
    document.getElementById('historyDrawer')?.classList.add('open');
    document.getElementById('historyOverlay')?.classList.add('open');
    document.body.style.overflow = 'hidden';
  },

  close() {
    document.getElementById('historyDrawer')?.classList.remove('open');
    document.getElementById('historyOverlay')?.classList.remove('open');
    document.body.style.overflow = '';
  },

  render() {
    const list = document.getElementById('historyList');
    if (!list) return;

    try {
      const data = JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '{"analyses":[]}');
      const analyses = [...(data.analyses || [])].reverse().slice(0, 15);

      if (analyses.length === 0) {
        list.innerHTML = `
          <div style="text-align:center; padding: var(--space-3xl); color: var(--text-tertiary);">
            <div style="font-size: 2rem; margin-bottom: var(--space-md);">📊</div>
            <p style="font-size: 0.85rem;">No analyses yet. Run your first prediction to see history here.</p>
          </div>
        `;
        return;
      }

      list.innerHTML = analyses.map((a, i) => `
        <div class="history-drawer-item" style="padding: var(--space-md); border-bottom: 1px solid var(--glass-border); display: flex; align-items: center; gap: var(--space-md);">
          <span class="badge ${a.is_fraud ? 'badge-danger' : 'badge-success'}" style="flex-shrink:0; font-size: 0.65rem;">
            ${a.is_fraud ? 'FRAUD' : 'GENUINE'}
          </span>
          <div style="flex: 1; min-width: 0;">
            <div style="font-size: 0.82rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
              ${a.loan_type || 'Unknown'} · $${Number(a.loan_amount || 0).toLocaleString()}
            </div>
            <div style="font-size: 0.72rem; color: var(--text-tertiary);">
              Risk: ${a.risk_score != null ? a.risk_score + '/100' : '—'} · ${a.time || ''}
            </div>
          </div>
          <span style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-tertiary); flex-shrink:0;">
            ${a.probability != null ? (a.probability * 100).toFixed(1) + '%' : '—'}
          </span>
        </div>
      `).join('');
    } catch { list.innerHTML = '<p style="color:var(--text-tertiary);font-size:0.85rem;padding:1rem;">Could not load history.</p>'; }
  },

  clear() {
    localStorage.removeItem(this.STORAGE_KEY);
    this.render();
    if (window.showToast) showToast('Analysis history cleared', 'info');
  }
};

// ============================================================
// KEYBOARD SHORTCUTS
// ============================================================
const KeyboardShortcuts = {
  modal: null,

  init() {
    document.addEventListener('keydown', e => {
      // Ignore when typing in inputs
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return;

      if (e.key === '?') { e.preventDefault(); this.showModal(); }
    });

    // Global shortcuts (work everywhere including inputs)
    document.addEventListener('keydown', e => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'R') {
        e.preventDefault();
        // Trigger random fill
        const randomForm = document.querySelector('form input[name="mode"][value="fill_random"]');
        if (randomForm) randomForm.closest('form').submit();
      }
      if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        window.location.href = '/advisor';
      }
    });

    // Close modal on Escape
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') this.hideModal();
    });
  },

  showModal() {
    const m = document.getElementById('shortcutsModal');
    if (m) { m.classList.add('open'); document.body.style.overflow = 'hidden'; }
  },

  hideModal() {
    const m = document.getElementById('shortcutsModal');
    if (m) { m.classList.remove('open'); document.body.style.overflow = ''; }
  }
};

// ============================================================
// CHART.JS RISK DONUT
// ============================================================
function initRiskChart() {
  const canvas = document.getElementById('riskChart');
  if (!canvas) return;

  const probability = parseFloat(canvas.dataset.probability || 0);
  const isFraud = canvas.dataset.fraud === 'true';
  const ctx = canvas.getContext('2d');

  if (canvas._chartInstance) canvas._chartInstance.destroy();

  const color = isFraud ? '#ef4444' : probability > 0.3 ? '#f59e0b' : '#10b981';

  canvas._chartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [probability * 100, 100 - probability * 100],
        backgroundColor: [color, 'rgba(255,255,255,0.04)'],
        borderWidth: 0,
        borderRadius: 6,
        spacing: 2
      }]
    },
    options: {
      cutout: '78%',
      responsive: true,
      maintainAspectRatio: true,
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      animation: { animateRotate: true, duration: 1500 }
    }
  });
}

// ============================================================
// PDF EXPORT
// ============================================================
function exportPDF() {
  const reportContainer = document.getElementById('reportContainer');
  if (!reportContainer) {
    if (window.showToast) showToast('No report to export. Run an analysis first.', 'warning');
    return;
  }

  // Show loading
  if (window.showToast) showToast('Preparing PDF export...', 'info');

  // Use browser print with print-specific styles
  const printContent = reportContainer.innerHTML;
  const printWindow = window.open('', '_blank', 'width=900,height=700');
  printWindow.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>RiskSense AI — Analysis Report</title>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #1e293b; background: white; padding: 2rem; }
        h1,h2,h3,h4 { color: #0f172a; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 700; }
        .badge-danger { background: #fee2e2; color: #dc2626; }
        .badge-success { background: #dcfce7; color: #16a34a; }
        .badge-warning { background: #fef3c7; color: #d97706; }
        .badge-accent { background: #ede9fe; color: #7c3aed; }
        .glass-card { border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
        .agent-report-section { padding: 1rem; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 0.75rem; }
        .signal-card { display: flex; gap: 0.75rem; padding: 0.5rem; border: 1px solid #e2e8f0; border-radius: 6px; margin-bottom: 0.5rem; }
        .signal-severity { width: 4px; border-radius: 2px; flex-shrink: 0; }
        .signal-severity.high { background: #dc2626; }
        .signal-severity.medium { background: #d97706; }
        .signal-severity.low { background: #16a34a; }
        .advisory-item { display: flex; gap: 0.75rem; padding: 0.5rem; border: 1px solid #e2e8f0; border-radius: 6px; margin-bottom: 0.5rem; }
        .decision-badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 12px; font-weight: 700; background: #ede9fe; color: #7c3aed; }
        .exec-summary { background: #f8fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }
        canvas { display: none; } /* hide charts in print */
        .report-actions { display: none; }
        .no-print { display: none; }
        .report-header { border-bottom: 2px solid #e2e8f0; padding-bottom: 1rem; margin-bottom: 1rem; }
        .print-header { background: linear-gradient(135deg, #0f172a, #1e293b); color: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; }
        .print-header h1 { font-size: 1.2rem; font-weight: 800; }
        .print-header p { font-size: 0.8rem; opacity: 0.7; margin-top: 0.25rem; }
        @media print { body { padding: 0; } .print-header { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
      </style>
    </head>
    <body>
      <div class="print-header">
        <h1>⬡ RiskSense AI — Agentic Fraud Analysis Report</h1>
        <p>Generated: ${new Date().toLocaleString()} · Confidential Banking Intelligence</p>
      </div>
      ${printContent}
      <script>window.onload = function() { window.print(); setTimeout(function() { window.close(); }, 1000); }<\/script>
    </body>
    </html>
  `);
  printWindow.document.close();
}

// ============================================================
// DASHBOARD SYNC — save to localStorage after analysis
// ============================================================
function saveToDashboard() {
  const canvas = document.getElementById('riskChart');
  if (!canvas) return;

  const probability = parseFloat(canvas.dataset.probability || 0);
  const isFraud = canvas.dataset.fraud === 'true';

  // Extract risk score
  let riskScore = null;
  document.querySelectorAll('.badge-danger, .badge-warning, .badge-success').forEach(el => {
    const m = el.textContent.match(/(\d+)\/100/);
    if (m) riskScore = parseInt(m[1]);
  });

  const form = document.getElementById('predictionForm');
  let loanType = '—', loanAmount = 0, decision = isFraud ? 'FRAUD' : 'GENUINE';
  if (form) {
    loanType = form.querySelector('#loan_type')?.value || '—';
    loanAmount = form.querySelector('#loan_amount')?.value || 0;
  }

  const decisionBadge = document.querySelector('.decision-badge');
  if (decisionBadge) decision = decisionBadge.textContent.trim();

  // Generate share URL
  const shareData = { label: isFraud ? 'FRAUD' : 'GENUINE', probability: (probability * 100).toFixed(1) + '%', risk_score: riskScore };
  const shareUrl = ShareLink.generate(shareData);

  // Show share button
  const shareBtn = document.getElementById('shareLinkBtn');
  if (shareBtn && shareUrl) {
    shareBtn.style.display = 'inline-flex';
    shareBtn.onclick = () => ShareLink.copyToClipboard(shareUrl);
  }

  // Save to dashboard storage
  try {
    const stored = JSON.parse(localStorage.getItem('risksense_dashboard') || '{"analyses":[]}');
    stored.analyses.push({ probability, is_fraud: isFraud, risk_score: riskScore, loan_type: loanType, loan_amount: loanAmount, decision, time: new Date().toLocaleTimeString() });
    if (stored.analyses.length > 50) stored.analyses = stored.analyses.slice(-50);
    localStorage.setItem('risksense_dashboard', JSON.stringify(stored));
  } catch (e) { /* non-critical */ }
}

// ============================================================
// TOAST GLOBAL ALIAS
// ============================================================
function showToast(msg, type) {
  if (typeof Toast !== 'undefined') Toast.show(msg, type);
}

// ============================================================
// SHAP EXPLAINABILITY PANEL RENDERER
// ============================================================
function initShapPanel() {
  const container = document.getElementById('shapBars');
  if (!container) return;

  const probability = parseFloat(container.dataset.probability || 0);
  let signals = [], severities = [];
  try { signals = JSON.parse(container.dataset.signals || '[]'); } catch {}
  try { severities = JSON.parse(container.dataset.severities || '[]'); } catch {}

  // Build feature importance from signals + fixed baseline
  const baseFeatures = [
    { name: 'Model Probability', weight: probability, positive: probability > 0.4 },
    { name: 'CIBIL Score Impact', weight: 0, positive: false },
    { name: 'DTI Ratio', weight: 0, positive: false },
    { name: 'Loan-to-Income', weight: 0, positive: false },
    { name: 'Employment Stability', weight: 0, positive: false },
    { name: 'Property Ownership', weight: 0, positive: false },
  ];

  // Overlay signal severities
  const sevMap = { high: 0.75, medium: 0.45, low: 0.20 };
  signals.forEach((sig, i) => {
    const sev = sevMap[severities[i]] || 0.1;
    baseFeatures.push({
      name: sig.replace(/[🚨⚠️✅]/g, '').trim(),
      weight: sev,
      positive: severities[i] === 'high' || severities[i] === 'medium'
    });
  });

  // Compute normalized weights
  const maxWeight = Math.max(...baseFeatures.map(f => f.weight), 0.01);
  const displayFeatures = baseFeatures.slice(0, 8).map(f => ({
    ...f, pct: Math.round((f.weight / maxWeight) * 100)
  }));

  container.innerHTML = displayFeatures.map(f => `
    <div class="shap-row">
      <div class="shap-label">${f.name}</div>
      <div class="shap-bar-track">
        <div class="shap-bar-fill ${f.positive ? 'positive' : 'negative'}"
             style="width: 0%;" data-target="${f.pct}"></div>
      </div>
      <div class="shap-value ${f.positive ? 'positive' : 'negative'}">${f.pct}%</div>
    </div>
  `).join('');

  // Animate bars in
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      container.querySelectorAll('.shap-bar-fill').forEach(bar => {
        bar.style.width = bar.dataset.target + '%';
      });
    });
  });
}

// ============================================================
// SAVE TO CASE (creates a case from current result)
// ============================================================
function initSaveToCase() {
  const btn = document.getElementById('saveToCaseBtn');
  if (!btn) return;

  btn.addEventListener('click', () => {
    const canvas = document.getElementById('riskChart');
    if (!canvas) return;

    const probability = parseFloat(canvas.dataset.probability || 0);
    const isFraud = canvas.dataset.fraud === 'true';
    const form = document.getElementById('predictionForm');
    const loanType = form?.querySelector('#loan_type')?.value || 'Unknown';
    const loanAmount = form?.querySelector('#loan_amount')?.value || 0;

    let riskScore = null;
    document.querySelectorAll('[class*=badge]').forEach(el => {
      const m = el.textContent.match(/(\d+)\/100/);
      if (m) riskScore = parseInt(m[1]);
    });

    const decisionBadge = document.querySelector('.decision-badge');
    const decision = decisionBadge?.textContent.trim() || '';

    // Save to cases storage
    const CASES_KEY = 'risksense_cases';
    let cases = [];
    try { cases = JSON.parse(localStorage.getItem(CASES_KEY) || '[]'); } catch {}

    const id = 'CASE-' + String(Date.now()).slice(-6);
    cases.unshift({
      id, loan_type: loanType, loan_amount: loanAmount,
      risk_score: riskScore, probability, is_fraud: isFraud, decision,
      status: 'open', notes: '', created: new Date().toLocaleString(), updated: new Date().toLocaleString()
    });
    try { localStorage.setItem(CASES_KEY, JSON.stringify(cases)); } catch {}

    if (window.showToast) showToast(`Case ${id} created! View in Case Management.`, 'success');

    // Fire alert
    if (isFraud && window.AlertSystem) {
      AlertSystem.addAlert(`New fraud case saved: ${id} — ${loanType}`, 'fraud');
    }
  });
}

// ============================================================
// INIT
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  // Form wizard
  if (document.getElementById('predictionForm')) {
    FormWizard.init();
  }

  // Live risk meter
  RiskMeter.init();

  // Chart if report already rendered
  initRiskChart();

  // SHAP panel
  initShapPanel();

  // Save to Case
  initSaveToCase();

  // Share link from URL hash
  ShareLink.checkHash();

  // History drawer
  HistoryDrawer.init();

  // Keyboard shortcuts
  KeyboardShortcuts.init();

  // Save to dashboard if report present
  if (document.getElementById('riskChart')) {
    setTimeout(saveToDashboard, 500);
  }

  // Animate report section in
  const reportContainer = document.getElementById('reportContainer');
  if (reportContainer) {
    reportContainer.style.opacity = '0';
    reportContainer.style.transform = 'translateY(20px)';
    setTimeout(() => {
      reportContainer.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
      reportContainer.style.opacity = '1';
      reportContainer.style.transform = 'translateY(0)';
    }, 100);
  }
});
