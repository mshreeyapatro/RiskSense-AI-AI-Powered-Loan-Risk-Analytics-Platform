/* ============================================================
   RiskSense AI — Core Application JavaScript
   Dark/Light Mode, Notifications, Alerts, Role System,
   GSAP Animations, Scroll Reveals, Toasts, Mobile Menu
   ============================================================ */

// ---- Theme System (Dark / Light Mode) ----
const ThemeSystem = {
  KEY: 'risksense_theme',

  init() {
    const saved = localStorage.getItem(this.KEY) || 'dark';
    this.apply(saved);
    const btn = document.getElementById('themeToggleBtn');
    if (btn) {
      btn.addEventListener('click', () => this.toggle());
    }
    // Keyboard shortcut: Ctrl+Shift+D
  },

  apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const btn = document.getElementById('themeToggleBtn');
    if (btn) btn.textContent = theme === 'dark' ? '🌙' : '☀️';
    localStorage.setItem(this.KEY, theme);
  },

  toggle() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    this.apply(current === 'dark' ? 'light' : 'dark');
    if (window.showToast) showToast(`Switched to ${current === 'dark' ? 'light' : 'dark'} mode`, 'info');
  },

  current() {
    return document.documentElement.getAttribute('data-theme') || 'dark';
  }
};

// ---- Role-Based Access System ----
const RoleSystem = {
  KEY: 'risksense_role',
  ROLES: {
    analyst: { label: 'Analyst', color: '#06b6d4', icon: '🔍' },
    manager: { label: 'Manager', color: '#f59e0b', icon: '📊' },
    admin: { label: 'Admin', color: '#7c3aed', icon: '⚡' }
  },

  init() {
    const saved = localStorage.getItem(this.KEY);
    if (saved) this.apply(saved);
  },

  apply(role) {
    const config = this.ROLES[role];
    if (!config) return;
    localStorage.setItem(this.KEY, role);
    const el = document.getElementById('roleDisplay');
    if (el) {
      el.textContent = `${config.icon} ${config.label}`;
      el.style.color = config.color;
      el.style.borderColor = config.color + '40';
    }
  },

  current() {
    return localStorage.getItem(this.KEY) || null;
  }
};

