// Agent Pitch — Strategies Section Module
// Phase 3a: List sub-view with routing to Editor/New placeholders
// Replaces the placeholder strategies section with full implementation

import { showDeleteConfirmModal, dismissOpenDeleteConfirmModal } from './modals.js';

// ── State ───────────────────────────────────────────────────────
let currentSubView = 'list';  // 'list' | 'editor' | 'new'
let currentStrategyName = null;
let strategiesData = [];
let isLoading = false;

// Editor state
let editorData = null;
let isDirty = false;
let lastSavedSource = '';

// ── Sub-view Routing ────────────────────────────────────────────
// Map a language identifier to the highlight.js class name + hljs language id.
// Centralised so adding a 4th language (currently python/javascript/rust) needs
// one edit instead of six.
function languageClass(language) {
  if (language === 'javascript') return 'language-javascript';
  if (language === 'rust') return 'language-rust';
  return 'language-python';
}
function languageHljsId(language) {
  if (language === 'javascript') return 'javascript';
  if (language === 'rust') return 'rust';
  return 'python';
}


function parseRoute(route) {
  // Expected format: { section: 'strategies', subsection: '' | '<name>' | 'new' }
  const { section, subsection } = route;

  if (section !== 'strategies') return { subView: 'list', strategyName: null };

  if (!subsection) {
    return { subView: 'list', strategyName: null };
  } else if (subsection === 'new') {
    return { subView: 'new', strategyName: null };
  } else {
    return { subView: 'editor', strategyName: subsection };
  }
}

function navigateToSubView(subView, strategyName = null) {
  const route = strategyName
    ? `#/strategies/${strategyName}`
    : `#/strategies${subView === 'new' ? '/new' : ''}`;

  window.location.hash = route;
}

// ── List Sub-view Implementation ────────────────────────────────
function renderListSubView() {
  currentSubView = 'list';
  currentStrategyName = null;

  // Show strategies section, hide placeholder if any
  const strategiesSection = document.getElementById('section-strategies');
  if (strategiesSection) {
    strategiesSection.removeAttribute('hidden');
  }

  updateSubtitle('STRATEGIES');

  // Create or show list view container
  showListViewContainer();

  // Load and render strategies
  loadStrategies();
}

function showListViewContainer() {
  let listView = document.getElementById('strategies-list-view');

  if (!listView) {
    listView = document.createElement('div');
    listView.id = 'strategies-list-view';

    // Replace any existing content in strategies section
    const strategiesSection = document.getElementById('section-strategies');
    if (strategiesSection) {
      strategiesSection.innerHTML = '';
      strategiesSection.appendChild(listView);
    }
  }

  listView.style.display = '';
}

function hideListViewContainer() {
  const listView = document.getElementById('strategies-list-view');
  if (listView) {
    listView.style.display = 'none';
  }
}

async function loadStrategies() {
  if (isLoading) return;

  isLoading = true;

  try {
    renderLoadingState();

    const response = await fetch('/api/strategies');
    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }

    strategiesData = await response.json();
    renderStrategiesList();

  } catch (error) {
    console.error('[strategies.js] Failed to load strategies:', error);
    renderErrorState();
  } finally {
    isLoading = false;
  }
}

function renderLoadingState() {
  const listView = document.getElementById('strategies-list-view');
  if (!listView) return;

  listView.innerHTML = `
    <div class="list-action-bar">
      <button class="btn btn-primary" disabled>+ New strategy</button>
      <div class="list-count">Loading...</div>
    </div>
    <div class="list-body strategies-list">
      ${generateSkeletonRows(3)}
    </div>
  `;
}

function generateSkeletonRows(count) {
  return Array(count).fill(0).map(() => `
    <div class="list-row skeleton">
      <div class="list-row-line-1">loading-strategy   loading</div>
      <div class="list-row-line-2">loading lines · loading bytes</div>
      <div class="list-row-actions">
        <button class="btn btn-sm" disabled>Edit</button>
        <button class="btn btn-sm btn-danger" disabled>Del</button>
      </div>
    </div>
  `).join('');
}

function renderErrorState() {
  const listView = document.getElementById('strategies-list-view');
  if (!listView) return;

  listView.innerHTML = `
    <div class="list-action-bar">
      <button class="btn btn-primary" onclick="navigateStrategiesSubView('new')">+ New strategy</button>
      <div class="list-count">Error</div>
    </div>
    <div class="list-error">
      <div class="error-message">Could not load strategies — server unreachable</div>
      <button class="btn" onclick="loadStrategies()">Retry</button>
    </div>
  `;
}

function renderStrategiesList() {
  const listView = document.getElementById('strategies-list-view');
  if (!listView) return;

  if (strategiesData.length === 0) {
    renderEmptyState();
    return;
  }

  // The list isn't empty — render rows. (No sparse-state CTA panel: the
  // action-bar's `+ NEW STRATEGY` button is already the primary way to add
  // a new one, so a second CTA below the rows would just duplicate it.)
  const strategyCount = strategiesData.length;
  const rowsHTML = strategiesData.map(renderStrategyRow).join('');

  listView.innerHTML = `
    <div class="list-action-bar">
      <button class="btn btn-primary" onclick="navigateStrategiesSubView('new')">+ New strategy</button>
      <div class="list-count">${strategyCount} strategies</div>
    </div>
    <div class="list-body strategies-list">
      ${rowsHTML}
    </div>
  `;
}

function renderEmptyState() {
  const listView = document.getElementById('strategies-list-view');
  if (!listView) return;

  listView.innerHTML = `
    <div class="list-empty-state">
      <div class="empty-heading">no strategies in your pool yet</div>
      <div class="empty-subtext">let's create one</div>
      <button class="btn btn-primary btn-lg" onclick="navigateStrategiesSubView('new')">+ New strategy</button>
    </div>
  `;
}

function renderStrategyRow(strategy) {
  const { name, line_count, size_bytes, modified_iso, meta } = strategy;

  // Format date
  const date = new Date(modified_iso);
  const dateStr = date.toISOString().slice(0, 16).replace('T', ' ');

  // Format size
  const sizeStr = size_bytes < 1024 ? `${size_bytes}B` : `${(size_bytes / 1024).toFixed(1)}KB`;

  const langBadge =
    strategy.language === 'javascript' ? 'JS' :
    strategy.language === 'rust' ? 'RS' : 'PY';

  // Provider/model badge from sidecar (ADR-0023). Legacy files without a
  // sidecar surface as `unknown` — show a dim "—" rather than a misleading badge.
  const providerLabel = formatProviderBadge(meta);

  // Accessible name for screen readers (Pattern 8 - Selectable List Row)
  const ariaLabel = `Strategy ${name}, ${providerLabel}, ${line_count} lines, modified ${dateStr}`;

  return `
    <div class="list-row" data-strategy-name="${name}">
      <div class="list-row-content"
           role="button"
           tabindex="0"
           aria-label="${ariaLabel}"
           onclick="openStrategyEditor('${name}')"
           onkeydown="if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); openStrategyEditor('${name}'); }">
        <div class="list-row-line-1"><span class="lang-badge" style="display:inline-block;padding:1px 6px;margin-right:6px;border:1px solid var(--rule);border-radius:3px;font-size:10px;color:var(--ink-dim)">${langBadge}</span>${name}   ${dateStr}</div>
        <div class="list-row-line-2">${providerLabel} · ${line_count} lines · ${sizeStr}</div>
      </div>
      <div class="list-row-actions">
        <button class="btn btn-sm" onclick="openStrategyEditor('${name}')" aria-label="Edit strategy ${name}">Edit</button>
        <button class="btn btn-sm btn-danger" onclick="openDeleteStrategyConfirm('${name}')" aria-label="Delete strategy ${name}">Del</button>
      </div>
    </div>
  `;
}

// Render the sidecar provider/model into a single human label.
//   ('anthropic', 'claude-sonnet-4-6')  → 'anthropic/claude-sonnet-4-6'
//   ('openai',    'gpt-4o')             → 'openai/gpt-4o'
//   ('baseline',  'hand-written')       → 'baseline'
//   ('manual',    'hand-written')       → 'manual'
//   ('unknown',   'unknown') / no meta  → '—'
function formatProviderBadge(meta) {
  if (!meta || !meta.provider || meta.provider === 'unknown') return '—';
  if (meta.provider === 'baseline' || meta.provider === 'manual') return meta.provider;
  if (!meta.model || meta.model === 'unknown') return meta.provider;
  return `${meta.provider}/${meta.model}`;
}

// ── Editor Sub-view Implementation ──────────────────────────────
function renderEditorSubView(strategyName) {
  currentSubView = 'editor';
  currentStrategyName = strategyName;

  hideListViewContainer();
  updateSubtitle(`STRATEGIES · ${strategyName.toUpperCase()}`);

  // Load strategy data and render editor
  loadStrategyForEditor(strategyName);
}

