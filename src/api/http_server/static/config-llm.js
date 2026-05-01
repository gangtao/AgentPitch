// Agent Pitch — Config LLM Tab Module
// Implements the LLM tab form with provider sections and Secret Input pattern
// Phase 3d scope: LLM tab implementation

// ── Constants ───────────────────────────────────────────────────
const BUILTIN_PROVIDERS = new Set(['openai', 'anthropic', 'gemini']);

const DEFAULT_PROVIDER_CONFIGS = {
  openai: { url: 'https://api.openai.com/v1', model: 'gpt-4o' },
  anthropic: { url: 'https://api.anthropic.com', model: 'claude-sonnet-4-6' },
  gemini: { url: 'https://generativelanguage.googleapis.com', model: 'gemini-2.0-flash' }
};

// ── State ───────────────────────────────────────────────────────
let rootElement = null;
let savedValues = {};
let currentValues = {};
let isDirty = false;
let isValid = true;

// Auto-rehide timers for secret inputs
const revealTimers = new Map(); // provider -> timer ID

// Available models per provider, populated by /api/config/llm/test responses.
// Empty until the user clicks Test connection successfully — see ADR-0020
// amendment 2026-04-25 (test-before-save) for the full flow.
const availableModels = {}; // { openai: ['gpt-4o', ...], anthropic: [...] }

// ── Validation ──────────────────────────────────────────────────
function validateProvider(providerData) {
  const errors = {};

  if (!providerData.url || !providerData.url.trim()) {
    errors.url = 'URL is required';
  } else {
    try {
      new URL(providerData.url);
    } catch (e) {
      errors.url = 'Must be a valid URL';
    }
  }

  if (!providerData.model || !providerData.model.trim()) {
    errors.model = 'Model is required';
  }

  return { valid: Object.keys(errors).length === 0, errors };
}

function validateAllProviders() {
  let allValid = true;

  for (const [providerName, providerData] of Object.entries(currentValues)) {
    const validation = validateProvider(providerData);
    if (!validation.valid) {
      allValid = false;
      break;
    }
  }

  isValid = allValid;
  _emitDirtyChangedEvent();
}

// ── DOM Rendering ───────────────────────────────────────────────
// Provider panel layout follows the design-system "In context — B. LLM · OpenAI"
// pattern: .form-sect outer panel · .ap-section header with em-dash rule and an
// inline .dot-status badge · .form-row rows where the control spans columns 2-3
// via .row-wide. Secrets use the .ipt-cluster pattern; "Source: …" lives in a
// .help line below the cluster.
function renderLLMTab() {
  if (!rootElement) return;

  // Separate built-in and custom providers
  const builtinProviders = Object.entries(currentValues).filter(([name]) => BUILTIN_PROVIDERS.has(name));
  const customProviders = Object.entries(currentValues).filter(([name]) => !BUILTIN_PROVIDERS.has(name));

  // Render built-in providers (A, B, C)
  let sectionIndex = 0;
  const builtinHTML = builtinProviders.map(([providerName, providerData]) => {
    const sectionLetter = String.fromCharCode(65 + sectionIndex++);
    return renderProviderPanel(providerName, providerData, sectionLetter, false);
  }).join('');

  // Render custom providers (continuing letter sequence)
  const customHTML = customProviders.length > 0 ? `
    <div class="ap-section" style="margin-top:32px;margin-bottom:18px">
      <span>Custom Providers</span>
      <span class="rule"></span>
    </div>
    ${customProviders.map(([providerName, providerData]) => {
      const sectionLetter = String.fromCharCode(65 + sectionIndex++);
      return renderProviderPanel(providerName, providerData, sectionLetter, true);
    }).join('')}
  ` : '';

  // Add Custom Provider button
  const addButtonHTML = `
    <div class="form-row" style="margin-top:24px">
      <div class="row-label"></div>
      <div class="row-wide">
        <button class="btn btn-secondary" type="button" id="add-custom-provider-btn">
          + Add Custom Provider
        </button>
      </div>
    </div>
  `;

  rootElement.innerHTML = `
    <div class="llm-tab-form">
      ${builtinHTML}
      ${customHTML}
      ${addButtonHTML}
    </div>
  `;

  // Wire up event handlers
  setupFormEventHandlers();
}