// ---- Alert / Notification System ----
const AlertSystem = {
  KEY: 'risksense_alerts',
  alerts: [],
  intervalId: null,
  panelOpen: false,

  ALERT_TEMPLATES: [
    { msg: 'Suspicious application detected — High DTI ratio flagged', type: 'fraud' },
    { msg: 'High-risk loan application #{{ID}} requires manual review', type: 'warning' },
    { msg: 'CIBIL score below threshold — Enhanced verification required', type: 'fraud' },
    { msg: 'Batch screening complete — 3 applications flagged', type: 'info' },
    { msg: 'Fraud probability spike detected in Business Loan category', type: 'fraud' },
    { msg: 'Case #{{ID}} status updated to Under Review', type: 'info' },
    { msg: 'New high-risk pattern identified — Debt consolidation cluster', type: 'warning' },
    { msg: 'Model confidence threshold exceeded — Auto-escalation triggered', type: 'fraud' },
  ],

  init() {
    this.loadFromStorage();
    this.renderBadge();

    const bellBtn = document.getElementById('notificationBellBtn');
    const overlay = document.getElementById('notificationOverlay');
    const panel = document.getElementById('notificationPanel');

    if (bellBtn) {
      bellBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.togglePanel();
      });
    }
    if (overlay) {
      overlay.addEventListener('click', () => this.closePanel());
    }

    // Start simulation after 30 seconds (random intervals 30–90s)
    this.scheduleNext();
  },

  scheduleNext() {
    const delay = (30 + Math.random() * 60) * 1000;
    setTimeout(() => {
      this.addSimulatedAlert();
      this.scheduleNext();
    }, delay);
  },

  addSimulatedAlert() {
    const template = this.ALERT_TEMPLATES[Math.floor(Math.random() * this.ALERT_TEMPLATES.length)];
    const id = Math.floor(Math.random() * 9000) + 1000;
    const msg = template.msg.replace('{{ID}}', id);
    this.addAlert(msg, template.type);
  },

  addAlert(message, type = 'info') {
    const alert = {
      id: Date.now(),
      message,
      type,
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      read: false
    };
    this.alerts.unshift(alert);
    if (this.alerts.length > 20) this.alerts = this.alerts.slice(0, 20);
    this.saveToStorage();
    this.renderBadge();
    this.renderPanel();

    // Show toast for fraud alerts
    if (type === 'fraud' && window.showToast) {
      showToast('🚨 ' + message.substring(0, 60) + (message.length > 60 ? '…' : ''), 'danger', 5000);
    }
  },

  clearAll() {
    this.alerts = [];
    this.saveToStorage();
    this.renderBadge();
    this.renderPanel();
  },

  markAllRead() {
    this.alerts.forEach(a => a.read = true);
    this.saveToStorage();
    this.renderBadge();
  },

  renderBadge() {
    const badge = document.getElementById('notificationBadge');
    const unread = this.alerts.filter(a => !a.read).length;
    if (badge) {
      badge.textContent = unread > 9 ? '9+' : unread;
      badge.style.display = unread > 0 ? 'flex' : 'none';
    }
  },

  renderPanel() {
    const list = document.getElementById('notificationList');
    if (!list) return;
    if (this.alerts.length === 0) {
      list.innerHTML = '<div class="no-alerts-msg" style="text-align:center;padding:2rem;color:var(--text-tertiary);font-size:0.82rem;">No alerts yet. Monitoring active.</div>';
      return;
    }
    const typeIcons = { fraud: '🚨', warning: '⚠️', info: 'ℹ️' };
    const typeColors = { fraud: 'var(--color-danger)', warning: 'var(--color-warning)', info: 'var(--color-info)' };
    list.innerHTML = this.alerts.map(a => `
      <div class="notification-item ${a.read ? 'read' : 'unread'}" style="padding:0.75rem 1rem;border-bottom:1px solid var(--glass-border);display:flex;gap:0.75rem;align-items:flex-start;">
        <span style="font-size:1rem;flex-shrink:0;">${typeIcons[a.type] || 'ℹ️'}</span>
        <div style="flex:1;min-width:0;">
          <div style="font-size:0.8rem;color:var(--text-primary);line-height:1.4;margin-bottom:2px;">${a.message}</div>
          <div style="font-size:0.7rem;color:var(--text-tertiary);">${a.time}</div>
        </div>
        ${!a.read ? '<div style="width:6px;height:6px;border-radius:50%;background:var(--color-danger);flex-shrink:0;margin-top:4px;"></div>' : ''}
      </div>
    `).join('');
  },

  togglePanel() {
    const panel = document.getElementById('notificationPanel');
    const overlay = document.getElementById('notificationOverlay');
    if (!panel) return;
    this.panelOpen = !this.panelOpen;
    if (this.panelOpen) {
      this.markAllRead();
      this.renderPanel();
      panel.classList.add('open');
      if (overlay) overlay.classList.add('open');
      panel.setAttribute('aria-hidden', 'false');
    } else {
      this.closePanel();
    }
  },

  closePanel() {
    const panel = document.getElementById('notificationPanel');
    const overlay = document.getElementById('notificationOverlay');
    if (panel) { panel.classList.remove('open'); panel.setAttribute('aria-hidden', 'true'); }
    if (overlay) overlay.classList.remove('open');
    this.panelOpen = false;
  },

  saveToStorage() {
    try { localStorage.setItem(this.KEY, JSON.stringify(this.alerts)); } catch(e) {}
  },

  loadFromStorage() {
    try { this.alerts = JSON.parse(localStorage.getItem(this.KEY) || '[]'); } catch(e) { this.alerts = []; }
  }
};

// Expose globally so templates can call it
window.AlertSystem = AlertSystem;

// ---- Scroll Progress Bar ----
function initScrollProgress() {
  const bar = document.querySelector('.scroll-progress');
  if (!bar) return;
  window.addEventListener('scroll', () => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    bar.style.width = pct + '%';
  }, { passive: true });
}