async function loadStrategyForEditor(strategyName) {
  try {
    const response = await fetch(`/api/strategies/${strategyName}`);
    if (!response.ok) {
      if (response.status === 404) {
        renderStrategyNotFound(strategyName);
        return;
      }
      throw new Error(`Server returned ${response.status}`);
    }

    editorData = await response.json();
    editorData.language = editorData.language || (editorData.meta && editorData.meta.language) || 'python';
    lastSavedSource = editorData.source;
    isDirty = false;

    renderEditor();

  } catch (error) {
    console.error('[strategies.js] Failed to load strategy:', error);
    renderEditorError(strategyName);
  }
}

function renderStrategyNotFound(strategyName) {
  const strategiesSection = document.getElementById('section-strategies');
  if (strategiesSection) {
    strategiesSection.innerHTML = `
      <div class="editor-error">
        <div class="error-heading">Strategy '${strategyName}' not found</div>
        <div class="error-subtext">It may have been deleted</div>
        <button class="btn" onclick="navigateStrategiesSubView('list')">Back to list</button>
      </div>
    `;
  }
}

function renderEditorError(strategyName) {
  const strategiesSection = document.getElementById('section-strategies');
  if (strategiesSection) {
    strategiesSection.innerHTML = `
      <div class="editor-error">
        <div class="error-heading">Could not load strategy '${strategyName}'</div>
        <div class="error-subtext">Server unreachable</div>
        <button class="btn" onclick="loadStrategyForEditor('${strategyName}')">Retry</button>
        <button class="btn" onclick="navigateStrategiesSubView('list')">Back to list</button>
      </div>
    `;
  }
}

function renderEditor() {
  const strategiesSection = document.getElementById('section-strategies');
  if (!strategiesSection || !editorData) return;

  const dirtyIndicator = isDirty ? ' ●modified' : '';

  strategiesSection.innerHTML = `
    <div class="editor-container">
      <div class="editor-header">
        <div class="strategy-name">${editorData.name}${dirtyIndicator}</div>
      </div>

      <div class="code-editor-container">
        <div class="code-editor">
          <div class="line-numbers" id="editor-line-numbers"></div>
          <div class="code-source-wrap">
            <pre class="code-highlight hljs" id="editor-highlight" aria-hidden="true"><code class="${languageClass(editorData.language)}"></code></pre>
            <textarea
              class="code-source"
              id="editor-textarea"
              aria-label="Strategy source code"
              aria-describedby="editor-escape-hint"
              spellcheck="false"
              autocapitalize="off"
              autocorrect="off"
            >${editorData.source}</textarea>
          </div>
        </div>
        <div class="editor-escape-hint" id="editor-escape-hint" style="display: none;">
          Press Esc to exit editor
        </div>
      </div>

      <div class="editor-footer">
        ${editorData.line_count} lines · ${formatFileSize(editorData.size_bytes)}
      </div>

      <div class="editor-action-row">
        <button class="btn" onclick="handleEditorCancel()">Cancel</button>
        <button class="btn" onclick="handleSaveAs()">Save as...</button>
        <button class="btn btn-primary" id="editor-save-btn" onclick="handleSave()" ${!isDirty ? 'disabled' : ''}>Save</button>
      </div>
    </div>
  `;

  // Set up editor functionality
  setupEditor();
}

function setupEditor() {
  const textarea = document.getElementById('editor-textarea');
  const lineNumbers = document.getElementById('editor-line-numbers');
  const escapeHint = document.getElementById('editor-escape-hint');

  if (!textarea || !lineNumbers) return;

  // Update line numbers
  updateLineNumbers();

  // Handle input changes
  textarea.oninput = () => {
    updateLineNumbers();
    updateDirtyState();
  };

  // Handle scrolling to sync line numbers
  textarea.onscroll = () => {
    lineNumbers.scrollTop = textarea.scrollTop;
  };

  // Layer the syntax-highlight overlay on top of the existing oninput /
  // onscroll handlers (they're decorated, not replaced).
  attachHighlightOverlay('editor-textarea', 'editor-highlight', editorData?.language || 'python');

  // Handle focus for escape hint
  textarea.onfocus = () => {
    if (escapeHint) escapeHint.style.display = 'block';
  };

  textarea.onblur = () => {
    if (escapeHint) escapeHint.style.display = 'none';
  };

  // Handle Tab key for indentation
  textarea.onkeydown = (e) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;

      // Insert 4 spaces
      const beforeTab = textarea.value.substring(0, start);
      const afterTab = textarea.value.substring(end);
      textarea.value = beforeTab + '    ' + afterTab;

      // Move cursor
      textarea.selectionStart = textarea.selectionEnd = start + 4;

      // Trigger input event to update line numbers and dirty state
      textarea.dispatchEvent(new Event('input'));
    } else if (e.key === 'Escape') {
      // Blur to exit editor
      textarea.blur();
    }
  };
}

function updateLineNumbers() {
  const textarea = document.getElementById('editor-textarea');
  const lineNumbers = document.getElementById('editor-line-numbers');

  if (!textarea || !lineNumbers) return;

  const lines = textarea.value.split('\n');
  const lineNumbersHTML = lines.map((_, index) =>
    `<div class="line-number">${index + 1}</div>`
  ).join('');

  lineNumbers.innerHTML = lineNumbersHTML;
}

function updateDirtyState() {
  const textarea = document.getElementById('editor-textarea');
  if (!textarea) return;

  const currentSource = textarea.value;
  const newIsDirty = currentSource !== lastSavedSource;

  if (newIsDirty !== isDirty) {
    isDirty = newIsDirty;
    updateEditorHeader();
    updateSaveButton();
  }
}

function updateEditorHeader() {
  const headerEl = document.querySelector('.strategy-name');
  if (headerEl && editorData) {
    const dirtyIndicator = isDirty ? ' ●modified' : '';
    headerEl.textContent = `${editorData.name}${dirtyIndicator}`;
  }
}

function updateSaveButton() {
  const saveBtn = document.getElementById('editor-save-btn');
  if (saveBtn) {
    saveBtn.disabled = !isDirty;
  }
}

function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes}B`;
  return `${(bytes / 1024).toFixed(1)}KB`;
}

function handleEditorExit(event) {
  if (event) event.preventDefault();

  if (isDirty) {
    showDiscardChangesModal();
  } else {
    navigateToSubView('list');
  }
}

function handleEditorCancel() {
  handleEditorExit();
}

function showDiscardChangesModal() {
  // Save the element that had focus before opening the modal
  const triggerElement = document.activeElement;

  // Create modal overlay
  const modal = document.createElement('div');
  modal.className = 'discard-modal-overlay';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');
  modal.setAttribute('aria-labelledby', 'discard-modal-title');
  modal.innerHTML = `
    <div class="discard-modal">
      <div class="discard-modal-title" id="discard-modal-title">Discard unsaved changes to ${editorData?.name || 'strategy'}?</div>
      <div class="discard-modal-body">Your edits will be lost.</div>
      <div class="discard-modal-actions">
        <button class="btn" onclick="closeDiscardChangesModal()">Cancel</button>
        <button class="btn btn-danger" onclick="confirmDiscardChanges()">Discard</button>
      </div>
    </div>
  `;

  // Close on backdrop click
  modal.onclick = (e) => {
    if (e.target === modal) closeDiscardChangesModal();
  };

  // Focus trap + Esc handler
  const focusableSelectors = '.discard-modal-cancel, .discard-modal-confirm';
  const trapHandler = (e) => {
    if (e.key === 'Escape') {
      e.preventDefault();
      closeDiscardChangesModal();
      return;
    }
    if (e.key !== 'Tab') return;
    const focusable = Array.from(modal.querySelectorAll(focusableSelectors))
      .filter(el => !el.disabled && el.offsetParent !== null);
    if (focusable.length === 0) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  };
  document.addEventListener('keydown', trapHandler);

  document.body.appendChild(modal);

  // Stash the trap handler + trigger for cleanup
  modal._trapHandler = trapHandler;
  modal._triggerElement = triggerElement;

  // Focus the Cancel button (default for discard modals)
  setTimeout(() => {
    const cancelBtn = modal.querySelector('.discard-modal-cancel');
    if (cancelBtn) cancelBtn.focus();
  }, 100);
}

function closeDiscardChangesModal() {
  const modal = document.querySelector('.discard-modal-overlay');
  if (modal) {
    // Clean up the focus-trap keydown handler
    if (modal._trapHandler) {
      document.removeEventListener('keydown', modal._trapHandler);
    }
    // Restore focus to the element that opened the modal
    const trigger = modal._triggerElement;
    modal.remove();
    if (trigger && typeof trigger.focus === 'function') {
      trigger.focus();
    }
  }
}

function confirmDiscardChanges() {
  closeDiscardChangesModal();
  navigateToSubView('list');
}

async function handleSave() {
  const textarea = document.getElementById('editor-textarea');
  if (!textarea || !editorData || !isDirty) return;

  const saveBtn = document.getElementById('editor-save-btn');
  if (saveBtn) {
    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving...';
  }

  try {
    const response = await fetch(`/api/strategies/${editorData.name}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        source: textarea.value
      })
    });

    if (!response.ok) {
      throw new Error(`Save failed: ${response.status}`);
    }

    const result = await response.json();

    // Update state
    lastSavedSource = textarea.value;
    isDirty = false;

    // Update editor data with new metadata
    editorData.size_bytes = result.size_bytes;
    editorData.line_count = result.line_count;
    editorData.modified_iso = result.modified_iso;

    updateEditorHeader();
    updateSaveButton();

    // Update footer
    const footerEl = document.querySelector('.editor-footer');
    if (footerEl) {
      footerEl.textContent = `${result.line_count} lines · ${formatFileSize(result.size_bytes)}`;
    }

    // Show brief "Saved" feedback
    showSavedFeedback();

    console.log(`[strategies.js] Successfully saved strategy: ${editorData.name}`);

  } catch (error) {
    console.error('[strategies.js] Failed to save strategy:', error);
    showSaveError();
  } finally {
    if (saveBtn) {
      saveBtn.disabled = !isDirty;
      saveBtn.textContent = 'Save';
    }
  }
}

