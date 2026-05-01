// Agent Pitch — Matches Start Sub-view Module
// Phase 3b: Form to launch a new match
// Implements the Start sub-view for the Matches section

// ── State ───────────────────────────────────────────────────────
let rootElement = null;
let configsData = [];
let strategiesData = [];
let isLoading = false;
let _escapeKeyAttached = false;

// ── Utility Functions ───────────────────────────────────────────
function generateDefaultMatchId() {
  return `match_${Date.now()}`;
}

function validateMatchId(value) {
  return /^[A-Za-z0-9_-]{1,128}$/.test(value);
}

function validateSeed(value) {
  if (value === '' || value === null || value === undefined) {
    return true; // Optional field
  }
  const num = parseInt(value);
  return !isNaN(num) && num >= 0 && num <= 2147483647;
}

function getApiBase() {
  return window.shell ? window.shell.getApiBase() : `${window.location.protocol}//${window.location.host}`;
}

// ── Top-strip "Back to list" button ─────────────────────────────
// Mounts a `.btn-link` button into the App Shell's #right-cap so the back
// affordance lives in the top-right header, consistent with the matches
// Replay sub-view and the config-match editor.
function addBackButton() {
  const rightCap = document.getElementById('right-cap');
  if (!rightCap) return;
  if (rightCap.querySelector('.matches-start-back-btn')) return;

  const backBtn = document.createElement('button');
  backBtn.className = 'btn-link matches-start-back-btn';
  backBtn.textContent = 'Back to list';
  backBtn.onclick = () => { window.location.hash = '#/matches'; };

  rightCap.innerHTML = '';
  rightCap.appendChild(backBtn);
}

function removeBackButton() {
  const rightCap = document.getElementById('right-cap');
  const backBtn = rightCap && rightCap.querySelector('.matches-start-back-btn');
  if (backBtn) backBtn.remove();
}

// ── Local Storage Persistence ───────────────────────────────────
function saveFormToStorage(formData) {
  try {
    localStorage.setItem('ap_match_lastForm', JSON.stringify(formData));
  } catch (error) {
    console.warn('[matches-start] Failed to save form to localStorage:', error);
  }
}

function loadFormFromStorage() {
  try {
    const saved = localStorage.getItem('ap_match_lastForm');
    return saved ? JSON.parse(saved) : null;
  } catch (error) {
    console.warn('[matches-start] Failed to load form from localStorage:', error);
    return null;
  }
}

function clearFormFromStorage() {
  try {
    localStorage.removeItem('ap_match_lastForm');
  } catch (error) {
    console.warn('[matches-start] Failed to clear form from localStorage:', error);
  }
}

// ── API Functions ───────────────────────────────────────────────
async function fetchConfigs() {
  const apiBase = getApiBase();
  const response = await fetch(`${apiBase}/api/config/match`);

  if (!response.ok) {
    throw new Error(`Failed to fetch configs: ${response.status}`);
  }

  return await response.json();
}

async function fetchStrategies() {
  const apiBase = getApiBase();
  const response = await fetch(`${apiBase}/api/strategies`);

  if (!response.ok) {
    throw new Error(`Failed to fetch strategies: ${response.status}`);
  }

  return await response.json();
}

async function fetchConfigDetails(configName) {
  const apiBase = getApiBase();
  const response = await fetch(`${apiBase}/api/config/match/${encodeURIComponent(configName)}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch config details: ${response.status}`);
  }

  return await response.json();
}

async function startMatch(payload) {
  const apiBase = getApiBase();
  const response = await fetch(`${apiBase}/api/matches`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || `HTTP ${response.status}`);
  }

  return await response.json();
}

