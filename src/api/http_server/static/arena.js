// Agent Pitch — Arena Section Module
// Implements 3 sub-views: List, Series Detail, New
// Route pattern: #/arena | #/arena/new | #/arena/<series_id>

import { showDeleteConfirmModal, dismissOpenDeleteConfirmModal } from './modals.js';

// ── State ───────────────────────────────────────────────────────
let currentSubView = 'list';  // 'list' | 'detail' | 'new'
let currentSeriesId = null;
let seriesListData = [];
let currentSeriesData = null;
let isLoading = false;
let sseSource = null;  // EventSource for live series updates

// Elapsed-time ticker for the running match progress segment
let _elapsedTimer = null;
let _elapsedStartedAt = null;
let _currentRunningMatchId = null;  // set from match-started SSE event

// Stage timeline — timestamps keyed by stage, set from SSE event data
let _stageTimestamps = {};

// PMEP attempt tracking: { [matchN_teamId]: { attempt, maxAttempts, provider } }
let _pmepAttempts = {};

function _startElapsedTimer(startMs) {
  if (_elapsedTimer) clearInterval(_elapsedTimer);
  _elapsedStartedAt = (startMs != null) ? startMs : Date.now();
  _elapsedTimer = setInterval(_tickElapsed, 1000);
  _tickElapsed();
}

function _stopElapsedTimer() {
  if (_elapsedTimer) { clearInterval(_elapsedTimer); _elapsedTimer = null; }
  _elapsedStartedAt = null;
}

function _tickElapsed() {
  if (!_elapsedStartedAt) return;
  const timeStr = _fmtMs(Date.now() - _elapsedStartedAt);
  const activeEl = document.getElementById('arena-active-elapsed');
  if (activeEl) activeEl.textContent = timeStr;
  const liveEl = document.getElementById('arena-live-elapsed');
  if (liveEl) liveEl.textContent = timeStr;
  // Keep progress bar running segments updated too
  document.querySelectorAll('.arena-progress-seg[data-state="running"]').forEach(el => {
    el.innerHTML = `<span class="arena-running-dot">●</span> <span class="arena-elapsed">${timeStr}</span>`;
  });
}

function _isoToMs(isoStr) {
  if (!isoStr) return null;
  const ms = new Date(isoStr).getTime();
  return isNaN(ms) ? null : ms;
}

function _fmtMs(ms) {
  if (ms == null || ms < 0) return '—';
  const s = Math.floor(ms / 1000);
  const m = Math.floor(s / 60);
  return `${m}:${String(s % 60).padStart(2, '0')}`;
}

function _resetStageState() {
  _stageTimestamps = {};
  _pmepAttempts = {};
  _stopElapsedTimer();
}

/**
 * Pure function — builds ordered stage array from series data + timestamps.
 * Each stage: { type, matchNum?, label, state, startedMs, endedMs, durationMs, result? }
 * @param {object} series
 * @param {object} timestamps
 * @returns {Array}
 */
function buildStagePipeline(series, timestamps) {
  const format = series.format || '3-match';
  const totalMatches = format === '5-match' ? 5 : 3;
  const isRunning = series.status === 'running';
  const matches = series.matches || [];
  const stages = [];

  // CGP stage — starts at series.started_iso, ends when match 1 starts
  const cgpStart = timestamps.cgp_started || null;
  const match1Start = timestamps.match1_started || null;
  stages.push({
    type: 'cgp',
    label: 'CGP',
    startedMs: cgpStart,
    endedMs: match1Start,
    state: !cgpStart ? 'pending'
         : match1Start ? 'done'
         : isRunning ? 'active'
         : 'done',
    durationMs: cgpStart && match1Start ? match1Start - cgpStart : null,
    result: null,
  });

  for (let i = 1; i <= totalMatches; i++) {
    const matchStart = timestamps[`match${i}_started`] || null;
    const matchEnd   = timestamps[`match${i}_completed`] || null;
    const matchResult = matches.find(m => m.match_number === i) || null;

    stages.push({
      type: 'match',
      matchNum: i,
      label: `M${i}`,
      startedMs: matchStart,
      endedMs: matchEnd,
      state: !matchStart ? 'pending'
           : matchEnd ? 'done'
           : isRunning ? 'active'
           : 'done',
      durationMs: matchStart && matchEnd ? matchEnd - matchStart : null,
      result: matchResult,
    });

    if (i < totalMatches) {
      const pmepStart = timestamps[`pmep${i}_started`] || null;
      const nextMatchStart = timestamps[`match${i + 1}_started`] || null;
      stages.push({
        type: 'pmep',
        matchNum: i,
        label: 'PMEP',
        startedMs: pmepStart,
        endedMs: nextMatchStart,
        state: !pmepStart ? 'pending'
             : nextMatchStart ? 'done'
             : isRunning ? 'active'
             : 'done',
        durationMs: pmepStart && nextMatchStart ? nextMatchStart - pmepStart : null,
        result: null,
      });
    }
  }

  return stages;
}

// Providers loaded from /api/config — used to populate model dropdowns.
// Array of { name, url, model, key_status, builtin }.
let loadedProviders = [];

// Per-series diff cache: { [seriesId]: { [matchN_team]: { loaded, data, error } } }
const diffCache = {};

// Known models for built-in providers (shown before user tests connection).
const BUILTIN_MODELS = {
  openai:    ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'o1', 'o1-mini', 'o3', 'o3-mini'],
  anthropic: ['claude-opus-4-7', 'claude-sonnet-4-6', 'claude-haiku-4-5-20251001'],
  gemini:    ['gemini-2.5-pro', 'gemini-2.0-flash', 'gemini-2.0-pro'],
};

// ── Sub-view Routing ────────────────────────────────────────────

/**
 * Parse a route object into a sub-view name and optional series ID.
 * @param {{ section: string, subsection: string }} route
 * @returns {{ subView: 'list'|'detail'|'new', seriesId: string|null }}
 */
function parseRoute(route) {
  const { section, subsection } = route;
  if (section !== 'arena') return { subView: 'list', seriesId: null };
  if (!subsection) return { subView: 'list', seriesId: null };
  if (subsection === 'new') return { subView: 'new', seriesId: null };
  return { subView: 'detail', seriesId: subsection };
}

/**
 * Navigate to an arena sub-view by updating the hash.
 * @param {'list'|'detail'|'new'} subView
 * @param {string|null} seriesId
 */
function arenaNavigateSubView(subView, seriesId = null) {
  if (subView === 'detail' && seriesId) {
    window.location.hash = `#/arena/${seriesId}`;
  } else if (subView === 'new') {
    window.location.hash = '#/arena/new';
  } else {
    window.location.hash = '#/arena';
  }
}

// ── Right-cap back button ───────────────────────────────────────

function mountArenaBackButton(label, targetHash) {
  const rightCap = document.getElementById('right-cap');
  if (!rightCap) return;
  if (rightCap.querySelector('.arena-back-btn')) return;

  const btn = document.createElement('button');
  btn.className = 'btn-link arena-back-btn';
  btn.textContent = label;
  btn.onclick = () => { window.location.hash = targetHash; };

  rightCap.innerHTML = '';
  rightCap.appendChild(btn);
}

function unmountArenaBackButton() {
  const rightCap = document.getElementById('right-cap');
  const btn = rightCap && rightCap.querySelector('.arena-back-btn');
  if (btn) btn.remove();
}

// ── Sub-view visibility helpers ─────────────────────────────────

