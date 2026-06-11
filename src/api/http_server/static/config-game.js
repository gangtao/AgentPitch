// Agent Pitch — Config Game Tab Module
// Implements the Game tab form with 5 sections and ~25 fields
// Phase 3b scope: Game tab implementation

// ── State ───────────────────────────────────────────────────────
let rootElement = null;
let savedValues = {};
let currentValues = {};
let isDirty = false;
let isValid = true;

// Field definitions with validation constraints (mirroring GameConfig Pydantic model)
const GAME_FIELDS = {
  // ── A. Match defaults ──
  match_defaults: {
    title: '── A. MATCH DEFAULTS ──',
    fields: [
      { key: 'tick_rate', label: 'TICK RATE', min: 1, max: 60, unit: 'ticks per second' },
      { key: 'duration_minutes', label: 'DURATION', min: 1, max: 120, unit: 'minutes' },
      { key: 'field_width', label: 'FIELD WIDTH', min: 0.1, max: 200, unit: 'units' },
      { key: 'field_height', label: 'FIELD HEIGHT', min: 0.1, max: 120, unit: 'units' },
      { key: 'goal_height', label: 'GOAL HEIGHT', min: 0.1, max: 12, unit: 'units' },
      { key: 'default_seed', label: 'DEFAULT SEED', min: -2147483648, max: 2147483647, unit: 'integer' }
    ]
  },

  // ── B. Action mechanics ──
  action_mechanics: {
    title: '── B. ACTION MECHANICS ──',
    fields: [
      { key: 'action_cooldown_ticks', label: 'ACTION COOLDOWN', min: 0, max: 100, unit: 'ticks' },
      { key: 'pass_max_deviation', label: 'PASS MAX DEVIATION', min: 0, max: 30, unit: 'units' },
      { key: 'shot_max_angle', label: 'SHOT MAX ANGLE', min: 0, max: 1, step: 0.01, unit: 'radians' },
      { key: 'tackle_clean_share', label: 'TACKLE CLEAN SHARE', min: 0, max: 1, step: 0.01, unit: 'fraction' },
      { key: 'tackle_blocked_floor', label: 'TACKLE BLOCKED FLOOR', min: 0, max: 1, step: 0.01, unit: 'fraction' },
      { key: 'tackle_block_speed_min', label: 'TACKLE BLOCK SPEED MIN', min: 0, max: 10, unit: 'u/tick' },
      { key: 'tackle_block_speed_max', label: 'TACKLE BLOCK SPEED MAX', min: 0, max: 10, unit: 'u/tick' },
      { key: 'tackle_range', label: 'TACKLE RANGE', min: 0, max: 10, unit: 'units' },
      { key: 'tackle_settle_grace_ticks', label: 'TACKLE SETTLE GRACE', min: 0, max: 30, unit: 'ticks' }
    ]
  },

  // ── C. Goalkeeper / ball physics ──
  gk_ball_physics: {
    title: '── C. GOALKEEPER / BALL PHYSICS ──',
    fields: [
      { key: 'gk_caught_share', label: 'GK CAUGHT SHARE', min: 0, max: 1, step: 0.01, unit: 'fraction' },
      { key: 'gk_block_speed_factor', label: 'GK BLOCK SPEED FACTOR', min: 0, max: 1, step: 0.01, unit: 'fraction' },
      { key: 'ball_control_range_gk', label: 'BALL CONTROL RANGE GK', min: 0, max: 5, unit: 'units' },
      { key: 'ball_control_range_outfield', label: 'BALL CONTROL RANGE OUTFIELD', min: 0, max: 5, unit: 'units' },
      { key: 'shot_deflection_min_speed', label: 'SHOT DEFLECTION MIN SPEED', min: 0, max: 10, unit: 'u/tick' },
      { key: 'shot_deflection_speed_factor_min', label: 'SHOT DEFLECTION FACTOR MIN', min: 0, max: 1, step: 0.01, unit: 'fraction' },
      { key: 'shot_deflection_speed_factor_max', label: 'SHOT DEFLECTION FACTOR MAX', min: 0, max: 1, step: 0.01, unit: 'fraction' }
    ]
  },

  // ── D. Stamina / health ──
  stamina_health: {
    title: '── D. STAMINA / HEALTH ──',
    fields: [
      { key: 'health_max', label: 'HEALTH MAX', min: 0.1, max: 1000, unit: 'health points' },
      { key: 'health_drain_factor', label: 'HEALTH DRAIN FACTOR', min: 0, max: 10, unit: 'multiplier' },
      { key: 'health_floor', label: 'HEALTH FLOOR', min: 0, max: 1, step: 0.01, unit: 'fraction' }
    ]
  },

  // ── E. Match-flow timing ──
  match_flow_timing: {
    title: '── E. MATCH-FLOW TIMING ──',
    fields: [
      { key: 'goal_reset_ticks', label: 'GOAL RESET TICKS', min: 0, max: 300, unit: 'ticks' },
      { key: 'half_time_pause_ticks', label: 'HALF TIME PAUSE TICKS', min: 0, max: 300, unit: 'ticks' },
      { key: 'min_player_separation', label: 'MIN PLAYER SEPARATION', min: 0, max: 5, unit: 'units' }
    ]
  },

  // ── F. Formation system (ADR-0022 amendment d) ──
  formation_system: {
    title: '── F. FORMATION SYSTEM ──',
    fields: [
      {
        key: 'formation_snap_enabled',
        label: 'FORMATION SNAP ENABLED',
        type: 'checkbox',
        unit: 'when off, strategy fully owns positioning'
      }
    ]
  },

  // ── G. Match rules (issue #31) ──
  match_rules: {
    title: '── G. MATCH RULES ──',
    fields: [
      {
        key: 'offside_enabled',
        label: 'OFFSIDE ENABLED',
        type: 'checkbox',
        unit: 'IFAB Law 11 — free kick when an offside player controls a pass'
      }
    ]
  }
};

