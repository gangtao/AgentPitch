// Agent Pitch — Config Shell Module
// Implements 4-tab navigation, hash routing, action row, and placeholder tab bodies
// Phase 3a scope: shell structure only, tab content comes in later phases

// ── State ───────────────────────────────────────────────────────
let isActive = false;
let currentTab = 'game';

// Global config cache - fetched once on first activation
let configData = null;

// ── DOM Elements ────────────────────────────────────────────────
let sectionConfig;
let tabStrip;
let tabBody;
let actionRow;

// Tab buttons
let gameTabBtn, llmTabBtn, storageTabBtn, matchTabBtn, teamsTabBtn;

// Action buttons
let resetBtn, discardBtn, saveBtn;

// ── Initialization ──────────────────────────────────────────────
function initializeElements() {
  sectionConfig = document.getElementById('section-config');

  if (!sectionConfig) {
    console.error('[config-shell] section-config element not found');
    return false;
  }

  return true;
}

// ── Configuration Data Management ───────────────────────────────
async function fetchConfigData() {
  if (configData) {
    return configData; // Return cached data
  }

  try {
    const apiBase = window.shell ? window.shell.getApiBase() : `${window.location.protocol}//${window.location.host}`;
    const response = await fetch(`${apiBase}/api/config`);

    if (!response.ok) {
      throw new Error(`Config fetch failed: ${response.status}`);
    }

    configData = await response.json();
    return configData;
  } catch (error) {
    console.error('[config-shell] Failed to fetch config data:', error);
    // Return fallback data so UI can still render
    return {
      game: {},
      llm: { providers: [], active: null },
      storage: { data_home: './logs' },
      match: { configs: [] }
    };
  }
}

// ── Tab Navigation ──────────────────────────────────────────────
function parseConfigRoute() {
  const hash = window.location.hash.slice(1); // Remove #
  const parts = hash.split('/').filter(p => p);

  // Expect format: /config/tab or /config/match/name or /config/match/new
  if (parts.length >= 2 && parts[0] === 'config') {
    const tab = parts[1];
    const subtab = parts[2] || null; // For match sub-routes
    return { tab, subtab };
  }

  return { tab: 'game', subtab: null }; // Default
}

function activateTab(tab, subtab = null) {
  currentTab = tab;

  // Update tab button states (visual + ARIA in tandem so screen readers
  // and sighted users see the same active-tab signal).
  [gameTabBtn, llmTabBtn, storageTabBtn, matchTabBtn, teamsTabBtn].forEach(btn => {
    if (btn) {
      btn.classList.remove('active');
      btn.setAttribute('aria-selected', 'false');
    }
  });

  // Activate appropriate tab button
  const activeBtn = {
    game: gameTabBtn,
    llm: llmTabBtn,
    storage: storageTabBtn,
    match: matchTabBtn,
    teams: teamsTabBtn
  }[tab];

  if (activeBtn) {
    activeBtn.classList.add('active');
    activeBtn.setAttribute('aria-selected', 'true');
  }

  // Action row visibility:
  //   Game / LLM / Storage  → always visible (singleton tab forms)
  //   Match / Teams List    → hidden (no save concept on the list)
  //   Match / Teams Editor / New → visible (saves act on the open form)
  if (actionRow) {
    const matchListView = tab === 'match' && (!subtab || subtab === '');
    const teamsListView = tab === 'teams' && (!subtab || subtab === '');
    actionRow.style.display = (matchListView || teamsListView) ? 'none' : 'flex';
  }

  // Render tab body content
  renderTabBody(tab, subtab);

  // Update subtitle
  const subtitles = {
    game: 'CONFIG · GAME',
    llm: 'CONFIG · LLM',
    storage: 'CONFIG · STORAGE',
    match: 'CONFIG · MATCH',
    teams: 'CONFIG · TEAMS'
  };

  window.dispatchEvent(new CustomEvent('shell:subtitleChanged', {
    detail: { subtitle: subtitles[tab] || 'CONFIG' }
  }));

  // Fire config tab change event
  window.dispatchEvent(new CustomEvent('config:tabChanged', {
    detail: { tab }
  }));

  // Store last active tab
  try {
    localStorage.setItem('ap_config_lastTab', tab);
  } catch (e) {
    console.warn('[config-shell] Could not save last tab to localStorage');
  }
}

