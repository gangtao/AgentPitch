// Agent Pitch — Config Match Tab Module
// Implements the Match tab with List / Editor / New sub-views
// Phase 3e scope: Match tab implementation

// ── State ───────────────────────────────────────────────────────
let rootElement = null;
let savedValues = {};
let currentSubView = 'list';  // 'list' | 'editor' | 'new'
let currentConfigName = null;  // For editor sub-view
let currentFormData = {};
// Set by setupEditorEventHandlers / setupNewEventHandlers; consumed by save()
// to dispatch to the right code path. null = New form (no name yet).
let currentEditingConfigName = null;

// ── Sub-view Management ─────────────────────────────────────────
function parseMatchSubRoute() {
  const hash = window.location.hash.slice(1); // Remove #
  const parts = hash.split('/').filter(p => p);

  // Expect format: /config/match or /config/match/name or /config/match/new
  if (parts.length >= 2 && parts[0] === 'config' && parts[1] === 'match') {
    if (parts.length === 2) {
      return { subView: 'list', name: null };
    } else if (parts[2] === 'new') {
      return { subView: 'new', name: null };
    } else {
      return { subView: 'editor', name: parts[2] };
    }
  }

  return { subView: 'list', name: null };
}

function navigateToSubView(subView, name = null) {
  const route = name
    ? `#/config/match/${name}`
    : `#/config/match${subView === 'new' ? '/new' : ''}`;

  window.location.hash = route;
  renderSubView(subView, name);
}

function renderSubView(subView, name = null) {
  currentSubView = subView;
  currentConfigName = name;

  if (!rootElement) return;

  if (subView === 'list') {
    removeBackButton();
    renderListSubView();
  } else if (subView === 'editor' && name) {
    addBackButton();
    renderEditorSubView(name);
  } else if (subView === 'new') {
    addBackButton();
    renderNewSubView();
  }
}

// ── Top-strip "Back to list" button ─────────────────────────────
// Mounts a `.btn-link` button into the App Shell's #right-cap when the user
// is in the editor / new sub-view. Mirrors the matches.js Replay back-button
// pattern so the back affordance lives in one consistent spot across the app
// (top-right of the header, not inline above the form).
function addBackButton() {
  const rightCap = document.getElementById('right-cap');
  if (!rightCap) return;
  if (rightCap.querySelector('.config-match-back-btn')) return;

  const backBtn = document.createElement('button');
  backBtn.className = 'btn-link config-match-back-btn';
  backBtn.textContent = 'Back to list';
  backBtn.onclick = () => navigateToSubView('list');

  rightCap.innerHTML = '';
  rightCap.appendChild(backBtn);
}

function removeBackButton() {
  const rightCap = document.getElementById('right-cap');
  const backBtn = rightCap && rightCap.querySelector('.config-match-back-btn');
  if (backBtn) backBtn.remove();
}