function showSavedFeedback() {
  const footerEl = document.querySelector('.editor-footer');
  if (!footerEl) return;

  const originalText = footerEl.textContent;
  footerEl.textContent = `${originalText} · Saved just now`;

  setTimeout(() => {
    if (footerEl && editorData) {
      footerEl.textContent = `${editorData.line_count} lines · ${formatFileSize(editorData.size_bytes)}`;
    }
  }, 5000);
}

function showSaveError() {
  // Create error banner
  const editor = document.querySelector('.editor-container');
  if (!editor) return;

  // Remove any existing error banner
  const existingBanner = editor.querySelector('.save-error-banner');
  if (existingBanner) existingBanner.remove();

  const banner = document.createElement('div');
  banner.className = 'banner err save-error-banner';
  banner.innerHTML = `
    <span class="b-mark">ERR ·</span>
    <div style="flex:1">Failed to save strategy — check server connection</div>
    <button class="btn-link" onclick="this.parentElement.remove()" style="color:var(--ink-dim)">dismiss</button>
  `;

  editor.insertBefore(banner, editor.firstChild);
}

function handleSaveAs() {
  // TODO: Implement Save As functionality
  console.log('[strategies.js] Save As not yet implemented');
}

// ── New Sub-view Implementation ────────────────────────────────
let newSubViewState = {
  currentMode: 'llm', // 'blank' | 'llm'
  blankForm: {
    name: '',
    language: 'python',
    isDirty: false
  },
  llmForm: {
    name: '',
    prompt: '',
    language: 'python',
    isDirty: false,
    isGenerating: false,
    generatedCode: null,
    generationError: null,
    // Provider/model selection — populated from /api/config on mount and
    // refreshed via /api/config/llm/test when the user picks a provider.
    // These get sent in the StrategyGeneratePayload when generation lands.
    provider: '',
    model: '',
    availableProviders: [],     // [{name, model}] from /api/config
    availableModels: []         // ['gpt-4o', ...] for current provider
  }
};

function resetNewSubViewState() {
  // Wipe user-entered content. Keep currentMode (driven by localStorage)
  // and provider/model selectors (driven by /api/config) so the form lands
  // pre-populated with the user's default LLM, not blank dropdowns.
  newSubViewState.blankForm.name = '';
  newSubViewState.blankForm.isDirty = false;
  newSubViewState.llmForm.name = '';
  newSubViewState.llmForm.prompt = '';
  newSubViewState.llmForm.isDirty = false;
  newSubViewState.llmForm.isGenerating = false;
  newSubViewState.llmForm.generatedCode = null;
  newSubViewState.llmForm.generationError = null;
  newSubViewState.blankForm.language = 'python';
  newSubViewState.llmForm.language = 'python';
}

function renderNewSubView({ freshEntry = true } = {}) {
  currentSubView = 'new';
  currentStrategyName = null;

  // Fresh entry (user opened "+ New Strategy" from list / nav) wipes any
  // leftover form state from a previous visit. Mode-switch re-renders pass
  // freshEntry=false so the in-progress form survives the switch (the
  // dirty-prompt flow handles that case explicitly).
  if (freshEntry) {
    resetNewSubViewState();
  }

  hideListViewContainer();
  updateSubtitle('STRATEGIES · NEW');

  // Load last used mode from localStorage
  const lastMode = localStorage.getItem('ap_strategy_lastNewMode') || 'llm';
  newSubViewState.currentMode = lastMode;

  const strategiesSection = document.getElementById('section-strategies');
  if (strategiesSection) {
    strategiesSection.innerHTML = `
      <div class="new-container">
        <div class="tabs new-mode-tabs">
          <button class="tab ${newSubViewState.currentMode === 'blank' ? 'active' : ''}"
                  onclick="switchNewMode('blank')" aria-pressed="${newSubViewState.currentMode === 'blank'}">Blank</button>
          <button class="tab ${newSubViewState.currentMode === 'llm' ? 'active' : ''}"
                  onclick="switchNewMode('llm')" aria-pressed="${newSubViewState.currentMode === 'llm'}">LLM</button>
        </div>

        <div class="new-mode-body">
          ${renderNewModeBody()}
        </div>
      </div>
    `;

    setupNewSubView();
  }
}

function renderNewModeBody() {
  if (newSubViewState.currentMode === 'blank') {
    return renderBlankModeBody();
  } else {
    return renderLLMModeBody();
  }
}

function renderBlankModeBody() {
  return `
    <div class="blank-mode">
      <div class="strategy-name-input-container">
        <label for="blank-name-input" class="field-label">Strategy Name</label>
        <input type="text"
               id="blank-name-input"
               class="ipt strategy-name-input"
               placeholder="my-strategy"
               value="${newSubViewState.blankForm.name}"
               aria-describedby="blank-name-help blank-name-error">
        <div id="blank-name-help" class="name-help">Alphanumeric, dash, underscore only</div>
        <div id="blank-name-error" class="field-error" style="display: none;"></div>
      </div>

      <div class="language-selector" style="margin-bottom:10px;display:flex;gap:8px;align-items:center">
        <label for="blank-language-select" style="color:var(--ink-dim);font-size:12px">Language</label>
        <select id="blank-language-select" class="sel" onchange="switchBlankLanguage(this.value)">
          <option value="python" ${newSubViewState.blankForm.language === 'python' ? 'selected' : ''}>Python</option>
          <option value="javascript" ${newSubViewState.blankForm.language === 'javascript' ? 'selected' : ''}>JavaScript</option>
          <option value="rust" ${newSubViewState.blankForm.language === 'rust' ? 'selected' : ''}>Rust</option>
        </select>
      </div>

      <div class="blank-editor-container">
        <div class="code-editor">
          <div class="line-numbers" id="blank-line-numbers"></div>
          <div class="code-source-wrap">
            <pre class="code-highlight hljs" id="blank-editor-highlight" aria-hidden="true"><code class="${languageClass(newSubViewState.blankForm.language)}"></code></pre>
            <textarea
              class="code-source"
              id="blank-editor-textarea"
              aria-label="Strategy source code"
              spellcheck="false"
              autocapitalize="off"
              autocorrect="off"
            >${getBlankTemplate()}</textarea>
          </div>
        </div>
      </div>

      <div class="blank-action-row">
        <button class="btn" onclick="handleNewCancel()">Cancel</button>
        <button class="btn btn-primary" id="blank-save-btn" onclick="handleBlankSave()" disabled>Save</button>
      </div>
    </div>
  `;
}

function renderLLMModeBody() {
  if (newSubViewState.llmForm.generatedCode) {
    return renderLLMPostGenerateBody();
  } else {
    return renderLLMPreGenerateBody();
  }
}