function renderTabBody(tab, subtab = null) {
  if (!tabBody) return;

  if (tab === 'game') {
    // Game tab is now implemented - mount the actual tab
    if (window.configGameTab && configData?.game) {
      window.configGameTab.mount(tabBody, configData.game);
    } else {
      tabBody.innerHTML = `<div class="tab-placeholder">Loading Game tab...</div>`;
    }
  } else if (tab === 'storage') {
    // Storage tab is now implemented - mount the actual tab
    if (window.configStorageTab && configData?.storage) {
      window.configStorageTab.mount(tabBody, configData.storage);
    } else {
      tabBody.innerHTML = `<div class="tab-placeholder">Loading Storage tab...</div>`;
    }
  } else if (tab === 'llm') {
    // LLM tab is now implemented - mount the actual tab
    if (window.configLLMTab && configData?.llm) {
      window.configLLMTab.mount(tabBody, configData.llm);
    } else {
      tabBody.innerHTML = `<div class="tab-placeholder">Loading LLM tab...</div>`;
    }
  } else if (tab === 'match') {
    // Match tab is now implemented - mount the actual tab
    if (window.configMatchTab && configData?.match) {
      window.configMatchTab.mount(tabBody, configData.match);
    } else {
      tabBody.innerHTML = `<div class="tab-placeholder">Loading Match tab...</div>`;
    }
  } else if (tab === 'teams') {
    // Teams tab - mount the Teams module (list/editor/new routed by subtab)
    if (window.configTeamsTab) {
      window.configTeamsTab.mount(tabBody, configData?.teams || null);
    } else {
      tabBody.innerHTML = `<div class="tab-placeholder">Loading Teams tab...</div>`;
    }
  } else {
    // Other tabs still show placeholder
    const placeholders = {
      // All tabs are now implemented
    };

    const placeholder = placeholders[tab] || 'Coming soon';
    tabBody.innerHTML = `<div class="tab-placeholder">${placeholder}</div>`;
  }
}