// ── Validation ──────────────────────────────────────────────────
function validateField(key, value) {
  const field = _findFieldByKey(key);
  if (!field) return { valid: true };

  // Boolean / checkbox fields — always valid (browser provides the value).
  if (field.type === 'checkbox') return { valid: true };

  const num = parseFloat(value);
  if (isNaN(num)) {
    return { valid: false, error: 'Must be a number' };
  }

  if (num < field.min) {
    return { valid: false, error: `Must be ${field.min}-${field.max}` };
  }

  if (num > field.max) {
    return { valid: false, error: `Must be ${field.min}-${field.max}` };
  }

  return { valid: true };
}

function _findFieldByKey(key) {
  for (const section of Object.values(GAME_FIELDS)) {
    const field = section.fields.find(f => f.key === key);
    if (field) return field;
  }
  return null;
}

function validateAllFields() {
  let allValid = true;
  for (const [key, value] of Object.entries(currentValues)) {
    const validation = validateField(key, value);
    if (!validation.valid) {
      allValid = false;
      break;
    }
  }
  isValid = allValid;
  _emitDirtyChangedEvent();
}

// ── DOM Rendering ───────────────────────────────────────────────
function renderGameTab() {
  if (!rootElement) return;

  const sectionsHTML = Object.entries(GAME_FIELDS).map(([sectionKey, section]) => {
    const fieldsHTML = section.fields.map(field => {
      // Checkbox / boolean field
      if (field.type === 'checkbox') {
        const checked = !!currentValues[field.key];
        return `
          <div class="form-field-row" data-field="${field.key}">
            <label class="field-label" for="field-${field.key}">${field.label}</label>
            <input
              type="checkbox"
              id="field-${field.key}"
              class="ipt ipt-check"
              ${checked ? 'checked' : ''}
              data-field="${field.key}"
            />
            <span class="unit-label">${field.unit || ''}</span>
            <div class="field-error" id="error-${field.key}"></div>
          </div>
        `;
      }
      // Numeric field (default)
      const value = currentValues[field.key] || '';
      const inputStep = field.step || (field.key === 'default_seed' ? '1' : '0.1');

      return `
        <div class="form-field-row" data-field="${field.key}">
          <label class="field-label" for="field-${field.key}">${field.label}</label>
          <input
            type="number"
            id="field-${field.key}"
            class="ipt ipt-num"
            value="${value}"
            min="${field.min}"
            max="${field.max}"
            step="${inputStep}"
            data-field="${field.key}"
          />
          <span class="unit-label">${field.unit}</span>
          <div class="field-error" id="error-${field.key}"></div>
        </div>
      `;
    }).join('');

    return `
      <section class="form-section" data-section="${sectionKey}">
        <div class="section-header">
          <span class="section-title">${section.title}</span>
          <button type="button" class="btn-link section-reset-link" data-section="${sectionKey}">Reset section</button>
        </div>
        ${fieldsHTML}
      </section>
    `;
  }).join('');

  rootElement.innerHTML = `
    <div class="game-tab-form">
      ${sectionsHTML}
    </div>
  `;

  // Wire up event handlers
  setupFormEventHandlers();
}

