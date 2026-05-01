// Agent Pitch — Cup Section Module
// Implements 3 sub-views: List, Detail, New
// Route pattern: #/cup | #/cup/new | #/cup/<cup_id>

import { showDeleteConfirmModal, dismissOpenDeleteConfirmModal } from './modals.js';

// ── State ───────────────────────────────────────────────────────
let currentSubView = 'list';  // 'list' | 'detail' | 'new'
let currentCupId = null;
let cupListData = [];
let currentCupData = null;
let isLoading = false;
let sseSource = null;  // EventSource for live cup updates
let _cupMatchStartTimes = {};  // matchId → epoch ms when match started (browser-side)
let _cupElapsedInterval = null;

// ── Sub-view Routing ────────────────────────────────────────────

/**
 * Parse a route object into a sub-view name and optional cup ID.
 * @param {{ section: string, subsection: string }} route
 * @returns {{ subView: 'list'|'detail'|'new', cupId: string|null }}
 */
function parseRoute(route) {
  const { section, subsection } = route;
  if (section !== 'cup') return { subView: 'list', cupId: null };
  if (!subsection) return { subView: 'list', cupId: null };
  if (subsection === 'new') return { subView: 'new', cupId: null };
  return { subView: 'detail', cupId: subsection };
}

/**
 * Navigate to a cup sub-view by updating the hash.
 * @param {'list'|'detail'|'new'} subView
 * @param {string|null} cupId
 */
function cupNavigateSubView(subView, cupId = null) {
  if (subView === 'detail' && cupId) {
    window.location.hash = `#/cup/${cupId}`;
  } else if (subView === 'new') {
    window.location.hash = '#/cup/new';
  } else {
    window.location.hash = '#/cup';
  }
}

// ── Right-cap back button ───────────────────────────────────────

function mountCupBackButton(label, targetHash) {
  const rightCap = document.getElementById('right-cap');
  if (!rightCap) return;
  if (rightCap.querySelector('.cup-back-btn')) return;

  const btn = document.createElement('button');
  btn.className = 'btn-link cup-back-btn';
  btn.textContent = label;
  btn.onclick = () => { window.location.hash = targetHash; };

  rightCap.innerHTML = '';
  rightCap.appendChild(btn);
}

function unmountCupBackButton() {
  const rightCap = document.getElementById('right-cap');
  const btn = rightCap && rightCap.querySelector('.cup-back-btn');
  if (btn) btn.remove();
}

// ── Sub-view visibility helpers ─────────────────────────────────

function showOnlySubView(activeId) {
  const ids = ['cup-list-view', 'cup-detail-view', 'cup-new-view'];
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    if (id === activeId) {
      el.removeAttribute('hidden');
    } else {
      el.setAttribute('hidden', '');
    }
  });
}

// ── Utility ─────────────────────────────────────────────────────

function updateSubtitle(subtitle) {
  window.dispatchEvent(new CustomEvent('shell:subtitleChanged', {
    detail: { subtitle }
  }));
}

function escapeHtml(str) {
  return String(str || '').replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[c]);
}

// ── Status badge ────────────────────────────────────────────────

function renderStatusBadge(status) {
  switch (status) {
    case 'running':
      return `<span class="cup-status-badge running"><span class="cup-running-dot">●</span> RUNNING</span>`;
    case 'complete':
      return `<span class="cup-status-badge complete">COMPLETE</span>`;
    case 'errored':
      return `<span class="cup-status-badge errored">ERRORED</span>`;
    case 'pending':
      return `<span class="cup-status-badge pending">PENDING</span>`;
    default:
      return `<span class="cup-status-badge">${String(status || '—').toUpperCase()}</span>`;
  }
}

// ── List Sub-view ───────────────────────────────────────────────

/**
 * Render and load the list sub-view.
 */
function renderCupListSubView() {
  currentSubView = 'list';
  currentCupId = null;

  closeSseSource();
  showOnlySubView('cup-list-view');
  updateSubtitle('CUP');
  unmountCupBackButton();

  loadCupList();
}