function renderLLMPreGenerateBody() {
  return `
    <div class="llm-mode">
      <div class="language-selector" style="margin-bottom:10px;display:flex;gap:8px;align-items:center">
        <label for="llm-language-select" style="color:var(--ink-dim);font-size:12px">Language</label>
        <select id="llm-language-select" class="sel" onchange="switchLLMLanguage(this.value)">
          <option value="python" ${newSubViewState.llmForm.language === 'python' ? 'selected' : ''}>Python</option>
          <option value="javascript" ${newSubViewState.llmForm.language === 'javascript' ? 'selected' : ''}>JavaScript</option>
          <option value="rust" ${newSubViewState.llmForm.language === 'rust' ? 'selected' : ''}>Rust</option>
        </select>
      </div>

      <details class="llm-template-panel" style="margin-bottom:14px;border:1px solid var(--rule);border-radius:4px;padding:8px 12px">
        <summary style="cursor:pointer;color:var(--ink-dim);font-size:12px;user-select:none">
          <span id="llm-template-summary">Show LLM template (loading…)</span>
        </summary>
        <pre id="llm-template-content"
             style="margin-top:10px;max-height:400px;overflow:auto;font-family:var(--mono,monospace);font-size:11px;line-height:1.4;color:var(--ink-dim);background:var(--panel,#1a1f24);padding:10px;border-radius:3px;white-space:pre-wrap;word-break:break-word">Loading template…</pre>
        <div style="font-size:11px;color:var(--ink-faint);margin-top:6px">
          This is the system context the LLM receives. Your prompt below is appended as supplemental guidance.
        </div>
      </details>

      <div class="llm-prompt-container">
        <label for="llm-prompt-textarea" class="field-label">Prompt</label>
        <textarea
          id="llm-prompt-textarea"
          class="ipt llm-prompt-textarea"
          placeholder="Write a strategy that focuses on dribbling through the midfield and shoots from outside the penalty area."
          aria-describedby="llm-prompt-help"
        >${newSubViewState.llmForm.prompt}</textarea>
        <div id="llm-prompt-help" class="prompt-help">Describe what you want the strategy to do</div>
      </div>

      <div class="llm-model-row">
        <div class="llm-model-selectors" style="display:flex;gap:10px;align-items:center;flex:1">
          <label for="llm-provider-select" style="color:var(--ink-dim);font-size:12px">Provider</label>
          <select id="llm-provider-select" class="sel" onchange="handleLLMProviderChange(this.value)">
            ${renderLLMProviderOptions()}
          </select>
          <label for="llm-model-select" style="color:var(--ink-dim);font-size:12px;margin-left:8px">Model</label>
          <select id="llm-model-select" class="sel" onchange="handleLLMModelChange(this.value)">
            ${renderLLMModelOptions()}
          </select>
        </div>
        <button class="btn btn-primary"
                id="llm-generate-btn"
                onclick="handleLLMGenerate()"
                disabled>Generate</button>
      </div>

      <div id="llm-generate-status"
           class="llm-generate-status"
           role="status"
           aria-live="polite"
           style="display:none">
        <span class="spinner" aria-hidden="true"></span>
        <span id="llm-generate-status-text">Generating…</span>
        <span class="elapsed" id="llm-generate-elapsed">0s</span>
      </div>

      ${newSubViewState.llmForm.generationError ? `
        <div class="banner err generation-error-banner">
          <span class="b-mark">ERR ·</span>
          <div style="flex:1">Generation failed: ${newSubViewState.llmForm.generationError}</div>
          <button class="btn-link" onclick="clearGenerationError()" style="color:var(--ink-dim)">dismiss</button>
        </div>
      ` : ''}
    </div>
  `;
}

