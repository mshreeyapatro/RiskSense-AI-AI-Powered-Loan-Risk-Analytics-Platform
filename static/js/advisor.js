/* ============================================================
   RiskSense AI — Advisor Chat JavaScript
   Full AJAX chat, typing indicator, message history, copy
   ============================================================ */

const AdvisorChat = {
  messages: [],
  applicationJson: null,

  init() {
    // Read hidden application context if present
    const appJsonEl = document.getElementById('applicationJsonField');
    if (appJsonEl) this.applicationJson = appJsonEl.value || null;

    // Restore message history from sessionStorage
    this._restoreHistory();

    // Form submit
    const form = document.getElementById('advisorForm');
    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        const textarea = document.getElementById('advisorMessage');
        if (!textarea) return;
        const msg = textarea.value.trim();
        if (!msg) return;
        textarea.value = '';
        textarea.style.height = 'auto';
        this.sendMessage(msg);
      });
    }

    // Ctrl+Enter / Cmd+Enter to submit
    const textarea = document.getElementById('advisorMessage');
    if (textarea) {
      textarea.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
          e.preventDefault();
          document.getElementById('advisorForm')?.dispatchEvent(new Event('submit'));
        }
        // Auto-resize
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
      });
    }

    // Scroll chat to bottom on init
    this._scrollToBottom();
  },

  sendMessage(message) {
    // Render user bubble immediately
    this._appendBubble(message, 'user');
    this._saveToHistory(message, 'user');
    this._showTyping();

    fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        application_data: this.applicationJson ? JSON.parse(this.applicationJson) : null
      })
    })
    .then(res => res.json())
    .then(data => {
      this._hideTyping();
      const reply = data.reply || data.error || 'Unable to process request.';
      this._appendBubble(reply, 'assistant');
      this._saveToHistory(reply, 'assistant');
    })
    .catch(() => {
      this._hideTyping();
      const errMsg = 'Connection error — please try again.';
      this._appendBubble(errMsg, 'assistant');
    });
  },

  _appendBubble(text, sender) {
    const window_ = document.getElementById('chatWindow');
    if (!window_) return;

    // Clear empty state if present
    const emptyState = window_.querySelector('.chat-empty-state');
    if (emptyState) emptyState.remove();

    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const msgEl = document.createElement('div');
    msgEl.className = `chat-message ${sender}`;

    if (sender === 'user') {
      msgEl.innerHTML = `
        <div class="message-sender">You</div>
        <div class="message-bubble">${this._escapeHtml(text)}</div>
        <div class="message-time">${time}</div>
      `;
    } else {
      const formattedText = this._formatReply(text);
      msgEl.innerHTML = `
        <div class="message-sender">RiskSense Advisor</div>
        <div class="message-with-avatar">
          <div class="assistant-avatar">⬡</div>
          <div>
            <div class="message-bubble">${formattedText}</div>
            <div class="message-meta">
              <span class="message-time">${time}</span>
              <button class="copy-btn" title="Copy response" onclick="AdvisorChat._copyText(this)">
                <svg viewBox="0 0 16 16" width="12" height="12" fill="currentColor">
                  <path d="M4 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V2Zm2-1a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H6ZM2 5a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-1h1v1a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h1v1H2Z"/>
                </svg>
                Copy
              </button>
            </div>
          </div>
        </div>
      `;
    }

    window_.appendChild(msgEl);
    this._scrollToBottom();
  },

  _showTyping() {
    const window_ = document.getElementById('chatWindow');
    if (!window_) return;
    const ind = document.createElement('div');
    ind.id = 'typingIndicator';
    ind.className = 'chat-message assistant';
    ind.innerHTML = `
      <div class="message-with-avatar">
        <div class="assistant-avatar">⬡</div>
        <div class="message-bubble typing-bubble">
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
        </div>
      </div>
    `;
    window_.appendChild(ind);
    this._scrollToBottom();
  },

  _hideTyping() {
    document.getElementById('typingIndicator')?.remove();
  },

  _scrollToBottom() {
    const win = document.getElementById('chatWindow');
    if (win) win.scrollTop = win.scrollHeight;
  },

  _escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  },

  _formatReply(text) {
    // Convert newlines to <br>, bold **text**, and bullet points
    return this._escapeHtml(text)
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/^- (.+)/gm, '<li>$1</li>')
      .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
      .replace(/\n/g, '<br>');
  },

  _copyText(btn) {
    const bubble = btn.closest('.message-with-avatar')?.querySelector('.message-bubble');
    if (!bubble) return;
    const text = bubble.innerText || bubble.textContent;
    navigator.clipboard.writeText(text).then(() => {
      btn.textContent = '✓ Copied';
      setTimeout(() => { btn.innerHTML = `<svg viewBox="0 0 16 16" width="12" height="12" fill="currentColor"><path d="M4 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V2Zm2-1a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H6ZM2 5a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-1h1v1a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h1v1H2Z"/></svg> Copy`; }, 1500);
    });
  },

  _saveToHistory(text, sender) {
    try {
      const key = 'risksense_chat_history';
      const hist = JSON.parse(sessionStorage.getItem(key) || '[]');
      hist.push({ text, sender, time: Date.now() });
      if (hist.length > 100) hist.splice(0, hist.length - 100);
      sessionStorage.setItem(key, JSON.stringify(hist));
    } catch (e) { /* non-critical */ }
  },

  _restoreHistory() {
    try {
      const key = 'risksense_chat_history';
      const hist = JSON.parse(sessionStorage.getItem(key) || '[]');
      if (hist.length === 0) return;
      hist.forEach(m => this._appendBubble(m.text, m.sender));
    } catch (e) { /* non-critical */ }
  },

  clearHistory() {
    sessionStorage.removeItem('risksense_chat_history');
    const win = document.getElementById('chatWindow');
    if (win) {
      win.innerHTML = `
        <div class="chat-empty-state">
          <div class="chat-empty-icon">⬡</div>
          <h3>RiskSense Advisor Ready</h3>
          <p>Chat history cleared. Ask about fraud risk signals, recommended banking actions, or how the agent pipeline works.</p>
        </div>
      `;
    }
    if (window.showToast) showToast('Chat history cleared', 'info');
  }
};

document.addEventListener('DOMContentLoaded', () => {
  AdvisorChat.init();

  // Bind suggestion chips
  document.querySelectorAll('.suggestion-chip').forEach(btn => {
    btn.addEventListener('click', () => {
      const textarea = document.getElementById('advisorMessage');
      if (textarea) {
        textarea.value = btn.textContent.trim();
        textarea.focus();
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
      }
    });
  });
});