function renderProviderPanel(providerName, providerData, sectionLetter, isCustom) {
    const displayName = isCustom ? providerName : providerName.toUpperCase();
    const models = availableModels[providerName] || [];

    // Determine key source and input state
    const keyStatus = providerData.key_status || 'unset';
    const isEnvOverridden = keyStatus === 'env_overridden';

    let sourceLabel;
    switch (keyStatus) {
      case 'env_overridden':
        sourceLabel = `Source: env var (${providerName.toUpperCase()}_API_KEY) — overrides secrets file`;
        break;
      case 'set':
        if (_hasEnvVar(providerName)) {
          sourceLabel = `Source: env var (${providerName.toUpperCase()}_API_KEY)`;
        } else {
          sourceLabel = 'Source: secrets file';
        }
        break;
      default:
        sourceLabel = 'Source: not set';
    }

    // Build the model <option> list. Three cases:
    //   1. No models loaded yet → single placeholder option, dropdown disabled.
    //   2. Models loaded and the saved value is in the list → render normally.
    //   3. Models loaded but the saved value is NOT in the list (model retired
    //      or key changed) → keep the saved value as a "(saved)" option so the
    //      form still validates and the user can see what they had before.
    const savedModel = providerData.model || '';
    let modelsHTML;
    if (models.length === 0) {
      modelsHTML = `<option value="${savedModel}" selected>${savedModel || 'Test connection to load models'}</option>`;
    } else {
      const savedInList = !savedModel || models.includes(savedModel);
      const savedFallback = (savedModel && !savedInList)
        ? `<option value="${savedModel}" selected>${savedModel} (saved — not in current list)</option>`
        : '';
      modelsHTML = savedFallback + models.map(model =>
        `<option value="${model}" ${model === savedModel ? 'selected' : ''}>${model}</option>`
      ).join('');
    }
    const modelSelectDisabled = models.length === 0 ? 'disabled' : '';

    const keyFieldDisabled = isEnvOverridden ? 'aria-disabled="true"' : '';
    const keyFieldClass = `ipt secret-input${isEnvOverridden ? ' env-overridden' : ''}`;
    const keyPlaceholder = providerName === 'anthropic' ? 'sk-ant-…' : 'sk-…';
    const buttonsDisabled = isEnvOverridden || !providerData.key ? 'disabled' : '';

    // Add remove button for custom providers
    const removeButton = isCustom ? `
      <button class="btn btn-text" type="button" style="margin-left:auto;font-size:11px;color:var(--text-muted)"
              data-action="remove-provider" data-provider="${providerName}">Remove</button>
    ` : '';

    return `
      <section class="form-sect llm-provider-panel" data-provider="${providerName}">
        <div class="ap-section" style="margin-top:0;margin-bottom:18px;display:flex;align-items:center">
          <span>${sectionLetter}. ${displayName}</span>
          <span class="rule"></span>
          <span class="dot-status warn" id="status-${providerName}" style="font-size:11px">Not tested</span>
          ${removeButton}
        </div>

        <div class="form-row">
          <div class="row-label"><label for="field-${providerName}-key">API key</label></div>
          <div class="row-wide" style="max-width:520px">
            <div class="ipt-cluster">
              <input
                type="password"
                id="field-${providerName}-key"
                class="${keyFieldClass}"
                value="${providerData.key || ''}"
                ${keyFieldDisabled}
                data-provider="${providerName}"
                data-field="key"
                placeholder="${keyPlaceholder}"
              />
              <button class="ipt-btn" type="button" ${buttonsDisabled}
                      data-provider="${providerName}" data-action="reveal" aria-pressed="false">Reveal</button>
              <button class="ipt-btn" type="button" ${buttonsDisabled}
                      data-provider="${providerName}" data-action="clear">Clear</button>
            </div>
            <div class="help" style="margin-top:6px" id="source-${providerName}">${sourceLabel}</div>
          </div>
        </div>

        <div class="form-row">
          <div class="row-label"><label for="field-${providerName}-url">URL</label></div>
          <div class="row-wide" style="max-width:520px">
            <input
              type="url"
              id="field-${providerName}-url"
              class="ipt"
              value="${providerData.url || ''}"
              data-provider="${providerName}"
              data-field="url"
              placeholder="https://api.example.com/v1"
            />
            <div class="help err" id="error-${providerName}-url" style="display:none"></div>
          </div>
        </div>

        <div class="form-row">
          <div class="row-label"><label for="field-${providerName}-model">Model</label></div>
          <div class="row-wide" style="max-width:260px">
            <select
              id="field-${providerName}-model"
              class="sel"
              data-provider="${providerName}"
              data-field="model"
              ${modelSelectDisabled}
            >
              ${modelsHTML}
            </select>
            <div class="help err" id="error-${providerName}-model" style="display:none"></div>
          </div>
        </div>

        <div class="form-row">
          <div class="row-label">Connection test</div>
          <div class="row-wide" style="display:flex;gap:14px;align-items:center">
            <button class="btn btn-primary test-connection-btn" type="button"
                    data-provider="${providerName}">Test connection</button>
            <span class="dot-status warn" id="test-result-${providerName}">Not tested</span>
          </div>
        </div>
      </section>
    `;
}