// Syntax-highlight Python via the vendored highlight.js (loaded as a
// classic script in index.html, so `hljs` is on window). Returns ready-
// to-inject HTML with the library's .hljs-* spans; styled by
// /static/highlight.theme.css. Falls back to escaped plain text if the
// library failed to load.
function highlightPython(code) {
  const safe = (code || '');
  if (typeof window !== 'undefined' && window.hljs) {
    return window.hljs.highlight(safe, { language: 'python' }).value;
  }
  return safe.replace(/[&<>"']/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}

function highlightCode(code, language) {
  const safe = (code || '');
  if (typeof window !== 'undefined' && window.hljs) {
    return window.hljs.highlight(safe, { language: languageHljsId(language) }).value;
  }
  return safe.replace(/[&<>"']/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}

// Wires a transparent <textarea> on top of a highlighted <pre><code>: as
// the user types, re-highlight; as they scroll, sync the pre's scroll
// position so the colored layer tracks the caret. The textarea retains
// focus + editing semantics; the pre is purely visual (pointer-events:none).
function attachHighlightOverlay(textareaId, highlightId, language = 'python') {
  const textarea = document.getElementById(textareaId);
  const highlight = document.getElementById(highlightId);
  if (!textarea || !highlight) return;
  const codeEl = highlight.querySelector('code');
  if (!codeEl) return;

  codeEl.className = languageClass(language);

  const renderHighlight = () => {
    const value = textarea.value;
    const padded = value.endsWith('\n') ? value + ' ' : value;
    codeEl.innerHTML = highlightCode(padded, language);
  };

  const syncScroll = () => {
    highlight.scrollTop = textarea.scrollTop;
    highlight.scrollLeft = textarea.scrollLeft;
  };

  const prevInput = textarea.oninput;
  textarea.oninput = (e) => {
    renderHighlight();
    if (typeof prevInput === 'function') prevInput.call(textarea, e);
  };
  const prevScroll = textarea.onscroll;
  textarea.onscroll = (e) => {
    syncScroll();
    if (typeof prevScroll === 'function') prevScroll.call(textarea, e);
  };

  renderHighlight();
  syncScroll();
}

function renderLLMPostGenerateBody() {
  return `
    <div class="llm-mode">
      <div class="llm-generated-container">
        <div class="generated-code-label">Generated Code</div>
        <div class="code-editor">
          <div class="line-numbers" id="generated-line-numbers"></div>
          <pre class="generated-code-preview hljs" id="generated-code-preview"><code class="${languageClass(newSubViewState.llmForm.language)}">${highlightCode(newSubViewState.llmForm.generatedCode || '', newSubViewState.llmForm.language)}</code></pre>
        </div>
      </div>

      <div class="llm-accept-container">
        <div class="strategy-name-input-container">
          <label for="generated-name-input" class="field-label">Strategy Name</label>
          <input type="text"
                 id="generated-name-input"
                 class="ipt strategy-name-input"
                 placeholder="generated-strategy"
                 value="${newSubViewState.llmForm.name}"
                 aria-describedby="generated-name-help generated-name-error">
          <div id="generated-name-help" class="name-help">Alphanumeric, dash, underscore only</div>
          <div id="generated-name-error" class="field-error" style="display: none;"></div>
        </div>

        <div class="llm-action-row">
          <button class="btn btn-danger" onclick="handleLLMDiscard()">Discard</button>
          <button class="btn" onclick="handleLLMRetry()">Retry</button>
          <button class="btn btn-primary" id="llm-accept-btn" onclick="handleLLMAccept()" disabled>Accept → Save</button>
        </div>
      </div>
    </div>
  `;
}

function getBlankTemplateForLanguage(language) {
  const defaultName = newSubViewState.blankForm.name || 'my-strategy';
  if (language === 'javascript') {
    return `// Strategy: ${defaultName}

function decide(game_state, player_state, history) {
    // Return one of: {type:"Hold"}, {type:"Move",dx,dy,speed}, {type:"Pass",target_pos,power}, {type:"Shoot",angle,power}, {type:"Tackle",target_player_id}
    return {type: "Hold"};
}`;
  }
  if (language === 'rust') {
    // Skeleton mirrors the cargo template (src/foundation/sandbox/cargo_template/
    // src/lib.rs.in). The user authors the whole lib.rs; only edit decide_logic.
    return `// Strategy: ${defaultName}
use serde::{Deserialize, Serialize};
use std::alloc::{alloc, dealloc, Layout};

#[derive(Deserialize)]
struct GameState { tick: u32, ball: Ball, field: Field, my_team: String, my_player_id: String }
#[derive(Deserialize)]
struct Ball { position: (f64, f64), carrier_id: Option<String> }
#[derive(Deserialize)]
struct Field { width: f64, height: f64, team_a_goal_x: f64, team_b_goal_x: f64 }
#[derive(Deserialize)]
struct PlayerState { role: String, position: (f64, f64), has_ball: bool, speed: i32 }
#[derive(Deserialize)]
struct TickRecord { tick: u32 }
#[derive(Serialize)]
#[serde(tag = "type")]
enum Action {
    Move { dx: f64, dy: f64, speed: f64 },
    Pass { target_pos: (f64, f64), power: i32 },
    Shoot { angle: f64, power: i32 },
    Tackle { target_player_id: String },
    Hold,
}

#[link(wasm_import_module = "host")]
extern "C" { fn random_u64() -> u64; }

// EDIT THIS — your strategy logic.
fn decide_logic(gs: &GameState, ps: &PlayerState, _hist: &[TickRecord]) -> Action {
    if ps.has_ball { return Action::Hold; }
    let (bx, by) = gs.ball.position;
    let (mx, my) = ps.position;
    let dx = bx - mx; let dy = by - my;
    let mag = (dx * dx + dy * dy).sqrt();
    let (ndx, ndy) = if mag > 0.001 { (dx / mag, dy / mag) } else { (1.0, 0.0) };
    Action::Move { dx: ndx, dy: ndy, speed: 1.0 }
}

// ── DO NOT EDIT BELOW: ABI surface required by WasmtimeSandbox ───────────
static mut RETURN_PTR: i32 = 0;
static mut RETURN_LEN: i32 = 0;
#[no_mangle] pub extern "C" fn alloc_buf(size: usize) -> *mut u8 {
    let layout = Layout::from_size_align(size.max(1), 8).unwrap();
    unsafe { alloc(layout) }
}
#[no_mangle] pub extern "C" fn dealloc_buf(ptr: *mut u8, size: usize) {
    let layout = Layout::from_size_align(size.max(1), 8).unwrap();
    unsafe { dealloc(ptr, layout) };
}
#[no_mangle] pub extern "C" fn return_ptr() -> i32 { unsafe { RETURN_PTR } }
#[no_mangle] pub extern "C" fn return_len() -> i32 { unsafe { RETURN_LEN } }
#[no_mangle] pub extern "C" fn decide(ptr: *const u8, len: usize) -> i32 {
    let bytes = unsafe { std::slice::from_raw_parts(ptr, len) };
    let (gs, ps, hist): (GameState, PlayerState, Vec<TickRecord>) =
        match rmp_serde::from_slice(bytes) { Ok(v) => v, Err(_) => return -1 };
    let action = decide_logic(&gs, &ps, &hist);
    let out = match rmp_serde::to_vec_named(&action) { Ok(v) => v, Err(_) => return -1 };
    let out_ptr = alloc_buf(out.len());
    unsafe {
        std::ptr::copy_nonoverlapping(out.as_ptr(), out_ptr, out.len());
        RETURN_PTR = out_ptr as i32; RETURN_LEN = out.len() as i32;
    }
    0
}`;
  }
  return `"""Strategy: ${defaultName}"""

def decide(game_state, player_state, history):
    """Return one of: Hold(), Move(direction), Pass(target_id), Shoot(), Tackle(target_id)."""
    return Hold()`;
}

function getBlankTemplate() {
  return getBlankTemplateForLanguage(newSubViewState.blankForm.language);
}

function setupNewSubView() {
  // Load active LLM config for model indicator
  loadActiveLLMConfig();

  if (newSubViewState.currentMode === 'blank') {
    setupBlankMode();
  } else {
    setupLLMMode();
  }
}

function renderLLMProviderOptions() {
  const providers = newSubViewState.llmForm.availableProviders;
  if (providers.length === 0) {
    return `<option value="">No providers configured</option>`;
  }
  const selected = newSubViewState.llmForm.provider;
  return providers.map(p =>
    `<option value="${p.name}" ${p.name === selected ? 'selected' : ''}>${p.name}</option>`
  ).join('');
}

function renderLLMModelOptions() {
  const models = newSubViewState.llmForm.availableModels;
  const savedModel = newSubViewState.llmForm.model;
  if (models.length === 0) {
    // Fallback so the form is still POSTable: show whatever model was loaded
    // from /api/config for the current provider, even before /test runs.
    const label = savedModel || 'Select provider to load models';
    return `<option value="${savedModel}" selected>${label}</option>`;
  }
  const savedInList = !savedModel || models.includes(savedModel);
  const fallback = (savedModel && !savedInList)
    ? `<option value="${savedModel}" selected>${savedModel} (saved — not in current list)</option>`
    : '';
  return fallback + models.map(m =>
    `<option value="${m}" ${m === savedModel ? 'selected' : ''}>${m}</option>`
  ).join('');
}

async function loadActiveLLMConfig() {
  try {
    const response = await fetch('/api/config');
    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }

    const config = await response.json();
    const llmConfig = config.llm || {};
    const providers = (llmConfig.providers || []).map(p => ({
      name: p.name,
      model: p.model,
      type: p.type || null,  // Custom providers have "openai_compatible", built-in are null
      url: p.url || null,    // Custom endpoint URL (ollama, vllm, etc.)
    }));

    newSubViewState.llmForm.availableProviders = providers;

    // Seed defaults from llm.active (server's "first provider with a key").
    // User can override either dropdown after this.
    if (!newSubViewState.llmForm.provider && llmConfig.active) {
      newSubViewState.llmForm.provider = llmConfig.active.provider;
      newSubViewState.llmForm.model = llmConfig.active.model;
    } else if (!newSubViewState.llmForm.provider && providers.length > 0) {
      newSubViewState.llmForm.provider = providers[0].name;
      newSubViewState.llmForm.model = providers[0].model;
    }

    refreshLLMSelectors();
    updateLLMGenerateButton();

    // Kick off a live model-list fetch so the model dropdown reflects what
    // the provider's key can actually access. Failure is non-fatal — the
    // saved-default fallback in renderLLMModelOptions keeps the form usable.
    if (newSubViewState.llmForm.provider) {
      fetchAvailableModels(newSubViewState.llmForm.provider);
    }

  } catch (error) {
    console.error('[strategies.js] Failed to load LLM config:', error);
    newSubViewState.llmForm.availableProviders = [];
    refreshLLMSelectors();
  }
}

function refreshLLMSelectors() {
  const providerSelect = document.getElementById('llm-provider-select');
  const modelSelect = document.getElementById('llm-model-select');
  if (providerSelect) providerSelect.innerHTML = renderLLMProviderOptions();
  if (modelSelect) modelSelect.innerHTML = renderLLMModelOptions();
}

async function fetchAvailableModels(provider) {
  if (!provider) return;
  try {
    // Build request body. For custom providers (ollama, vllm, etc.), include
    // type and url so the backend knows how to route the test request.
    const body = { provider };
    const providerMeta = newSubViewState.llmForm.availableProviders.find(p => p.name === provider);
    if (providerMeta && providerMeta.type) {
      body.type = providerMeta.type;
      body.url = providerMeta.url;
    }

    const response = await fetch('/api/config/llm/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const result = await response.json();
    if (result.ok && Array.isArray(result.models) && result.models.length > 0) {
      newSubViewState.llmForm.availableModels = result.models;
      // If the saved model isn't in the live list, fall back to the first.
      if (!result.models.includes(newSubViewState.llmForm.model)) {
        newSubViewState.llmForm.model = result.models[0];
      }
      refreshLLMSelectors();
    }
    // On !ok we leave availableModels empty — fallback option keeps form usable.
  } catch (error) {
    console.warn('[strategies.js] Could not fetch models for', provider, error);
  }
}

function handleLLMProviderChange(provider) {
  newSubViewState.llmForm.provider = provider;
  // Default the model to whatever's saved for this provider in /api/config.
  const providerEntry = newSubViewState.llmForm.availableProviders
    .find(p => p.name === provider);
  if (providerEntry) {
    newSubViewState.llmForm.model = providerEntry.model;
  }
  // Clear stale model list — the new provider has its own.
  newSubViewState.llmForm.availableModels = [];
  refreshLLMSelectors();
  fetchAvailableModels(provider);
}

function handleLLMModelChange(model) {
  newSubViewState.llmForm.model = model;
}

function setupBlankMode() {
  const nameInput = document.getElementById('blank-name-input');
  const textarea = document.getElementById('blank-editor-textarea');

  if (nameInput) {
    nameInput.oninput = validateBlankForm;
    validateBlankForm(); // Initial validation
  }

  if (textarea) {
    updateBlankLineNumbers();
    textarea.oninput = () => {
      updateBlankLineNumbers();
      markBlankFormDirty();
    };

    // Handle Tab key for indentation
    textarea.onkeydown = (e) => {
      if (e.key === 'Tab') {
        e.preventDefault();
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;

        const beforeTab = textarea.value.substring(0, start);
        const afterTab = textarea.value.substring(end);
        textarea.value = beforeTab + '    ' + afterTab;

        textarea.selectionStart = textarea.selectionEnd = start + 4;
        textarea.dispatchEvent(new Event('input'));
      }
    };

    attachHighlightOverlay('blank-editor-textarea', 'blank-editor-highlight', newSubViewState.blankForm.language);
  }
}

function setupLLMMode() {
  const promptTextarea = document.getElementById('llm-prompt-textarea');

  if (promptTextarea) {
    promptTextarea.oninput = () => {
      newSubViewState.llmForm.prompt = promptTextarea.value;
      updateLLMGenerateButton();
    };
    updateLLMGenerateButton(); // Initial state
  }

  // Fetch the raw template once per mode mount. Cheap (single file read),
  // and the template only changes on process restart so no need to refresh.
  loadLLMTemplate();

  if (newSubViewState.llmForm.generatedCode) {
    updateGeneratedLineNumbers();
    const nameInput = document.getElementById('generated-name-input');
    if (nameInput) {
      nameInput.oninput = validateLLMAcceptForm;
      validateLLMAcceptForm(); // Initial validation
    }
  }
}

async function loadLLMTemplate() {
  const summary = document.getElementById('llm-template-summary');
  const content = document.getElementById('llm-template-content');
  if (!summary || !content) return;

  const lang = newSubViewState.llmForm.language;
  const mode = lang === 'javascript' ? 'generation-js'
             : lang === 'rust' ? 'generation-rust'
             : 'generation';
  try {
    const response = await fetch(`/api/strategies/llm-template?mode=${mode}`);
    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }
    const body = await response.json();
    const kb = (body.size_bytes / 1024).toFixed(1);
    summary.textContent = `Show LLM template (${body.filename} · v${body.version} · ${kb} KB)`;
    content.textContent = body.content;  // textContent escapes Jinja braces safely
  } catch (error) {
    console.warn('[strategies.js] Failed to load LLM template:', error);
    summary.textContent = 'LLM template (failed to load)';
    content.textContent = `Error: ${error.message}`;
  }
}

function updateBlankLineNumbers() {
  const textarea = document.getElementById('blank-editor-textarea');
  const lineNumbers = document.getElementById('blank-line-numbers');

  if (!textarea || !lineNumbers) return;

  const lines = textarea.value.split('\n');
  const lineNumbersHTML = lines.map((_, index) =>
    `<div class="line-number">${index + 1}</div>`
  ).join('');

  lineNumbers.innerHTML = lineNumbersHTML;
}

function updateGeneratedLineNumbers() {
  const codePreview = document.getElementById('generated-code-preview');
  const lineNumbers = document.getElementById('generated-line-numbers');

  if (!codePreview || !lineNumbers || !newSubViewState.llmForm.generatedCode) return;

  const lines = newSubViewState.llmForm.generatedCode.split('\n');
  const lineNumbersHTML = lines.map((_, index) =>
    `<div class="line-number">${index + 1}</div>`
  ).join('');

  lineNumbers.innerHTML = lineNumbersHTML;
}

function validateBlankForm() {
  const nameInput = document.getElementById('blank-name-input');
  const saveBtn = document.getElementById('blank-save-btn');
  const errorDiv = document.getElementById('blank-name-error');

  if (!nameInput || !saveBtn || !errorDiv) return;

  const name = nameInput.value.trim();
  newSubViewState.blankForm.name = name;

  const validation = validateStrategyName(name);

  if (validation.valid) {
    nameInput.classList.remove('field-error-state');
    errorDiv.style.display = 'none';
    saveBtn.disabled = false;
  } else {
    nameInput.classList.add('field-error-state');
    errorDiv.textContent = validation.error;
    errorDiv.style.display = 'block';
    saveBtn.disabled = true;
  }
}

function validateLLMAcceptForm() {
  const nameInput = document.getElementById('generated-name-input');
  const acceptBtn = document.getElementById('llm-accept-btn');
  const errorDiv = document.getElementById('generated-name-error');

  if (!nameInput || !acceptBtn || !errorDiv) return;

  const name = nameInput.value.trim();
  newSubViewState.llmForm.name = name;

  const validation = validateStrategyName(name);

  if (validation.valid) {
    nameInput.classList.remove('field-error-state');
    errorDiv.style.display = 'none';
    acceptBtn.disabled = false;
  } else {
    nameInput.classList.add('field-error-state');
    errorDiv.textContent = validation.error;
    errorDiv.style.display = 'block';
    acceptBtn.disabled = true;
  }
}

function validateStrategyName(name) {
  if (!name) {
    return { valid: false, error: 'Strategy name is required' };
  }

  if (name.length > 64) {
    return { valid: false, error: 'Strategy name must be 64 characters or less' };
  }

  if (!/^[A-Za-z0-9_-]+$/.test(name)) {
    return { valid: false, error: 'Strategy name can only contain letters, numbers, dashes, and underscores' };
  }

  // TODO: Check for uniqueness against existing strategies
  // For now, we'll rely on the server-side 409 check

  return { valid: true };
}

function updateLLMGenerateButton() {
  const generateBtn = document.getElementById('llm-generate-btn');
  if (!generateBtn) return;

  // Empty prompt is allowed (template's USER INTENT section has a fallback);
  // only block while a generation is already in flight.
  generateBtn.disabled = newSubViewState.llmForm.isGenerating;

  if (newSubViewState.llmForm.isGenerating) {
    generateBtn.textContent = 'Generating…';
  } else {
    generateBtn.textContent = 'Generate';
  }
}

function markBlankFormDirty() {
  newSubViewState.blankForm.isDirty = true;
}

function switchBlankLanguage(language) {
  if (language === newSubViewState.blankForm.language) return;
  newSubViewState.blankForm.language = language;
  const textarea = document.getElementById('blank-editor-textarea');
  if (textarea && !newSubViewState.blankForm.isDirty) {
    textarea.value = getBlankTemplate();
  }
  const modeBody = document.querySelector('.new-mode-body');
  if (modeBody) {
    modeBody.innerHTML = renderNewModeBody();
    setupNewSubView();
  }
}

function switchLLMLanguage(language) {
  if (language === newSubViewState.llmForm.language) return;
  newSubViewState.llmForm.language = language;
  const modeBody = document.querySelector('.new-mode-body');
  if (modeBody) {
    modeBody.innerHTML = renderNewModeBody();
    setupLLMMode();
  }
}

function switchNewMode(mode) {
  if (mode === newSubViewState.currentMode) return;

  // Check if current mode has unsaved changes
  let isDirty = false;
  if (newSubViewState.currentMode === 'blank') {
    isDirty = newSubViewState.blankForm.isDirty;
  } else {
    isDirty = newSubViewState.llmForm.isDirty || newSubViewState.llmForm.generatedCode !== null;
  }

  if (isDirty) {
    showModeDiscardModal(mode);
    return;
  }

  // Safe to switch
  completeModeSwitch(mode);
}

function completeModeSwitch(mode) {
  newSubViewState.currentMode = mode;
  localStorage.setItem('ap_strategy_lastNewMode', mode);

  // Re-render the entire sub-view. freshEntry=false preserves the
  // already-entered form state for the OTHER mode (the discard prompt
  // upstream handled clearing the previous mode's state when needed).
  renderNewSubView({ freshEntry: false });
}

function showModeDiscardModal(targetMode) {
  const triggerElement = document.activeElement;

  const modal = document.createElement('div');
  modal.className = 'discard-modal-overlay';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');
  modal.setAttribute('aria-labelledby', 'mode-discard-modal-title');
  modal.innerHTML = `
    <div class="discard-modal">
      <div class="discard-modal-title" id="mode-discard-modal-title">Switch modes?</div>
      <div class="discard-modal-body">You have unsaved changes in the current mode. Switching will discard them.</div>
      <div class="discard-modal-actions">
        <button class="btn" onclick="closeModeDiscardModal()">Cancel</button>
        <button class="btn btn-danger" onclick="confirmModeSwitch('${targetMode}')">Switch & Discard</button>
      </div>
    </div>
  `;

  modal.onclick = (e) => {
    if (e.target === modal) closeModeDiscardModal();
  };

  const focusableSelectors = '.discard-modal-cancel, .discard-modal-confirm';
  const trapHandler = (e) => {
    if (e.key === 'Escape') {
      e.preventDefault();
      closeModeDiscardModal();
      return;
    }
    if (e.key !== 'Tab') return;
    const focusable = Array.from(modal.querySelectorAll(focusableSelectors))
      .filter(el => !el.disabled && el.offsetParent !== null);
    if (focusable.length === 0) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  };

  document.addEventListener('keydown', trapHandler);
  document.body.appendChild(modal);

  modal._trapHandler = trapHandler;
  modal._triggerElement = triggerElement;

  setTimeout(() => {
    const cancelBtn = modal.querySelector('.discard-modal-cancel');
    if (cancelBtn) cancelBtn.focus();
  }, 100);
}

function closeModeDiscardModal() {
  const modal = document.querySelector('.discard-modal-overlay');
  if (modal) {
    if (modal._trapHandler) {
      document.removeEventListener('keydown', modal._trapHandler);
    }
    const trigger = modal._triggerElement;
    modal.remove();
    if (trigger && typeof trigger.focus === 'function') {
      trigger.focus();
    }
  }
}

function confirmModeSwitch(targetMode) {
  closeModeDiscardModal();

  // Reset state for current mode
  if (newSubViewState.currentMode === 'blank') {
    newSubViewState.blankForm = { name: '', language: 'python', isDirty: false };
  } else {
    newSubViewState.llmForm = {
      name: '',
      prompt: '',
      language: 'python',
      isDirty: false,
      isGenerating: false,
      generatedCode: null,
      generationError: null
    };
  }

  completeModeSwitch(targetMode);
}

function handleNewExit(event) {
  if (event) event.preventDefault();

  // Check if any mode has unsaved changes
  let isDirty = false;
  if (newSubViewState.currentMode === 'blank') {
    isDirty = newSubViewState.blankForm.isDirty;
  } else {
    isDirty = newSubViewState.llmForm.isDirty || newSubViewState.llmForm.generatedCode !== null;
  }

  if (isDirty) {
    showNewExitDiscardModal();
  } else {
    navigateToSubView('list');
  }
}

function handleNewCancel() {
  handleNewExit();
}

function showNewExitDiscardModal() {
  const triggerElement = document.activeElement;

  const modal = document.createElement('div');
  modal.className = 'discard-modal-overlay';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');
  modal.setAttribute('aria-labelledby', 'new-exit-modal-title');
  modal.innerHTML = `
    <div class="discard-modal">
      <div class="discard-modal-title" id="new-exit-modal-title">Discard unsaved work?</div>
      <div class="discard-modal-body">You have unsaved changes. Leaving will discard them.</div>
      <div class="discard-modal-actions">
        <button class="btn" onclick="closeNewExitDiscardModal()">Cancel</button>
        <button class="btn btn-danger" onclick="confirmNewExit()">Discard & Leave</button>
      </div>
    </div>
  `;

  modal.onclick = (e) => {
    if (e.target === modal) closeNewExitDiscardModal();
  };

  const focusableSelectors = '.discard-modal-cancel, .discard-modal-confirm';
  const trapHandler = (e) => {
    if (e.key === 'Escape') {
      e.preventDefault();
      closeNewExitDiscardModal();
      return;
    }
    if (e.key !== 'Tab') return;
    const focusable = Array.from(modal.querySelectorAll(focusableSelectors))
      .filter(el => !el.disabled && el.offsetParent !== null);
    if (focusable.length === 0) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  };

  document.addEventListener('keydown', trapHandler);
  document.body.appendChild(modal);

  modal._trapHandler = trapHandler;
  modal._triggerElement = triggerElement;

  setTimeout(() => {
    const cancelBtn = modal.querySelector('.discard-modal-cancel');
    if (cancelBtn) cancelBtn.focus();
  }, 100);
}

function closeNewExitDiscardModal() {
  const modal = document.querySelector('.discard-modal-overlay');
  if (modal) {
    if (modal._trapHandler) {
      document.removeEventListener('keydown', modal._trapHandler);
    }
    const trigger = modal._triggerElement;
    modal.remove();
    if (trigger && typeof trigger.focus === 'function') {
      trigger.focus();
    }
  }
}

function confirmNewExit() {
  closeNewExitDiscardModal();
  navigateToSubView('list');
}

async function handleBlankSave() {
  const nameInput = document.getElementById('blank-name-input');
  const textarea = document.getElementById('blank-editor-textarea');
  const saveBtn = document.getElementById('blank-save-btn');

  if (!nameInput || !textarea || !saveBtn) return;

  const name = nameInput.value.trim();
  const source = textarea.value;

  if (!name || saveBtn.disabled) return;

  saveBtn.disabled = true;
  saveBtn.textContent = 'Saving...';

  try {
    const response = await fetch('/api/strategies', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: name,
        source: source,
        language: newSubViewState.blankForm.language,
      })
    });

    if (!response.ok) {
      if (response.status === 409) {
        throw new Error(`A strategy named '${name}' already exists`);
      }
      throw new Error(`Save failed: ${response.status}`);
    }

    const result = await response.json();
    console.log(`[strategies.js] Successfully created strategy: ${name}`);

    // Clear blank-form dirty flag — the strategy is now persisted, so the
    // "discard unsaved work?" prompt would be a lie if the user leaves.
    newSubViewState.blankForm.isDirty = false;

    // Navigate to the editor for the new strategy
    navigateToSubView('editor', name);

  } catch (error) {
    console.error('[strategies.js] Failed to save blank strategy:', error);

    // Show error in validation area
    const errorDiv = document.getElementById('blank-name-error');
    if (errorDiv) {
      errorDiv.textContent = error.message;
      errorDiv.style.display = 'block';
    }

  } finally {
    if (saveBtn) {
      saveBtn.disabled = false;
      saveBtn.textContent = 'Save';
    }
  }
}

async function handleLLMGenerate() {
  const promptTextarea = document.getElementById('llm-prompt-textarea');
  const generateBtn = document.getElementById('llm-generate-btn');

  if (!promptTextarea || !generateBtn) return;

  // Empty prompt is OK — backend uses USER INTENT fallback prose. Only
  // block re-entry while an in-flight generation hasn't returned yet.
  const prompt = promptTextarea.value.trim();
  if (newSubViewState.llmForm.isGenerating) return;

  const provider = newSubViewState.llmForm.provider;
  const model = newSubViewState.llmForm.model;
  if (!provider || !model) {
    newSubViewState.llmForm.generationError = 'Please pick a provider and model first.';
    rerenderLLMMode();
    return;
  }

  // Find the provider config to get type and url for custom providers
  const providerConfig = newSubViewState.llmForm.availableProviders.find(p => p.name === provider);
  const providerType = providerConfig?.type || null;
  const baseUrl = providerConfig?.url || null;

  // Backend (subprocess) doesn't save — it just returns validated code.
  // The user picks a final name in the post-generate panel and saves via
  // the existing handleLLMAccept flow (POST /api/strategies).
  // Server schema requires `name` even for generate; pass a placeholder.
  const placeholderName = `gen-${Date.now()}`;

  newSubViewState.llmForm.isGenerating = true;
  newSubViewState.llmForm.generationError = null;
  updateLLMGenerateButton();  // flips label to "Generating..."
  const stopStatusTicker = startLLMGenerateStatus(provider, model);

  try {
    const payload = {
      name: placeholderName,
      prompt,
      provider,
      model,
      language: newSubViewState.llmForm.language
    };
    // Include provider_type and base_url for custom providers (ollama, vllm, etc.)
    if (providerType) payload.provider_type = providerType;
    if (baseUrl) payload.base_url = baseUrl;

    const response = await fetch('/api/strategies/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();

    if (response.ok && result.ok) {
      newSubViewState.llmForm.generatedCode = result.code;
      // Default name: <language>-<provider>-<model>-<ms-timestamp>. Sanitize defensively
      // so unusual model ids don't break the strategy-name regex (^[A-Za-z0-9_-]+$).
      const sanitize = s => String(s).replace(/[^A-Za-z0-9_-]/g, '-');
      const language = newSubViewState.llmForm.language || 'python';
      newSubViewState.llmForm.name = `${sanitize(language)}-${sanitize(provider)}-${sanitize(model)}-${Date.now()}`;
      // Stash the provenance so handleLLMAccept can write a truthful sidecar
      // (per ADR-0023). The server echoes back what we sent plus the
      // template_version it actually used.
      newSubViewState.llmForm.savedProvenance = {
        provider:               result.provider || provider,
        model:                  result.model || model,
        prompt:                 result.prompt != null ? result.prompt : prompt,
        template_version:       result.template_version || null,
        generation_latency_ms:  result.latency_ms != null ? result.latency_ms : null,
        generation_input_tokens: result.input_tokens != null ? result.input_tokens : null,
        generation_output_tokens: result.output_tokens != null ? result.output_tokens : null,
      };
    } else {
      const detail = result.error || result.detail || `HTTP ${response.status}`;
      // Diagnostic (stderr tail from the subprocess) — useful for path-mismatch
      // and other env issues. Concatenate when present.
      const diag = result.diagnostic ? `\n\n[diagnostic]\n${result.diagnostic}` : '';
      newSubViewState.llmForm.generationError = detail + diag;
    }
  } catch (error) {
    console.error('[strategies.js] Generation request failed:', error);
    newSubViewState.llmForm.generationError = `Request failed: ${error.message}`;
  } finally {
    newSubViewState.llmForm.isGenerating = false;
    stopStatusTicker();
    rerenderLLMMode();
  }
}

// Reveals the in-flight status block and starts a 1Hz elapsed-seconds
// ticker. Returns a stop() callback to invoke in the request's finally
// block — caller owns lifecycle so a thrown fetch can't leak the timer.
function startLLMGenerateStatus(provider, model) {
  const status = document.getElementById('llm-generate-status');
  const text = document.getElementById('llm-generate-status-text');
  const elapsed = document.getElementById('llm-generate-elapsed');
  if (!status) return () => {};

  if (text) text.textContent = `Generating with ${provider}/${model}…`;
  if (elapsed) elapsed.textContent = '0s';
  status.style.display = '';

  const startedAt = Date.now();
  const intervalId = setInterval(() => {
    if (!elapsed) return;
    const secs = Math.floor((Date.now() - startedAt) / 1000);
    elapsed.textContent = `${secs}s`;
  }, 1000);

  return () => {
    clearInterval(intervalId);
    // The post-generate render swaps the whole panel out, so DOM-cleanup
    // here is only for the error path (panel stays on the pre-generate body).
    if (status && status.isConnected) status.style.display = 'none';
  };
}

function rerenderLLMMode() {
  const modeBody = document.querySelector('.new-mode-body');
  if (modeBody) {
    modeBody.innerHTML = renderNewModeBody();
    setupLLMMode();
  }
}

function clearGenerationError() {
  newSubViewState.llmForm.generationError = null;

  // Re-render to hide the error
  const modeBody = document.querySelector('.new-mode-body');
  if (modeBody) {
    modeBody.innerHTML = renderNewModeBody();
    setupLLMMode();
  }
}

function handleLLMDiscard() {
  newSubViewState.llmForm.generatedCode = null;
  newSubViewState.llmForm.name = '';
  newSubViewState.llmForm.isDirty = false;

  // Re-render to go back to pre-generate state
  const modeBody = document.querySelector('.new-mode-body');
  if (modeBody) {
    modeBody.innerHTML = renderNewModeBody();
    setupLLMMode();
  }
}

function handleLLMRetry() {
  // For now, just go back to pre-generate and show the not-yet-wired message again
  handleLLMDiscard();
  setTimeout(() => {
    handleLLMGenerate();
  }, 100);
}

async function handleLLMAccept() {
  const nameInput = document.getElementById('generated-name-input');
  const acceptBtn = document.getElementById('llm-accept-btn');

  if (!nameInput || !acceptBtn || !newSubViewState.llmForm.generatedCode) return;

  const name = nameInput.value.trim();
  if (!name || acceptBtn.disabled) return;

  acceptBtn.disabled = true;
  acceptBtn.textContent = 'Saving...';

  try {
    // Build the sidecar meta from the provenance we stashed at generate time.
    // Per ADR-0023, an LLM-generated strategy must include provider, model,
    // prompt, and template_version. Defensive fallback: if savedProvenance is
    // missing (shouldn't happen — generate must run before accept) we save
    // as 'manual' rather than blocking the user.
    const prov = newSubViewState.llmForm.savedProvenance;
    const meta = prov
      ? {
          provider:                 prov.provider,
          model:                    prov.model,
          created_by:               'llm',
          prompt:                   prov.prompt || '',
          template_version:         prov.template_version || 'unknown',
          generation_latency_ms:    prov.generation_latency_ms ?? null,
          generation_input_tokens:  prov.generation_input_tokens ?? null,
          generation_output_tokens: prov.generation_output_tokens ?? null,
        }
      : null;

    const response = await fetch('/api/strategies', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name:     name,
        source:   newSubViewState.llmForm.generatedCode,
        meta:     meta,
        language: newSubViewState.llmForm.language,
      })
    });

    if (!response.ok) {
      if (response.status === 409) {
        throw new Error(`A strategy named '${name}' already exists`);
      }
      throw new Error(`Save failed: ${response.status}`);
    }

    const result = await response.json();
    console.log(`[strategies.js] Successfully created strategy from LLM: ${name}`);

    // Clear LLM-form state — the work is now persisted, so leaving the
    // workflow should NOT trigger the "discard unsaved" modal. (The form
    // is destroyed when we navigate away anyway, but the dirty flag lives
    // on `newSubViewState` which outlives the DOM.)
    newSubViewState.llmForm.generatedCode = null;
    newSubViewState.llmForm.isDirty = false;

    // Navigate to the editor for the new strategy
    navigateToSubView('editor', name);

  } catch (error) {
    console.error('[strategies.js] Failed to save LLM strategy:', error);

    // Show error in validation area
    const errorDiv = document.getElementById('generated-name-error');
    if (errorDiv) {
      errorDiv.textContent = error.message;
      errorDiv.style.display = 'block';
    }

  } finally {
    if (acceptBtn) {
      acceptBtn.disabled = false;
      acceptBtn.textContent = 'Accept → Save';
    }
  }
}

