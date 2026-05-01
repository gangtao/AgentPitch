// Agent Pitch — Config Storage Tab Module
// Implements the Storage tab with data home path input, computed paths display, and disk stats
// Phase 3c scope: Storage tab implementation

// ── State ───────────────────────────────────────────────────────
let rootElement = null;
let savedValues = {};
let currentValues = {};
let isDirty = false;
let isValid = true;

// ── Validation ──────────────────────────────────────────────────
function validateDataHomePath(path) {
  if (!path.trim()) {
    return { valid: false, error: 'Required' };
  }

  // Check for .. in path (security risk)
  if (path.includes('..')) {
    return { valid: false, error: 'Path may not contain ".."' };
  }

  return { valid: true };
}

function validateAllFields() {
  const pathValidation = validateDataHomePath(currentValues.data_home || '');
  isValid = pathValidation.valid;
  _emitDirtyChangedEvent();
}

// ── DOM Rendering ───────────────────────────────────────────────
function renderStorageTab() {
  if (!rootElement) return;

  const dataHomePath = currentValues.data_home || '';
  const resolvedPath = _computeResolvedPath(dataHomePath);
  const subdirs = currentValues.subdirs || {};
  const freeBytes = currentValues.free_bytes || 0;

  rootElement.innerHTML = `
    <div class="storage-tab-form">
      <!-- Data Home Section (READ-ONLY) -->
      <section class="form-section" data-section="data_home">
        <div class="section-header">
          <span class="section-title">── DATA HOME ──</span>
        </div>
        <div class="form-field-row" data-field="data_home">
          <label class="field-label">DATA HOME PATH</label>
          <div class="readonly-value" id="field-data-home">${dataHomePath || '(not set)'}</div>
        </div>
        <div class="resolved-path-display">
          <span class="resolved-label">Resolved to:</span>
          <span class="resolved-value">${resolvedPath}</span>
        </div>
        <div class="readonly-hint">
          The data directory is fixed at server startup.
          To change it, restart with <code>agent-pitch serve --data-dir &lt;path&gt;</code>.
        </div>
      </section>

      <!-- Computed Paths Section -->
      <section class="form-section" data-section="computed_paths">
        <div class="section-header">
          <span class="section-title">── COMPUTED PATHS ──</span>
        </div>
        <div class="computed-paths-list">
          ${_renderComputedPaths(subdirs)}
        </div>
      </section>

      <!-- Disk Usage Section -->
      <section class="form-section" data-section="disk">
        <div class="section-header">
          <span class="section-title">── DISK ──</span>
        </div>
        <div class="disk-stats">
          <div class="disk-free-space">
            Free space: ${_formatBytes(freeBytes)} on volume
          </div>
        </div>
      </section>
    </div>
  `;

  // Storage tab is read-only as of 2026-04-24 — no input handlers to wire.
  // Tell config-shell the tab is never dirty so the global Save stays disabled.
  window.dispatchEvent(new CustomEvent('config:tabDirtyChanged', {
    detail: { tab: 'storage', dirty: false, valid: true }
  }));
}

function setupFormEventHandlers() {
  if (!rootElement) return;

  const dataHomeInput = rootElement.querySelector('#field-data-home');
  if (dataHomeInput) {
    let debounceTimer;

    dataHomeInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        handleDataHomeChange(dataHomeInput);
      }, 300); // 300ms debounce per UX spec
    });

    dataHomeInput.addEventListener('blur', () => {
      clearTimeout(debounceTimer);
      handleDataHomeChange(dataHomeInput);
    });
  }
}

function handleDataHomeChange(input) {
  const value = input.value;

  // Update current values
  currentValues.data_home = value;

  // Validate field
  const validation = validateDataHomePath(value);
  const errorElement = rootElement.querySelector('#error-data-home');

  if (!validation.valid) {
    input.classList.add('field-error-state');
    errorElement.textContent = `⚠ ${validation.error}`;
    errorElement.style.display = 'block';
  } else {
    input.classList.remove('field-error-state');
    errorElement.textContent = '';
    errorElement.style.display = 'none';
  }

  // Update resolved path display
  const resolvedElement = rootElement.querySelector('.resolved-value');
  if (resolvedElement) {
    resolvedElement.textContent = _computeResolvedPath(value);
  }

  // Update warning banner
  const warningBanner = _renderWarningBanner();
  const existingBanner = rootElement.querySelector('.path-warning-banner');
  if (existingBanner) {
    existingBanner.remove();
  }

  if (warningBanner.trim()) {
    const sectionElement = rootElement.querySelector('[data-section="data_home"]');
    if (sectionElement) {
      sectionElement.insertAdjacentHTML('beforeend', warningBanner);
    }
  }

  // Update dirty state
  _updateDirtyState();
  validateAllFields();
}