function showOnlySubView(activeId) {
  const ids = ['arena-list-view', 'arena-detail-view', 'arena-new-view'];
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

// ── List Sub-view ───────────────────────────────────────────────

/**
 * Render and load the list sub-view.
 */
function renderArenaListSubView() {
  currentSubView = 'list';
  currentSeriesId = null;

  _resetStageState();
  closeSseSource();
  showOnlySubView('arena-list-view');
  updateSubtitle('ARENA');
  unmountArenaBackButton();

  loadSeriesList();
}

async function loadSeriesList() {
  if (isLoading) return;
  isLoading = true;

  renderListLoading();

  try {
    const response = await fetch('/api/arena');
    if (!response.ok) throw new Error(`Server returned ${response.status}`);
    seriesListData = await response.json();
    renderSeriesList();

    // Emit list-loaded event
    if (window.appBus) {
      window.appBus.dispatchEvent(new CustomEvent('arena:listLoaded', {
        detail: { count: seriesListData.length }
      }));
    }
  } catch (error) {
    console.error('[arena.js] Failed to load series list:', error);
    renderListError();
  } finally {
    isLoading = false;
  }
}

function renderListLoading() {
  const listEl = document.getElementById('arena-list');
  const countEl = document.getElementById('arena-count');
  const newBtn = document.getElementById('arena-new-btn');

  if (countEl) countEl.textContent = 'Loading…';
  if (newBtn) newBtn.disabled = true;

  if (!listEl) return;
  listEl.innerHTML = generateSkeletonRows(3);
}

function generateSkeletonRows(count) {
  return Array(count).fill(0).map(() => `
    <div class="arena-series-row skeleton" role="listitem">
      <div class="arena-row-content">
        <div class="arena-row-line-1 dimer">TEAM A — — TEAM B   loading   loading</div>
        <div class="arena-row-line-2 dimer">loading vs loading · loading</div>
      </div>
      <div class="arena-row-actions">
        <button class="btn btn-sm" disabled>View</button>
        <button class="btn btn-sm btn-danger" disabled>Del</button>
      </div>
    </div>
  `).join('');
}

function renderListError() {
  const listEl = document.getElementById('arena-list');
  const countEl = document.getElementById('arena-count');
  const newBtn = document.getElementById('arena-new-btn');

  if (countEl) countEl.textContent = 'Error';
  if (newBtn) newBtn.disabled = false;

  if (!listEl) return;
  listEl.innerHTML = `
    <div class="arena-list-error">
      <div class="arena-error-message">Could not load series — server unreachable</div>
      <button class="btn btn-sm" onclick="window.arenaRetryList()">Retry</button>
    </div>
  `;
}

function renderSeriesList() {
  const listEl = document.getElementById('arena-list');
  const countEl = document.getElementById('arena-count');
  const newBtn = document.getElementById('arena-new-btn');

  if (countEl) countEl.textContent = `${seriesListData.length} series`;
  if (newBtn) newBtn.disabled = false;

  if (!listEl) return;

  if (seriesListData.length === 0) {
    renderListEmpty();
    return;
  }

  listEl.innerHTML = seriesListData.map(renderSeriesRow).join('');
}

function renderListEmpty() {
  const listEl = document.getElementById('arena-list');
  if (!listEl) return;
  listEl.innerHTML = `
    <div class="arena-empty-state">
      <div class="arena-empty-heading">No series yet — start your first comparison</div>
      <button class="btn btn-primary" onclick="window.arenaNavigateSubView('new')">+ Start a new series</button>
    </div>
  `;
}

function _langTag(lang) {
  if (lang === 'javascript') return 'JS';
  if (lang === 'rust')       return 'RS';
  return 'PY';
}

function renderSeriesRow(series) {
  const {
    series_id, format, status, config_name,
    started_iso, score, models
  } = series;

  const date = started_iso
    ? new Date(started_iso).toISOString().slice(0, 16).replace('T', ' ')
    : '—';

  const scoreA = score ? score.team_a : 0;
  const scoreB = score ? score.team_b : 0;
  const ties   = score ? (score.ties || 0) : 0;

  const modelA  = models ? (models.team_a || '—') : '—';
  const modelB  = models ? (models.team_b || '—') : '—';
  const langA   = models ? (models.team_a_language || 'python') : 'python';
  const langB   = models ? (models.team_b_language || 'python') : 'python';
  const tagA    = _langTag(langA);
  const tagB    = _langTag(langB);

  // Line 1: scoreboard
  let line1;
  if (status === 'tied') {
    line1 = `TIE  ${scoreA} <span class="dim">—</span> ${scoreB}${ties > 0 ? ` (${ties} TIED)` : ''}   ${format}   ${date}`;
  } else {
    line1 = `<span class="team-a-text">TEAM A ${scoreA}</span> <span class="dim">—</span> <span class="team-b-text">${scoreB} TEAM B</span>   ${format}   ${date}`;
  }

  // Status badge
  const badgeHtml = renderStatusBadge(status);

  const ariaLabel = `Series ${series_id}, ${format}, ${scoreA} to ${scoreB}, ${date}`;

  return `
    <div class="arena-series-row" role="listitem" data-series-id="${series_id}">
      <div class="arena-row-content"
           role="button"
           tabindex="0"
           aria-label="${ariaLabel}"
           onclick="window.arenaOpenSeriesDetail('${series_id}')"
           onkeydown="if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); window.arenaOpenSeriesDetail('${series_id}'); }">
        <div class="arena-row-line-1">${line1}</div>
        <div class="arena-row-line-2">${modelA} [${tagA}] vs ${modelB} [${tagB}] · ${config_name || '—'}</div>
      </div>
      <div class="arena-row-meta">
        ${badgeHtml}
        <div class="arena-row-actions">
          <button class="btn btn-sm" onclick="window.arenaOpenSeriesDetail('${series_id}')" aria-label="View series ${series_id}">View</button>
          <button class="btn btn-sm btn-danger" onclick="window.arenaDeleteSeries('${series_id}')" aria-label="Delete series ${series_id}">Del</button>
        </div>
      </div>
    </div>
  `;
}

function renderStatusBadge(status) {
  switch (status) {
    case 'running':
      return `<span class="arena-status-badge running"><span class="arena-running-dot">●</span> RUNNING</span>`;
    case 'complete':
      return `<span class="arena-status-badge complete">COMPLETE</span>`;
    case 'tied':
      return `<span class="arena-status-badge tied">TIED</span>`;
    case 'errored':
      return `<span class="arena-status-badge errored">ERRORED</span>`;
    default:
      return `<span class="arena-status-badge">${String(status || '—').toUpperCase()}</span>`;
  }
}

// ── Series Detail Sub-view ──────────────────────────────────────

/**
 * Render the series detail sub-view for the given series ID.
 * @param {string} seriesId
 */
function renderArenaDetailSubView(seriesId) {
  currentSubView = 'detail';
  currentSeriesId = seriesId;

  _resetStageState();
  closeSseSource();
  showOnlySubView('arena-detail-view');
  updateSubtitle('ARENA · SERIES');
  mountArenaBackButton('Back to list', '#/arena');

  loadSeriesDetail(seriesId);
}

async function loadSeriesDetail(seriesId) {
  // Clear all detail panels while loading
  clearDetailPanels();

  try {
    const response = await fetch(`/api/arena/${encodeURIComponent(seriesId)}`);
    if (!response.ok) {
      if (response.status === 404) {
        renderSeriesNotFound(seriesId);
        return;
      }
      throw new Error(`Server returned ${response.status}`);
    }

    currentSeriesData = await response.json();

    // Set CGP start from series created time (always available)
    if (currentSeriesData.started_iso) {
      _stageTimestamps.cgp_started = _isoToMs(currentSeriesData.started_iso);
    }

    // Timer: start from the active stage's real start time; stop when no active stage
    const _pipeline = buildStagePipeline(currentSeriesData, _stageTimestamps);
    const _activeStage = _pipeline.find(s => s.state === 'active') || null;
    if (_activeStage && _activeStage.startedMs) {
      if (!_elapsedTimer) _startElapsedTimer(_activeStage.startedMs);
    } else if (_activeStage && !_activeStage.startedMs) {
      // Active stage with no timestamp yet — start from now
      if (!_elapsedTimer) _startElapsedTimer(Date.now());
    } else {
      _stopElapsedTimer();
    }

    renderDetailPanels(currentSeriesData);

    // Open SSE for any non-terminal status — only if not already connected.
    if (['running', 'generating', 'pmep_running', 'evolving'].includes(currentSeriesData.status) && !sseSource) {
      openSseSource(seriesId);
    }

    if (window.appBus) {
      window.appBus.dispatchEvent(new CustomEvent('arena:seriesOpened', {
        detail: { seriesId }
      }));
    }

  } catch (error) {
    console.error('[arena.js] Failed to load series detail:', error);
    renderDetailError(seriesId);
  }
}

function clearDetailPanels() {
  const headerEl = document.getElementById('arena-series-header');
  const barEl = document.getElementById('arena-progression-bar');
  const liveSection = document.getElementById('arena-live-section');
  const bannerEl = document.getElementById('arena-result-banner');
  const matchListEl = document.getElementById('arena-matches-list');
  const footerEl = document.getElementById('arena-config-footer');

  if (headerEl) headerEl.innerHTML = '<div class="dimer">Loading…</div>';
  if (barEl) barEl.innerHTML = '';
  if (liveSection) liveSection.setAttribute('hidden', '');
  if (bannerEl) { bannerEl.setAttribute('hidden', ''); bannerEl.innerHTML = ''; }
  if (matchListEl) matchListEl.innerHTML = '';
  if (footerEl) footerEl.innerHTML = '';
}

function renderSeriesNotFound(seriesId) {
  const headerEl = document.getElementById('arena-series-header');
  if (headerEl) {
    headerEl.innerHTML = `
      <div class="arena-not-found">
        <div class="arena-error-message">Series "${seriesId}" not found — it may have been deleted</div>
        <button class="btn btn-sm" onclick="window.arenaNavigateSubView('list')">Back to list</button>
      </div>
    `;
  }
}

function renderDetailError(seriesId) {
  const headerEl = document.getElementById('arena-series-header');
  if (headerEl) {
    headerEl.innerHTML = `
      <div class="arena-not-found">
        <div class="arena-error-message">Could not load series — server unreachable</div>
        <button class="btn btn-sm" onclick="window.arenaRetryDetail('${seriesId}')">Retry</button>
        <button class="btn btn-sm" onclick="window.arenaNavigateSubView('list')">Back to list</button>
      </div>
    `;
  }
}

function renderDetailPanels(series) {
  renderSeriesHeader(series);
  renderProgressionBar(series);
  renderStagePipeline(series);
  renderResultBanner(series);
  renderMatchesList(series);
  renderConfigFooter(series);
}

function renderSeriesHeader(series) {
  const el = document.getElementById('arena-series-header');
  if (!el) return;

  const format = series.format || '—';
  const matches = series.matches || [];
  const completedCount = matches.filter(m => m.result && m.result !== 'running').length;
  const totalCount = format === '5-match' ? 5 : 3;
  const currentMatchNum = completedCount + 1;
  const score = series.score || { team_a: 0, team_b: 0 };
  const models = series.models || {};
  const modelA = models.team_a || '—';
  const modelB = models.team_b || '—';
  const langA  = models.team_a_language || 'python';
  const langB  = models.team_b_language || 'python';
  const tagA   = _langTag(langA);
  const tagB   = _langTag(langB);

  const statusHtml = renderStatusText(series.status);

  const matchLabel = series.status === 'running'
    ? `MATCH ${currentMatchNum} of ${totalCount}`
    : format.toUpperCase();

  el.innerHTML = `
    <div class="arena-series-header-inner">
      <span class="arena-header-format">${matchLabel}</span>
      <span class="arena-header-sep">·</span>
      <span class="arena-header-score">
        <span class="team-a-text">TEAM A ${score.team_a}</span>
        <span class="arena-header-dash"> — </span>
        <span class="team-b-text">${score.team_b} TEAM B</span>
      </span>
      <span class="arena-header-sep">·</span>
      <span class="arena-header-status">STATUS: ${statusHtml}</span>
    </div>
    <div class="arena-series-header-models">
      <span class="team-a-text">A</span>: <span class="arena-model-label">${escapeHtml(modelA)}</span>
      <span class="arena-lang-tag team-a-text">[${tagA}]</span>
      <span class="arena-header-sep"> · </span>
      <span class="team-b-text">B</span>: <span class="arena-model-label">${escapeHtml(modelB)}</span>
      <span class="arena-lang-tag team-b-text">[${tagB}]</span>
    </div>
  `;
}

function renderStatusText(status) {
  switch (status) {
    case 'running':      return '<span class="arena-status-running"><span class="arena-running-dot">●</span> running</span>';
    case 'generating':   return '<span class="arena-header-status dimer">GENERATING STRATEGIES (CGP)</span>';
    case 'pmep_running':
    case 'evolving':     return '<span class="arena-header-status dimer">EVOLVING STRATEGIES (PMEP)</span>';
    case 'complete':     return '<span class="dimer">complete</span>';
    case 'tied':         return '<span class="dimer">tied</span>';
    case 'errored':      return '<span class="arena-status-errored">errored</span>';
    default:             return `<span class="dimer">${String(status || '—').toLowerCase()}</span>`;
  }
}

function renderProgressionBar(series) {
  const el = document.getElementById('arena-progression-bar');
  if (!el) return;

  const format = series.format || '3-match';
  const totalCount = format === '5-match' ? 5 : 3;
  const matches = series.matches || [];
  const completedCount = matches.filter(m => m.result && m.result !== 'running').length;
  const isCurrentlyRunning = series.status === 'running';

  const segments = [];
  for (let i = 0; i < totalCount; i++) {
    const match = matches[i];
    if (!match) {
      // No match record yet — check if this slot is the currently-running match.
      // series.status === 'running' + i === completedCount means this slot is active
      // even when series.json hasn't added it to the matches array yet (first match).
      if (isCurrentlyRunning && i === completedCount) {
        segments.push({ state: 'running', text: '● running' });
      } else {
        segments.push({ state: 'pending', text: 'pending' });
      }
    } else if (match.result === 'team_a') {
      const sa = match.final_score ? match.final_score.team_a : '?';
      const sb = match.final_score ? match.final_score.team_b : '?';
      segments.push({ state: 'team_a', text: `A ${sa}-${sb}` });
    } else if (match.result === 'team_b') {
      const sa = match.final_score ? match.final_score.team_a : '?';
      const sb = match.final_score ? match.final_score.team_b : '?';
      segments.push({ state: 'team_b', text: `B ${sa}-${sb}` });
    } else if (match.result === 'tie') {
      const sa = match.final_score ? match.final_score.team_a : '?';
      const sb = match.final_score ? match.final_score.team_b : '?';
      segments.push({ state: 'tie', text: `TIE ${sa}-${sb}` });
    } else if (match.result === 'running' || (!match.result && match.match_id && series.status === 'running' && i === matches.length - 1)) {
      segments.push({ state: 'running', text: '● running' });
    } else if (match.result === 'error') {
      segments.push({ state: 'error', text: '[error]' });
    } else {
      segments.push({ state: 'pending', text: 'pending' });
    }
  }

  const segmentsHtml = segments.map(seg => {
    let inner;
    if (seg.state === 'running') {
      const elapsed = _elapsedStartedAt
        ? (() => {
            const s = Math.floor((Date.now() - _elapsedStartedAt) / 1000);
            return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
          })()
        : '0:00';
      inner = `<span class="arena-running-dot">●</span> <span class="arena-elapsed">${elapsed}</span>`;
    } else {
      inner = escapeHtml(seg.text);
    }
    return `<div class="arena-progress-seg" data-state="${seg.state}">${inner}</div>`;
  }).join('');

  el.innerHTML = `
    <div class="arena-progression-label">PROGRESSION:</div>
    <div class="arena-progression-segments">${segmentsHtml}</div>
  `;
}

/**
 * Render the stage pipeline into #arena-live-section / #arena-live-status.
 * Replaces the old renderLiveSection function.
 * @param {object} series
 */
function renderStagePipeline(series) {
  const section = document.getElementById('arena-live-section');
  const statusEl = document.getElementById('arena-live-status');
  if (!section || !statusEl) return;

  if (!series || !series.status) {
    section.setAttribute('hidden', '');
    return;
  }
  section.removeAttribute('hidden');

  const pipeline = buildStagePipeline(series, _stageTimestamps);
  const activeStage = pipeline.find(s => s.state === 'active') || null;

  // Build chip HTML for each stage
  const chipsHtml = pipeline.map((stage, idx) => {
    const arrow = idx === 0 ? '' : '<div class="arena-stage-arrow">›</div>';

    let timeHtml;
    if (stage.state === 'active') {
      const elapsed = _elapsedStartedAt != null ? _fmtMs(Date.now() - _elapsedStartedAt) : '0:00';
      timeHtml = `<span class="arena-running-dot">●</span> <span id="arena-active-elapsed">${elapsed}</span>`;
    } else if (stage.state === 'done') {
      if (stage.type === 'match' && stage.result) {
        const r = stage.result;
        const sa = r.final_score ? r.final_score.team_a : '?';
        const sb = r.final_score ? r.final_score.team_b : '?';
        let resultStr;
        if (r.result === 'team_a')      resultStr = `<span class="team-a-text">A</span>${sa}-${sb}`;
        else if (r.result === 'team_b') resultStr = `<span class="team-b-text">B</span>${sa}-${sb}`;
        else                            resultStr = `${sa}-${sb}`;
        const dur = stage.durationMs != null ? `·${_fmtMs(stage.durationMs)}` : '';
        timeHtml = `${resultStr}${dur ? `<span class="dimer"> ${dur}</span>` : ''}`;
      } else {
        timeHtml = `<span class="dimer">✓</span> ${stage.durationMs != null ? _fmtMs(stage.durationMs) : ''}`;
      }
    } else {
      timeHtml = '<span class="dimer">—</span>';
    }

    return `${arrow}<div class="arena-stage-step ${stage.state}" data-type="${stage.type}">
      <div class="arena-stage-label">${escapeHtml(stage.label)}</div>
      <div class="arena-stage-time">${timeHtml}</div>
    </div>`;
  }).join('');

  // Current stage callout (only when active)
  let calloutHtml = '';
  if (activeStage) {
    const models = series.models || {};
    const modelA = escapeHtml(models.team_a || '—');
    const modelB = escapeHtml(models.team_b || '—');
    const totalMatches = series.format === '5-match' ? 5 : 3;
    let desc = '';
    if (activeStage.type === 'cgp') {
      desc = 'Generating strategies';
    } else if (activeStage.type === 'match') {
      desc = `Match ${activeStage.matchNum}/${totalMatches}`;
    } else if (activeStage.type === 'pmep') {
      // Show per-team attempt progress if available
      const keyA = `${activeStage.matchNum}_team_a`;
      const keyB = `${activeStage.matchNum}_team_b`;
      const attA = _pmepAttempts[keyA];
      const attB = _pmepAttempts[keyB];
      if (attA || attB) {
        const fmtTeam = (att) => att ? `${att.attempt}/${att.maxAttempts}` : '…';
        desc = `Evolving · A:${fmtTeam(attA)} B:${fmtTeam(attB)}`;
      } else {
        desc = 'Evolving strategies';
      }
    }

    const elapsed = _elapsedStartedAt != null ? _fmtMs(Date.now() - _elapsedStartedAt) : '0:00';
    const viewLink = (_currentRunningMatchId && activeStage.type === 'match')
      ? ` · <a class="arena-live-match-link" href="#/matches/${_currentRunningMatchId}">view live ↗</a>`
      : '';

    calloutHtml = `<div class="arena-current-callout">
      <span class="arena-running-dot">●</span> ${escapeHtml(desc)} · <span id="arena-live-elapsed">${elapsed}</span>${viewLink}
      <span class="dimer"> · </span><span class="team-a-text">${modelA}</span> <span class="dimer">vs</span> <span class="team-b-text">${modelB}</span>
    </div>`;
  }

  statusEl.innerHTML = `<div class="arena-stage-pipeline">${chipsHtml}</div>${calloutHtml}`;
}

function renderResultBanner(series) {
  const bannerEl = document.getElementById('arena-result-banner');
  if (!bannerEl) return;

  if (series.status === 'errored') {
    bannerEl.removeAttribute('hidden');
    bannerEl.innerHTML = `
      <div class="arena-error-banner">
        <span class="arena-error-banner-icon">✕</span>
        <div>
          <strong>Series failed</strong>
          <div class="arena-error-banner-detail">The strategy generation pipeline encountered an error. Check server logs for details.</div>
        </div>
      </div>
    `;
    return;
  }

  if (series.status !== 'complete' && series.status !== 'tied') {
    bannerEl.setAttribute('hidden', '');
    bannerEl.innerHTML = '';
    return;
  }

  bannerEl.removeAttribute('hidden');

  const score = series.score || { team_a: 0, team_b: 0, ties: 0 };
  const sa = score.team_a;
  const sb = score.team_b;
  const ties = score.ties || 0;

  let headlineHtml;
  let subLine = '';

  if (series.status === 'tied') {
    headlineHtml = `TIE  ${sa} — ${sb}`;
    if (ties > 0) {
      subLine = `<div class="arena-banner-subline">(${ties} match${ties > 1 ? 'es' : ''} drawn)</div>`;
    }
  } else if (sa > sb) {
    headlineHtml = `<span class="team-a-text">TEAM A</span>  WINS  ${sa} — ${sb}`;
  } else if (sb > sa) {
    headlineHtml = `<span class="team-b-text">TEAM B</span>  WINS  ${sb} — ${sa}`;
  } else {
    headlineHtml = `TIE  ${sa} — ${sb}`;
  }

  // Build per-match sequence
  const matches = series.matches || [];
  const sequenceParts = matches.map(m => {
    if (!m.final_score) return '?';
    const msa = m.final_score.team_a;
    const msb = m.final_score.team_b;
    if (m.result === 'team_a') return `<span class="team-a-text">A</span>${msa}-${msb}`;
    if (m.result === 'team_b') return `<span class="team-b-text">B</span>${msb}-${msa}`;
    return `TIE ${msa}-${msb}`;
  });
  const sequenceHtml = sequenceParts.length
    ? `<div class="arena-banner-sequence">Final: ${sequenceParts.join(', ')}</div>`
    : '';

  bannerEl.innerHTML = `
    <div class="arena-banner-headline">${headlineHtml}</div>
    ${subLine}
    ${sequenceHtml}
  `;

  // Emit completed event
  if (window.appBus && currentSeriesId) {
    const winner = sa > sb ? 'team_a' : sb > sa ? 'team_b' : 'tie';
    window.appBus.dispatchEvent(new CustomEvent('arena:seriesCompleted', {
      detail: {
        seriesId: currentSeriesId,
        winner,
        finalScore: { team_a: sa, team_b: sb, ties }
      }
    }));
  }
}

function renderMatchesList(series) {
  const matchListEl = document.getElementById('arena-matches-list');
  if (!matchListEl) return;

  const matches = (series.matches || []).filter(m => m.result && m.result !== 'running');
  if (matches.length === 0) {
    matchListEl.innerHTML = '<div class="dimer" style="padding:16px">No completed matches yet.</div>';
    return;
  }

  matchListEl.innerHTML = matches.map((match, idx) => renderExpandableMatchRow(series.series_id, match, idx)).join('');
}

function renderExpandableMatchRow(seriesId, match, idx) {
  const matchNum = match.match_number || (idx + 1);
  const matchId  = match.match_id || '—';
  const result   = match.result;
  const score    = match.final_score || {};
  const date     = match.completed_iso
    ? new Date(match.completed_iso).toISOString().slice(11, 16)
    : '—';

  let resultBadge = '';
  if (result === 'team_a') {
    resultBadge = `<span class="team-a-text">A ${score.team_a}-${score.team_b}</span>`;
  } else if (result === 'team_b') {
    resultBadge = `<span class="team-b-text">B ${score.team_a}-${score.team_b}</span>`;
  } else if (result === 'tie') {
    resultBadge = `TIE ${score.team_a}-${score.team_b}`;
  } else {
    resultBadge = result || '—';
  }

  const rowId = `arena-match-row-${seriesId}-${matchNum}`;
  const bodyId = `arena-match-body-${seriesId}-${matchNum}`;

  return `
    <div class="arena-expandable-row" id="${rowId}">
      <div class="arena-expandable-row-header">
        <button class="arena-expandable-header"
                aria-expanded="false"
                aria-controls="${bodyId}"
                onclick="window.arenaToggleMatchRow('${rowId}', '${bodyId}')">
          <span class="arena-disclosure">▶</span>
          <span class="arena-match-label">Match ${matchNum}</span>
          <span class="arena-match-result">${resultBadge}</span>
          <span class="arena-match-date dimer">${date}</span>
        </button>
        <button class="btn btn-sm arena-view-match-btn"
                onclick="window.location.hash='#/matches/${matchId}'"
                aria-label="View match ${matchNum}">
          View match ↗
        </button>
      </div>
      <div class="arena-expandable-body" id="${bodyId}" hidden>
        ${renderDiffSubRows(seriesId, matchNum)}
      </div>
    </div>
  `;
}

function renderDiffSubRows(seriesId, matchNum) {
  const teams = ['team_a', 'team_b'];
  return teams.map(team => {
    const subRowId   = `arena-diff-subrow-${seriesId}-${matchNum}-${team}`;
    const diffBodyId = `arena-diff-body-${seriesId}-${matchNum}-${team}`;
    const label = `STRATEGY DIFF (${team === 'team_a' ? 'TEAM A' : 'TEAM B'})`;
    return `
      <div class="arena-diff-subrow" id="${subRowId}">
        <button class="arena-diff-trigger"
                aria-expanded="false"
                aria-controls="${diffBodyId}"
                onclick="window.arenaToggleDiffRow('${subRowId}', '${diffBodyId}', '${seriesId}', '${team}', ${matchNum})">
          <span class="arena-disclosure-inner">▶</span>
          <span class="arena-diff-label">${label}</span>
        </button>
        <div class="arena-diff-body" id="${diffBodyId}" hidden></div>
      </div>
    `;
  }).join('');
}

function renderConfigFooter(series) {
  const footerEl = document.getElementById('arena-config-footer');
  if (!footerEl) return;

  const config = series.config_name || '—';
  const models = series.models || {};
  const modelA = models.team_a || '—';
  const modelB = models.team_b || '—';

  footerEl.innerHTML = `
    <div class="arena-footer-line">CONFIG: ${escapeHtml(config)}</div>
    <div class="arena-footer-line">
      <span>TEAM A: ${escapeHtml(modelA)}</span>
      <span class="arena-footer-sep"> · </span>
      <span>TEAM B: ${escapeHtml(modelB)}</span>
    </div>
  `;
}

// ── Match Row / Diff Expand/Collapse ────────────────────────────

/**
 * Toggle a completed-match expandable row.
 * @param {string} rowId
 * @param {string} bodyId
 */
function arenaToggleMatchRow(rowId, bodyId) {
  const header = document.querySelector(`#${rowId} .arena-expandable-header`);
  const body   = document.getElementById(bodyId);
  if (!header || !body) return;

  const isExpanded = header.getAttribute('aria-expanded') === 'true';
  header.setAttribute('aria-expanded', String(!isExpanded));

  const triangle = header.querySelector('.arena-disclosure');
  if (triangle) triangle.textContent = isExpanded ? '▶' : '▼';

  if (isExpanded) {
    body.setAttribute('hidden', '');
  } else {
    body.removeAttribute('hidden');
  }
}

/**
 * Toggle a strategy diff sub-row. Fetches diff data on first expand.
 * @param {string} subRowId
 * @param {string} diffBodyId
 * @param {string} seriesId
 * @param {string} team
 * @param {number} matchNum
 */
function arenaToggleDiffRow(subRowId, diffBodyId, seriesId, team, matchNum) {
  const trigger  = document.querySelector(`#${subRowId} .arena-diff-trigger`);
  const diffBody = document.getElementById(diffBodyId);
  if (!trigger || !diffBody) return;

  const isExpanded = trigger.getAttribute('aria-expanded') === 'true';
  trigger.setAttribute('aria-expanded', String(!isExpanded));

  const triangle = trigger.querySelector('.arena-disclosure-inner');
  if (triangle) triangle.textContent = isExpanded ? '▶' : '▼';

  if (isExpanded) {
    diffBody.setAttribute('hidden', '');
    return;
  }

  diffBody.removeAttribute('hidden');

  // Check cache first
  const cacheKey = `${seriesId}__${matchNum}__${team}`;
  const cached = diffCache[cacheKey];

  if (cached) {
    if (cached.error) {
      renderDiffError(diffBody, seriesId, team, matchNum);
    } else if (cached.data) {
      renderDiffContent(diffBody, cached.data);
    }
    return;
  }

  // First expand — load diff
  diffBody.innerHTML = '<div class="dimer arena-diff-loading">Loading…</div>';
  loadDiff(diffBody, seriesId, team, matchNum, cacheKey);
}

async function loadDiff(diffBodyEl, seriesId, team, matchNum, cacheKey) {
  try {
    const url = `/api/arena/${encodeURIComponent(seriesId)}/diff/${encodeURIComponent(team)}/${matchNum}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Server returned ${response.status}`);

    const data = await response.json();
    diffCache[cacheKey] = { data, error: null };
    renderDiffContent(diffBodyEl, data);

  } catch (error) {
    console.error('[arena.js] Failed to load diff:', error);
    diffCache[cacheKey] = { data: null, error: error.message };
    renderDiffError(diffBodyEl, seriesId, team, matchNum);
  }
}