// ── List Sub-view ───────────────────────────────────────────────
async function renderListSubView() {
  if (!rootElement) return;

  try {
    const configs = await fetchMatchConfigs();

    const configRowsHTML = configs.map(config => {
      const summary = createSummaryString(config.summary);
      const lastModified = new Date(config.modified_iso).toLocaleDateString();

      return `
        <div class="list-row" data-config="${config.name}">
          <div class="list-row-content"
               role="button"
               tabindex="0"
               aria-label="Edit configuration ${config.name}"
               onclick="window.configMatchTab.openEditor('${config.name}')"
               onkeydown="if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); window.configMatchTab.openEditor('${config.name}'); }">
            <div class="list-row-line-1">${config.name}</div>
            <div class="list-row-line-2">${summary} · ${lastModified}</div>
          </div>
          <div class="list-row-actions">
            <button class="btn btn-sm config-edit-btn" data-config="${config.name}">Edit</button>
            <button class="btn btn-sm btn-danger config-delete-btn" data-config="${config.name}">Del</button>
          </div>
        </div>
      `;
    }).join('');

    const emptyStateHTML = configs.length === 0 ? `
      <div class="list-empty-state">
        <div class="empty-heading">no match configs yet</div>
        <div class="empty-subtext">create your first configuration to get started</div>
        <button class="btn btn-primary btn-lg" id="new-config-btn-empty">+ New config</button>
      </div>
    ` : '';

    rootElement.innerHTML = `
      <div class="match-list-view">
        <div class="list-action-bar">
          <button class="btn btn-primary new-config-btn" id="new-config-btn">+ New config</button>
          <div class="list-count">${configs.length} ${configs.length === 1 ? 'config' : 'configs'}</div>
        </div>

        <div class="list-body" id="config-list">
          ${configRowsHTML}
          ${emptyStateHTML}
        </div>
      </div>
    `;

    setupListEventHandlers();

  } catch (error) {
    console.error('[config-match] Failed to load match configs:', error);
    rootElement.innerHTML = `
      <div class="match-list-view">
        <div class="list-action-bar">
          <button class="btn btn-primary" disabled>+ New config</button>
          <div class="list-count">Error</div>
        </div>
        <div class="list-error">
          <div class="error-message">Failed to load match configurations</div>
          <button class="btn" onclick="window.configMatchTab.mount(this.closest('.config-tab-body'), {})">Retry</button>
        </div>
      </div>
    `;
  }
}

function setupListEventHandlers() {
  if (!rootElement) return;

  // "+ New config" buttons (action bar + empty state)
  ['#new-config-btn', '#new-config-btn-empty'].forEach(sel => {
    const btn = rootElement.querySelector(sel);
    if (btn) btn.addEventListener('click', () => navigateToSubView('new'));
  });

  // Edit buttons — also handle clicks on the row content (it has its own
  // inline onclick that calls window.configMatchTab.openEditor — see the
  // list-row-content markup above).
  rootElement.querySelectorAll('.config-edit-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      navigateToSubView('editor', btn.dataset.config);
    });
  });

  // Delete buttons
  rootElement.querySelectorAll('.config-delete-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      showDeleteConfirmModal(btn.dataset.config);
    });
  });
}

function createSummaryString(summary) {
  // Team-vs-team count: "11v11" (or asymmetric like "5v6"). Falls back to the
  // legacy players_per_team field for older API responses that lack player_count.
  const countA = summary.player_count?.team_a ?? summary.players_per_team ?? '?';
  const countB = summary.player_count?.team_b ?? summary.players_per_team ?? '?';
  const matchup = `${countA}v${countB}`;

  // Formations rendered with hyphens preserved, joined by "vs" so the team
  // boundary is unambiguous (avoids "2-1-1-2-1-1" which reads as one formation).
  const formA = summary.formation?.team_a || '?';
  const formB = summary.formation?.team_b || '?';
  const formations = `${formA} vs ${formB}`;

  return `${matchup} · ${formations} · ${summary.duration_min}min · ${summary.field_w}×${summary.field_h}`;
}

// ── Editor Sub-view ─────────────────────────────────────────────
async function renderEditorSubView(configName) {
  if (!rootElement) return;

  try {
    const config = await fetchMatchConfig(configName);
    // Drop simulation.* and output.* — UI doesn't show them (both are
    // runtime concerns supplied at match-start time). Keeping them in
    // currentFormData would dirty-mark the form on every render and ship
    // stale values back on save.
    const { simulation: _s, output: _o, ...clean } = config;
    currentFormData = clean;

    rootElement.innerHTML = `
      <div class="match-editor-view">
        <div class="editor-header">
          <h2 class="config-title">
            ${configName}
            <a href="#" class="save-as-link" id="save-as-link" title="Save under a different name">save as…</a>
          </h2>
        </div>

        <div class="editor-form" id="editor-form">
          ${renderConfigForm(config)}
        </div>
      </div>
    `;

    setupEditorEventHandlers(configName);

  } catch (error) {
    console.error('[config-match] Failed to load config for editing:', error);
    rootElement.innerHTML = `
      <div class="match-editor-view">
        <div class="editor-header">
          <h2 class="config-title">${configName}</h2>
        </div>
        <div class="error-message">
          <p>Failed to load configuration.</p>
          <a href="#/config/match" class="btn">Back to list</a>
        </div>
      </div>
    `;
  }
}

