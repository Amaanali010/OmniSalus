/* ==========================================================================
   OmniSalus Client Engine JS
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initGroqKeyModal();
  initFormCalculators();
  initPageChatbot();
  initBMICalculators();
});

// --------------------------------------------------------------------------
// 1. GROQ API KEY MODAL, TESTING & STORAGE
// --------------------------------------------------------------------------
function initGroqKeyModal() {
  const modal = document.getElementById('groqModal');
  const btnOpen = document.getElementById('btnGroqKey');
  const btnChatKey = document.getElementById('btnChatKey');
  const btnClose = document.getElementById('btnCloseGroqModal');
  const btnSave = document.getElementById('btnSaveGroqKey');
  const btnClear = document.getElementById('btnClearGroqKey');
  const btnTest = document.getElementById('btnTestGroqKey');
  const btnToggleEye = document.getElementById('btnToggleKeyVisibility');
  const keyInput = document.getElementById('groqKeyInput');
  const modelSelect = document.getElementById('groqModelSelect');

  const navKeyDot = document.getElementById('navKeyDot');
  const navKeyText = document.getElementById('navKeyText');
  const chatKeyDot = document.getElementById('chatKeyDot');
  const modalStatusDot = document.getElementById('modalStatusDot');
  const modalStatusTitle = document.getElementById('modalStatusTitle');
  const modalStatusSub = document.getElementById('modalStatusSub');
  const modalStatusBanner = document.getElementById('modalStatusBanner');
  const modalTestResult = document.getElementById('modalTestResult');

  if (!modal) return;

  function updateKeyUI(key) {
    const hasKey = Boolean(key && key.trim());
    const displayKey = hasKey ? (key.slice(0, 7) + '...' + key.slice(-4)) : '';
    const activeModel = localStorage.getItem('omni_groq_active_model') || (modelSelect && modelSelect.value !== 'auto' ? modelSelect.value : 'LLaMA Cloud');

    if (btnOpen) {
      btnOpen.classList.toggle('is-connected', hasKey);
      btnOpen.title = hasKey ? `Groq Key Configured (${displayKey})` : 'Configure Groq AI API Key';
    }
    if (navKeyDot) navKeyDot.classList.toggle('active', hasKey);
    if (navKeyText) navKeyText.textContent = hasKey ? 'AI Active' : 'AI Key';

    if (chatKeyDot) chatKeyDot.classList.toggle('active', hasKey);

    if (modalStatusDot) modalStatusDot.classList.toggle('active', hasKey);
    if (modalStatusBanner) modalStatusBanner.classList.toggle('connected', hasKey);

    if (modalStatusTitle) {
      modalStatusTitle.textContent = hasKey ? `Groq Active (${activeModel})` : 'Rule Engine Fallback Mode';
    }
    if (modalStatusSub) {
      modalStatusSub.textContent = hasKey 
        ? `Using configured key (${displayKey}) for real-time explanations.`
        : 'Add your Groq API key to unlock real-time LLaMA diagnostic guidance.';
    }

    if (keyInput && document.activeElement !== keyInput) {
      keyInput.value = key || '';
    }
  }

  const initialKey = getStoredGroqKey();
  updateKeyUI(initialKey);

  window.addEventListener('storage', (event) => {
    if (event.key === 'omni_groq_api_key' || event.key === null) {
      updateKeyUI(getStoredGroqKey());
    }
  });

  function openModal() {
    modal.classList.add('open');
    document.body.classList.add('modal-open');
    if (modalTestResult) modalTestResult.textContent = '';
    const current = getStoredGroqKey();
    if (keyInput) {
      keyInput.value = current;
      setTimeout(() => keyInput.focus(), 50);
    }
    if (modelSelect) {
      modelSelect.value = localStorage.getItem('omni_groq_model') || 'auto';
    }
    updateKeyUI(current);
  }

  function closeModal() {
    modal.classList.remove('open');
    document.body.classList.remove('modal-open');
  }

  if (btnOpen) btnOpen.addEventListener('click', openModal);
  if (btnChatKey) btnChatKey.addEventListener('click', openModal);
  if (btnClose) btnClose.addEventListener('click', closeModal);

  // Toggle key visibility (Eye button)
  if (btnToggleEye && keyInput) {
    btnToggleEye.addEventListener('click', () => {
      const isPassword = keyInput.type === 'password';
      keyInput.type = isPassword ? 'text' : 'password';
      btnToggleEye.textContent = isPassword ? '🙈' : '👁';
    });
  }

  // Save Key
  if (btnSave && keyInput) {
    btnSave.addEventListener('click', () => {
      const key = keyInput.value.trim();
      const modelVal = modelSelect ? modelSelect.value : 'auto';
      window.omniSessionKey = key;
      let persisted = true;
      try {
        if (key) {
          localStorage.setItem('omni_groq_api_key', key);
          localStorage.setItem('omni_groq_model', modelVal);
        } else {
          localStorage.removeItem('omni_groq_api_key');
          localStorage.removeItem('omni_groq_model');
          localStorage.removeItem('omni_groq_active_model');
        }
      } catch (_) {
        persisted = false;
      }

      updateKeyUI(key);
      closeModal();
      document.querySelector('.logo-brand')?.focus();

      if (!key) {
        showToast('API key removed. Running in offline rule fallback mode.');
      } else {
        showToast(!persisted ? 'API key active for this session only.' : 'Groq settings saved successfully!');
      }
    });
  }

  // Clear Key
  if (btnClear && keyInput) {
    btnClear.addEventListener('click', () => {
      keyInput.value = '';
      window.omniSessionKey = '';
      try { 
        localStorage.removeItem('omni_groq_api_key'); 
        localStorage.removeItem('omni_groq_model');
        localStorage.removeItem('omni_groq_active_model');
      } catch (_) {}
      if (modelSelect) modelSelect.value = 'auto';
      updateKeyUI('');
      if (modalTestResult) modalTestResult.innerHTML = '<span style="color:var(--text-muted);">Key cleared. Using local rule engine.</span>';
      showToast('API key cleared. Offline rule engine enabled.');
    });
  }

  // Test Key Connection
  if (btnTest && keyInput) {
    btnTest.addEventListener('click', async () => {
      const key = keyInput.value.trim();
      const modelVal = modelSelect ? modelSelect.value : 'auto';
      if (!key) {
        if (modalTestResult) modalTestResult.innerHTML = '<span style="color:#f87171;">Please enter an API key first to test.</span>';
        showToast('Please enter an API key before testing.');
        return;
      }

      const origText = btnTest.innerHTML;
      btnTest.disabled = true;
      btnTest.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Testing...`;
      if (modalTestResult) modalTestResult.innerHTML = '<span style="color:var(--primary-cyan);">Pinging Groq AI API...</span>';

      try {
        const resp = await fetch('/api/test-key', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            groq_api_key: key,
            model: modelVal
          })
        });
        const data = await resp.json();
        btnTest.disabled = false;
        btnTest.innerHTML = origText;

        if (data.status === 'success') {
          if (data.verified_model) {
            localStorage.setItem('omni_groq_active_model', data.verified_model);
          }
          if (modalTestResult) modalTestResult.innerHTML = `<span style="color:#58ebc6;">✓ ${data.message}</span>`;
          showToast(`Connection verified! ${data.verified_model || 'Groq'} active.`);
          updateKeyUI(key);
        } else {
          if (modalTestResult) modalTestResult.innerHTML = `<span style="color:#f87171;">✗ ${data.message}</span>`;
          showToast(`Test failed: ${data.message}`);
        }
      } catch (err) {
        btnTest.disabled = false;
        btnTest.innerHTML = origText;
        if (modalTestResult) modalTestResult.innerHTML = `<span style="color:#f87171;">✗ Network error reaching server.</span>`;
        showToast('Network error while testing API key.');
      }
    });
  }
}

function getStoredGroqKey() {
  try { return localStorage.getItem('omni_groq_api_key') || window.omniSessionKey || ''; }
  catch (_) { return window.omniSessionKey || ''; }
}

// --------------------------------------------------------------------------
// 2. FORM CALCULATORS & AJAX PREDICTION
// --------------------------------------------------------------------------
function initFormCalculators() {
  const forms = document.querySelectorAll('.prediction-form');

  forms.forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const modelType = form.dataset.modelType;
      const formData = new FormData(form);
      const payload = {};

      formData.forEach((val, key) => {
        payload[key] = !isNaN(val) && val !== '' ? parseFloat(val) : val;
      });

      if (modelType === 'heart') {
        const activeToggle = document.querySelector('.toggle-btn.active');
        payload.model_variant = activeToggle ? activeToggle.dataset.variant : 'all';
      }

      const btnSubmit = form.querySelector('button[type="submit"]');
      const origText = btnSubmit.innerHTML;
      btnSubmit.disabled = true;
      btnSubmit.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Calculating Diagnostic Score...`;

      try {
        const resp = await fetch(`/api/predict/${modelType}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        
        const data = await resp.json();
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = origText;

        if (data.status === 'success') {
          renderPredictionResult(modelType, data.result, payload, data.report_token);
        } else {
          showToast(`Prediction error: ${data.message}`);
        }
      } catch (err) {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = origText;
        console.error('API Error:', err);
        showToast('Could not reach the server. Please try again.');
      }
    });
  });

  const toggleBtns = document.querySelectorAll('.model-toggle-group .toggle-btn');
  toggleBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      toggleBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });
}

function renderPredictionResult(modelType, res, userInputs, reportToken) {
  const resultCard = document.getElementById('resultCard');
  if (!resultCard) return;

  resultCard.style.display = 'block';
  document.querySelector('.assistant-welcome')?.setAttribute('hidden', '');
  resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  const gaugeFill = document.getElementById('gaugeFill');
  const scoreText = document.getElementById('scoreText');
  const severityBadge = document.getElementById('severityBadge');
  const diagText = document.getElementById('diagText');

  let pct = null;
  if (res.probability_pct !== undefined) pct = res.probability_pct;
  else if (res.confidence_pct !== undefined) pct = res.confidence_pct;
  else if (res.consensus_prob_pct !== undefined) pct = res.consensus_prob_pct;

  if (scoreText) scoreText.textContent = pct === null ? 'N/A' : `${pct}%`;
  if (diagText) diagText.textContent = res.diagnosis || res.obesity_level || 'Evaluation Complete';

  if (severityBadge) {
    severityBadge.textContent = res.severity || 'Risk Evaluated';
    severityBadge.className = `severity-badge badge-${res.badge_class || 'info'}`;
  }

  if (gaugeFill) {
    const strokeDash = 502;
    const offset = strokeDash - (strokeDash * (pct / 100));
    gaugeFill.style.strokeDasharray = strokeDash;
    gaugeFill.style.strokeDashoffset = offset;

    if (res.badge_class === 'success') gaugeFill.style.stroke = '#10b981';
    else if (res.badge_class === 'warning') gaugeFill.style.stroke = '#f59e0b';
    else if (res.badge_class === 'danger') gaugeFill.style.stroke = '#f43f5e';
    else gaugeFill.style.stroke = '#ef4444';
  }

  const compBox = document.getElementById('heartComparisonBox');
  if (compBox) { compBox.style.display = 'none'; compBox.innerHTML = ''; }
  if (compBox && res.lgbm) {
    compBox.style.display = 'block';
    compBox.innerHTML = `
      <div style="font-weight:700; margin-bottom:0.75rem; font-size:0.9rem;">Model Comparison Breakdown:</div>
      <div class="comp-row">
        <span>LightGBM (AUC: 83.66%)</span>
        <strong>${res.lgbm.probability_pct}% (${res.lgbm.severity})</strong>
      </div>
      <div class="comp-row">
        <span>XGBoost (AUC: 83.64%)</span>
        <strong>${res.xgb.probability_pct}% (${res.xgb.severity})</strong>
      </div>
      <div class="comp-row">
        <span>Logistic Regression (AUC: 83.23%)</span>
        <strong>${res.logreg.probability_pct}% (${res.logreg.severity})</strong>
      </div>
    `;
  }

  const topDownload = document.getElementById('downloadReport');
  const topToken = document.getElementById('reportToken');
  const reportHint = document.getElementById('reportHint');
  if (topToken) topToken.value = reportToken || '';
  if (topDownload) topDownload.disabled = !reportToken;
  if (reportHint) reportHint.textContent = reportToken ? 'Your report is ready. It includes this result and the inputs you submitted.' : 'Restart the updated server, then run the assessment again.';
  resultCard.querySelector('.server-report-form')?.remove();
  const downloadForm = document.createElement('form');
  downloadForm.className = 'server-report-form';
  downloadForm.method = 'POST';
  downloadForm.action = '/api/report';
  const token = document.createElement('input');
  token.type = 'hidden'; token.name = 'report_token'; token.value = reportToken || '';
  const reportButton = document.createElement('button');
  reportButton.type = 'submit'; reportButton.className = 'btn-primary download-report';
  reportButton.style.marginTop = '20px'; reportButton.textContent = 'Download result PDF';
  reportButton.disabled = !reportToken;
  downloadForm.append(token, reportButton); resultCard.append(downloadForm);
  if (!reportToken) showToast('Restart the updated Python app and run the assessment again to enable PDF reports.');
  const unit = resultCard.querySelector('.gauge-unit');
  if (unit) unit.textContent = res.confidence_pct !== undefined ? 'Classification confidence' : 'Model probability';
  if (modelType === 'obesity') {
    const ring = resultCard.querySelector('.gauge-svg');
    if (ring) ring.style.display = 'none';
    if (scoreText) scoreText.textContent = res.calculated_bmi ?? 'N/A';
    if (unit) unit.textContent = 'Calculated BMI';
    let bmi = resultCard.querySelector('.result-bmi');
    if (!bmi) { bmi = document.createElement('p'); bmi.className = 'result-bmi assessment-intro'; resultCard.insertBefore(bmi, downloadForm); }
    bmi.textContent = `Model confidence in this category: ${res.confidence_pct ?? 'N/A'}%. This is not an obesity severity score.`;
    let details = resultCard.querySelector('.class-probabilities');
    if (!details) { details = document.createElement('details'); details.className = 'class-probabilities'; resultCard.insertBefore(details, downloadForm); }
    details.replaceChildren();
    const summary = document.createElement('summary'); summary.textContent = 'View all category probabilities'; details.append(summary);
    Object.entries(res.class_probabilities_pct || {}).forEach(([name, value]) => {
      const row = document.createElement('p'); row.textContent = `${name}: ${value}%`; details.append(row);
    });
  }
  window.currentModelResult = res;
  window.currentUserInputs = userInputs;
  try {
    sessionStorage.setItem('omni_report_' + modelType, JSON.stringify({
      result: res,
      inputs: userInputs,
      timestamp: Date.now()
    }));
  } catch (_) {}

  showToast('Assessment complete. Diagnostic score calculated.');
}

function getLiveFormInputs() {
  const form = document.querySelector('.prediction-form');
  if (!form) return {};
  const formData = new FormData(form);
  const inputs = {};
  formData.forEach((val, key) => {
    inputs[key] = !isNaN(val) && val !== '' ? parseFloat(val) : val;
  });
  return inputs;
}

function getActiveReportContext(pageId) {
  let res = window.currentModelResult;
  let inputs = window.currentUserInputs;

  if (!res) {
    try {
      const saved = sessionStorage.getItem('omni_report_' + pageId);
      if (saved) {
        const parsed = JSON.parse(saved);
        res = parsed.result;
        inputs = parsed.inputs;
        window.currentModelResult = res;
        window.currentUserInputs = inputs;
      }
    } catch (_) {}
  }

  const live = getLiveFormInputs();
  const mergedInputs = Object.assign({}, live, inputs || {});
  return { modelResult: res || null, userInputs: mergedInputs };
}

window.omniChatHistory = window.omniChatHistory || [];

// --------------------------------------------------------------------------
// 3. PAGE-SPECIFIC CHATBOT (ONLY ON DISEASE CALCULATOR PAGES)
// --------------------------------------------------------------------------
function initPageChatbot() {
  const trigger = document.getElementById('chatTrigger');
  const drawer = document.getElementById('chatDrawer');
  const btnClose = document.getElementById('btnCloseChat');
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');

  if (!trigger || !drawer) return;

  const currentPageId = drawer.dataset.pageId;

  trigger.addEventListener('click', () => {
    drawer.classList.toggle('open');
  });

  if (btnClose) {
    btnClose.addEventListener('click', () => {
      drawer.classList.remove('open');
    });
  }

  if (chatForm) {
    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const msg = chatInput.value.trim();
      if (!msg) return;

      appendChatMessage('user', msg);
      window.omniChatHistory.push({ role: 'user', content: msg });
      chatInput.value = '';

      const typingId = appendChatMessage('assistant', 'Thinking…');
      const ctx = getActiveReportContext(currentPageId);

      try {
        const resp = await fetch('/api/chat/page', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            page_id: currentPageId,
            message: msg,
            user_inputs: ctx.userInputs,
            model_result: ctx.modelResult,
            groq_api_key: getStoredGroqKey(),
            model: localStorage.getItem('omni_groq_model') || 'auto',
            history: window.omniChatHistory.slice(-8)
          })
        });

        const data = await resp.json();
        removeChatMessage(typingId);

        if (data.status === 'success') {
          appendChatMessage('assistant', data.reply);
          window.omniChatHistory.push({ role: 'assistant', content: data.reply });
        } else {
          appendChatMessage('assistant', 'Sorry, I encountered an error answering your question.');
        }
      } catch (err) {
        removeChatMessage(typingId);
        appendChatMessage('assistant', 'Unable to reach page assistant.');
      }
    });
  }
}

function appendChatMessage(sender, text) {
  const chatBody = document.getElementById('chatBody');
  if (!chatBody) return;

  const msgDiv = document.createElement('div');
  const msgId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`;
  msgDiv.id = msgId;
  msgDiv.className = `chat-msg ${sender}`;
  
  let formatted = String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.*?)`/g, '<code>$1</code>');

  msgDiv.innerHTML = formatted;
  chatBody.appendChild(msgDiv);
  chatBody.scrollTop = chatBody.scrollHeight;
  return msgId;
}

function removeChatMessage(msgId) {
  const el = document.getElementById(msgId);
  if (el) el.remove();
}

// --------------------------------------------------------------------------
// 4. REAL-TIME BMI CALCULATOR HELPER
// --------------------------------------------------------------------------
function initBMICalculators() {
  const heightInput = document.getElementById('inputHeight');
  const weightInput = document.getElementById('inputWeight');
  const bmiDisplay = document.getElementById('bmiDisplay');

  if (!heightInput || !weightInput || !bmiDisplay) return;

  function calc() {
    const h = parseFloat(heightInput.value);
    const w = parseFloat(weightInput.value);
    if (h > 0 && w > 0) {
      const h_m = h > 3 ? h / 100 : h;
      const bmi = (w / (h_m * h_m)).toFixed(1);
      bmiDisplay.textContent = `Calculated BMI: ${bmi}`;
    }
  }

  heightInput.addEventListener('input', calc);
  weightInput.addEventListener('input', calc);
}