function renderDiffContent(diffBodyEl, data) {
  const diffText = data.diff_text || '';
  if (!diffText.trim()) {
    diffBodyEl.innerHTML = '<div class="dimer" style="padding:8px 12px;font-size:11px">No changes between versions.</div>';
    return;
  }

  const lines = diffText.split('\n');
  const htmlLines = lines.map(line => {
    const escaped = escapeHtml(line);
    if (line.startsWith('+') && !line.startsWith('+++')) {
      return `<div class="arena-diff-add">${escaped}</div>`;
    } else if (line.startsWith('-') && !line.startsWith('---')) {
      return `<div class="arena-diff-remove">${escaped}</div>`;
    } else if (line.startsWith('@@')) {
      return `<div class="arena-diff-hunk">${escaped}</div>`;
    } else {
      return `<div class="arena-diff-context">${escaped}</div>`;
    }
  }).join('');

  diffBodyEl.innerHTML = `<section aria-label="Strategy diff for ${escapeHtml(data.team || 'team')}, match ${escapeHtml(String(data.match_num || ''))}">\n  <pre class="arena-diff-viewer">${htmlLines}</pre>\n</section>`;
}

function renderDiffError(diffBodyEl, seriesId, team, matchNum) {
  const cacheKey = `${seriesId}__${matchNum}__${team}`;
  diffBodyEl.innerHTML = `
    <div class="arena-diff-err">
      Could not load diff —
      <button class="arena-diff-retry-link"
              onclick="delete diffCache['${cacheKey}']; window.arenaRetryDiff(this, '${seriesId}', '${team}', ${matchNum})">
        retry
      </button>
    </div>
  `;
}