function setupEditorEventHandlers(configName) {
  if (!rootElement) return;

  // Save / Discard / Cancel are handled by the GLOBAL action row + breadcrumb
  // (config-shell.js calls window.configMatchTab.save() on the global Save).
  // Save-as remains a per-config action — exposed inline next to the title.
  const saveAsLink = rootElement.querySelector('#save-as-link');
  if (saveAsLink) {
    saveAsLink.addEventListener('click', (e) => {
      e.preventDefault();
      showSaveAsModal(currentFormData);
    });
  }

  // Track the currently-edited config name so save() / discard() know what to act on
  currentEditingConfigName = configName;

  setupFormEventHandlers();

  // Tell the global action row this tab is now editable (Save enabled).
  _emitDirtyState();
}

// ── New Sub-view ────────────────────────────────────────────────
function renderNewSubView() {
  if (!rootElement) return;

  // Pre-fill with sensible defaults
  const defaultConfig = createDefaultConfig();
  currentFormData = { ...defaultConfig };

  rootElement.innerHTML = `
    <div class="match-new-view">
      <div class="editor-header">
        <h2 class="config-title">New Configuration</h2>
      </div>

      <div class="config-name-section">
        <label class="field-label" for="config-name-input">CONFIGURATION NAME</label>
        <input
          type="text"
          id="config-name-input"
          class="ipt"
          placeholder="match_config_name"
          pattern="[A-Za-z0-9_-]{1,64}"
          maxlength="64"
          spellcheck="false"
          autocapitalize="none"
          autocorrect="off"
        />
        <div class="field-error" id="name-error"></div>
      </div>

      <div class="editor-form" id="editor-form">
        ${renderConfigForm(defaultConfig)}
      </div>
    </div>
  `;

  // Mark this as a "New" form (no existing config name yet)
  currentEditingConfigName = null;

  setupNewEventHandlers();
}

function setupNewEventHandlers() {
  if (!rootElement) return;

  // Save / Cancel are handled by the GLOBAL action row + breadcrumb
  // (config-shell.js calls window.configMatchTab.save() on the global Save).
  // Validate name input as the user types so the global Save can know whether
  // this New form is submittable; emit config:tabDirtyChanged to gate the button.
  const nameInput = rootElement.querySelector('#config-name-input');
  if (nameInput) {
    nameInput.addEventListener('input', () => {
      validateNameInput(nameInput);
      _emitDirtyState();
    });
  }

  setupFormEventHandlers();

  // New form is "dirty + invalid" until a valid name is entered, so the global
  // Save button stays disabled.
  _emitDirtyState();
}

function validateNameInput(input) {
  const value = input.value.trim();
  const isValid = validateConfigName(value);

  const errorElement = rootElement.querySelector('#name-error');

  if (!isValid && value) {
    input.classList.add('field-error-state');
    errorElement.textContent = '⚠ Use letters, numbers, hyphens, underscores only (1-64 chars)';
    errorElement.style.display = 'block';
  } else {
    input.classList.remove('field-error-state');
    errorElement.textContent = '';
    errorElement.style.display = 'none';
  }
}

function validateConfigName(name) {
  return /^[A-Za-z0-9_-]{1,64}$/.test(name);
}