function _computeResolvedPath(path) {
  if (!path.trim()) return '';

  try {
    // Basic path resolution (client-side approximation)
    if (path.startsWith('~/')) {
      // Approximate home directory expansion
      return path.replace('~', '/Users/username'); // Placeholder for demo
    }

    if (path.startsWith('./') || path.startsWith('../')) {
      // Relative path - show as relative for now
      return `${window.location.pathname}${path}`;
    }

    // Absolute path
    return path;
  } catch (e) {
    return path;
  }
}

function _renderWarningBanner() {
  if (!isDirty) return '';

  return `
    <div class="path-warning-banner">
      <span class="warning-icon">⚠</span>
      <span class="warning-text">
        Changing the data home does not migrate existing data.
        Save will switch to the new path; existing data stays at the old path.
      </span>
    </div>
  `;
}

function _renderComputedPaths(subdirs) {
  const paths = [
    { path: 'matches/', label: 'matches/' },
    { path: 'strategies/', label: 'strategies/' },
    { path: 'configs/', label: 'configs/' },
    { path: 'arena/', label: 'arena/' },
    { path: 'cups/', label: 'cups/' },
    { path: 'leagues/', label: 'leagues/' },
    { path: 'global-defaults.yaml', label: 'global-defaults.yaml' },
    { path: 'llm-providers.yaml', label: 'llm-providers.yaml' },
    { path: '.secrets.json', label: '.secrets.json (hidden — gitignored)' }
  ];

  return paths.map(pathInfo => {
    const stats = subdirs[pathInfo.path] || { entries: 0, size_mb: 0.0 };
    const statsText = `${stats.entries} entries · ${stats.size_mb} MB`;

    return `
      <div class="computed-path-row" data-path="${pathInfo.path}">
        <span class="path-label">${pathInfo.label}</span>
        <span class="path-stats">${statsText}</span>
      </div>
    `;
  }).join('');
}

function _formatBytes(bytes) {
  if (bytes === 0) return '0 GB';

  const gb = bytes / (1024 * 1024 * 1024);
  if (gb >= 1) {
    return `${Math.round(gb)} GB`;
  }

  const mb = bytes / (1024 * 1024);
  if (mb >= 1) {
    return `${Math.round(mb)} MB`;
  }

  const kb = bytes / 1024;
  return `${Math.round(kb)} KB`;
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
  const savedPath = savedValues.data_home || '';
  const currentPath = currentValues.data_home || '';
  return savedPath !== currentPath;
}

function _emitDirtyChangedEvent() {
  window.dispatchEvent(new CustomEvent('config:tabDirtyChanged', {
    detail: {
      tab: 'storage',
      dirty: isDirty,
      valid: isValid
    }
  }));
}

// ── Public API ──────────────────────────────────────────────────
function mount(element, initialValues = {}) {
  rootElement = element;
  savedValues = {
    data_home: initialValues.data_home || '',
    subdirs: initialValues.subdirs || {},
    free_bytes: initialValues.free_bytes || 0
  };
  currentValues = {
    data_home: savedValues.data_home,
    subdirs: savedValues.subdirs,
    free_bytes: savedValues.free_bytes
  };

  isDirty = false;
  isValid = true;

  renderStorageTab();
  _emitDirtyChangedEvent();

  console.log('[config-storage] Mounted with values:', savedValues);
}

function unmount() {
  rootElement = null;
  savedValues = {};
  currentValues = {};
  isDirty = false;
  isValid = true;

  console.log('[config-storage] Unmounted');
}

function getDirty() {
  // Storage tab is read-only — never dirty.
  return false;
}

function getValues() {
  return {
    data_home: currentValues.data_home || ''
  };
}

function reset() {
  // Reset to factory default
  const defaultValues = {
    data_home: './data',
    subdirs: {},
    free_bytes: 0
  };

  currentValues = { ...defaultValues };

  // Update form
  if (rootElement) {
    const dataHomeInput = rootElement.querySelector('#field-data-home');
    if (dataHomeInput) {
      dataHomeInput.value = currentValues.data_home;
      dataHomeInput.classList.remove('field-error-state');
    }

    const errorElement = rootElement.querySelector('#error-data-home');
    if (errorElement) {
      errorElement.textContent = '';
      errorElement.style.display = 'none';
    }

    // Update resolved path display
    const resolvedElement = rootElement.querySelector('.resolved-value');
    if (resolvedElement) {
      resolvedElement.textContent = _computeResolvedPath(currentValues.data_home);
    }

    // Remove any warning banner
    const existingBanner = rootElement.querySelector('.path-warning-banner');
    if (existingBanner) {
      existingBanner.remove();
    }
  }

  _updateDirtyState();
  validateAllFields();

  console.log('[config-storage] Reset to defaults');
}

// ── Module Exports ──────────────────────────────────────────────
window.configStorageTab = {
  mount,
  unmount,
  getDirty,
  getValues,
  reset
};

console.log('[config-storage] Config Storage tab module loaded');