// ── New Series Sub-view ─────────────────────────────────────────

/**
 * Render the New series sub-view.
 */
function renderArenaNewSubView() {
  currentSubView = 'new';
  currentSeriesId = null;

  _resetStageState();
  closeSseSource();
  showOnlySubView('arena-new-view');
  updateSubtitle('ARENA · NEW');
  mountArenaBackButton('Back to list', '#/arena');

  // Wire cancel button
  const cancelBtn = document.getElementById('arena-cancel-btn');
  if (cancelBtn) cancelBtn.onclick = () => arenaNavigateSubView('list');

  // Wire "Edit configs →" link — persist form first
  const editLink = document.getElementById('arena-edit-configs-link');
  if (editLink) {
    editLink.onclick = (e) => {
      e.preventDefault();
      persistNewForm();
      window.location.hash = '#/config/match';
    };
  }

  // Populate config picker and provider pickers (independent, run in parallel)
  loadConfigsForPicker();
  loadProvidersForPicker();

  // Restore from localStorage (model text values restored inside loadProvidersForPicker)
  restoreNewForm();

  // Wire form events
  setupNewFormEvents();
}

async function loadConfigsForPicker() {
  const selectEl = document.getElementById('arena-config-select');
  if (!selectEl) return;

  try {
    const response = await fetch('/api/config/match');
    if (!response.ok) throw new Error(`Server returned ${response.status}`);
    const configs = await response.json();

    // Restore saved value
    const saved = (() => {
      try { return JSON.parse(localStorage.getItem('ap_arena_lastForm') || '{}').config_name || ''; }
      catch { return ''; }
    })();

    // Clear existing options except the placeholder
    selectEl.innerHTML = '<option value="">— select a config —</option>';
    configs.forEach(cfg => {
      const name = typeof cfg === 'string' ? cfg : (cfg.name || cfg);
      const opt = document.createElement('option');
      opt.value = name;
      opt.textContent = name;
      if (name === saved) opt.selected = true;
      selectEl.appendChild(opt);
    });

    updateEstimatedTime();
  } catch (error) {
    console.error('[arena.js] Failed to load configs:', error);
    if (selectEl) {
      selectEl.innerHTML = '<option value="">Could not load configs</option>';
    }
  }
}