function _hasEnvVar(provider) {
  // This is a UI heuristic - in practice the server determines the actual precedence
  const envVarName = `${provider.toUpperCase()}_API_KEY`;
  return false; // We can't actually check env vars from the browser
}

function setupFormEventHandlers() {
  if (!rootElement) return;

  // Field input/select handlers — covers .ipt and .sel inputs that carry
  // both data-provider and data-field. (Replaces the old .field-input class.)
  rootElement.querySelectorAll('[data-provider][data-field]').forEach(input => {
    const evt = input.tagName === 'SELECT' ? 'change' : 'input';
    input.addEventListener(evt, () => handleFieldChange(input));
    input.addEventListener('blur',  () => handleFieldChange(input));
  });

  // Secret cluster button handlers — Reveal toggles, Clear opens confirm modal.
  rootElement.querySelectorAll('.ipt-btn[data-action="reveal"]').forEach(btn => {
    btn.addEventListener('click', () => handleSecretReveal(btn.dataset.provider));
  });
  rootElement.querySelectorAll('.ipt-btn[data-action="clear"]').forEach(btn => {
    btn.addEventListener('click', () => handleSecretClear(btn.dataset.provider));
  });

  // Test connection handlers
  rootElement.querySelectorAll('.test-connection-btn').forEach(btn => {
    btn.addEventListener('click', () => handleTestConnection(btn.dataset.provider));
  });

  // Auto-rehide timer reset for revealed secret inputs
  rootElement.querySelectorAll('.secret-input').forEach(input => {
    input.addEventListener('focus', () => {
      if (input.type === 'text') resetRevealTimer(input.dataset.provider);
    });
    input.addEventListener('input', () => {
      if (input.type === 'text') resetRevealTimer(input.dataset.provider);
    });
  });

  // Add Custom Provider button
  const addBtn = rootElement.querySelector('#add-custom-provider-btn');
  if (addBtn) {
    addBtn.addEventListener('click', handleAddCustomProvider);
  }

  // Remove Provider buttons
  rootElement.querySelectorAll('[data-action="remove-provider"]').forEach(btn => {
    btn.addEventListener('click', () => handleRemoveProvider(btn.dataset.provider));
  });
}