// ── Form Rendering ──────────────────────────────────────────────
function renderConfigForm(config) {
  return `
    <div class="config-form">
      <!-- Simple form fields stay in the narrow 720px column for legibility. -->
      <div class="match-form-column">
        <section class="form-section">
          <h3 class="section-title">── MATCH PARAMETERS ──</h3>
          <div class="form-grid">
            <div class="form-field">
              <label class="field-label" for="seed">SEED</label>
              <input type="number" id="seed" class="ipt ipt-num" value="${config.match.seed}" min="0" max="2147483647" step="1" data-field="match.seed" />
            </div>
            <div class="form-field">
              <label class="field-label" for="tick-rate">TICK RATE</label>
              <input type="number" id="tick-rate" class="ipt ipt-num" value="${config.match.tick_rate}" min="1" max="60" step="1" data-field="match.tick_rate" />
              <span class="unit-label">ticks/sec</span>
            </div>
            <div class="form-field">
              <label class="field-label" for="duration">DURATION</label>
              <input type="number" id="duration" class="ipt ipt-num" value="${config.match.duration_minutes}" min="1" max="60" step="1" data-field="match.duration_minutes" />
              <span class="unit-label">minutes</span>
            </div>
            <div class="form-field">
              <label class="field-label" for="field-width">FIELD WIDTH</label>
              <input type="number" id="field-width" class="ipt ipt-num" value="${config.match.field_width}" min="50" max="200" step="0.1" data-field="match.field_width" />
              <span class="unit-label">units</span>
            </div>
            <div class="form-field">
              <label class="field-label" for="field-height">FIELD HEIGHT</label>
              <input type="number" id="field-height" class="ipt ipt-num" value="${config.match.field_height}" min="30" max="120" step="0.1" data-field="match.field_height" />
              <span class="unit-label">units</span>
            </div>
            <!-- match_id is per-run, supplied at match-start time (Matches'
                 Start sub-view), not stored in saved configs. -->
          </div>
        </section>

        <!-- Simulation parameters intentionally omitted: they always come from
             the global Game tab (Config → Game) at match-start time. The CLI
             overlays them onto MatchConfig at match-start so saved match
             configs no longer carry their own copy. -->
      </div>

      <!-- Team rosters break out of the 720px column — wide data tables
           with all 9 player attributes need full available width. -->
      ${renderTeamSection('team_a', 'A. Team A', config.team_a)}
      ${renderTeamSection('team_b', 'B. Team B', config.team_b)}
    </div>
  `;
}