// ── UI Rendering ────────────────────────────────────────────────
function renderConfigShell() {
  if (!sectionConfig) return;

  sectionConfig.innerHTML = `
    <div class="config-shell">
      <div class="tabs config-tab-strip" id="config-tab-strip" role="tablist" aria-label="Config tabs">
        <button class="tab" id="config-game-tab" data-tab="game"
                role="tab" aria-selected="false" aria-controls="config-tab-body">Game</button>
        <button class="tab" id="config-match-tab" data-tab="match"
                role="tab" aria-selected="false" aria-controls="config-tab-body">Match</button>
        <button class="tab" id="config-teams-tab" data-tab="teams"
                role="tab" aria-selected="false" aria-controls="config-tab-body">Teams</button>
        <button class="tab" id="config-llm-tab" data-tab="llm"
                role="tab" aria-selected="false" aria-controls="config-tab-body">LLM</button>
        <button class="tab" id="config-storage-tab" data-tab="storage"
                role="tab" aria-selected="false" aria-controls="config-tab-body">Storage</button>
      </div>

      <div class="config-tab-body" id="config-tab-body" role="tabpanel">
        <!-- Tab content rendered by renderTabBody() -->
      </div>

      <div class="config-action-row" id="config-action-row">
        <button class="btn config-reset-btn" id="config-reset-btn" disabled>
          Reset to defaults
        </button>
        <div class="action-row-right">
          <button class="btn config-discard-btn" id="config-discard-btn" disabled>
            Discard
          </button>
          <button class="btn btn-primary config-save-btn" id="config-save-btn" disabled>
            Save
          </button>
        </div>
      </div>
    </div>
  `;

  // Cache DOM elements
  tabStrip = document.getElementById('config-tab-strip');
  tabBody = document.getElementById('config-tab-body');
  actionRow = document.getElementById('config-action-row');

  gameTabBtn = document.getElementById('config-game-tab');
  llmTabBtn = document.getElementById('config-llm-tab');
  storageTabBtn = document.getElementById('config-storage-tab');
  matchTabBtn = document.getElementById('config-match-tab');
  teamsTabBtn = document.getElementById('config-teams-tab');

  resetBtn = document.getElementById('config-reset-btn');
  discardBtn = document.getElementById('config-discard-btn');
  saveBtn = document.getElementById('config-save-btn');

  // Set up tab button event handlers
  [gameTabBtn, llmTabBtn, storageTabBtn, matchTabBtn, teamsTabBtn].forEach(btn => {
    if (btn) {
      btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        const route = `#/config/${tab}`;
        if (window.location.hash !== route) {
          window.location.hash = route;
        }
        activateTab(tab);
      });
    }
  });

  // Action button handlers
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      handleResetToDefaults();
    });
  }

  if (discardBtn) {
    discardBtn.addEventListener('click', () => {
      handleDiscardChanges();
    });
  }

  if (saveBtn) {
    saveBtn.addEventListener('click', () => {
      handleSave();
    });
  }
}

// ── Route Handling ──────────────────────────────────────────────
function handleConfigRoute() {
  if (!isActive) return;

  const route = parseConfigRoute();
  activateTab(route.tab, route.subtab);
}

// ── Lifecycle Management ────────────────────────────────────────
async function activate({ section, subsection } = {}) {
  if (section !== 'config') {
    return; // Not our section
  }

  if (!initializeElements()) {
    return;
  }

  isActive = true;

  // Fetch config data on first activation
  await fetchConfigData();

  // Render the config shell UI
  renderConfigShell();

  // Determine initial tab from route or localStorage
  const route = parseConfigRoute();
  let initialTab = route.tab;

  // If no specific route, try to restore last tab
  if (initialTab === 'game' && !subsection) {
    try {
      const lastTab = localStorage.getItem('ap_config_lastTab');
      if (lastTab && ['game', 'llm', 'storage', 'match', 'teams'].includes(lastTab)) {
        initialTab = lastTab;
      }
    } catch (e) {
      // Ignore localStorage errors
    }
  }

  // Activate the initial tab
  activateTab(initialTab, route.subtab);

  console.log('[config-shell] Activated with tab:', initialTab);
}

function deactivate() {
  isActive = false;

  // Clear cached elements
  tabStrip = null;
  tabBody = null;
  actionRow = null;
  gameTabBtn = llmTabBtn = storageTabBtn = matchTabBtn = teamsTabBtn = null;
  resetBtn = discardBtn = saveBtn = null;

  console.log('[config-shell] Deactivated');
}

// ── Action Handlers ─────────────────────────────────────────────
async function handleSave() {
  if (currentTab === 'game') {
    await handleGameSave();
  } else if (currentTab === 'storage') {
    await handleStorageSave();
  } else if (currentTab === 'llm') {
    await handleLLMSave();
  } else if (currentTab === 'match') {
    // Delegate to Match-tab module — it knows whether we're in Editor
    // (saves to the open name) or New (creates new from the name input).
    if (window.configMatchTab && typeof window.configMatchTab.save === 'function') {
      await window.configMatchTab.save();
    }
  } else if (currentTab === 'teams') {
    // Delegate to Teams-tab module — it knows whether we're in Editor
    // (saves to the open slug) or New (creates new from the form values).
    if (window.configTeamsTab && typeof window.configTeamsTab.save === 'function') {
      await window.configTeamsTab.save();
    }
  } else {
    console.log(`[config-shell] Save not implemented for ${currentTab} tab`);
  }
}