async function loadProvidersForPicker() {
  const selA = document.getElementById('arena-team-a-provider');
  const selB = document.getElementById('arena-team-b-provider');
  if (!selA || !selB) return;

  try {
    const response = await fetch('/api/config');
    if (!response.ok) throw new Error(`Server returned ${response.status}`);
    const cfg = await response.json();

    // /api/config returns { game, llm: { providers: [...], active }, storage, match }
    // providers is an array of { name, url, model, key_status, builtin, type? }
    const llmCfg = cfg.llm || {};
    const providerArray = Array.isArray(llmCfg.providers) ? llmCfg.providers : [];
    loadedProviders = providerArray;

    // Restore saved selections
    const saved = (() => {
      try { return JSON.parse(localStorage.getItem('ap_arena_lastForm') || '{}'); }
      catch { return {}; }
    })();

    [selA, selB].forEach((sel, idx) => {
      const savedVal = idx === 0 ? (saved.team_a_provider || '') : (saved.team_b_provider || '');
      sel.innerHTML = '<option value="">— provider —</option>';
      providerArray.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.name;
        opt.textContent = p.name;
        if (p.name === savedVal) opt.selected = true;
        sel.appendChild(opt);
      });
    });

    // Restore language selections
    const langA = document.getElementById('arena-team-a-language');
    const langB = document.getElementById('arena-team-b-language');
    if (langA && saved.team_a_language) langA.value = saved.team_a_language;
    if (langB && saved.team_b_language) langB.value = saved.team_b_language;

    // Populate model dropdowns for restored providers in parallel.
    // populateModelDropdown uses configLLMTab cache first, then fetches live.
    await Promise.all([
      populateModelDropdown('arena-team-a-model', saved.team_a_provider || '', saved.team_a_model || ''),
      populateModelDropdown('arena-team-b-model', saved.team_b_provider || '', saved.team_b_model || ''),
    ]);

  } catch (error) {
    console.error('[arena.js] Failed to load providers:', error);
    // Non-fatal — user can still proceed (blank = global LLM config)
  }
}