// Roster editor — uses the design-system .tbl pattern (Data Display A. Table).
// Each row is one player; the Role <select> drives whether the REACH cell is
// editable (GK only) or shows an em-dash. Mirrors PlayerPayload's full schema:
// every editable attribute (speed, skill, strength, dribbling, passing,
// shooting, stamina, discipline, save) gets a column. Optional fields
// (passing, shooting) default to 10 in the form so users always see a value
// they can edit; on save Pydantic preserves whatever's set.
function renderTeamSection(teamKey, teamLabel, teamData) {
  const ROLES = ['GK', 'DEF', 'MID', 'FWD'];

  // <attr key>, <header>, <whether GK-only or fully optional>.
  // Order matches the rendering order; non-GK rows render "—" for save.
  const ATTR_COLS = [
    { key: 'speed',      header: 'SPD' },
    { key: 'skill',      header: 'SKL' },
    { key: 'strength',   header: 'STR' },
    { key: 'dribbling',  header: 'DRB' },
    { key: 'passing',    header: 'PAS' },
    { key: 'shooting',   header: 'SHO' },
    { key: 'stamina',    header: 'STA' },
    { key: 'discipline', header: 'DSC' },
  ];

  const numCell = (player, fieldPath, attr) => {
    // Optional fields (passing, shooting) come back as null when unset.
    // Show 10 as a starting point so the cell is always editable; the
    // user-edited value lands in currentFormData via existing handleFieldChange.
    const val = player[attr] != null ? player[attr] : 10;
    return `<td class="num"><input type="number" class="ipt ipt-num ipt-cell" value="${val}" min="1" max="20" step="1" data-field="${fieldPath(attr)}" /></td>`;
  };

  const playersHTML = teamData.players.map((player, index) => {
    const fieldPath = (attr) => `${teamKey}.players.${index}.${attr}`;
    const reachCell = player.role === 'GK'
      ? `<input type="number" class="ipt ipt-num ipt-cell" value="${player.save ?? 16}" min="0" max="20" step="1" data-field="${fieldPath('save')}" />`
      : `<span class="dimer">—</span>`;
    const attrCellsHTML = ATTR_COLS.map(c => numCell(player, fieldPath, c.key)).join('');
    return `
      <tr data-team="${teamKey}" data-index="${index}">
        <td>
          <select class="sel sel-cell role-select" data-field="${fieldPath('role')}">
            ${ROLES.map(r => `<option value="${r}" ${player.role === r ? 'selected' : ''}>${r}</option>`).join('')}
          </select>
        </td>
        ${attrCellsHTML}
        <td class="num">${reachCell}</td>
        <td class="cell-action">
          <button class="btn btn-icon btn-ghost remove-player-btn"
                  data-team="${teamKey}" data-index="${index}"
                  aria-label="Remove player ${index + 1}">×</button>
        </td>
      </tr>
    `;
  }).join('');

  const headerCellsHTML = ATTR_COLS.map(c => `<th class="num">${c.header}</th>`).join('');

  return `
    <section class="form-section team-section" data-team="${teamKey}">
      <div class="ap-section" style="margin-top:32px;margin-bottom:14px">
        <span>${teamLabel}</span><span class="rule"></span>
        <span class="dimer" style="font-size:11px">${teamData.players.length} players</span>
      </div>
      <div class="ap-panel" style="padding:0">
        <table class="tbl">
          <thead>
            <tr>
              <th style="width:90px">Role</th>
              ${headerCellsHTML}
              <th class="num">SAV</th>
              <th style="width:50px"></th>
            </tr>
          </thead>
          <tbody>
            ${playersHTML}
          </tbody>
        </table>
        <div class="tbl-footer">
          <button class="btn btn-sm add-player-btn" data-team="${teamKey}">+ Add player</button>
        </div>
      </div>
    </section>
  `;
}

function createDefaultConfig() {
  return {
    match: {
      seed: 42,
      tick_rate: 10,
      duration_minutes: 5,
      field_width: 100.0,
      field_height: 60.0,
      // match_id intentionally absent — supplied at match-start time
    },
    // simulation.* and output.* intentionally omitted — both are runtime
    // concerns supplied at match-start time:
    //   simulation → overlaid from global Game tab via --global-defaults
    //   output     → overridden by --log-dir (API always passes it)
    // The PUT handler auto-fills output with a sensible default so the
    // saved YAML stays loadable by the engine.
    team_a: {
      players: [
        { role: "GK", speed: 8, skill: 10, strength: 8, save: 16 },
        { role: "DEF", speed: 12, skill: 12, strength: 14 },
        { role: "DEF", speed: 12, skill: 12, strength: 14 },
        { role: "MID", speed: 14, skill: 14, strength: 12 },
        { role: "FWD", speed: 16, skill: 8, strength: 10 }
      ]
    },
    team_b: {
      players: [
        { role: "GK", speed: 8, skill: 10, strength: 8, save: 16 },
        { role: "DEF", speed: 12, skill: 12, strength: 14 },
        { role: "DEF", speed: 12, skill: 12, strength: 14 },
        { role: "MID", speed: 14, skill: 14, strength: 12 },
        { role: "FWD", speed: 16, skill: 8, strength: 10 }
      ]
    }
  };
}

function setupFormEventHandlers() {
  if (!rootElement) return;

  // Field change handlers
  rootElement.querySelectorAll('.field-input').forEach(input => {
    input.addEventListener('input', () => {
      handleFieldChange(input);
    });
  });

  // Add player buttons
  rootElement.querySelectorAll('.add-player-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const team = btn.dataset.team;
      addPlayer(team);
    });
  });

  // Remove player buttons
  rootElement.querySelectorAll('.remove-player-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const team = btn.dataset.team;
      const index = parseInt(btn.dataset.index);
      removePlayer(team, index);
    });
  });
}