// ── Strategy Actions ────────────────────────────────────────────
function openStrategyEditor(strategyName) {
  navigateToSubView('editor', strategyName);
}

function openDeleteStrategyConfirm(strategyName) {
  showDeleteConfirmModal({
    title: `Delete strategy ${strategyName}?`,
    body: 'This removes its file permanently.',
    expectedText: strategyName,
    onConfirm: async (ctx) => {
      ctx.setBusy('Deleting…');
      const response = await fetch(`/api/strategies/${strategyName}`, { method: 'DELETE' });
      if (!response.ok) {
        ctx.setError('Delete Failed');
        console.error(`[strategies.js] DELETE /api/strategies/${strategyName} → ${response.status}`);
        return;
      }
      ctx.close();
      await loadStrategies();
      console.log(`[strategies.js] Successfully deleted strategy: ${strategyName}`);
    },
  });
}

// ── Utility Functions ───────────────────────────────────────────
function updateSubtitle(subtitle) {
  window.dispatchEvent(new CustomEvent('shell:subtitleChanged', {
    detail: { subtitle }
  }));
}

// ── Main Section API ────────────────────────────────────────────
function activate(route = {}) {
  console.log('[strategies.js] Activating with route:', route);

  // Show strategies section, hide other sections
  const sectionsToHide = ['section-matches', 'section-arena', 'section-config', 'section-cup', 'section-league'];
  const strategiesSection = document.getElementById('section-strategies');

  if (strategiesSection) {
    strategiesSection.removeAttribute('hidden');
  }

  sectionsToHide.forEach(sectionId => {
    const sectionEl = document.getElementById(sectionId);
    if (sectionEl) {
      sectionEl.setAttribute('hidden', '');
    }
  });

  // Parse route and render appropriate sub-view
  const { subView, strategyName } = parseRoute(route);

  if (subView === 'list') {
    removeBackButton();
    renderListSubView();
  } else if (subView === 'editor') {
    addBackButton(handleEditorExit);
    renderEditorSubView(strategyName);
  } else if (subView === 'new') {
    addBackButton(handleNewExit);
    renderNewSubView();
  }
}