/**
 * Fetch live model list for a provider, mirroring strategies.js fetchAvailableModels.
 * Uses loadedProviders (always available from /api/config) to get type/url for
 * custom providers — never relies on configLLMTab.currentValues.
 *
 * @param {string} providerName
 * @returns {Promise<string[]>} model names, or [] on failure
 */
async function arenaFetchModels(providerName) {
  if (!providerName) return [];
  try {
    const body = { provider: providerName };
    const providerMeta = loadedProviders.find(p => p.name === providerName);
    if (providerMeta && providerMeta.type) {
      body.type = providerMeta.type;
      body.url  = providerMeta.url;
    }
    const response = await fetch('/api/config/llm/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const result = await response.json();
    if (result.ok && Array.isArray(result.models) && result.models.length > 0) {
      return result.models;
    }
  } catch (e) {
    console.warn('[arena.js] arenaFetchModels failed for', providerName, e);
  }
  return [];
}

/**
 * Populate a model <select> for the given provider.
 * 1. Check configLLMTab cache (fast path, available if LLM tab was visited).
 * 2. Live-fetch via arenaFetchModels (works for custom providers — uses loadedProviders for type/url).
 * 3. Fall back to BUILTIN_MODELS + configured model.
 *
 * @param {string} modelSelId   - Element ID of the model <select>
 * @param {string} providerName - Selected provider name (empty = clear)
 * @param {string} savedModel   - Previously-saved model value to pre-select
 */
async function populateModelDropdown(modelSelId, providerName, savedModel) {
  const sel = document.getElementById(modelSelId);
  if (!sel) return;

  sel.innerHTML = '<option value="">— model —</option>';
  sel.disabled = true;

  if (!providerName) return;

  // Provider's configured model from the last /api/config load
  const providerCfg = loadedProviders.find(p => p.name === providerName);
  const configuredModel = providerCfg ? (providerCfg.model || '') : '';

  // 1. Check if config-llm.js already has live models cached for this provider
  const llmTab = window.configLLMTab;
  const cachedModels = llmTab ? (llmTab.getAvailableModels()[providerName] || null) : null;

  let models = cachedModels;

  if (!models) {
    // 2. Live-fetch via arenaFetchModels (includes type/url for custom providers)
    sel.innerHTML = '<option value="">Loading models…</option>';
    const fetched = await arenaFetchModels(providerName);
    if (fetched.length > 0) {
      models = fetched;
    }
  }

  if (!models || models.length === 0) {
    // 3. Fall back: built-in known models + configured model
    const builtins = BUILTIN_MODELS[providerName] || [];
    const fallback = [];
    if (configuredModel) fallback.push(configuredModel);
    builtins.forEach(m => { if (!fallback.includes(m)) fallback.push(m); });
    models = fallback;
  }

  // De-dupe and include any saved model not already in the list
  const finalModels = [...models];
  if (savedModel && !finalModels.includes(savedModel)) finalModels.unshift(savedModel);

  sel.innerHTML = '<option value="">— model —</option>';
  finalModels.forEach(m => {
    const opt = document.createElement('option');
    opt.value = m;
    opt.textContent = m;
    if (m === savedModel || (!savedModel && m === configuredModel)) opt.selected = true;
    sel.appendChild(opt);
  });

  sel.disabled = finalModels.length === 0;
}

function restoreNewForm() {
  try {
    const saved = JSON.parse(localStorage.getItem('ap_arena_lastForm') || '{}');
    const formatInputs = document.querySelectorAll('input[name="series-format"]');
    if (saved.format && formatInputs.length) {
      formatInputs.forEach(input => {
        input.checked = (input.value === saved.format);
      });
    }
    // Config picker is restored in loadConfigsForPicker
    updateEstimatedTime();
  } catch {
    // ignore corrupt localStorage
  }
}

let _persistDebounceTimer = null;
function persistNewForm() {
  clearTimeout(_persistDebounceTimer);
  _persistDebounceTimer = setTimeout(() => {
    try {
      const formatEl  = document.querySelector('input[name="series-format"]:checked');
      const configEl  = document.getElementById('arena-config-select');
      const provAEl  = document.getElementById('arena-team-a-provider');
      const modelAEl = document.getElementById('arena-team-a-model');
      const langAEl  = document.getElementById('arena-team-a-language');
      const provBEl  = document.getElementById('arena-team-b-provider');
      const modelBEl = document.getElementById('arena-team-b-model');
      const langBEl  = document.getElementById('arena-team-b-language');
      const data = {
        format:           formatEl  ? formatEl.value  : '3-match',
        config_name:      configEl  ? configEl.value  : '',
        team_a_provider:  provAEl   ? provAEl.value   : '',
        team_a_model:     modelAEl  ? modelAEl.value  : '',
        team_a_language:  langAEl   ? langAEl.value   : 'python',
        team_b_provider:  provBEl   ? provBEl.value   : '',
        team_b_model:     modelBEl  ? modelBEl.value  : '',
        team_b_language:  langBEl   ? langBEl.value   : 'python',
      };
      localStorage.setItem('ap_arena_lastForm', JSON.stringify(data));
    } catch { /* quota exceeded or private mode */ }
  }, 500);
}

function updateEstimatedTime() {
  const estEl = document.getElementById('arena-est-time');
  if (!estEl) return;

  const formatEl = document.querySelector('input[name="series-format"]:checked');
  const format = formatEl ? formatEl.value : '3-match';
  const n = format === '5-match' ? 5 : 3;

  // Assume ~5 min per match + ~0.5 min PMEP between matches
  const minEst = n * 5 + (n - 1) * 0.5;
  const maxEst = n * 15 + (n - 1) * 2;
  estEl.textContent = `~${Math.round(minEst)}–${Math.round(maxEst)} minutes (${n} matches)`;
}

function setupNewFormEvents() {
  // Series length radio
  const radios = document.querySelectorAll('input[name="series-format"]');
  radios.forEach(radio => {
    radio.onchange = () => {
      updateEstimatedTime();
      persistNewForm();
    };
  });

  // Config picker
  const configSel = document.getElementById('arena-config-select');
  if (configSel) {
    configSel.onchange = () => {
      persistNewForm();
      updateEstimatedTime();
    };
  }

  // Provider change → repopulate model dropdown, then persist
  const provA = document.getElementById('arena-team-a-provider');
  const provB = document.getElementById('arena-team-b-provider');
  if (provA) {
    provA.onchange = async () => {
      await populateModelDropdown('arena-team-a-model', provA.value, '');
      persistNewForm();
    };
  }
  if (provB) {
    provB.onchange = async () => {
      await populateModelDropdown('arena-team-b-model', provB.value, '');
      persistNewForm();
    };
  }
  // Model/language dropdown change → persist
  ['arena-team-a-model', 'arena-team-b-model', 'arena-team-a-language', 'arena-team-b-language'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.onchange = persistNewForm;
  });

  // Form submit
  const formEl = document.getElementById('arena-new-form');
  if (formEl) {
    formEl.onsubmit = (e) => {
      e.preventDefault();
      handleArenaStartSeries();
    };
  }
}