async function handleGameSave() {
  if (!window.configGameTab) {
    console.error('[config-shell] configGameTab not available');
    return;
  }

  try {
    const values = window.configGameTab.getValues();
    const apiBase = window.shell ? window.shell.getApiBase() : `${window.location.protocol}//${window.location.host}`;

    console.log('[config-shell] Saving Game tab values:', values);

    const response = await fetch(`${apiBase}/api/config/game`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(values)
    });

    if (response.ok) {
      const result = await response.json();
      console.log('[config-shell] Game save successful:', result);

      // Fire saved event
      window.dispatchEvent(new CustomEvent('config:gameSaved', {
        detail: { timestamp: result.timestamp }
      }));

      // Show success feedback
      showActionFeedback('Saved');

    } else {
      const error = await response.json();
      console.error('[config-shell] Game save failed:', error);

      if (response.status === 422 && error.detail) {
        // Handle validation errors - show inline if possible
        handleValidationErrors(error.detail);
      } else {
        showActionFeedback('Save failed', 'error');
      }
    }

  } catch (e) {
    console.error('[config-shell] Game save request failed:', e);
    showActionFeedback('Save failed', 'error');
  }
}

async function handleStorageSave() {
  if (!window.configStorageTab) {
    console.error('[config-shell] configStorageTab not available');
    return;
  }

  try {
    const values = window.configStorageTab.getValues();
    const apiBase = window.shell ? window.shell.getApiBase() : `${window.location.protocol}//${window.location.host}`;

    console.log('[config-shell] Saving Storage tab values:', values);

    const response = await fetch(`${apiBase}/api/config/storage`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(values)
    });

    if (response.ok) {
      const result = await response.json();
      console.log('[config-shell] Storage save successful:', result);

      // Fire saved event
      window.dispatchEvent(new CustomEvent('config:storageSaved', {
        detail: {
          timestamp: result.timestamp,
          oldPath: result.old_path,
          newPath: result.new_path
        }
      }));

      // Show success feedback
      showActionFeedback('Saved');

      // Re-fetch config data to refresh all tabs (storage change affects everything)
      await refetchConfigData();

    } else {
      const error = await response.json();
      console.error('[config-shell] Storage save failed:', error);

      if (response.status === 422 && error.detail) {
        // Handle validation errors - show inline if possible
        handleValidationErrors(error.detail);
      } else {
        showActionFeedback('Save failed', 'error');
      }
    }

  } catch (e) {
    console.error('[config-shell] Storage save request failed:', e);
    showActionFeedback('Save failed', 'error');
  }
}

async function handleLLMSave() {
  if (!window.configLLMTab) {
    console.error('[config-shell] configLLMTab not available');
    return;
  }

  try {
    const values = window.configLLMTab.getValues();
    const apiBase = window.shell ? window.shell.getApiBase() : `${window.location.protocol}//${window.location.host}`;

    console.log('[config-shell] Saving LLM tab values:', values);

    const response = await fetch(`${apiBase}/api/config/llm`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(values)
    });

    if (response.ok) {
      const result = await response.json();
      console.log('[config-shell] LLM save successful:', result);

      // Fire saved event
      window.dispatchEvent(new CustomEvent('config:llmSaved', {
        detail: { timestamp: result.timestamp }
      }));

      // Show success feedback
      showActionFeedback('Saved');

      // Re-fetch config data to refresh all tabs
      await refetchConfigData();

    } else {
      const error = await response.json();
      console.error('[config-shell] LLM save failed:', error);

      if (response.status === 422 && error.detail) {
        // Handle validation errors
        handleValidationErrors(error.detail);
      } else {
        showActionFeedback('Save failed', 'error');
      }
    }

  } catch (e) {
    console.error('[config-shell] LLM save request failed:', e);
    showActionFeedback('Save failed', 'error');
  }
}