// ── Top-strip "Back to list" button ─────────────────────────────
// Mirrors the matches-replay pattern: parks the back affordance in the
// App Shell's #right-cap so it's always in the same spot regardless of
// section/sub-view. The handler defers to the editor/new-specific exit
// callback so dirty-check confirm modals still fire correctly.
function addBackButton(exitHandler) {
  const rightCap = document.getElementById('right-cap');
  if (!rightCap) return;

  // Reuse the existing button if present so we don't churn DOM, but always
  // re-bind onclick to the current handler. The previous early-return when
  // a button already existed left the handler bound to whichever sub-view
  // installed it FIRST — e.g. transitioning new→editor (post-save) kept the
  // back button calling handleNewExit, which then checked the new-form's
  // (now-stale) dirty state and popped a spurious "Discard unsaved work?"
  // modal even though the strategy had just been saved.
  let backBtn = rightCap.querySelector('.strategies-back-btn');
  if (!backBtn) {
    backBtn = document.createElement('button');
    backBtn.className = 'btn-link strategies-back-btn';
    backBtn.textContent = 'Back to list';
    rightCap.innerHTML = '';
    rightCap.appendChild(backBtn);
  }
  backBtn.onclick = (e) => {
    if (typeof exitHandler === 'function') {
      exitHandler(e);
    } else {
      navigateToSubView('list');
    }
  };
}