function setupFormEventHandlers() {
  if (!rootElement) return;

  // Number-input field handlers (debounced for typing)
  rootElement.querySelectorAll('.ipt-num').forEach(input => {
    let debounceTimer;

    input.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        handleFieldChange(input);
      }, 300); // 300ms debounce per UX spec
    });

    input.addEventListener('blur', () => {
      clearTimeout(debounceTimer);
      handleFieldChange(input);
    });
  });

  // Checkbox handlers — fire on every change (no debounce needed)
  rootElement.querySelectorAll('.ipt-check').forEach(input => {
    input.addEventListener('change', () => {
      handleFieldChange(input);
    });
  });

  // Section reset handlers
  rootElement.querySelectorAll('.section-reset-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const sectionKey = link.dataset.section;
      resetSection(sectionKey);
    });
  });
}

function handleFieldChange(input) {
  const fieldKey = input.dataset.field;
  // Read boolean value for checkboxes; string value for number inputs
  const value = input.type === 'checkbox' ? input.checked : input.value;

  // Update current values
  currentValues[fieldKey] = value;

  // Validate field
  const validation = validateField(fieldKey, value);
  const errorElement = rootElement.querySelector(`#error-${fieldKey}`);

  if (!validation.valid) {
    input.classList.add('field-error-state');
    input.setAttribute('aria-invalid', 'true');
    input.setAttribute('aria-describedby', `error-${fieldKey}`);
    errorElement.textContent = `⚠ ${validation.error}`;
    errorElement.style.display = 'block';
    errorElement.setAttribute('role', 'status');
  } else {
    input.classList.remove('field-error-state');
    input.removeAttribute('aria-invalid');
    input.removeAttribute('aria-describedby');
    errorElement.textContent = '';
    errorElement.style.display = 'none';
  }

  // Update dirty state
  _updateDirtyState();
  validateAllFields();
}

function resetSection(sectionKey) {
  const section = GAME_FIELDS[sectionKey];
  if (!section) return;

  // Reset fields in this section to their default values
  section.fields.forEach(field => {
    const defaultValue = _getDefaultValue(field.key);
    currentValues[field.key] = defaultValue;

    // Update input element (checkbox vs number)
    const input = rootElement.querySelector(`#field-${field.key}`);
    if (input) {
      if (input.type === 'checkbox') {
        input.checked = !!defaultValue;
      } else {
        input.value = defaultValue;
      }
      input.classList.remove('field-error-state');
    }

    // Clear error
    const errorElement = rootElement.querySelector(`#error-${field.key}`);
    if (errorElement) {
      errorElement.textContent = '';
      errorElement.style.display = 'none';
    }
  });

  _updateDirtyState();
  validateAllFields();
}