function handleFieldChange(input) {
  const provider = input.dataset.provider;
  const field = input.dataset.field;
  const value = input.value;

  if (!currentValues[provider]) {
    currentValues[provider] = {};
  }

  currentValues[provider][field] = value;

  // Validate the provider
  const validation = validateProvider(currentValues[provider]);
  const errorElement = rootElement.querySelector(`#error-${provider}-${field}`);

  if (errorElement) {
    const fieldError = validation.errors[field];
    if (fieldError) {
      input.classList.add('field-error-state');
      errorElement.textContent = `⚠ ${fieldError}`;
      errorElement.style.display = 'block';
    } else {
      input.classList.remove('field-error-state');
      errorElement.textContent = '';
      errorElement.style.display = 'none';
    }
  }

  // Update secret input button states for key fields
  if (field === 'key') {
    updateSecretInputButtons(provider);
  }

  _updateDirtyState();
  validateAllProviders();
}

function updateSecretInputButtons(provider) {
  const providerData = currentValues[provider] || {};
  const hasKey = providerData.key && providerData.key.trim();
  const isEnvOverridden = providerData.key_status === 'env_overridden';

  const revealBtn = rootElement.querySelector(`[data-provider="${provider}"][data-action="reveal"]`);
  const clearBtn = rootElement.querySelector(`[data-provider="${provider}"][data-action="clear"]`);

  if (revealBtn) {
    revealBtn.disabled = !hasKey || isEnvOverridden;
  }
  if (clearBtn) {
    clearBtn.disabled = !hasKey || isEnvOverridden;
  }
}

function handleSecretReveal(provider) {
  const input = rootElement.querySelector(`#field-${provider}-key`);
  const btn = rootElement.querySelector(`[data-provider="${provider}"][data-action="reveal"]`);

  if (!input || !btn) return;

  if (input.type === 'password') {
    // Reveal
    input.type = 'text';
    btn.textContent = 'Hide';
    btn.setAttribute('aria-pressed', 'true');

    // Start auto-rehide timer
    startRevealTimer(provider);

    // Announce to screen readers
    announceToScreenReader('API key revealed');
  } else {
    // Hide
    hideSecretInput(provider);
  }
}

function hideSecretInput(provider) {
  const input = rootElement.querySelector(`#field-${provider}-key`);
  const btn = rootElement.querySelector(`[data-provider="${provider}"][data-action="reveal"]`);

  if (!input || !btn) return;

  input.type = 'password';
  btn.textContent = 'Reveal';
  btn.setAttribute('aria-pressed', 'false');

  // Clear timer
  clearRevealTimer(provider);

  // Announce to screen readers
  announceToScreenReader('API key hidden');
}

function startRevealTimer(provider) {
  clearRevealTimer(provider); // Clear any existing timer

  const timerId = setTimeout(() => {
    hideSecretInput(provider);
  }, 30000); // 30 seconds per ADR-0020

  revealTimers.set(provider, timerId);
}

function resetRevealTimer(provider) {
  if (revealTimers.has(provider)) {
    startRevealTimer(provider); // Restart the timer
  }
}

function clearRevealTimer(provider) {
  if (revealTimers.has(provider)) {
    clearTimeout(revealTimers.get(provider));
    revealTimers.delete(provider);
  }
}

function handleSecretClear(provider) {
  const displayName = provider.charAt(0).toUpperCase() + provider.slice(1);

  showClearConfirmModal(provider, displayName, () => {
    // Clear the key field
    const input = rootElement.querySelector(`#field-${provider}-key`);
    if (input) {
      input.value = '';
      handleFieldChange(input); // Trigger change handling
    }
  });
}