// ── Form Rendering ──────────────────────────────────────────────
function renderStartForm(initialData = {}) {
  if (!rootElement) return;

  const defaultMatchId = generateDefaultMatchId();
  const savedData = loadFormFromStorage() || {};

  const formData = {
    config_name: savedData.config_name || initialData.config_name || '',
    strategy_a: savedData.strategy_a || initialData.strategy_a || '',
    strategy_b: savedData.strategy_b || initialData.strategy_b || '',
    match_id: savedData.match_id || initialData.match_id || defaultMatchId,
    seed_override: savedData.seed_override || initialData.seed_override || ''
  };

  const configOptions = configsData.map(config => `
    <option value="${config.name}" ${config.name === formData.config_name ? 'selected' : ''}>
      ${config.name}
    </option>
  `).join('');

  const strategyOptions = strategiesData.map(strategy => `
    <option value="${strategy.name}" ${strategy.name === formData.strategy_a || strategy.name === formData.strategy_b ? 'selected' : ''}>
      ${strategy.name}
    </option>
  `).join('');

  rootElement.innerHTML = `
    <div class="matches-start-view">
      <form class="start-form" id="start-form">
        <div class="form-column">

          <!-- Config Section -->
          <div class="form-section">
            <label class="section-label">CONFIG</label>
            <div class="config-picker-group">
              <select class="sel" id="config-select" name="config_name" required>
                <option value="">Select configuration...</option>
                ${configOptions}
              </select>
              <a href="#/config/match" class="btn-link" id="edit-configs-link">Edit configs</a>
            </div>
          </div>

          <!-- Strategy Sections -->
          <div class="form-section">
            <label class="section-label">STRATEGY (TEAM A)</label>
            <select class="sel" id="strategy-a-select" name="strategy_a" required>
              <option value="">Select strategy...</option>
              ${strategyOptions}
            </select>
          </div>

          <div class="form-section">
            <label class="section-label">STRATEGY (TEAM B)</label>
            <select class="sel" id="strategy-b-select" name="strategy_b" required>
              <option value="">Select strategy...</option>
              ${strategyOptions}
            </select>
          </div>

          <!-- Match ID Section -->
          <div class="form-section">
            <label class="section-label">MATCH ID</label>
            <input
              type="text"
              class="ipt"
              id="match-id-input"
              name="match_id"
              value="${formData.match_id}"
              pattern="[A-Za-z0-9_-]{1,128}"
              maxlength="128"
              required
              spellcheck="false"
              autocapitalize="none"
              autocorrect="off"
            />
            <div class="field-error" id="match-id-error"></div>
          </div>

          <!-- Seed Override Section -->
          <div class="form-section">
            <label class="section-label">SEED OVERRIDE</label>
            <input
              type="number"
              class="ipt ipt-num"
              id="seed-input"
              name="seed_override"
              value="${formData.seed_override}"
              min="0"
              max="2147483647"
              step="1"
              placeholder="Leave blank to use config seed"
            />
            <div class="field-help">(blank = use config seed)</div>
            <div class="field-error" id="seed-error"></div>
          </div>

          <!-- Preview Section -->
          <div class="preview-block" id="preview-block">
            <div class="preview-header">PREVIEW</div>
            <div class="preview-content" id="preview-content">
              <div class="preview-message">Select a configuration to see match preview</div>
            </div>
          </div>

          <!-- Action Row -->
          <div class="action-row">
            <button type="button" class="btn" id="cancel-btn">Cancel</button>
            <button type="submit" class="btn btn-primary" id="start-match-btn" disabled>Start match</button>
          </div>

        </div>
      </form>
    </div>
  `;

  setupFormEventHandlers(formData);
  updateFormFromSaved(formData);
  validateForm();
}

function updateFormFromSaved(formData) {
  if (!rootElement) return;

  const configSelect = rootElement.querySelector('#config-select');
  const strategyASelect = rootElement.querySelector('#strategy-a-select');
  const strategyBSelect = rootElement.querySelector('#strategy-b-select');

  if (configSelect && formData.config_name) {
    configSelect.value = formData.config_name;
    updatePreview();
  }

  if (strategyASelect && formData.strategy_a) {
    strategyASelect.value = formData.strategy_a;
  }

  if (strategyBSelect && formData.strategy_b) {
    strategyBSelect.value = formData.strategy_b;
  }
}

function setupFormEventHandlers(initialData) {
  if (!rootElement) return;

  const form = rootElement.querySelector('#start-form');
  const configSelect = rootElement.querySelector('#config-select');
  const matchIdInput = rootElement.querySelector('#match-id-input');
  const seedInput = rootElement.querySelector('#seed-input');
  const cancelBtn = rootElement.querySelector('#cancel-btn');
  const startBtn = rootElement.querySelector('#start-match-btn');
  const editConfigsLink = rootElement.querySelector('#edit-configs-link');

  // Config selection change
  if (configSelect) {
    configSelect.addEventListener('change', () => {
      updatePreview();
      validateForm();
      saveCurrentFormState();
    });
  }

  // Strategy selection changes
  const strategySelects = rootElement.querySelectorAll('[name="strategy_a"], [name="strategy_b"]');
  strategySelects.forEach(select => {
    select.addEventListener('change', () => {
      validateForm();
      saveCurrentFormState();
    });
  });

  // Match ID validation
  if (matchIdInput) {
    matchIdInput.addEventListener('input', () => {
      validateMatchIdField(matchIdInput);
      validateForm();
      saveCurrentFormState();
    });
  }

  // Seed validation
  if (seedInput) {
    seedInput.addEventListener('input', () => {
      validateSeedField(seedInput);
      validateForm();
      saveCurrentFormState();
    });
  }

  // Cancel button
  if (cancelBtn) {
    cancelBtn.addEventListener('click', (e) => {
      e.preventDefault();
      navigateToMatchList();
    });
  }

  // Edit configs link - persist form state before navigating
  if (editConfigsLink) {
    editConfigsLink.addEventListener('click', () => {
      saveCurrentFormState();
    });
  }

  // Form submission
  if (form) {
    form.addEventListener('submit', handleFormSubmit);
  }

  // Listen for Esc key — guard prevents stacking on re-renders.
  if (!_escapeKeyAttached) {
    document.addEventListener('keydown', handleEscapeKey);
    _escapeKeyAttached = true;
  }
}