function handleFieldChange(input) {
  const fieldPath = input.dataset.field;
  const value = input.type === 'number' ? parseFloat(input.value) || 0 : input.value;

  setNestedValue(currentFormData, fieldPath, value);
}

function setNestedValue(obj, path, value) {
  const keys = path.split('.');
  let current = obj;

  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i];
    if (!(key in current)) {
      current[key] = {};
    }
    current = current[key];
  }

  current[keys[keys.length - 1]] = value;
}

function addPlayer(teamKey) {
  const newPlayer = {
    role: "DEF",
    speed: 10,
    skill: 10,
    strength: 10
  };

  if (!currentFormData[teamKey]) {
    currentFormData[teamKey] = { players: [] };
  }

  currentFormData[teamKey].players.push(newPlayer);

  // Re-render the form
  const form = rootElement.querySelector('#editor-form');
  if (form) {
    form.innerHTML = renderConfigForm(currentFormData);
    setupFormEventHandlers();
  }
}

function removePlayer(teamKey, index) {
  if (currentFormData[teamKey] && currentFormData[teamKey].players) {
    currentFormData[teamKey].players.splice(index, 1);

    // Re-render the form
    const form = rootElement.querySelector('#editor-form');
    if (form) {
      form.innerHTML = renderConfigForm(currentFormData);
      setupFormEventHandlers();
    }
  }
}

// ── API Functions ───────────────────────────────────────────────
async function fetchMatchConfigs() {
  try {
    const apiBase = window.shell ? window.shell.getApiBase() : `${window.location.protocol}//${window.location.host}`;
    const response = await fetch(`${apiBase}/api/config/match`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('[config-match] Failed to fetch match configs:', error);
    throw error;
  }
}

async function fetchMatchConfig(name) {
  try {
    const apiBase = window.shell ? window.shell.getApiBase() : `${window.location.protocol}//${window.location.host}`;
    const response = await fetch(`${apiBase}/api/config/match/${encodeURIComponent(name)}`);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error(`Configuration '${name}' not found`);
      }
      throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('[config-match] Failed to fetch match config:', error);
    throw error;
  }
}

async function saveConfig(name, data) {
  try {
    const apiBase = window.shell ? window.shell.getApiBase() : `${window.location.protocol}//${window.location.host}`;
    const response = await fetch(`${apiBase}/api/config/match/${encodeURIComponent(name)}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP ${response.status}`);
    }

    const result = await response.json();

    // Fire event
    window.dispatchEvent(new CustomEvent('config:matchConfigSaved', {
      detail: { name, source: 'editor' }
    }));

    // Navigate back to list
    navigateToSubView('list');

  } catch (error) {
    console.error('[config-match] Failed to save config:', error);
    alert(`Failed to save configuration: ${error.message}`);
  }
}

async function saveNewConfig(name, data) {
  try {
    const apiBase = window.shell ? window.shell.getApiBase() : `${window.location.protocol}//${window.location.host}`;
    const response = await fetch(`${apiBase}/api/config/match/${encodeURIComponent(name)}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP ${response.status}`);
    }

    const result = await response.json();

    // Fire event
    window.dispatchEvent(new CustomEvent('config:matchConfigSaved', {
      detail: { name, source: 'new' }
    }));

    // Navigate to editor for the new config
    navigateToSubView('editor', name);

  } catch (error) {
    console.error('[config-match] Failed to save new config:', error);
    alert(`Failed to create configuration: ${error.message}`);
  }
}

async function deleteConfig(name) {
  try {
    const apiBase = window.shell ? window.shell.getApiBase() : `${window.location.protocol}//${window.location.host}`;
    const response = await fetch(`${apiBase}/api/config/match/${encodeURIComponent(name)}`, {
      method: 'DELETE'
    });

    if (!response.ok && response.status !== 204) {
      throw new Error(`HTTP ${response.status}`);
    }

    // Fire event
    window.dispatchEvent(new CustomEvent('config:matchConfigDeleted', {
      detail: { name }
    }));

    // Refresh list view
    if (currentSubView === 'list') {
      renderListSubView();
    }

  } catch (error) {
    console.error('[config-match] Failed to delete config:', error);
    alert(`Failed to delete configuration: ${error.message}`);
  }
}