async function loadCupList() {
  if (isLoading) return;
  isLoading = true;

  renderListLoading();

  try {
    const response = await fetch('/api/cups');
    if (!response.ok) throw new Error(`Server returned ${response.status}`);
    cupListData = await response.json();
    renderCupList();
  } catch (error) {
    console.error('[cup.js] Failed to load cup list:', error);
    renderListError();
  } finally {
    isLoading = false;
  }
}

function renderListLoading() {
  const listEl = document.getElementById('cup-list');
  const countEl = document.getElementById('cup-count');
  const newBtn = document.getElementById('cup-new-btn');

  if (countEl) countEl.textContent = 'Loading…';
  if (newBtn) newBtn.disabled = true;

  if (!listEl) return;
  listEl.innerHTML = `
    <div class="cup-list-row skeleton" role="listitem">
      <div class="cup-row-content dimer">Loading cups…</div>
    </div>
  `;
}

function renderListError() {
  const listEl = document.getElementById('cup-list');
  const countEl = document.getElementById('cup-count');
  const newBtn = document.getElementById('cup-new-btn');

  if (countEl) countEl.textContent = 'Error';
  if (newBtn) newBtn.disabled = false;

  if (!listEl) return;
  listEl.innerHTML = `
    <div class="cup-list-error">
      <div class="cup-error-message">Could not load cups — server unreachable</div>
      <button class="btn btn-sm" onclick="window.cupRetryList()">Retry</button>
    </div>
  `;
}

function renderCupList() {
  const listEl = document.getElementById('cup-list');
  const countEl = document.getElementById('cup-count');
  const newBtn = document.getElementById('cup-new-btn');

  if (countEl) countEl.textContent = `${cupListData.length} cup${cupListData.length !== 1 ? 's' : ''}`;
  if (newBtn) newBtn.disabled = false;

  if (!listEl) return;

  if (cupListData.length === 0) {
    listEl.innerHTML = `
      <div class="cup-empty-state">
        <div class="cup-empty-heading">No cups yet — create your first tournament</div>
        <button class="btn btn-primary" onclick="window.cupNavigateSubView('new')">+ Create a new cup</button>
      </div>
    `;
    return;
  }

  listEl.innerHTML = cupListData.map(renderCupRow).join('');
}

function renderCupRow(cup) {
  const {
    cup_id, name, status, config_name, bracket_size, created_iso, winner
  } = cup;

  const date = created_iso
    ? new Date(created_iso).toISOString().slice(0, 16).replace('T', ' ')
    : '—';

  const bracketLabel = bracket_size ? `${bracket_size} teams` : '—';
  const badgeHtml = renderStatusBadge(status);
  const winnerHtml = winner ? ` · Winner: <strong>${escapeHtml(winner)}</strong>` : '';

  return `
    <div class="cup-list-row" role="listitem" data-cup-id="${cup_id}">
      <div class="cup-row-content"
           role="button"
           tabindex="0"
           aria-label="Cup ${escapeHtml(name || cup_id)}"
           onclick="window.cupOpenDetail('${escapeHtml(cup_id)}')"
           onkeydown="if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); window.cupOpenDetail('${escapeHtml(cup_id)}'); }">
        <div class="cup-row-line-1">${escapeHtml(name || cup_id)}${winnerHtml}</div>
        <div class="cup-row-line-2">${bracketLabel} · ${escapeHtml(config_name || '—')} · ${date}</div>
      </div>
      <div class="cup-row-meta">
        ${badgeHtml}
        <div class="cup-row-actions">
          <button class="btn btn-sm" onclick="window.cupOpenDetail('${escapeHtml(cup_id)}')" aria-label="View cup ${escapeHtml(cup_id)}">View</button>
          <button class="btn btn-sm btn-danger" onclick="window.cupDeleteCup('${escapeHtml(cup_id)}')" aria-label="Delete cup ${escapeHtml(cup_id)}">Del</button>
        </div>
      </div>
    </div>
  `;
}

// ── Detail Sub-view ─────────────────────────────────────────────

/**
 * Render the cup detail sub-view for the given cup ID.
 * @param {string} cupId
 */