function handleResetToDefaults() {
  if (currentTab === 'game' || currentTab === 'storage' || currentTab === 'llm' || currentTab === 'match' || currentTab === 'teams') {
    showResetConfirmModal();
  } else {
    console.log(`[config-shell] Reset not implemented for ${currentTab} tab`);
  }
}

function handleDiscardChanges() {
  if (currentTab === 'game' || currentTab === 'storage' || currentTab === 'llm' || currentTab === 'match' || currentTab === 'teams') {
    showDiscardConfirmModal();
  } else {
    console.log(`[config-shell] Discard not implemented for ${currentTab} tab`);
  }
}

function handleValidationErrors(errors) {
  // Log validation errors - actual inline display would require
  // more coordination with the Game tab module
  console.error('[config-shell] Validation errors:', errors);
  showActionFeedback('Validation failed', 'error');
}

function showActionFeedback(message, type = 'success') {
  // Simple feedback - could be enhanced with proper toast/notification system
  console.log(`[config-shell] ${type}: ${message}`);

  // Update action row with temporary feedback
  if (actionRow) {
    const existing = actionRow.querySelector('.action-feedback');
    if (existing) existing.remove();

    const feedback = document.createElement('div');
    feedback.className = `action-feedback action-feedback-${type}`;
    feedback.textContent = message;
    actionRow.appendChild(feedback);

    setTimeout(() => {
      feedback.remove();
    }, 3000);
  }
}

// ── Config Data Management ──────────────────────────────────────
async function refetchConfigData() {
  try {
    configData = null; // Clear cache
    await fetchConfigData(); // Re-fetch
    console.log('[config-shell] Config cache refreshed');
  } catch (e) {
    console.warn('[config-shell] Failed to refresh config cache:', e);
  }
}

// ── Modal Handlers ──────────────────────────────────────────────
function showResetConfirmModal() {
  const tabDisplayName = currentTab.charAt(0).toUpperCase() + currentTab.slice(1);
  const modal = document.createElement('dialog');
  modal.className = 'confirm-modal reset-confirm-modal';
  modal.innerHTML = `
    <div class="modal-content">
      <h3 class="modal-title">Reset all ${tabDisplayName}-tab values to defaults?</h3>
      <p class="modal-body">This will reset all fields in the ${tabDisplayName} tab to their schema defaults. Your current changes will be lost.</p>
      <div class="modal-actions">
        <button class="btn modal-cancel-btn">Cancel</button>
        <button class="btn btn-danger modal-confirm-btn" data-action="reset">Reset to defaults</button>
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
    if (currentTab === 'game' && window.configGameTab) {
      window.configGameTab.reset();
    } else if (currentTab === 'storage' && window.configStorageTab) {
      window.configStorageTab.reset();
    } else if (currentTab === 'llm' && window.configLLMTab) {
      window.configLLMTab.reset();
    } else if (currentTab === 'match' && window.configMatchTab && typeof window.configMatchTab.reset === 'function') {
      window.configMatchTab.reset();
    } else if (currentTab === 'teams' && window.configTeamsTab && typeof window.configTeamsTab.reset === 'function') {
      window.configTeamsTab.reset();
    }
    modal.close();
    modal.remove();
  });

  modal.addEventListener('close', () => {
    modal.remove();
  });

  // Focus cancel by default per UX spec
  cancelBtn.focus();
  modal.showModal();
}

function showDiscardConfirmModal() {
  const tabDisplayName = currentTab.charAt(0).toUpperCase() + currentTab.slice(1);
  const modal = document.createElement('dialog');
  modal.className = 'confirm-modal discard-confirm-modal';
  modal.innerHTML = `
    <div class="modal-content">
      <h3 class="modal-title">Discard unsaved changes to ${tabDisplayName} tab?</h3>
      <p class="modal-body">Your edits will be lost.</p>
      <div class="modal-actions">
        <button class="btn modal-cancel-btn">Cancel</button>
        <button class="btn btn-danger modal-discard-btn" data-action="discard">Discard</button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  const cancelBtn = modal.querySelector('.modal-cancel-btn');
  const discardBtn = modal.querySelector('.modal-discard-btn');

  cancelBtn.addEventListener('click', () => {
    modal.close();
    modal.remove();
  });

  discardBtn.addEventListener('click', () => {
    // Re-mount with saved values to discard changes
    if (currentTab === 'game' && window.configGameTab && configData?.game) {
      window.configGameTab.mount(tabBody, configData.game);
    } else if (currentTab === 'storage' && window.configStorageTab && configData?.storage) {
      window.configStorageTab.mount(tabBody, configData.storage);
    } else if (currentTab === 'llm' && window.configLLMTab && configData?.llm) {
      window.configLLMTab.mount(tabBody, configData.llm);
    } else if (currentTab === 'match' && window.configMatchTab && typeof window.configMatchTab.discard === 'function') {
      window.configMatchTab.discard();
    } else if (currentTab === 'teams' && window.configTeamsTab && typeof window.configTeamsTab.discard === 'function') {
      window.configTeamsTab.discard();
    }
    modal.close();
    modal.remove();
  });

  modal.addEventListener('close', () => {
    modal.remove();
  });

  // Focus cancel by default per UX spec
  cancelBtn.focus();
  modal.showModal();
}