// ── Modal Handlers ──────────────────────────────────────────────
function showDeleteConfirmModal(configName) {
  const modal = document.createElement('dialog');
  modal.className = 'confirm-modal delete-confirm-modal';
  modal.innerHTML = `
    <div class="modal-content">
      <h3 class="modal-title">Delete match configuration "${configName}"?</h3>
      <p class="modal-body">Type the configuration name to confirm deletion:</p>
      <input type="text" id="confirm-name-input" class="ipt" placeholder="${configName}" />
      <div class="field-error" id="confirm-error"></div>
      <div class="modal-actions">
        <button class="btn" id="modal-cancel-btn">Cancel</button>
        <button class="btn btn-danger" id="modal-delete-btn" disabled>Delete</button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  const cancelBtn = modal.querySelector('#modal-cancel-btn');
  const deleteBtn = modal.querySelector('#modal-delete-btn');
  const nameInput = modal.querySelector('#confirm-name-input');
  const errorElement = modal.querySelector('#confirm-error');

  // Validate name input
  nameInput.addEventListener('input', () => {
    const isValid = nameInput.value.trim() === configName;
    deleteBtn.disabled = !isValid;

    if (nameInput.value.trim() && !isValid) {
      errorElement.textContent = '⚠ Name must match exactly';
      errorElement.style.display = 'block';
    } else {
      errorElement.textContent = '';
      errorElement.style.display = 'none';
    }
  });

  cancelBtn.addEventListener('click', () => {
    modal.close();
    modal.remove();
  });

  deleteBtn.addEventListener('click', () => {
    deleteConfig(configName);
    modal.close();
    modal.remove();
  });

  modal.addEventListener('close', () => {
    modal.remove();
  });

  nameInput.focus();
  modal.showModal();
}

function showSaveAsModal(configData) {
  const modal = document.createElement('dialog');
  modal.className = 'confirm-modal save-as-modal';
  modal.innerHTML = `
    <div class="modal-content">
      <h3 class="modal-title">Save configuration as…</h3>
      <label class="field-label" for="save-as-name-input">CONFIGURATION NAME</label>
      <input type="text" id="save-as-name-input" class="ipt" placeholder="new_config_name" pattern="[A-Za-z0-9_-]{1,64}" maxlength="64" />
      <div class="field-error" id="save-as-error"></div>
      <div class="modal-actions">
        <button class="btn" id="modal-cancel-btn">Cancel</button>
        <button class="btn btn-primary" id="modal-save-btn" disabled>Save</button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  const cancelBtn = modal.querySelector('#modal-cancel-btn');
  const saveBtn = modal.querySelector('#modal-save-btn');
  const nameInput = modal.querySelector('#save-as-name-input');
  const errorElement = modal.querySelector('#save-as-error');

  nameInput.addEventListener('input', () => {
    const value = nameInput.value.trim();
    const isValid = validateConfigName(value);

    saveBtn.disabled = !isValid || !value;

    if (value && !isValid) {
      errorElement.textContent = '⚠ Use letters, numbers, hyphens, underscores only (1-64 chars)';
      errorElement.style.display = 'block';
    } else {
      errorElement.textContent = '';
      errorElement.style.display = 'none';
    }
  });

  cancelBtn.addEventListener('click', () => {
    modal.close();
    modal.remove();
  });

  saveBtn.addEventListener('click', () => {
    const newName = nameInput.value.trim();
    if (newName && validateConfigName(newName)) {
      saveNewConfig(newName, configData);
      modal.close();
      modal.remove();
    }
  });

  modal.addEventListener('close', () => {
    modal.remove();
  });

  nameInput.focus();
  modal.showModal();
}