function removeBackButton() {
  const rightCap = document.getElementById('right-cap');
  const backBtn = rightCap && rightCap.querySelector('.strategies-back-btn');
  if (backBtn) backBtn.remove();
}

function deactivate() {
  // Hide the strategies section
  const strategiesSection = document.getElementById('section-strategies');
  if (strategiesSection) {
    strategiesSection.setAttribute('hidden', '');
  }

  // Clean up any modals
  dismissOpenDeleteConfirmModal();
  // Tear down the right-cap back button so it doesn't linger when the
  // user navigates to a different top-level section.
  removeBackButton();

  console.log('[strategies.js] Deactivated strategies section');
}

// ── Export Section Object ───────────────────────────────────────
window.strategiesSection = {
  activate,
  deactivate
};

// Expose handlers that inline onclick="..." attributes call. Without these,
// `<script type="module">` keeps the functions in module scope and clicks
// silently fail because window.<name> is undefined.
window.navigateStrategiesSubView = navigateToSubView;
window.loadStrategies = loadStrategies;
window.openStrategyEditor = openStrategyEditor;
window.openDeleteStrategyConfirm = openDeleteStrategyConfirm;
// closeDeleteStrategyModal / confirmDeleteStrategy removed 2026-04-25 — the
// shared modals.js helper wires its own event listeners; no inline onclick
// refs remain to need a window-global.

// Editor handlers
window.handleEditorExit = handleEditorExit;
window.handleEditorCancel = handleEditorCancel;
window.handleSave = handleSave;
window.handleSaveAs = handleSaveAs;
window.closeDiscardChangesModal = closeDiscardChangesModal;
window.confirmDiscardChanges = confirmDiscardChanges;
window.loadStrategyForEditor = loadStrategyForEditor;

// New sub-view handlers
window.handleNewExit = handleNewExit;
window.handleNewCancel = handleNewCancel;
window.switchNewMode = switchNewMode;
window.closeModeDiscardModal = closeModeDiscardModal;
window.confirmModeSwitch = confirmModeSwitch;
window.closeNewExitDiscardModal = closeNewExitDiscardModal;
window.confirmNewExit = confirmNewExit;
window.handleBlankSave = handleBlankSave;
window.handleLLMGenerate = handleLLMGenerate;
window.clearGenerationError = clearGenerationError;
window.handleLLMDiscard = handleLLMDiscard;
window.handleLLMRetry = handleLLMRetry;
window.handleLLMAccept = handleLLMAccept;
window.handleLLMProviderChange = handleLLMProviderChange;
window.handleLLMModelChange = handleLLMModelChange;
window.switchBlankLanguage = switchBlankLanguage;
window.switchLLMLanguage = switchLLMLanguage;

console.log('[strategies.js] Strategies section module loaded (Phase 3a)');