function renderCupDetailSubView(cupId) {
  currentSubView = 'detail';
  currentCupId = cupId;

  closeSseSource();
  showOnlySubView('cup-detail-view');
  updateSubtitle('CUP · DETAIL');
  mountCupBackButton('Back to list', '#/cup');

  loadCupDetail(cupId);
}

async function loadCupDetail(cupId) {
  clearDetailPanels();

  try {
    const response = await fetch(`/api/cups/${encodeURIComponent(cupId)}`);
    if (!response.ok) {
      if (response.status === 404) {
        renderCupNotFound(cupId);
        return;
      }
      throw new Error(`Server returned ${response.status}`);
    }

    currentCupData = await response.json();
    renderDetailPanels(currentCupData);

    // Open SSE for active cups only if not already connected
    if (['running', 'pending'].includes(currentCupData.status) && !sseSource) {
      openSseSource(cupId);
    }

  } catch (error) {
    console.error('[cup.js] Failed to load cup detail:', error);
    renderDetailError(cupId);
  }
}

function clearDetailPanels() {
  const headerEl = document.getElementById('cup-detail-header');
  const bracketEl = document.getElementById('cup-bracket-container');
  const bannerEl = document.getElementById('cup-result-banner');

  if (headerEl) headerEl.innerHTML = '<div class="dimer">Loading…</div>';
  if (bracketEl) bracketEl.innerHTML = '';
  if (bannerEl) { bannerEl.setAttribute('hidden', ''); bannerEl.innerHTML = ''; }
}

function renderCupNotFound(cupId) {
  const headerEl = document.getElementById('cup-detail-header');
  if (headerEl) {
    headerEl.innerHTML = `
      <div class="cup-not-found">
        <div class="cup-error-message">Cup "${escapeHtml(cupId)}" not found — it may have been deleted</div>
        <button class="btn btn-sm" onclick="window.cupNavigateSubView('list')">Back to list</button>
      </div>
    `;
  }
}

function renderDetailError(cupId) {
  const headerEl = document.getElementById('cup-detail-header');
  if (headerEl) {
    headerEl.innerHTML = `
      <div class="cup-not-found">
        <div class="cup-error-message">Could not load cup — server unreachable</div>
        <button class="btn btn-sm" onclick="window.cupRetryDetail('${cupId}')">Retry</button>
        <button class="btn btn-sm" onclick="window.cupNavigateSubView('list')">Back to list</button>
      </div>
    `;
  }
}

function renderDetailPanels(cup) {
  renderCupHeader(cup);
  renderCupBracket(cup);
  renderResultBanner(cup);
  _syncRunningMatchTimers(cup);
  if (cup.status === 'running') {
    _startElapsedTimer();
  } else {
    _stopElapsedTimer();
  }
}

// Seed _cupMatchStartTimes for any matches already running when the page loads.
// Uses Date.now() as an approximation — elapsed will count from page load, not match start.
function _syncRunningMatchTimers(cup) {
  (cup.rounds || []).forEach(round => {
    (round.matches || []).forEach(match => {
      if (match.status === 'running' && match.match_id) {
        if (!_cupMatchStartTimes[match.match_id]) {
          _cupMatchStartTimes[match.match_id] = Date.now();
        }
      }
    });
  });
}

function _startElapsedTimer() {
  if (_cupElapsedInterval) return;
  _cupElapsedInterval = setInterval(() => {
    document.querySelectorAll('.cup-elapsed[data-match-start]').forEach(span => {
      const start = parseInt(span.dataset.matchStart, 10);
      if (!start) return;
      const elapsed = Math.floor((Date.now() - start) / 1000);
      const m = Math.floor(elapsed / 60);
      const s = elapsed % 60;
      span.textContent = `${m}:${s.toString().padStart(2, '0')}`;
    });
  }, 1000);
}

function _stopElapsedTimer() {
  if (_cupElapsedInterval) {
    clearInterval(_cupElapsedInterval);
    _cupElapsedInterval = null;
  }
}