function _getDefaultValue(key) {
  // Hard-coded defaults matching GameConfig Pydantic model defaults
  const defaults = {
    tick_rate: 10,
    duration_minutes: 5,
    field_width: 100.0,
    field_height: 60.0,
    goal_height: 7.32,
    default_seed: 42,
    action_cooldown_ticks: 10,
    pass_max_deviation: 8.0,
    shot_max_angle: 0.30,
    tackle_clean_share: 0.55,
    tackle_blocked_floor: 0.15,
    tackle_block_speed_min: 1.0,
    tackle_block_speed_max: 3.0,
    tackle_range: 2.0,
    tackle_settle_grace_ticks: 3,
    gk_caught_share: 0.60,
    gk_block_speed_factor: 0.4,
    ball_control_range_gk: 1.5,
    ball_control_range_outfield: 1.0,
    shot_deflection_min_speed: 2.0,
    shot_deflection_speed_factor_min: 0.3,
    shot_deflection_speed_factor_max: 0.5,
    health_max: 100.0,
    health_drain_factor: 1.0,
    health_floor: 0.6,
    goal_reset_ticks: 30,
    half_time_pause_ticks: 60,
    min_player_separation: 1.0,
    formation_snap_enabled: false,
    offside_enabled: true
  };

  return defaults[key] || '';
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
  for (const [key, value] of Object.entries(currentValues)) {
    const savedValue = savedValues[key];
    if (String(value) !== String(savedValue)) {
      return true;
    }
  }
  return false;
}

function _emitDirtyChangedEvent() {
  window.dispatchEvent(new CustomEvent('config:tabDirtyChanged', {
    detail: {
      tab: 'game',
      dirty: isDirty,
      valid: isValid
    }
  }));
}

// ── Public API ──────────────────────────────────────────────────
function mount(element, initialValues = {}) {
  rootElement = element;
  savedValues = { ...initialValues };
  currentValues = { ...initialValues };

  // Fill in missing values with defaults
  Object.keys(_getAllFieldKeys()).forEach(key => {
    if (!(key in currentValues)) {
      currentValues[key] = _getDefaultValue(key);
      savedValues[key] = _getDefaultValue(key);
    }
  });

  isDirty = false;
  isValid = true;

  renderGameTab();
  _emitDirtyChangedEvent();

  console.log('[config-game] Mounted with values:', savedValues);
}

function unmount() {
  rootElement = null;
  savedValues = {};
  currentValues = {};
  isDirty = false;
  isValid = true;

  console.log('[config-game] Unmounted');
}

function getDirty() {
  return isDirty;
}

function getValues() {
  return { ...currentValues };
}

function reset() {
  // Reset all fields to schema defaults
  Object.keys(currentValues).forEach(key => {
    currentValues[key] = _getDefaultValue(key);
  });

  // Update form
  if (rootElement) {
    Object.entries(currentValues).forEach(([key, value]) => {
      const input = rootElement.querySelector(`#field-${key}`);
      if (input) {
        if (input.type === 'checkbox') {
          input.checked = !!value;
        } else {
          input.value = value;
        }
        input.classList.remove('field-error-state');
      }

      const errorElement = rootElement.querySelector(`#error-${key}`);
      if (errorElement) {
        errorElement.textContent = '';
        errorElement.style.display = 'none';
      }
    });
  }

  _updateDirtyState();
  validateAllFields();

  console.log('[config-game] Reset to defaults');
}

function _getAllFieldKeys() {
  const keys = {};
  Object.values(GAME_FIELDS).forEach(section => {
    section.fields.forEach(field => {
      keys[field.key] = true;
    });
  });
  return keys;
}

// ── Module Exports ──────────────────────────────────────────────
window.configGameTab = {
  mount,
  unmount,
  getDirty,
  getValues,
  reset
};

console.log('[config-game] Config Game tab module loaded');