// ---- Navbar scroll state ----
function initNavbar() {
  const nav = document.querySelector('.navbar');
  if (!nav) return;
  const onScroll = () => {
    nav.classList.toggle('scrolled', window.scrollY > 20);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

// ---- Mobile Menu ----
function initMobileMenu() {
  const toggle = document.querySelector('.menu-toggle');
  const navMenu = document.querySelector('.navbar-nav');
  if (!toggle || !navMenu) return;

  toggle.addEventListener('click', () => {
    toggle.classList.toggle('open');
    navMenu.classList.toggle('open');
    document.body.style.overflow = navMenu.classList.contains('open') ? 'hidden' : '';
  });

  // Close on nav link click
  navMenu.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
      toggle.classList.remove('open');
      navMenu.classList.remove('open');
      document.body.style.overflow = '';
    });
  });
}

// ---- Scroll Reveal (IntersectionObserver) ----
function initScrollReveal() {
  const reveals = document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale, .stagger-children');
  if (!reveals.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  reveals.forEach(el => observer.observe(el));
}

// ---- Animated Counters ----
function initCounters() {
  const counters = document.querySelectorAll('[data-count]');
  if (!counters.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  counters.forEach(el => observer.observe(el));
}

function animateCounter(el) {
  const target = parseFloat(el.dataset.count);
  const suffix = el.dataset.suffix || '';
  const prefix = el.dataset.prefix || '';
  const duration = 2000;
  const start = performance.now();
  const isFloat = String(target).includes('.');

  function tick(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 4); // easeOutQuart
    const current = eased * target;

    el.textContent = prefix + (isFloat ? current.toFixed(1) : Math.floor(current)) + suffix;

    if (progress < 1) {
      requestAnimationFrame(tick);
    }
  }

  requestAnimationFrame(tick);
}

// ---- Toast Notification System ----
const Toast = {
  container: null,

  init() {
    this.container = document.querySelector('.toast-container');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  },

  show(message, type = 'info', duration = 4000) {
    if (!this.container) this.init();

    const icons = {
      success: '✓',
      warning: '⚠',
      danger: '✕',
      info: 'ℹ'
    };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${icons[type] || icons.info}</span>
      <span class="toast-text">${message}</span>
      <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
    `;

    this.container.appendChild(toast);

    // Trigger reflow then animate in
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        toast.classList.add('show');
      });
    });

    // Auto remove
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 400);
    }, duration);
  }
};

// ---- 3D Tilt Effect on Cards ----
function initTiltCards() {
  const cards = document.querySelectorAll('[data-tilt]');
  cards.forEach(card => {
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const maxTilt = 6;

      const rotateX = ((y - centerY) / centerY) * -maxTilt;
      const rotateY = ((x - centerX) / centerX) * maxTilt;

      card.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-2px)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(800px) rotateX(0deg) rotateY(0deg) translateY(0)';
      card.style.transition = 'transform 0.5s cubic-bezier(0.16, 1, 0.3, 1)';
    });

    card.addEventListener('mouseenter', () => {
      card.style.transition = 'none';
    });
  });
}

// ---- Hero Text Reveal Animation ----
function initHeroTextReveal() {
  const heroTitle = document.querySelector('.hero-title');
  if (!heroTitle) return;

  const text = heroTitle.textContent;
  heroTitle.innerHTML = '';

  // Split into words and wrap each
  const words = text.split(' ');
  words.forEach((word, i) => {
    const span = document.createElement('span');
    span.className = 'hero-word';
    span.style.display = 'inline-block';
    span.style.opacity = '0';
    span.style.transform = 'translateY(40px)';
    span.style.transition = `opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1) ${i * 0.08}s, transform 0.6s cubic-bezier(0.16, 1, 0.3, 1) ${i * 0.08}s`;
    span.textContent = word;
    heroTitle.appendChild(span);

    if (i < words.length - 1) {
      heroTitle.appendChild(document.createTextNode(' '));
    }
  });

  // Trigger animation
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      heroTitle.querySelectorAll('.hero-word').forEach(w => {
        w.style.opacity = '1';
        w.style.transform = 'translateY(0)';
      });
    });
  });
}

// ---- Page Load Animation ----
function initPageLoad() {
  document.body.classList.add('loaded');

  // Fade in main content
  const main = document.querySelector('main');
  if (main) {
    main.style.opacity = '0';
    main.style.transform = 'translateY(10px)';
    main.style.transition = 'opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        main.style.opacity = '1';
        main.style.transform = 'translateY(0)';
      });
    });
  }
}

// ---- Loading Overlay ----
const LoadingOverlay = {
  overlay: null,
  steps: [],
  currentStep: 0,
  intervalId: null,

  show(stepTexts = ['Processing...']) {
    this.overlay = document.querySelector('.loading-overlay');
    if (!this.overlay) return;

    const stepsContainer = this.overlay.querySelector('.loading-steps');
    if (stepsContainer) {
      stepsContainer.innerHTML = stepTexts.map(text =>
        `<div class="loading-step"><span class="loading-step-dot"></span>${text}</div>`
      ).join('');
      this.steps = Array.from(stepsContainer.querySelectorAll('.loading-step'));
    }

    this.overlay.classList.add('active');
    this.currentStep = 0;

    if (this.steps.length > 0) {
      this.steps[0].classList.add('active');
      this.intervalId = setInterval(() => this.nextStep(), 1200);
    }
  },

  nextStep() {
    if (this.currentStep < this.steps.length) {
      this.steps[this.currentStep].classList.remove('active');
      this.steps[this.currentStep].classList.add('done');
    }
    this.currentStep++;
    if (this.currentStep < this.steps.length) {
      this.steps[this.currentStep].classList.add('active');
    } else {
      clearInterval(this.intervalId);
    }
  },

  hide() {
    clearInterval(this.intervalId);
    if (this.overlay) {
      this.overlay.classList.remove('active');
    }
  }
};


// ---- Expose globals ----
window.showToast = (msg, type, duration) => Toast.show(msg, type, duration);
window.LoadingOverlay = LoadingOverlay;

// ---- Global Keyboard Shortcuts ----
function initGlobalKeyboard() {
  document.addEventListener('keydown', e => {
    // '?' key — show shortcuts modal (when not in an input)
    if (e.key === '?' && !['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName)) {
      e.preventDefault();
      const modal = document.getElementById('shortcutsModal');
      if (modal) {
        modal.classList.toggle('open');
        document.body.style.overflow = modal.classList.contains('open') ? 'hidden' : '';
      }
    }
    // Escape — close any open modal
    if (e.key === 'Escape') {
      document.querySelectorAll('.shortcuts-modal.open, .history-drawer.open').forEach(el => {
        el.classList.remove('open');
        document.body.style.overflow = '';
      });
      document.querySelectorAll('.history-overlay.open').forEach(el => el.classList.remove('open'));
      AlertSystem.closePanel();
    }
    // Ctrl+/ → advisor
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
      e.preventDefault();
      window.location.href = '/advisor';
    }
    // Ctrl+Shift+D → toggle theme
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
      e.preventDefault();
      ThemeSystem.toggle();
    }
  });
}

// ---- PDF Report Generator ----
window.exportPDF = async function() {
  if (typeof window.jspdf === 'undefined' && typeof jspdf === 'undefined') {
    if (window.showToast) showToast('PDF library loading... please try again in a moment', 'warning');
    return;
  }

  if (window.showToast) showToast('Generating PDF report...', 'info');

  try {
    const { jsPDF } = window.jspdf || jspdf;
    const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
    const pageW = doc.internal.pageSize.getWidth();
    const margin = 15;
    let y = margin;

    // Helper: add text
    const addText = (text, x, yPos, size = 10, style = 'normal', color = [220, 220, 220]) => {
      doc.setFontSize(size);
      doc.setFont('helvetica', style);
      doc.setTextColor(...color);
      doc.text(text, x, yPos);
    };

    const addLine = (yPos, color = [60, 60, 90]) => {
      doc.setDrawColor(...color);
      doc.line(margin, yPos, pageW - margin, yPos);
    };

    // Background
    doc.setFillColor(6, 8, 15);
    doc.rect(0, 0, pageW, 297, 'F');

    // Header Bar
    doc.setFillColor(30, 15, 60);
    doc.rect(0, 0, pageW, 30, 'F');

    // Logo/Title
    addText('⬡ RiskSense AI', margin, 12, 16, 'bold', [124, 58, 237]);
    addText('Agentic Banking Fraud Analytics & Advisory Report', margin, 20, 9, 'normal', [150, 150, 200]);
    addText(new Date().toLocaleString(), pageW - margin - 50, 20, 8, 'normal', [120, 120, 160]);

    y = 40;

    // Grab data from DOM
    const execEl = document.querySelector('.exec-summary p');
    if (execEl) {
      // Executive Summary section
      doc.setFillColor(20, 10, 40);
      doc.roundedRect(margin, y, pageW - margin*2, 28, 3, 3, 'F');
      addText('EXECUTIVE SUMMARY', margin + 5, y + 7, 8, 'bold', [124, 58, 237]);
      const execText = execEl.textContent.trim();
      const wrapped = doc.splitTextToSize(execText, pageW - margin*2 - 10);
      addText(wrapped[0] || execText, margin + 5, y + 14, 9, 'normal', [200, 200, 220]);
      if (wrapped[1]) addText(wrapped[1], margin + 5, y + 20, 9, 'normal', [200, 200, 220]);
      y += 35;
    }

    // Prediction Result
    const predEl = document.querySelector('.prob-value');
    const decisionEl = document.querySelector('.decision-badge');
    if (predEl) {
      addText('DETECTION RESULT', margin, y, 9, 'bold', [100, 200, 255]);
      addLine(y + 2);
      y += 8;
      addText('Fraud Probability: ' + (predEl.textContent || '').trim(), margin + 5, y, 11, 'bold', [255, 255, 255]);
      y += 7;
      if (decisionEl) addText('Decision: ' + decisionEl.textContent.trim(), margin + 5, y, 10, 'normal', [200, 200, 200]);
      y += 12;
    }

    // Risk Signals
    const signals = document.querySelectorAll('.signal-card');
    if (signals.length) {
      addText('RISK SIGNALS', margin, y, 9, 'bold', [100, 200, 255]);
      addLine(y + 2);
      y += 8;
      signals.forEach(s => {
        const factor = s.querySelector('.signal-factor')?.textContent?.trim() || '';
        const detail = s.querySelector('.signal-detail')?.textContent?.trim() || '';
        addText('• ' + factor, margin + 5, y, 9, 'bold', [220, 180, 100]);
        y += 5;
        const detailWrapped = doc.splitTextToSize(detail, pageW - margin*2 - 15);
        detailWrapped.slice(0,2).forEach(line => {
          addText(line, margin + 10, y, 8, 'normal', [170, 170, 200]);
          y += 4.5;
        });
        y += 2;
        if (y > 265) { doc.addPage(); doc.setFillColor(6, 8, 15); doc.rect(0, 0, pageW, 297, 'F'); y = 20; }
      });
    }

    // Advisory Items
    const items = document.querySelectorAll('.advisory-item');
    if (items.length) {
      y += 5;
      addText('ADVISORY ACTIONS', margin, y, 9, 'bold', [100, 200, 255]);
      addLine(y + 2);
      y += 8;
      items.forEach(item => {
        const priority = item.querySelector('.advisory-priority')?.textContent?.trim() || '';
        const action = item.querySelector('h4')?.textContent?.trim() || '';
        const rationale = item.querySelector('p')?.textContent?.trim() || '';
        addText(`[${priority}] ${action}`, margin + 5, y, 9, 'bold', [220, 220, 240]);
        y += 5;
        const rWrapped = doc.splitTextToSize(rationale, pageW - margin*2 - 15);
        rWrapped.slice(0,2).forEach(line => {
          addText(line, margin + 10, y, 8, 'normal', [150, 150, 180]);
          y += 4.5;
        });
        y += 2;
        if (y > 265) { doc.addPage(); doc.setFillColor(6, 8, 15); doc.rect(0, 0, pageW, 297, 'F'); y = 20; }
      });
    }

    // Footer
    addLine(280);
    addText('Generated by RiskSense AI — For authorized bank personnel only. Not a substitute for human judgment.', margin, 286, 7, 'italic', [100, 100, 130]);

    doc.save('RiskSense_AI_Report_' + Date.now() + '.pdf');
    if (window.showToast) showToast('PDF report downloaded successfully!', 'success');
  } catch(err) {
    console.error('PDF error:', err);
    if (window.showToast) showToast('PDF generation failed. Check console.', 'danger');
  }
};

// ---- Init All ----
document.addEventListener('DOMContentLoaded', () => {
  ThemeSystem.init();
  RoleSystem.init();
  AlertSystem.init();
  initScrollProgress();
  initNavbar();
  initMobileMenu();
  initScrollReveal();
  initCounters();
  initTiltCards();
  initHeroTextReveal();
  initPageLoad();
  Toast.init();
  initGlobalKeyboard();

  // Init history drawer on every page (data stored in localStorage)
  if (typeof HistoryDrawer !== 'undefined') {
    HistoryDrawer.init();
  } else {
    // Inline init for pages that don't load prediction.js
    (function() {
      const btn = document.getElementById('historyDrawerBtn');
      const drawer = document.getElementById('historyDrawer');
      const overlay = document.getElementById('historyOverlay');
      const closeBtn = document.getElementById('historyCloseBtn');
      const STORAGE_KEY = 'risksense_dashboard';

      function renderHistory() {
        const list = document.getElementById('historyList');
        if (!list) return;
        try {
          const data = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{"analyses":[]}');
          const analyses = [...(data.analyses || [])].reverse().slice(0, 15);
          if (analyses.length === 0) {
            list.innerHTML = '<div style="text-align:center;padding:3rem;color:var(--text-tertiary);font-size:0.85rem;">No analyses yet.</div>';
            return;
          }
          list.innerHTML = analyses.map(a => `
            <div style="padding:var(--space-md);border-bottom:1px solid var(--glass-border);display:flex;align-items:center;gap:var(--space-md);">
              <span class="badge ${a.is_fraud?'badge-danger':'badge-success'}" style="flex-shrink:0;font-size:0.65rem;">${a.is_fraud?'FRAUD':'GENUINE'}</span>
              <div style="flex:1;min-width:0;">
                <div style="font-size:0.82rem;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${a.loan_type||'Unknown'} · $${Number(a.loan_amount||0).toLocaleString()}</div>
                <div style="font-size:0.72rem;color:var(--text-tertiary);">Risk: ${a.risk_score!=null?a.risk_score+'/100':'—'} · ${a.time||''}</div>
              </div>
              <span style="font-family:var(--font-mono);font-size:0.75rem;color:var(--text-tertiary);flex-shrink:0;">${a.probability!=null?(a.probability*100).toFixed(1)+'%':'—'}</span>
            </div>
          `).join('');
        } catch { list.innerHTML = '<p style="color:var(--text-tertiary);font-size:0.85rem;padding:1rem;">Could not load history.</p>'; }
      }

      function openDrawer() {
        renderHistory();
        drawer?.classList.add('open');
        overlay?.classList.add('open');
        document.body.style.overflow = 'hidden';
      }

      function closeDrawer() {
        drawer?.classList.remove('open');
        overlay?.classList.remove('open');
        document.body.style.overflow = '';
      }

      btn?.addEventListener('click', openDrawer);
      closeBtn?.addEventListener('click', closeDrawer);
      overlay?.addEventListener('click', closeDrawer);

      // Expose global clear
      window.HistoryDrawer = {
        init() {},
        open: openDrawer,
        close: closeDrawer,
        clear() {
          localStorage.removeItem(STORAGE_KEY);
          renderHistory();
          Toast.show('Analysis history cleared', 'info');
        }
      };
    })();
  }
});