function renderCupHeader(cup) {
  const el = document.getElementById('cup-detail-header');
  if (!el) return;

  const name = escapeHtml(cup.name || cup.cup_id);
  const configName = escapeHtml(cup.config_name || '—');
  const bracketSize = cup.bracket_size ? `${cup.bracket_size} teams` : '—';
  const badgeHtml = renderStatusBadge(cup.status);

  el.innerHTML = `
    <div class="cup-detail-header-inner">
      <span class="cup-detail-name">${name}</span>
      <span class="cup-header-sep">·</span>
      ${badgeHtml}
      <span class="cup-header-sep">·</span>
      <span class="cup-header-meta">${bracketSize}</span>
      <span class="cup-header-sep">·</span>
      <span class="cup-header-meta">CONFIG: ${configName}</span>
    </div>
    <div class="cup-detail-actions">
      <button class="btn btn-sm btn-danger"
              onclick="window.cupDeleteCup('${escapeHtml(cup.cup_id)}')"
              aria-label="Delete cup ${escapeHtml(cup.cup_id)}">
        Delete Cup
      </button>
    </div>
  `;
}

/**
 * Build the bracket visualization from cup data.
 * @param {object} cup
 */
function renderCupBracket(cup) {
  const containerEl = document.getElementById('cup-bracket-container');
  if (!containerEl) return;

  const rounds = cup.rounds || [];
  if (rounds.length === 0) {
    containerEl.innerHTML = '<div class="dimer" style="padding:16px">No rounds yet.</div>';
    return;
  }

  // Build slot → strategy_name lookup from cup.teams
  const slotNames = {};
  (cup.teams || []).forEach(t => { slotNames[t.slot] = t.strategy_name || `Slot ${t.slot}`; });

  const roundsHtml = rounds.map((round, roundIdx) => {
    const roundLabel = getRoundLabel(round.round_number, rounds.length);
    const matchesHtml = renderBracketRound(round, roundIdx, slotNames);

    return `
      <div class="bracket-round" data-round="${round.round_number}">
        <div class="bracket-round-label">${roundLabel}</div>
        <div class="bracket-matches">
          ${matchesHtml}
        </div>
      </div>
    `;
  }).join('');

  containerEl.innerHTML = `
    <div class="cup-bracket" data-rounds="${rounds.length}">
      ${roundsHtml}
    </div>
  `;
}

function getRoundLabel(roundNumber, totalRounds) {
  const roundsFromEnd = totalRounds - roundNumber;
  if (roundsFromEnd === 0) return 'Final';
  if (roundsFromEnd === 1) return 'Semi-Finals';
  if (roundsFromEnd === 2) return 'Quarter-Finals';
  return `Round ${roundNumber}`;
}

function renderBracketRound(round, roundIdx, slotNames) {
  const matches = round.matches || [];
  if (matches.length === 0) {
    return '<div class="bracket-match" data-status="pending"><div class="bracket-team dimer">TBD</div><div class="bracket-team dimer">TBD</div></div>';
  }

  const matchesHtml = matches.map((match, matchIdx) => {
    const slotKey = `R${round.round_number}M${matchIdx + 1}`;
    return renderBracketMatch(match, slotKey, slotNames);
  }).join('<div class="bracket-spacer"></div>');

  return matchesHtml;
}