function saveCurrentFormState() {
  if (!rootElement) return;

  const form = rootElement.querySelector('#start-form');
  if (!form) return;

  const formData = new FormData(form);
  const data = {
    config_name: formData.get('config_name') || '',
    strategy_a: formData.get('strategy_a') || '',
    strategy_b: formData.get('strategy_b') || '',
    match_id: formData.get('match_id') || '',
    seed_override: formData.get('seed_override') || ''
  };

  saveFormToStorage(data);
}

function validateMatchIdField(input) {
  const value = input.value.trim();
  const errorElement = rootElement.querySelector('#match-id-error');
  const isValid = validateMatchId(value);

  if (value && !isValid) {
    input.classList.add('field-error-state');
    errorElement.textContent = '⚠ Use letters, numbers, hyphens, underscores only (1-128 chars)';
    errorElement.style.display = 'block';
  } else {
    input.classList.remove('field-error-state');
    errorElement.textContent = '';
    errorElement.style.display = 'none';
  }

  return isValid;
}

function validateSeedField(input) {
  const value = input.value.trim();
  const errorElement = rootElement.querySelector('#seed-error');
  const isValid = validateSeed(value);

  if (value && !isValid) {
    input.classList.add('field-error-state');
    errorElement.textContent = '⚠ Must be a number between 0 and 2,147,483,647';
    errorElement.style.display = 'block';
  } else {
    input.classList.remove('field-error-state');
    errorElement.textContent = '';
    errorElement.style.display = 'none';
  }

  return isValid;
}

function validateForm() {
  if (!rootElement) return false;

  const form = rootElement.querySelector('#start-form');
  const startBtn = rootElement.querySelector('#start-match-btn');

  if (!form || !startBtn) return false;

  const formData = new FormData(form);
  const configName = formData.get('config_name');
  const strategyA = formData.get('strategy_a');
  const strategyB = formData.get('strategy_b');
  const matchId = formData.get('match_id');
  const seedValue = formData.get('seed_override');

  const isValid = configName &&
                  strategyA &&
                  strategyB &&
                  matchId &&
                  validateMatchId(matchId) &&
                  validateSeed(seedValue);

  startBtn.disabled = !isValid;
  return isValid;
}

async function updatePreview() {
  if (!rootElement) return;

  const configSelect = rootElement.querySelector('#config-select');
  const previewContent = rootElement.querySelector('#preview-content');

  if (!configSelect || !previewContent) return;

  const configName = configSelect.value;

  if (!configName) {
    previewContent.innerHTML = '<div class="preview-message">Select a configuration to see match preview</div>';
    return;
  }

  try {
    previewContent.innerHTML = '<div class="preview-message">Loading preview...</div>';

    const configDetails = await fetchConfigDetails(configName);

    const playersPerTeam = Math.max(
      configDetails.team_a?.players?.length || 0,
      configDetails.team_b?.players?.length || 0
    );

    previewContent.innerHTML = `
      <div class="preview-row">
        <span class="preview-label">Players per team:</span>
        <span class="preview-value">${playersPerTeam}</span>
      </div>
      <div class="preview-row">
        <span class="preview-label">Match duration:</span>
        <span class="preview-value">${configDetails.match?.duration_minutes || 5} minutes</span>
      </div>
      <div class="preview-row">
        <span class="preview-label">Field:</span>
        <span class="preview-value">${configDetails.match?.field_width || 100} × ${configDetails.match?.field_height || 60}</span>
      </div>
    `;

  } catch (error) {
    console.error('[matches-start] Failed to load config preview:', error);
    previewContent.innerHTML = '<div class="preview-error">Failed to load configuration details</div>';
  }
}

async function handleFormSubmit(event) {
  event.preventDefault();

  if (!validateForm()) {
    return;
  }

  const startBtn = rootElement.querySelector('#start-match-btn');
  const originalText = startBtn.textContent;

  try {
    // Show loading state
    startBtn.disabled = true;
    startBtn.textContent = 'Starting...';

    const formData = new FormData(event.target);
    const payload = {
      config_name: formData.get('config_name'),
      strategy_a: formData.get('strategy_a'),
      strategy_b: formData.get('strategy_b'),
      match_id: formData.get('match_id'),
      seed_override: formData.get('seed_override') ? parseInt(formData.get('seed_override')) : null
    };

    const result = await startMatch(payload);

    // Success - clear saved form and navigate to replay
    clearFormFromStorage();
    const matchId = result.match_id || payload.match_id;
    window.location.hash = `#/matches/${matchId}`;

  } catch (error) {
    console.error('[matches-start] Failed to start match:', error);

    // Show error banner
    showErrorBanner(error.message);

    // Reset button
    startBtn.disabled = false;
    startBtn.textContent = originalText;
  }
}

