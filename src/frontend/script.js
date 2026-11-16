/**
 * script.js — KIET AI Chatbot Help Desk Frontend Logic
 * Institution: KIET Group of Institutions, Ghaziabad
 * Pure Vanilla JavaScript (No external frameworks)
 */

(function () {
  'use strict';

  // ──────────────────────────────────────────────
  // Configuration & State
  // ──────────────────────────────────────────────
  const API_ENDPOINT = (window.location.protocol === 'file:' || !window.location.port || window.location.port !== '5000')
    ? 'https://ai-chatbot-for-university-help-desk.onrender.com/api/chat'
    : '/api/chat';

  const STORAGE_KEY = 'kiet_chat_session_id';

  // DOM Elements
  const chatMessages = document.getElementById('chat-messages');
  const welcomeSection = document.getElementById('welcome-section');
  const chatForm = document.getElementById('chat-form');
  const userInput = document.getElementById('user-input');
  const sendBtn = document.getElementById('send-btn');
  const charCounter = document.getElementById('char-counter');
  const typingIndicator = document.getElementById('typing-indicator');
  const clearChatBtn = document.getElementById('clear-chat-btn');
  const clearModal = document.getElementById('clear-modal');
  const cancelClearBtn = document.getElementById('cancel-clear-btn');
  const confirmClearBtn = document.getElementById('confirm-clear-btn');
  const suggestedQuestions = document.getElementById('suggested-questions');
  const toast = document.getElementById('toast');

  let isSending = false;

  // ──────────────────────────────────────────────
  // Session ID Management (Reused across messages)
  // ──────────────────────────────────────────────
  function generateUUID() {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
      return crypto.randomUUID();
    }
    return 'kiet_' + Date.now() + '_' + Math.random().toString(36).substring(2, 11);
  }

  function getSessionId() {
    let sid = localStorage.getItem(STORAGE_KEY);
    if (!sid) {
      sid = generateUUID();
      localStorage.setItem(STORAGE_KEY, sid);
    }
    return sid;
  }

  function resetSessionId() {
    const newSid = generateUUID();
    localStorage.setItem(STORAGE_KEY, newSid);
    return newSid;
  }

  // ──────────────────────────────────────────────
  // Toast Notifications
  // ──────────────────────────────────────────────
  let toastTimer = null;
  function showToast(message, isError = false) {
    if (toastTimer) clearTimeout(toastTimer);
    toast.textContent = message;
    toast.className = 'toast' + (isError ? ' error' : '');
    toastTimer = setTimeout(() => {
      toast.className = 'toast hidden';
    }, 3500);
  }

  // ──────────────────────────────────────────────
  // Textarea Auto-Resize & Character Counter
  // ──────────────────────────────────────────────
  function updateInputState() {
    const val = userInput.value;
    charCounter.textContent = `${val.length}/500`;

    // Auto-adjust height
    userInput.style.height = 'auto';
    const newHeight = Math.min(userInput.scrollHeight, 120);
    userInput.style.height = Math.max(newHeight, 24) + 'px';

    // Enable/disable send button
    const hasText = val.trim().length >= 2;
    sendBtn.disabled = !hasText || isSending;
  }

  userInput.addEventListener('input', updateInputState);

  // Keyboard shortcut: Enter to send, Shift+Enter for newline
  userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!sendBtn.disabled) {
        handleFormSubmit();
      }
    }
  });

  // ──────────────────────────────────────────────
  // Message Rendering
  // ──────────────────────────────────────────────
  function formatTimestamp() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function appendUserMessage(text) {
    // Hide welcome card on first message
    if (welcomeSection && !welcomeSection.classList.contains('hidden')) {
      welcomeSection.classList.add('hidden');
    }

    const row = document.createElement('div');
    row.className = 'message-row user';

    const avatar = document.createElement('div');
    avatar.className = 'avatar user-avatar';
    avatar.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
        <circle cx="12" cy="7" r="4"/>
      </svg>
    `;

    const content = document.createElement('div');
    content.className = 'message-content';

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;

    const meta = document.createElement('div');
    meta.className = 'message-meta';
    meta.innerHTML = `<span>${formatTimestamp()}</span>`;

    content.appendChild(bubble);
    content.appendChild(meta);
    row.appendChild(avatar);
    row.appendChild(content);

    // Insert before typing indicator
    chatMessages.insertBefore(row, typingIndicator);
    scrollToBottom();
  }

  function appendBotMessage(data) {
    const row = document.createElement('div');
    row.className = 'message-row bot';

    const avatar = document.createElement('div');
    avatar.className = 'avatar bot-avatar';
    avatar.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 2a2 2 0 0 1 2 2v2h4a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4V4a2 2 0 0 1 2-2z"/>
        <circle cx="9" cy="13" r="1"/>
        <circle cx="15" cy="13" r="1"/>
      </svg>
    `;

    const content = document.createElement('div');
    content.className = 'message-content';

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = data.answer || "I'm sorry, I could not process your query.";

    // Meta row (category, confidence, time)
    const meta = document.createElement('div');
    meta.className = 'message-meta';

    let metaHtml = `<span>${formatTimestamp()}</span>`;

    if (data.category && data.category !== 'Unknown') {
      metaHtml += `<span class="category-tag">${escapeHtml(data.category)}</span>`;
    }

    if (typeof data.confidence === 'number' && data.confidence > 0) {
      const pct = Math.round(data.confidence * 100);
      metaHtml += `<span class="confidence-tag" title="Calculated Cosine Similarity: ${data.confidence}">
        &bull; ${pct}% Match
      </span>`;
    }

    meta.innerHTML = metaHtml;
    content.appendChild(bubble);

    // Source link if available
    if (data.source && data.source.startsWith('http') && data.category !== 'Unknown') {
      const sourceCard = document.createElement('div');
      sourceCard.className = 'source-card';
      const labelText = data.is_verified ? 'Verified Source:' : 'Reference Link:';
      const badgeIcon = data.is_verified ? '✓ ' : '';
      sourceCard.innerHTML = `
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
          <polyline points="15 3 21 3 21 9"/>
          <line x1="10" y1="14" x2="21" y2="3"/>
        </svg>
        <span>${escapeHtml(badgeIcon + labelText)}</span>
        <a href="${escapeHtml(data.source)}" target="_blank" rel="noopener noreferrer">${escapeHtml(data.source)}</a>
      `;
      content.appendChild(sourceCard);
    }

    content.appendChild(meta);
    row.appendChild(avatar);
    row.appendChild(content);

    chatMessages.insertBefore(row, typingIndicator);
    scrollToBottom();
  }

  function appendErrorMessage(errorText) {
    const row = document.createElement('div');
    row.className = 'message-row bot';

    const avatar = document.createElement('div');
    avatar.className = 'avatar bot-avatar';
    avatar.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
    `;

    const content = document.createElement('div');
    content.className = 'message-content';

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.style.borderColor = 'var(--danger-red)';
    bubble.style.backgroundColor = '#FEF2F2';
    bubble.textContent = `⚠️ ${errorText}`;

    const meta = document.createElement('div');
    meta.className = 'message-meta';
    meta.innerHTML = `<span>${formatTimestamp()}</span> &bull; <span style="color:var(--danger-red);">Error</span>`;

    content.appendChild(bubble);
    content.appendChild(meta);
    row.appendChild(avatar);
    row.appendChild(content);

    chatMessages.insertBefore(row, typingIndicator);
    scrollToBottom();
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function scrollToBottom() {
    requestAnimationFrame(() => {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    });
  }

  // ──────────────────────────────────────────────
  // API Communication (POST /api/chat)
  // ──────────────────────────────────────────────
  async function sendChatMessage(messageText) {
    const trimmed = messageText.trim();
    if (!trimmed || trimmed.length < 2) {
      showToast('Please enter at least 2 characters.', true);
      return;
    }

    if (isSending) return;
    isSending = true;

    // Display user bubble
    appendUserMessage(trimmed);

    // Reset input
    userInput.value = '';
    updateInputState();

    // Show typing animation
    typingIndicator.classList.remove('hidden');
    scrollToBottom();

    const sessionId = getSessionId();

    try {
      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: trimmed,
          session_id: sessionId,
        }),
      });

      typingIndicator.classList.add('hidden');

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        const errorMsg = (data && data.error) || `Server error (${response.status}). Please try again.`;
        appendErrorMessage(errorMsg);
        showToast(errorMsg, true);
        return;
      }

      if (data && data.success) {
        appendBotMessage(data);
      } else {
        const errorMsg = (data && data.error) || 'Failed to retrieve response from server.';
        appendErrorMessage(errorMsg);
      }
    } catch (err) {
      typingIndicator.classList.add('hidden');
      console.error('Chat API Error:', err);
      const networkError = 'Unable to connect to KIET Help Desk server. Please check your backend connection.';
      appendErrorMessage(networkError);
      showToast(networkError, true);
    } finally {
      isSending = false;
      updateInputState();
      userInput.focus();
    }
  }

  function handleFormSubmit(e) {
    if (e) e.preventDefault();
    const text = userInput.value;
    sendChatMessage(text);
  }

  chatForm.addEventListener('submit', handleFormSubmit);

  // ──────────────────────────────────────────────
  // Suggested Questions
  // ──────────────────────────────────────────────
  if (suggestedQuestions) {
    suggestedQuestions.addEventListener('click', (e) => {
      const btn = e.target.closest('.chip-btn');
      if (btn) {
        const query = btn.getAttribute('data-query');
        if (query) {
          sendChatMessage(query);
        }
      }
    });
  }

  // ──────────────────────────────────────────────
  // Clear Conversation Modal & Handling
  // ──────────────────────────────────────────────
  clearChatBtn.addEventListener('click', () => {
    clearModal.classList.remove('hidden');
  });

  cancelClearBtn.addEventListener('click', () => {
    clearModal.classList.add('hidden');
  });

  clearModal.addEventListener('click', (e) => {
    if (e.target === clearModal) {
      clearModal.classList.add('hidden');
    }
  });

  confirmClearBtn.addEventListener('click', () => {
    clearModal.classList.add('hidden');

    // Remove all message rows
    const rows = chatMessages.querySelectorAll('.message-row');
    rows.forEach((row) => row.remove());

    // Show welcome section again
    if (welcomeSection) {
      welcomeSection.classList.remove('hidden');
    }

    // Reset session ID
    resetSessionId();

    // Reset input
    userInput.value = '';
    updateInputState();

    showToast('Started a new conversation.');
    userInput.focus();
  });

  // ──────────────────────────────────────────────
  // Initial Setup
  // ──────────────────────────────────────────────
  getSessionId(); // Ensure session ID is initialized
  updateInputState();
  userInput.focus();
})();