function renderBracketMatch(match, slotKey, slotNames) {
  slotNames = slotNames || {};
  const status = match.status || 'pending';

  // Resolve team names from slot numbers using the cup.teams lookup
  const slotA = match.team_a_slot;
  const slotB = match.team_b_slot;
  const team1Name = slotA != null ? escapeHtml(slotNames[slotA] || `Slot ${slotA}`) : 'TBD';
  const team2Name = slotB != null ? escapeHtml(slotNames[slotB] || `Slot ${slotB}`) : 'TBD';

  // Scores from final_score.team_a / final_score.team_b
  const finalScore = match.final_score || null;
  const score1 = finalScore != null ? finalScore.team_a : null;
  const score2 = finalScore != null ? finalScore.team_b : null;

  // Winner from winner_slot; tiebreak from tiebreak field
  const winnerSlot = match.winner_slot != null ? match.winner_slot : null;
  const isTiebreak = match.tiebreak || false;
  const matchId = match.match_id || null;

  const team1IsWinner = winnerSlot != null && winnerSlot === slotA;
  const team2IsWinner = winnerSlot != null && winnerSlot === slotB;
  const team1Class = team1IsWinner ? 'bracket-team winner' : 'bracket-team';
  const team2Class = team2IsWinner ? 'bracket-team winner' : 'bracket-team';

  const winnerBadge1 = '';
  const winnerBadge2 = '';

  const score1Html = score1 != null ? ` <span class="score">${score1}</span>` : '';
  const score2Html = score2 != null ? ` <span class="score">${score2}</span>` : '';

  let matchInfoHtml = '';
  if (matchId && (status === 'running' || status === 'complete')) {
    const linkLabel = status === 'running' ? '▶ watching' : '▶ replay';
    const statusLabel = status === 'running'
      ? '<span class="cup-match-status running">running</span>'
      : '<span class="cup-match-status complete">completed</span>';
    const startTs = _cupMatchStartTimes[matchId];
    const elapsedHtml = (status === 'running' && startTs)
      ? `<span class="cup-elapsed" data-match-start="${startTs}">0:00</span>`
      : '';
    matchInfoHtml = `
      <div class="bracket-match-link">
        ${statusLabel}${elapsedHtml}
        <a href="#/matches/${escapeHtml(matchId)}" class="cup-live-link">${linkLabel}</a>
      </div>
    `;
  }

  return `
    <div class="bracket-match" data-slot="${slotKey}" data-status="${status}">
      <div class="${team1Class}">${team1Name}${score1Html}${winnerBadge1}</div>
      <div class="${team2Class}">${team2Name}${score2Html}${winnerBadge2}</div>
      ${matchInfoHtml}
    </div>
  `;
}

function renderResultBanner(cup) {
  const bannerEl = document.getElementById('cup-result-banner');
  if (!bannerEl) return;

  if (cup.status === 'errored') {
    bannerEl.removeAttribute('hidden');
    bannerEl.innerHTML = `
      <div class="cup-error-banner">
        <span class="cup-error-banner-icon">✕</span>
        <div>
          <strong>Cup failed</strong>
          <div class="cup-error-banner-detail">The cup pipeline encountered an error. Check server logs for details.</div>
        </div>
      </div>
    `;
    return;
  }

  if (cup.status !== 'complete') {
    bannerEl.setAttribute('hidden', '');
    bannerEl.innerHTML = '';
    return;
  }

  bannerEl.removeAttribute('hidden');

  const winner = cup.winner ? escapeHtml(cup.winner) : '—';
  bannerEl.innerHTML = `
    <div class="cup-result-banner-inner">
      🏆 Winner: <strong>${winner}</strong>
    </div>
  `;
}

// ── New Cup Sub-view ────────────────────────────────────────────

/**
 * Render the New cup sub-view.
 */
function renderCupNewSubView() {
  currentSubView = 'new';
  currentCupId = null;

  closeSseSource();
  showOnlySubView('cup-new-view');
  updateSubtitle('CUP · NEW');
  mountCupBackButton('Back to list', '#/cup');

  // Wire cancel button
  const cancelBtn = document.getElementById('cup-cancel-btn');
  if (cancelBtn) cancelBtn.onclick = () => cupNavigateSubView('list');

  // Populate pickers
  loadConfigsForCupPicker();
  loadStrategiesForCupPicker();

  // Restore form state
  restoreCupNewForm();

  // Wire form events
  setupCupNewFormEvents();
}

async function loadConfigsForCupPicker() {
  const selectEl = document.getElementById('cup-config-select');
  if (!selectEl) return;

  try {
    const response = await fetch('/api/config/match');
    if (!response.ok) throw new Error(`Server returned ${response.status}`);
    const configs = await response.json();

    const saved = (() => {
      try { return JSON.parse(localStorage.getItem('ap_cup_lastForm') || '{}').config_name || ''; }
      catch { return ''; }
    })();

    selectEl.innerHTML = '<option value="">— select a config —</option>';
    configs.forEach(cfg => {
      const name = typeof cfg === 'string' ? cfg : (cfg.name || cfg);
      const opt = document.createElement('option');
      opt.value = name;
      opt.textContent = name;
      if (name === saved) opt.selected = true;
      selectEl.appendChild(opt);
    });
  } catch (error) {
    console.error('[cup.js] Failed to load configs:', error);
    if (selectEl) {
      selectEl.innerHTML = '<option value="">Could not load configs</option>';
    }
  }
}