function showErrorBanner(message) {
  // Remove any existing error banner
  const existingBanner = rootElement.querySelector('.error-banner');
  if (existingBanner) {
    existingBanner.remove();
  }

  const banner = document.createElement('div');
  banner.className = 'banner err error-banner';

  const mark = document.createElement('span');
  mark.className = 'b-mark';
  mark.textContent = 'ERR ·';

  const msg = document.createElement('div');
  msg.style.flex = '1';
  msg.textContent = `Could not start match: ${message}`;

  const dismiss = document.createElement('button');
  dismiss.className = 'btn-link error-dismiss';
  dismiss.setAttribute('aria-label', 'Dismiss error');
  dismiss.style.color = 'var(--ink-dim)';
  dismiss.textContent = 'dismiss';

  banner.appendChild(mark);
  banner.appendChild(msg);
  banner.appendChild(dismiss);

  // Insert at top of form
  const form = rootElement.querySelector('#start-form');
  if (form) {
    form.insertBefore(banner, form.firstChild);
  }

  // Auto-dismiss after 10 seconds
  setTimeout(() => {
    if (banner.parentNode) {
      banner.remove();
    }
  }, 10000);

  // Manual dismiss
  const dismissBtn = banner.querySelector('.error-dismiss');
  if (dismissBtn) {
    dismissBtn.addEventListener('click', () => {
      banner.remove();
    });
  }
}

function handleEscapeKey(event) {
  if (event.key === 'Escape') {
    navigateToMatchList();
  }
}

function navigateToMatchList() {
  window.location.hash = '#/matches';
}

// ── Config Event Listeners ──────────────────────────────────────
function setupConfigEventListeners() {
  // Listen for config changes from Config section
  window.addEventListener('config:matchConfigSaved', handleConfigSaved);
  window.addEventListener('config:matchConfigDeleted', handleConfigDeleted);
}

function handleConfigSaved(event) {
  // Refresh config picker
  loadDataAndRender();
}

function handleConfigDeleted(event) {
  // Refresh config picker and check if current selection was deleted
  const deletedName = event.detail?.name;
  const configSelect = rootElement?.querySelector('#config-select');

  if (configSelect && configSelect.value === deletedName) {
    configSelect.value = '';
    updatePreview();
    validateForm();
  }

  loadDataAndRender();
}

// ── Data Loading ────────────────────────────────────────────────
async function loadDataAndRender() {
  if (isLoading) return;

  isLoading = true;

  try {
    // Load configs and strategies in parallel
    const [configs, strategies] = await Promise.all([
      fetchConfigs(),
      fetchStrategies()
    ]);

    configsData = configs;
    strategiesData = strategies;

    renderStartForm();

  } catch (error) {
    console.error('[matches-start] Failed to load data:', error);
    renderErrorState(error.message);
  } finally {
    isLoading = false;
  }
}

function renderErrorState(errorMessage) {
  if (!rootElement) return;

  rootElement.innerHTML = `
    <div class="matches-start-view">
      <div class="error-state">
        <div class="error-icon">⚠</div>
        <div class="error-title">Failed to load match configuration</div>
        <div class="error-message">${errorMessage}</div>
        <div class="error-actions">
          <button class="btn" onclick="window.matchesStartView.mount(this.closest('.matches-start-view'))">Retry</button>
          <a href="#/matches" class="btn">Back to list</a>
        </div>
      </div>
    </div>
  `;
}

// ── Public API ──────────────────────────────────────────────────
function mount(element) {
  rootElement = element;

  // Set up event listeners
  setupConfigEventListeners();

  // Mount top-right back button
  addBackButton();

  // Load data and render
  loadDataAndRender();

  console.log('[matches-start] Mounted Start sub-view');
}

function unmount() {
  // Clean up event listeners
  window.removeEventListener('config:matchConfigSaved', handleConfigSaved);
  window.removeEventListener('config:matchConfigDeleted', handleConfigDeleted);
  document.removeEventListener('keydown', handleEscapeKey);
  _escapeKeyAttached = false;

  // Remove top-right back button
  removeBackButton();

  rootElement = null;
  configsData = [];
  strategiesData = [];
  isLoading = false;

  console.log('[matches-start] Unmounted Start sub-view');
}

// ── Export ──────────────────────────────────────────────────────
window.matchesStartView = {
  mount,
  unmount
};

console.log('[matches-start] Matches Start sub-view module loaded');