// ── Event Handlers ──────────────────────────────────────────────
function setupEventHandlers() {
  // Listen for hash changes to handle routing
  window.addEventListener('hashchange', handleConfigRoute);

  // Listen for shell section changes to deactivate when leaving config
  window.addEventListener('app:sectionChanged', (event) => {
    if (event.detail && event.detail.section !== 'config' && isActive) {
      deactivate();
    }
  });

  // Listen for tab dirty state changes
  window.addEventListener('config:tabDirtyChanged', (event) => {
    handleTabDirtyChanged(event.detail);
  });

  // Listen for game saved events
  window.addEventListener('config:gameSaved', (event) => {
    handleGameSaved();
  });
}

function handleTabDirtyChanged(detail) {
  if (!actionRow) return;

  const { tab, dirty, valid } = detail;

  if (tab === currentTab) {
    // Update action row button states
    if (saveBtn) {
      saveBtn.disabled = !dirty || !valid;
    }
    if (discardBtn) {
      discardBtn.disabled = !dirty;
    }
    // Reset to defaults stays enabled at all times per spec

    // Update tab label with dirty indicator
    const tabBtn = {
      game: gameTabBtn,
      llm: llmTabBtn,
      storage: storageTabBtn,
      match: matchTabBtn,
      teams: teamsTabBtn
    }[tab];

    if (tabBtn) {
      const label = tabBtn.querySelector('.tab-label');
      if (label) {
        const baseName = tab.charAt(0).toUpperCase() + tab.slice(1);
        label.textContent = dirty ? `${baseName} ●` : baseName;
      }
    }
  }
}

async function handleGameSaved() {
  // Re-fetch config data to refresh the cache
  try {
    configData = null; // Clear cache
    await fetchConfigData(); // Re-fetch
    console.log('[config-shell] Config cache refreshed after save');
  } catch (e) {
    console.warn('[config-shell] Failed to refresh config cache:', e);
  }

  // Clear any dirty indicators
  if (gameTabBtn) {
    const label = gameTabBtn.querySelector('.tab-label');
    if (label) {
      label.textContent = 'Game';
    }
  }
}

// ── Module Exports ──────────────────────────────────────────────
window.configShellSection = {
  activate,
  deactivate
};

// ── Bootstrap ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  setupEventHandlers();
});

console.log('[config-shell] Config shell module loaded');