// Strategies data cached for team slot pickers
let _strategiesCache = [];

async function loadStrategiesForCupPicker() {
  try {
    const response = await fetch('/api/strategies');
    if (!response.ok) throw new Error(`Server returned ${response.status}`);
    _strategiesCache = await response.json();

    // Re-render team slots with fresh strategy data
    const bracketSizeEl = document.getElementById('cup-bracket-size');
    const size = bracketSizeEl ? parseInt(bracketSizeEl.value, 10) : 4;
    renderTeamSlots(size);

  } catch (error) {
    console.error('[cup.js] Failed to load strategies:', error);
    _strategiesCache = [];
  }
}

/**
 * Render N team slot selects in #cup-team-slots.
 * @param {number} count
 */
function renderTeamSlots(count) {
  const container = document.getElementById('cup-team-slots');
  if (!container) return;

  const saved = (() => {
    try { return JSON.parse(localStorage.getItem('ap_cup_lastForm') || '{}').teams || []; }
    catch { return []; }
  })();

  const strategies = Array.isArray(_strategiesCache) ? _strategiesCache : [];
  const strategyNames = strategies.map(s => (typeof s === 'string' ? s : (s.name || s)));

  let warningHtml = '';
  if (strategyNames.length < count) {
    warningHtml = `
      <div class="cup-team-warning">
        ⚠ Only ${strategyNames.length} strateg${strategyNames.length !== 1 ? 'ies' : 'y'} available — need ${count} for this bracket size.
      </div>
    `;
  }

  const slotsHtml = Array.from({ length: count }, (_, i) => {
    const savedTeam = saved[i] || '';
    const options = strategyNames.map(name => {
      const selected = name === savedTeam ? ' selected' : '';
      return `<option value="${escapeHtml(name)}"${selected}>${escapeHtml(name)}</option>`;
    }).join('');

    return `
      <div class="cup-team-slot">
        <label class="cup-team-slot-label" for="cup-team-slot-${i}">Team ${i + 1}</label>
        <select id="cup-team-slot-${i}" class="sel cup-team-select" data-slot="${i}" aria-label="Team ${i + 1} strategy">
          <option value="">— select strategy —</option>
          ${options}
        </select>
      </div>
    `;
  }).join('');

  container.innerHTML = warningHtml + slotsHtml;

  // Wire change events for persistence
  container.querySelectorAll('.cup-team-select').forEach(sel => {
    sel.onchange = persistCupNewForm;
  });
}

function restoreCupNewForm() {
  try {
    const saved = JSON.parse(localStorage.getItem('ap_cup_lastForm') || '{}');

    const nameEl = document.getElementById('cup-name-input');
    if (nameEl && saved.name) nameEl.value = saved.name;

    const bracketEl = document.getElementById('cup-bracket-size');
    if (bracketEl && saved.bracket_size) {
      bracketEl.value = String(saved.bracket_size);
    }
  } catch {
    // ignore corrupt localStorage
  }
}

let _cupPersistTimer = null;
function persistCupNewForm() {
  clearTimeout(_cupPersistTimer);
  _cupPersistTimer = setTimeout(() => {
    try {
      const nameEl = document.getElementById('cup-name-input');
      const configEl = document.getElementById('cup-config-select');
      const bracketEl = document.getElementById('cup-bracket-size');

      const size = bracketEl ? parseInt(bracketEl.value, 10) : 4;
      const teams = [];
      for (let i = 0; i < size; i++) {
        const slotEl = document.getElementById(`cup-team-slot-${i}`);
        teams.push(slotEl ? slotEl.value : '');
      }

      const data = {
        name: nameEl ? nameEl.value : '',
        config_name: configEl ? configEl.value : '',
        bracket_size: size,
        teams,
      };
      localStorage.setItem('ap_cup_lastForm', JSON.stringify(data));
    } catch { /* quota exceeded or private mode */ }
  }, 500);
}