function showClearConfirmModal(provider, displayName, onConfirm) {
  const modal = document.createElement('dialog');
  modal.className = 'confirm-modal clear-secret-modal';
  modal.innerHTML = `
    <div class="modal-content">
      <h3 class="modal-title">Clear ${displayName} API key?</h3>
      <p class="modal-body">Save will write the secrets file without it.</p>
      <div class="modal-actions">
        <button class="btn modal-cancel-btn">Cancel</button>
        <button class="btn btn-danger modal-confirm-btn">Clear</button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  const cancelBtn = modal.querySelector('.modal-cancel-btn');
  const confirmBtn = modal.querySelector('.modal-confirm-btn');

  cancelBtn.addEventListener('click', () => {
    modal.close();
    modal.remove();
  });

  confirmBtn.addEventListener('click', () => {
    onConfirm();
    modal.close();
    modal.remove();
  });

  modal.addEventListener('close', () => {
    modal.remove();
  });

  cancelBtn.focus();
  modal.showModal();
}

async function handleTestConnection(provider) {
  const btn = rootElement.querySelector(`[data-provider="${provider}"] .test-connection-btn`);
  if (!btn) return;

  // Update both indicators (connection-row + panel header) in lockstep so
  // the panel header always reflects the latest test outcome.
  const originalText = btn.textContent;
  btn.textContent = 'Testing…';
  btn.disabled = true;
  _setProviderTestStatus(provider, 'warn', 'Testing…');

  try {
    const apiBase = window.shell ? window.shell.getApiBase() : `${window.location.protocol}//${window.location.host}`;

    // Send the in-flight key from the input field so the user can test
    // before saving. Server falls back to env/secrets file when key is omitted.
    const body = { provider };
    const typedKey = (currentValues[provider] && currentValues[provider].key || '').trim();
    if (typedKey) body.key = typedKey;

    // For custom providers, include url and type
    if (currentValues[provider] && currentValues[provider].type) {
      body.type = currentValues[provider].type;
      body.url = currentValues[provider].url;
    }

    const response = await fetch(`${apiBase}/api/config/llm/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    const result = await response.json();

    if (result.ok) {
      // Populate the model dropdown from the response. The server filters
      // OpenAI models down to chat-capable ones; Anthropic returns its
      // already-curated list. Re-render the panel BEFORE setting the status
      // text so the rerender doesn't overwrite our success message.
      if (Array.isArray(result.models) && result.models.length > 0) {
        availableModels[provider] = result.models;

        // If the saved/typed model isn't in the new list, fall back to the
        // first available so the form stays valid. The render preserves the
        // old value as a "(saved)" option for visibility.
        const currentModel = (currentValues[provider] && currentValues[provider].model) || '';
        if (!result.models.includes(currentModel)) {
          if (!currentValues[provider]) currentValues[provider] = {};
          currentValues[provider].model = result.models[0];
          _updateDirtyState();
        }
        renderLLMTab();
      }

      _setProviderTestStatus(provider, 'ok',
        `Last tested ${getRelativeTime(result.timestamp)} — OK (${result.latency_ms}ms, ${(result.models || []).length} models)`);
    } else {
      _setProviderTestStatus(provider, 'err', result.error || 'Connection failed');
    }

  } catch (error) {
    console.error(`[config-llm] Test connection failed for ${provider}:`, error);
    _setProviderTestStatus(provider, 'err', 'Test failed — check network connection');
  }

  // Re-query the button — renderLLMTab() above may have replaced the DOM node,
  // making the original `btn` reference an orphan that no longer affects the UI.
  const liveBtn = rootElement.querySelector(`[data-provider="${provider}"] .test-connection-btn`);
  if (liveBtn) {
    liveBtn.textContent = originalText;
    liveBtn.disabled = false;
  }
}

function handleAddCustomProvider() {
  // Prompt for provider name
  const providerName = window.prompt('Enter a name for the custom provider (e.g., "ollama", "my-vllm"):');

  if (!providerName) return; // User cancelled

  // Sanitize name: lowercase, replace spaces with hyphens
  const sanitizedName = providerName.toLowerCase().trim().replace(/\s+/g, '-');

  // Check if name already exists or conflicts with built-in providers
  if (BUILTIN_PROVIDERS.has(sanitizedName)) {
    alert(`"${sanitizedName}" is a built-in provider. Please choose a different name.`);
    return;
  }

  if (currentValues[sanitizedName]) {
    alert(`A provider named "${sanitizedName}" already exists.`);
    return;
  }

  // Add new custom provider
  const newProvider = {
    url: '',
    model: '',
    key: '',
    key_status: 'unset',
    type: 'openai_compatible',
    builtin: false
  };

  currentValues[sanitizedName] = newProvider;
  savedValues[sanitizedName] = { ...newProvider };

  // Mark as dirty and re-render
  _updateDirtyState();
  renderLLMTab();

  console.log(`[config-llm] Added custom provider: ${sanitizedName}`);
}

function handleRemoveProvider(providerName) {
  // Confirm removal
  if (!confirm(`Remove provider "${providerName}"? This cannot be undone.`)) {
    return;
  }

  // Remove from both current and saved values
  delete currentValues[providerName];
  delete savedValues[providerName];
  delete availableModels[providerName];

  // Clear any reveal timers
  if (revealTimers.has(providerName)) {
    clearTimeout(revealTimers.get(providerName));
    revealTimers.delete(providerName);
  }

  // Mark as dirty and re-render
  _updateDirtyState();
  renderLLMTab();

  console.log(`[config-llm] Removed custom provider: ${providerName}`);
}

// Sync both .dot-status spans (connection-row + panel header) for a provider.
// `state` is one of "ok" | "warn" | "err" — matches design-system .dot-status modifiers.
function _setProviderTestStatus(provider, state, text) {
  ['test-result-' + provider, 'status-' + provider].forEach(id => {
    const el = rootElement.querySelector('#' + id);
    if (!el) return;
    el.className = `dot-status ${state}`;
    el.textContent = text;
    if (id.startsWith('status-')) el.style.fontSize = '11px';
  });
}

function getRelativeTime(timestamp) {
  const now = Date.now() / 1000;
  const diff = now - timestamp;

  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

function announceToScreenReader(message) {
  // Create a temporary live region for screen reader announcements
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', 'polite');
  announcement.setAttribute('aria-atomic', 'true');
  announcement.style.position = 'absolute';
  announcement.style.left = '-10000px';
  announcement.style.width = '1px';
  announcement.style.height = '1px';
  announcement.style.overflow = 'hidden';

  document.body.appendChild(announcement);

  // Set the text to trigger the announcement
  announcement.textContent = message;

  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}

// ── State Management ────────────────────────────────────────────
function _updateDirtyState() {
  const wasDirty = isDirty;
  isDirty = _hasChanges();

  if (isDirty !== wasDirty) {
    _emitDirtyChangedEvent();
  }
}

function _hasChanges() {
  for (const [provider, providerData] of Object.entries(currentValues)) {
    const savedProviderData = savedValues[provider] || {};

    for (const [field, value] of Object.entries(providerData)) {
      // Skip key_status field as it's read-only
      if (field === 'key_status') continue;

      const savedValue = savedProviderData[field];
      if (String(value || '') !== String(savedValue || '')) {
        return true;
      }
    }
  }
  return false;
}

function _emitDirtyChangedEvent() {
  window.dispatchEvent(new CustomEvent('config:tabDirtyChanged', {
    detail: {
      tab: 'llm',
      dirty: isDirty,
      valid: isValid
    }
  }));
}

// ── Public API ──────────────────────────────────────────────────
function mount(element, initialValues = {}) {
  rootElement = element;

  // Extract providers data from the API response format
  const providers = initialValues.providers || [];
  savedValues = {};
  currentValues = {};

  // Convert API response to internal format
  providers.forEach(provider => {
    const providerConfig = {
      url: provider.url,
      model: provider.model,
      key: '', // Never show actual keys
      key_status: provider.key_status,
      builtin: provider.builtin !== false // Built-in providers are true, custom are false
    };
    // Add type field for custom providers
    if (provider.type) {
      providerConfig.type = provider.type;
    }
    savedValues[provider.name] = providerConfig;
    currentValues[provider.name] = { ...providerConfig };
  });

  // Ensure all built-in providers exist even if not in API response
  for (const [providerName, defaults] of Object.entries(DEFAULT_PROVIDER_CONFIGS)) {
    if (!currentValues[providerName]) {
      const defaultConfig = {
        url: defaults.url,
        model: defaults.model,
        key: '',
        key_status: 'unset',
        builtin: true
      };
      savedValues[providerName] = defaultConfig;
      currentValues[providerName] = { ...defaultConfig };
    }
  }

  isDirty = false;
  isValid = true;

  renderLLMTab();
  _emitDirtyChangedEvent();

  console.log('[config-llm] Mounted with values:', savedValues);
}

function unmount() {
  // Clear all reveal timers
  revealTimers.forEach((timerId) => clearTimeout(timerId));
  revealTimers.clear();

  rootElement = null;
  savedValues = {};
  currentValues = {};
  isDirty = false;
  isValid = true;

  console.log('[config-llm] Unmounted');
}

function getDirty() {
  return isDirty;
}

function getValues() {
  // Convert internal format to API format
  const providers = [];

  for (const [providerName, providerData] of Object.entries(currentValues)) {
    const savedProviderData = savedValues[providerName] || {};

    const provider = {
      name: providerName,
      url: providerData.url,
      model: providerData.model
    };

    // Include type field for custom providers
    if (providerData.type) {
      provider.type = providerData.type;
    }

    // Only include key if it changed
    if (providerData.key !== savedProviderData.key) {
      provider.key = providerData.key || null; // empty string becomes null (clear)
    }

    providers.push(provider);
  }

  return { providers };
}

function reset() {
  // Reset to built-in providers only, remove all custom providers
  savedValues = {};
  currentValues = {};

  for (const [providerName, defaults] of Object.entries(DEFAULT_PROVIDER_CONFIGS)) {
    const providerConfig = {
      url: defaults.url,
      model: defaults.model,
      key: '',
      key_status: 'unset',
      builtin: true
    };
    savedValues[providerName] = providerConfig;
    currentValues[providerName] = { ...providerConfig };
  }

  // Re-render
  if (rootElement) {
    renderLLMTab();
  }

  _updateDirtyState();
  validateAllProviders();

  console.log('[config-llm] Reset to defaults');
}

// ── Module Exports ──────────────────────────────────────────────
/**
 * Return a snapshot of the availableModels cache.
 * { providerName: ['model-a', 'model-b', ...] }
 * Populated when the user clicks "Test connection" in the LLM config tab.
 */
function getAvailableModels() {
  return availableModels;
}

/**
 * Fetch the model list for a provider by calling POST /api/config/llm/test.
 * Uses the server-side stored key + URL (same as clicking "Test connection").
 * Returns { ok: true, models: [...] } on success, { ok: false, error: '...' } on failure.
 * Also populates availableModels[providerName] on success.
 * @param {string} providerName
 * @returns {Promise<{ ok: boolean, models?: string[], error?: string }>}
 */
async function fetchModelsForProvider(providerName) {
  try {
    const apiBase = window.shell
      ? window.shell.getApiBase()
      : `${window.location.protocol}//${window.location.host}`;

    const body = { provider: providerName };

    // For custom providers, include url and type from currentValues so server
    // can route to the right endpoint (e.g. OpenAI-compatible base URL).
    const provCfg = currentValues[providerName];
    if (provCfg && provCfg.type) {
      body.type = provCfg.type;
      body.url  = provCfg.url;
    }

    const response = await fetch(`${apiBase}/api/config/llm/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const result = await response.json();
    if (result.ok && Array.isArray(result.models)) {
      availableModels[providerName] = result.models;
      return { ok: true, models: result.models };
    }
    return { ok: false, error: result.error || 'Test failed' };
  } catch (e) {
    return { ok: false, error: String(e) };
  }
}

window.configLLMTab = {
  mount,
  unmount,
  getDirty,
  getValues,
  reset,
  getAvailableModels,
  fetchModelsForProvider,
};

console.log('[config-llm] Config LLM tab module loaded');