async function handleArenaStartSeries() {
  const configEl  = document.getElementById('arena-config-select');
  const formatEl  = document.querySelector('input[name="series-format"]:checked');
  const startBtn  = document.getElementById('arena-start-btn');
  const errorEl   = document.getElementById('arena-form-error');
  const formEl    = document.getElementById('arena-new-form');
  const provAEl   = document.getElementById('arena-team-a-provider');
  const modelAEl  = document.getElementById('arena-team-a-model');
  const langAEl   = document.getElementById('arena-team-a-language');
  const provBEl   = document.getElementById('arena-team-b-provider');
  const modelBEl  = document.getElementById('arena-team-b-model');
  const langBEl   = document.getElementById('arena-team-b-language');

  const configName    = configEl ? configEl.value.trim() : '';
  const format        = formatEl ? formatEl.value : '3-match';
  const teamAProvider = provAEl  ? provAEl.value.trim()  : '';
  const teamAModel    = modelAEl ? modelAEl.value.trim() : '';
  const teamALanguage = langAEl  ? langAEl.value         : 'python';
  const teamBProvider = provBEl  ? provBEl.value.trim()  : '';
  const teamBModel    = modelBEl ? modelBEl.value.trim() : '';
  const teamBLanguage = langBEl  ? langBEl.value         : 'python';

  // Validate
  if (errorEl) { errorEl.setAttribute('hidden', ''); errorEl.textContent = ''; }
  if (!configName) {
    if (errorEl) {
      errorEl.removeAttribute('hidden');
      errorEl.textContent = 'Please select a config before starting.';
    }
    if (configEl) configEl.setAttribute('aria-invalid', 'true');
    return;
  }
  if (configEl) configEl.removeAttribute('aria-invalid');

  // Submit
  if (startBtn) { startBtn.disabled = true; startBtn.textContent = 'Starting…'; }
  if (formEl) {
    Array.from(formEl.elements).forEach(el => { el.disabled = true; });
  }

  const body = { config_name: configName, format };
  if (teamAProvider)                        body.team_a_provider = teamAProvider;
  if (teamAModel)                           body.team_a_model    = teamAModel;
  if (teamALanguage && teamALanguage !== 'python') body.team_a_language = teamALanguage;
  if (teamBProvider)                        body.team_b_provider = teamBProvider;
  if (teamBModel)                           body.team_b_model    = teamBModel;
  if (teamBLanguage && teamBLanguage !== 'python') body.team_b_language = teamBLanguage;

  try {
    const response = await fetch('/api/arena', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      const detail = Array.isArray(err.detail)
        ? err.detail.map(e => e.msg || JSON.stringify(e)).join('; ')
        : (err.detail || err.error || `Server returned ${response.status}`);
      throw new Error(detail);
    }

    const result = await response.json();
    const newSeriesId = result.series_id;

    // Clear saved form on success
    try { localStorage.removeItem('ap_arena_lastForm'); } catch {}

    // Emit event
    if (window.appBus) {
      window.appBus.dispatchEvent(new CustomEvent('arena:seriesStarted', {
        detail: { seriesId: newSeriesId, format, configName }
      }));
    }

    // Navigate to detail
    arenaNavigateSubView('detail', newSeriesId);

  } catch (error) {
    console.error('[arena.js] Failed to start series:', error);
    if (errorEl) {
      errorEl.removeAttribute('hidden');
      errorEl.textContent = `Could not start series: ${error.message}`;
    }
    // Re-enable form
    if (startBtn) { startBtn.disabled = false; startBtn.textContent = 'Start series'; }
    if (formEl) {
      Array.from(formEl.elements).forEach(el => { el.disabled = false; });
    }
  }
}

// ── SSE for live series updates ─────────────────────────────────