function setupCupNewFormEvents() {
  const nameEl = document.getElementById('cup-name-input');
  if (nameEl) nameEl.oninput = persistCupNewForm;

  const configEl = document.getElementById('cup-config-select');
  if (configEl) configEl.onchange = persistCupNewForm;

  const bracketEl = document.getElementById('cup-bracket-size');
  if (bracketEl) {
    bracketEl.onchange = () => {
      const size = parseInt(bracketEl.value, 10);
      renderTeamSlots(size);
      persistCupNewForm();
    };
  }

  const formEl = document.getElementById('cup-new-form');
  if (formEl) {
    formEl.onsubmit = (e) => {
      e.preventDefault();
      handleCupCreate();
    };
  }
}

async function handleCupCreate() {
  const nameEl = document.getElementById('cup-name-input');
  const configEl = document.getElementById('cup-config-select');
  const bracketEl = document.getElementById('cup-bracket-size');
  const submitBtn = document.getElementById('cup-submit-btn');
  const errorEl = document.getElementById('cup-form-error');
  const formEl = document.getElementById('cup-new-form');

  const name = nameEl ? nameEl.value.trim() : '';
  const configName = configEl ? configEl.value.trim() : '';
  const bracketSize = bracketEl ? parseInt(bracketEl.value, 10) : 4;

  const teams = [];
  for (let i = 0; i < bracketSize; i++) {
    const slotEl = document.getElementById(`cup-team-slot-${i}`);
    teams.push(slotEl ? slotEl.value.trim() : '');
  }

  // Validate
  if (errorEl) { errorEl.setAttribute('hidden', ''); errorEl.textContent = ''; }

  if (!name) {
    if (errorEl) { errorEl.removeAttribute('hidden'); errorEl.textContent = 'Cup name is required.'; }
    if (nameEl) nameEl.focus();
    return;
  }

  if (!configName) {
    if (errorEl) { errorEl.removeAttribute('hidden'); errorEl.textContent = 'Please select a config.'; }
    if (configEl) configEl.setAttribute('aria-invalid', 'true');
    return;
  }
  if (configEl) configEl.removeAttribute('aria-invalid');

  const emptySlots = teams.filter(t => !t);
  if (emptySlots.length > 0) {
    if (errorEl) { errorEl.removeAttribute('hidden'); errorEl.textContent = `Please assign a strategy to all ${bracketSize} team slots.`; }
    return;
  }

  // Submit
  if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Creating…'; }
  if (formEl) {
    Array.from(formEl.elements).forEach(el => { el.disabled = true; });
  }

  try {
    const body = {
      name,
      config_name: configName,
      bracket_size: bracketSize,
      strategies: teams,
    };

    const response = await fetch('/api/cups', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      const detail = Array.isArray(err.detail)
        ? err.detail.map(e => e.msg || JSON.stringify(e)).join('; ')
        : (err.detail || err.error || `Server returned ${response.status}`);
      throw new Error(detail);
    }

    const result = await response.json();
    const newCupId = result.cup_id;

    // Clear saved form on success
    try { localStorage.removeItem('ap_cup_lastForm'); } catch {}

    // Navigate to detail
    cupNavigateSubView('detail', newCupId);

  } catch (error) {
    console.error('[cup.js] Failed to create cup:', error);
    if (errorEl) {
      errorEl.removeAttribute('hidden');
      errorEl.textContent = `Could not create cup: ${error.message}`;
    }
    // Re-enable form
    if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = 'Create Cup'; }
    if (formEl) {
      Array.from(formEl.elements).forEach(el => { el.disabled = false; });
    }
  }
}

// ── SSE for live cup updates ────────────────────────────────────