// ── Public API ──────────────────────────────────────────────────
function mount(element, initialValues = {}) {
  rootElement = element;
  savedValues = { ...initialValues };

  // Parse current route to determine sub-view
  const route = parseMatchSubRoute();
  renderSubView(route.subView, route.name);

  // Listen for hash changes within match tab
  window.addEventListener('hashchange', () => {
    const newRoute = parseMatchSubRoute();
    if (newRoute.subView !== currentSubView || newRoute.name !== currentConfigName) {
      renderSubView(newRoute.subView, newRoute.name);
    }
  });

  console.log('[config-match] Mounted with sub-view:', route.subView, route.name);
}

function unmount() {
  // Tear down the right-cap back button — it's parented to the App Shell,
  // so without an explicit cleanup it would linger when the user switches
  // to a different config tab (LLM / Storage / Game) or section entirely.
  removeBackButton();

  rootElement = null;
  savedValues = {};
  currentFormData = {};
  currentSubView = 'list';
  currentConfigName = null;

  console.log('[config-match] Unmounted');
}

function getDirty() {
  // Editor / New sub-views are always considered dirty enough to enable Save
  // (the user wants to commit edits or create a new file). List has nothing to save.
  return currentSubView === 'editor' || currentSubView === 'new';
}

function getValues() {
  return currentFormData;
}

function reset() {
  // Reset to defaults works only on Editor / New (List has nothing to reset).
  if (currentSubView === 'editor' || currentSubView === 'new') {
    const defaults = createDefaultConfig();
    currentFormData = { ...defaults };
    // Re-render the form section with default values
    const formContainer = rootElement?.querySelector('#editor-form');
    if (formContainer) {
      formContainer.innerHTML = renderConfigForm(defaults);
      setupFormEventHandlers();
    }
    _emitDirtyState();
  }
}

// ── Save (called by global action row via window.configMatchTab.save()) ────
async function save() {
  if (currentSubView === 'editor' && currentEditingConfigName) {
    await saveConfig(currentEditingConfigName, currentFormData);
  } else if (currentSubView === 'new') {
    const nameInput = rootElement?.querySelector('#config-name-input');
    const configName = nameInput?.value?.trim();
    if (configName && validateConfigName(configName)) {
      await saveNewConfig(configName, currentFormData);
    } else {
      console.warn('[config-match] Cannot save New form: invalid name');
    }
  }
}

// ── Discard (called by global action row via window.configMatchTab.discard())
function discard() {
  // Re-mount the current sub-view to revert to last-saved values
  if (currentSubView === 'editor' && currentEditingConfigName) {
    renderEditorSubView(currentEditingConfigName);
  } else if (currentSubView === 'new') {
    renderNewSubView();
  }
}

// ── Dirty-state emission for global action row ─────────────────
function _emitDirtyState() {
  // For Match tab the global action row needs:
  //   - Save enabled when sub-view is editor (always) OR
  //     New with a valid name typed
  //   - Discard always enabled when on editor/new (allows revert to saved)
  const onEditOrNew = currentSubView === 'editor' || currentSubView === 'new';
  let valid = false;
  if (currentSubView === 'editor') {
    valid = true;
  } else if (currentSubView === 'new') {
    const nameInput = rootElement?.querySelector('#config-name-input');
    const name = nameInput?.value?.trim() || '';
    valid = validateConfigName(name);
  }
  window.dispatchEvent(new CustomEvent('config:tabDirtyChanged', {
    detail: { tab: 'match', dirty: onEditOrNew, valid }
  }));
}

// ── Module Exports ──────────────────────────────────────────────
window.configMatchTab = {
  mount,
  unmount,
  getDirty,
  getValues,
  reset,
  save,
  discard,
  // Used by the list view's row-content inline onclick / onkeydown handlers
  // (clicking the row body opens the editor; clicking Edit/Del buttons
  // stops propagation so the row click doesn't double-fire).
  openEditor: (name) => navigateToSubView('editor', name),
};

console.log('[config-match] Config Match tab module loaded');