function openSseSource(seriesId) {
  closeSseSource();
  try {
    sseSource = new EventSource(`/api/arena/${encodeURIComponent(seriesId)}/stream`);

    sseSource.addEventListener('match-started', (e) => {
      try {
        const data = JSON.parse(e.data);
        _currentRunningMatchId = data.match_id || null;
        const startMs = _isoToMs(data.started_at);
        if (startMs) _stageTimestamps[`match${data.match_number}_started`] = startMs;
        // Timer lifecycle managed by loadSeriesDetail
        if (window.appBus) {
          window.appBus.dispatchEvent(new CustomEvent('arena:matchStarted', { detail: data }));
        }
        if (currentSeriesId === seriesId) loadSeriesDetail(seriesId);
      } catch {}
    });

    sseSource.addEventListener('match-completed', (e) => {
      try {
        const data = JSON.parse(e.data);
        _currentRunningMatchId = null;
        const endMs = _isoToMs(data.completed_at);
        if (endMs) _stageTimestamps[`match${data.match_number}_completed`] = endMs;
        if (window.appBus) {
          window.appBus.dispatchEvent(new CustomEvent('arena:matchCompleted', { detail: data }));
        }
        if (currentSeriesId === seriesId) loadSeriesDetail(seriesId);
      } catch {}
    });

    sseSource.addEventListener('pmep-running', (e) => {
      try {
        const data = JSON.parse(e.data);
        const startMs = _isoToMs(data.started_at);
        if (startMs) _stageTimestamps[`pmep${data.match_number}_started`] = startMs;
        if (window.appBus) {
          window.appBus.dispatchEvent(new CustomEvent('arena:pmepRunning', { detail: data }));
        }
        if (currentSeriesId === seriesId) loadSeriesDetail(seriesId);
      } catch {}
    });

    sseSource.addEventListener('pmep-attempt', (e) => {
      try {
        const data = JSON.parse(e.data);
        const key = `${data.match_number}_${data.team_id}`;
        _pmepAttempts[key] = { attempt: data.attempt, maxAttempts: data.max_attempts, provider: data.provider };
        if (currentSeriesId === seriesId) renderStagePipeline(currentSeriesData);
      } catch {}
    });

    sseSource.addEventListener('pmep-attempt-failed', (e) => {
      try {
        const data = JSON.parse(e.data);
        const key = `${data.match_number}_${data.team_id}`;
        const prev = _pmepAttempts[key] || {};
        _pmepAttempts[key] = { ...prev, failed: true, reason: data.reason };
        if (currentSeriesId === seriesId) renderStagePipeline(currentSeriesData);
      } catch {}
    });

    sseSource.addEventListener('series-completed', () => {
      closeSseSource();  // close before loadSeriesDetail so !sseSource check doesn't reopen
      if (currentSeriesId === seriesId) loadSeriesDetail(seriesId);
    });

    sseSource.addEventListener('series-errored', () => {
      closeSseSource();
      if (currentSeriesId === seriesId) loadSeriesDetail(seriesId);
    });

    sseSource.onerror = () => {
      console.warn('[arena.js] SSE connection closed or errored');
    };

  } catch (error) {
    console.error('[arena.js] Failed to open SSE source:', error);
  }
}

function closeSseSource() {
  _currentRunningMatchId = null;
  if (sseSource) {
    sseSource.close();
    sseSource = null;
  }
}

// ── Delete Series ───────────────────────────────────────────────

function arenaDeleteSeries(seriesId) {
  // Find the series to get match count for cascade-delete hint
  const series = seriesListData.find(s => s.series_id === seriesId);
  const matchCount = series && series.matches ? series.matches.length : 0;

  // Ask about cascade deletion first, then show type-to-confirm modal.
  let cascade = false;
  if (matchCount > 0) {
    cascade = window.confirm(
      `Also delete the ${matchCount} constituent match log${matchCount !== 1 ? 's' : ''} inside this series?\n\n` +
      `OK = delete series + match logs\nCancel = delete series directory only`
    );
  }

  const bodyText = cascade
    ? `This removes the series directory and all ${matchCount} match log${matchCount !== 1 ? 's' : ''} permanently.`
    : 'This removes the series directory permanently (match logs kept).';

  showDeleteConfirmModal({
    title: `Delete series ${seriesId}?`,
    body: bodyText,
    expectedText: seriesId,
    onConfirm: async (ctx) => {
      ctx.setBusy('Deleting…');
      try {
        const url = cascade
          ? `/api/arena/${encodeURIComponent(seriesId)}?cascade=true`
          : `/api/arena/${encodeURIComponent(seriesId)}`;
        const response = await fetch(url, { method: 'DELETE' });
        if (!response.ok && response.status !== 204) {
          ctx.setError('Delete Failed');
          console.error(`[arena.js] DELETE /api/arena/${seriesId} → ${response.status}`);
          return;
        }
        ctx.close();

        if (window.appBus) {
          window.appBus.dispatchEvent(new CustomEvent('arena:seriesDeleted', {
            detail: { seriesId, cascade }
          }));
        }

        await loadSeriesList();
        console.log(`[arena.js] Successfully deleted series: ${seriesId} (cascade=${cascade})`);
      } catch (error) {
        ctx.setError('Delete Failed');
        console.error('[arena.js] Delete series error:', error);
      }
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

// ── Main Section API ────────────────────────────────────────────

/**
 * Called by app.js router when the section=arena.
 * @param {{ section: string, subsection: string }} route
 */
function arenaHandleRoute(route = {}) {
  console.log('[arena.js] arenaHandleRoute called with route:', route);

  // Show arena section, hide other sections
  const allSectionIds = ['section-matches', 'section-strategies', 'section-arena', 'section-config', 'section-cup', 'section-league'];
  allSectionIds.forEach(sectionId => {
    const el = document.getElementById(sectionId);
    if (!el) return;
    if (sectionId === 'section-arena') {
      el.removeAttribute('hidden');
    } else {
      el.setAttribute('hidden', '');
    }
  });

  const { subView, seriesId } = parseRoute(route);

  if (subView === 'list') {
    renderArenaListSubView();
  } else if (subView === 'detail') {
    renderArenaDetailSubView(seriesId);
  } else if (subView === 'new') {
    renderArenaNewSubView();
  }
}

/**
 * Called when the Arena section becomes visible (section shown).
 */
function arenaOnSectionShown() {
  console.log('[arena.js] Arena section shown');
}

/**
 * Called when the Arena section is hidden (navigating away).
 */
function arenaOnSectionHidden() {
  console.log('[arena.js] Arena section hidden — closing SSE');
  closeSseSource();
  unmountArenaBackButton();
  dismissOpenDeleteConfirmModal();
}

// ── Export Section Object (matches app.js router contract) ──────
window.arenaSection = {
  activate: arenaHandleRoute,
  deactivate: arenaOnSectionHidden
};

// ── Window Globals (all arena-prefixed) ─────────────────────────
window.arenaHandleRoute = arenaHandleRoute;
window.arenaOnSectionShown = arenaOnSectionShown;
window.arenaOnSectionHidden = arenaOnSectionHidden;
window.arenaNavigateSubView = arenaNavigateSubView;
window.arenaOpenSeriesDetail = (seriesId) => arenaNavigateSubView('detail', seriesId);
window.arenaDeleteSeries = arenaDeleteSeries;
window.arenaToggleMatchRow = arenaToggleMatchRow;
window.arenaToggleDiffRow = arenaToggleDiffRow;
window.arenaRetryList = loadSeriesList;
window.arenaRetryDetail = loadSeriesDetail;
window.arenaRetryDiff = (btn, seriesId, team, matchNum) => {
  const diffBodyId = `arena-diff-body-${seriesId}-${matchNum}-${team}`;
  const diffBodyEl = document.getElementById(diffBodyId);
  if (!diffBodyEl) return;
  const cacheKey = `${seriesId}__${matchNum}__${team}`;
  diffBodyEl.innerHTML = '<div class="dimer arena-diff-loading">Loading…</div>';
  loadDiff(diffBodyEl, seriesId, team, matchNum, cacheKey);
};

// Listen for config updates to refresh the picker
if (window.appBus) {
  window.appBus.addEventListener('config:matchConfigSaved', () => {
    if (currentSubView === 'new') loadConfigsForPicker();
  });
  window.appBus.addEventListener('config:matchConfigDeleted', () => {
    if (currentSubView === 'new') loadConfigsForPicker();
  });
}

console.log('[arena.js] Arena section module loaded');