function openSseSource(cupId) {
  closeSseSource();
  try {
    sseSource = new EventSource(`/api/cups/${encodeURIComponent(cupId)}/stream`);

    sseSource.addEventListener('cup-round-started', () => {
      if (currentCupId === cupId) loadCupDetail(cupId);
    });

    sseSource.addEventListener('cup-match-started', (e) => {
      try {
        const d = JSON.parse(e.data || '{}');
        if (d.match_id) _cupMatchStartTimes[d.match_id] = Date.now();
      } catch {}
      if (currentCupId === cupId) loadCupDetail(cupId);
    });

    sseSource.addEventListener('cup-match-completed', () => {
      if (currentCupId === cupId) loadCupDetail(cupId);
    });

    sseSource.addEventListener('cup-round-completed', () => {
      if (currentCupId === cupId) loadCupDetail(cupId);
    });

    sseSource.addEventListener('cup-completed', () => {
      _stopElapsedTimer();
      closeSseSource();
      if (currentCupId === cupId) loadCupDetail(cupId);
    });

    sseSource.addEventListener('cup-errored', () => {
      _stopElapsedTimer();
      closeSseSource();
      if (currentCupId === cupId) loadCupDetail(cupId);
    });

    sseSource.onerror = () => {
      console.warn('[cup.js] SSE connection closed or errored');
    };

  } catch (error) {
    console.error('[cup.js] Failed to open SSE source:', error);
  }
}

function closeSseSource() {
  if (sseSource) {
    sseSource.close();
    sseSource = null;
  }
}

// ── Delete Cup ──────────────────────────────────────────────────

function cupDeleteCup(cupId) {
  showDeleteConfirmModal({
    title: `Delete cup ${cupId}?`,
    body: 'This removes the cup permanently.',
    expectedText: cupId,
    onConfirm: async (ctx) => {
      ctx.setBusy('Deleting…');
      try {
        const response = await fetch(`/api/cups/${encodeURIComponent(cupId)}`, { method: 'DELETE' });
        if (!response.ok && response.status !== 204) {
          ctx.setError('Delete Failed');
          console.error(`[cup.js] DELETE /api/cups/${cupId} → ${response.status}`);
          return;
        }
        ctx.close();
        cupNavigateSubView('list');
      } catch (error) {
        ctx.setError('Delete Failed');
        console.error('[cup.js] Delete cup error:', error);
      }
    }
  });
}

// ── Main Section API ────────────────────────────────────────────

/**
 * Called by shell.js router when section=cup.
 * @param {{ section: string, subsection: string }} route
 */
function cupHandleRoute(route = {}) {
  console.log('[cup.js] cupHandleRoute called with route:', route);

  // Show cup section, hide all others
  const allSectionIds = ['section-matches', 'section-strategies', 'section-arena', 'section-config', 'section-cup', 'section-league'];
  allSectionIds.forEach(sectionId => {
    const el = document.getElementById(sectionId);
    if (!el) return;
    if (sectionId === 'section-cup') {
      el.removeAttribute('hidden');
    } else {
      el.setAttribute('hidden', '');
    }
  });

  const { subView, cupId } = parseRoute(route);

  if (subView === 'list') {
    renderCupListSubView();
  } else if (subView === 'detail') {
    renderCupDetailSubView(cupId);
  } else if (subView === 'new') {
    renderCupNewSubView();
  }
}

/**
 * Called when the Cup section is hidden (navigating away).
 */
function cupOnSectionHidden() {
  console.log('[cup.js] Cup section hidden — closing SSE');
  _stopElapsedTimer();
  _cupMatchStartTimes = {};
  closeSseSource();
  unmountCupBackButton();
  dismissOpenDeleteConfirmModal();
}

// ── Export Section Object (matches shell.js router contract) ────
window.cupSection = {
  activate: cupHandleRoute,
  deactivate: cupOnSectionHidden,
};

// ── Window Globals (all cup-prefixed) ───────────────────────────
window.cupHandleRoute = cupHandleRoute;
window.cupNavigateSubView = cupNavigateSubView;
window.cupOpenDetail = (cupId) => cupNavigateSubView('detail', cupId);
window.cupDeleteCup = cupDeleteCup;
window.cupRetryList = loadCupList;
window.cupRetryDetail = loadCupDetail;

// Listen for config updates to refresh the picker
if (window.appBus) {
  window.appBus.addEventListener('config:matchConfigSaved', () => {
    if (currentSubView === 'new') loadConfigsForCupPicker();
  });
  window.appBus.addEventListener('config:matchConfigDeleted', () => {
    if (currentSubView === 'new') loadConfigsForCupPicker();
  });
}

console.log('[cup.js] Cup section module loaded');
