// Agent Pitch — Matches Section Module
// Phase 3a: List + Replay sub-views with full routing
// Manages List view of past matches, "+ Start a new match" (placeholder), and Replay integration

import { showDeleteConfirmModal, dismissOpenDeleteConfirmModal } from './modals.js';

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ── State ───────────────────────────────────────────────────────
let currentSubView = 'list';  // 'list' | 'replay' | 'new'
let currentMatchId = null;
let matchesData = [];
let isLoading = false;

// ── Sub-view Routing ────────────────────────────────────────────
function parseRoute(route) {
  // Expected format: { section: 'matches', subsection: '' | '<match_id>' | 'new' }
  const { section, subsection } = route;

  if (section !== 'matches') return { subView: 'list', matchId: null };

  if (!subsection) {
    return { subView: 'list', matchId: null };
  } else if (subsection === 'new') {
    return { subView: 'new', matchId: null };
  } else {
    return { subView: 'replay', matchId: subsection };
  }
}

function navigateToSubView(subView, matchId = null) {
  const route = matchId
    ? `#/matches/${matchId}`
    : `#/matches${subView === 'new' ? '/new' : ''}`;

  window.location.hash = route;
}

// ── List Sub-view Implementation ────────────────────────────────
function renderListSubView() {
  currentSubView = 'list';
  currentMatchId = null;

  if (window.matchStats) window.matchStats.clear();

  // Hide live viewer DOM + Start sub-view, show list view container
  hideAllLiveViewerDOM();
  hideStartSubViewContainer();
  showListViewContainer();

  // Update subtitle
  updateSubtitle('MATCHES');

  // Load and render matches
  loadMatches();
}

function hideAllLiveViewerDOM() {
  // Hide the live viewer components that are normally visible
  const liveViewerElements = [
    'field-canvas',
    'goal-flash',
    'goal-chyron',
    'play-pause',
    'scrub-track',
    'tick-display',
    'speed-pill',
    'event-log-sidebar',
    'stats-toggle',
    'match-stats-panel',
  ];

  liveViewerElements.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.style.display = 'none';
    }
  });

  // Also hide the chyron and body containers
  const chyron = document.querySelector('#section-matches .chyron');
  const body = document.querySelector('#section-matches .body');

  if (chyron) chyron.style.display = 'none';
  if (body) body.style.display = 'none';
}

function showAllLiveViewerDOM() {
  // Show the live viewer components
  const liveViewerElements = [
    'field-canvas',
    'goal-flash',
    'goal-chyron',
    'play-pause',
    'scrub-track',
    'tick-display',
    'speed-pill',
    'event-log-sidebar'
  ];

  liveViewerElements.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.style.display = '';
    }
  });

  // Show the chyron and body containers
  const chyron = document.querySelector('#section-matches .chyron');
  const body = document.querySelector('#section-matches .body');

  if (chyron) chyron.style.display = '';
  if (body) body.style.display = '';
}

function showListViewContainer() {
  let listView = document.getElementById('matches-list-view');

  if (!listView) {
    listView = document.createElement('div');
    listView.id = 'matches-list-view';

    // Insert at the top of #section-matches
    const matchesSection = document.getElementById('section-matches');
    if (matchesSection && matchesSection.firstChild) {
      matchesSection.insertBefore(listView, matchesSection.firstChild);
    } else if (matchesSection) {
      matchesSection.appendChild(listView);
    }
  }

  listView.style.display = '';
}

function hideListViewContainer() {
  const listView = document.getElementById('matches-list-view');
  if (listView) {
    listView.style.display = 'none';
  }
}

function hideStartSubViewContainer() {
  const startContainer = document.getElementById('start-subview-container');
  if (startContainer) {
    startContainer.style.display = 'none';
    if (window.matchesStartView && typeof window.matchesStartView.unmount === 'function') {
      window.matchesStartView.unmount();
    }
  }
}

async function loadMatches() {
  if (isLoading) return;

  isLoading = true;

  try {
    renderLoadingState();

    const response = await fetch('/api/matches');
    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }

    matchesData = await response.json();
    renderMatchesList();

  } catch (error) {
    console.error('[matches.js] Failed to load matches:', error);
    renderErrorState();
  } finally {
    isLoading = false;
  }
}

function renderLoadingState() {
  const listView = document.getElementById('matches-list-view');
  if (!listView) return;

  listView.innerHTML = `
    <div class="list-action-bar">
      <button class="btn btn-primary" disabled>+ Start a new match</button>
      <div class="list-count">Loading...</div>
    </div>
    <div class="list-body matches-list">
      ${generateSkeletonRows(4)}
    </div>
  `;
}

function generateSkeletonRows(count) {
  return Array(count).fill(0).map(() => `
    <div class="list-row skeleton">
      <div class="list-row-line-1">TEAM A —:— TEAM B   loading   loading</div>
      <div class="list-row-line-2">loading · seed — · —min</div>
      <div class="list-row-actions">
        <button class="btn btn-sm" disabled>View</button>
        <button class="btn btn-sm btn-danger" disabled>Del</button>
      </div>
    </div>
  `).join('');
}

function renderErrorState() {
  const listView = document.getElementById('matches-list-view');
  if (!listView) return;

  listView.innerHTML = `
    <div class="list-action-bar">
      <button class="btn btn-primary" onclick="navigateMatchesSubView('new')">+ Start a new match</button>
      <div class="list-count">Error</div>
    </div>
    <div class="list-error">
      <div class="error-message">Could not load matches — server unreachable</div>
      <button class="btn" onclick="loadMatches()">Retry</button>
    </div>
  `;
}

function renderMatchesList() {
  const listView = document.getElementById('matches-list-view');
  if (!listView) return;

  if (matchesData.length === 0) {
    renderEmptyState();
    return;
  }

  const matchCount = matchesData.length;
  const rowsHTML = matchesData.map(renderMatchRow).join('');

  listView.innerHTML = `
    <div class="list-action-bar">
      <button class="btn btn-primary" onclick="navigateMatchesSubView('new')">+ Start a new match</button>
      <div class="list-count">${matchCount} matches</div>
    </div>
    <div class="list-body matches-list">
      ${rowsHTML}
    </div>
  `;

  setupMatchRowEventHandlers();
}

function renderEmptyState() {
  const listView = document.getElementById('matches-list-view');
  if (!listView) return;

  listView.innerHTML = `
    <div class="list-empty-state">
      <div class="empty-heading">no matches yet</div>
      <div class="empty-subtext">start your first one to see it here</div>
      <button class="btn btn-primary btn-lg" onclick="navigateMatchesSubView('new')">+ Start a new match</button>
    </div>
  `;
}

function renderMatchRow(match) {
  const { final_score, models, strategies, date_iso, config_name, seed, duration_sec } = match;

  // Format date
  const date = new Date(date_iso);
  const dateStr = date.toISOString().slice(0, 16).replace('T', ' ');

  // Format duration
  const minutes = Math.floor(duration_sec / 60);
  const durationStr = `${minutes}min`;

  // Format score with team colors
  const teamA = (match.team_names && match.team_names.team_a) || 'TEAM A';
  const teamB = (match.team_names && match.team_names.team_b) || 'TEAM B';
  const scoreText = `<span class="team-a-score">${escapeHtml(teamA)} ${final_score.team_a}</span>:<span class="team-b-score">${final_score.team_b} ${escapeHtml(teamB)}</span>`;

  // Per-team label: when a team used the seeded baseline.py, models.team_x
  // is "baseline" (provider+model uninformative) — so swap in the strategy
  // file-stem name from strategies.team_x to disambiguate. Library strategies
  // generated by an LLM keep the provider/model display (per ADR-0023 the
  // sidecar carries truthful values now, so models.team_x is e.g.
  // "anthropic/claude-sonnet-4-6", not the old "baseline" placeholder).
  const teamLabel = (model, name) => (model === 'baseline' && name) ? name : model;
  const labelA = teamLabel(models.team_a, strategies?.team_a);
  const labelB = teamLabel(models.team_b, strategies?.team_b);
  const modelsText = `${labelA} vs ${labelB}`;

  const safeId = escapeHtml(match.match_id);
  // Accessible name read by screen readers — Pattern 8 (Selectable List Row).
  const ariaLabel = `Match ${safeId}, ${final_score.team_a} to ${final_score.team_b}, ${config_name}, ${dateStr}`;

  return `
    <div class="list-row" data-match-id="${safeId}">
      <div class="list-row-content"
           role="button"
           tabindex="0"
           aria-label="${ariaLabel}"
           onclick="openMatchReplay('${safeId}')"
           onkeydown="if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); openMatchReplay('${safeId}'); }">
        <div class="list-row-line-1">${scoreText}   ${modelsText}   ${dateStr}</div>
        <div class="list-row-line-2">${config_name} · seed ${seed} · ${durationStr}</div>
      </div>
      <div class="list-row-actions">
        <button class="btn btn-sm" onclick="openMatchReplay('${safeId}')" aria-label="View match ${safeId}">View</button>
        <button class="btn btn-sm btn-danger" onclick="openDeleteConfirm('${safeId}')" aria-label="Delete match ${safeId}">Del</button>
      </div>
    </div>
  `;
}

function setupMatchRowEventHandlers() {
  // Event handlers are set up via onclick attributes in renderMatchRow
  // No additional setup needed for Phase 3a
}

// ── Replay Sub-view Implementation ──────────────────────────────
function renderReplaySubView(matchId) {
  currentSubView = 'replay';
  currentMatchId = matchId;

  // Hide list view + Start sub-view, show live viewer DOM
  hideListViewContainer();
  hideStartSubViewContainer();
  showAllLiveViewerDOM();

  if (window.matchStats) window.matchStats.load(matchId);

  // Update subtitle with match ID
  // Subtitle stays "MATCHES" on replay — the per-match identity (match_id +
  // seed) lives in the chyron's brand block, no need to duplicate up top.
  updateSubtitle('MATCHES');

  // Add back button to right cap (if live viewer allows)
  addReplayBackButton();

  // Tell app.js to re-fetch for THIS match (its bootstrap only ran once at
  // page load; without this call the viewer keeps showing whichever match
  // was active at initial load).
  console.log(`[matches.js] renderReplaySubView called for: ${matchId}`);
  console.log(`[matches.js] window.reloadLiveViewer is: ${typeof window.reloadLiveViewer}`);
  if (typeof window.reloadLiveViewer === 'function') {
    console.log(`[matches.js] calling window.reloadLiveViewer()...`);
    window.reloadLiveViewer();
  } else {
    console.error(`[matches.js] reloadLiveViewer NOT DEFINED — app.js didn't expose it. Stale cached app.js?`);
  }
}

function addReplayBackButton() {
  const rightCap = document.getElementById('right-cap');
  if (!rightCap) return;

  // Check if back button already exists
  if (rightCap.querySelector('.replay-back-btn')) return;

  const backBtn = document.createElement('button');
  backBtn.className = 'btn-link replay-back-btn';
  backBtn.textContent = 'Back to list';
  backBtn.onclick = () => navigateToSubView('list');

  // Clear existing content and add back button
  rightCap.innerHTML = '';
  rightCap.appendChild(backBtn);
}

function removeReplayBackButton() {
  const rightCap = document.getElementById('right-cap');
  if (rightCap) {
    const backBtn = rightCap.querySelector('.replay-back-btn');
    if (backBtn) {
      backBtn.remove();
    }
  }
}

// ── New Sub-view (Phase 3b implementation) ──────────────────────
function renderNewSubView() {
  currentSubView = 'new';
  currentMatchId = null;

  if (window.matchStats) window.matchStats.clear();

  // Hide live viewer DOM and list view
  hideAllLiveViewerDOM();
  hideListViewContainer();

  updateSubtitle('MATCHES · NEW');

  const matchesSection = document.getElementById('section-matches');
  if (!matchesSection) return;

  // Create or reuse a sibling container for the Start sub-view.
  // Do NOT wipe matchesSection.innerHTML — that would destroy the live-viewer
  // DOM (chyron/canvas/scrub/events) which Replay needs.
  let container = document.getElementById('start-subview-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'start-subview-container';
    container.className = 'start-subview-container';
    matchesSection.appendChild(container);
  }
  // Use empty string so the CSS rule (display: flex) wins; explicit 'block'
  // would shrink the container vertically inside its flex-column parent.
  container.style.display = '';

  // Diagnostic fallback: if the Start module isn't loaded, render a visible
  // error so the page never appears blank.
  if (window.matchesStartView && typeof window.matchesStartView.mount === 'function') {
    try {
      window.matchesStartView.mount(container);
    } catch (err) {
      console.error('[matches.js] matchesStartView.mount threw:', err);
      container.innerHTML = `
        <div style="padding:40px;color:#f2c14b;font-family:monospace;">
          <h3>Start sub-view crashed</h3>
          <pre>${String(err && err.stack || err)}</pre>
        </div>`;
    }
  } else {
    console.error('[matches.js] window.matchesStartView is undefined — script tag missing?');
    container.innerHTML = `
      <div style="padding:40px;color:#f2c14b;font-family:monospace;">
        Start sub-view module not loaded.
        Check that <code>&lt;script&gt;</code> tag for matches-start.js is in index.html.
      </div>`;
  }
}

// ── Match Actions ───────────────────────────────────────────────
function openMatchReplay(matchId) {
  navigateToSubView('replay', matchId);
}

function openDeleteConfirm(matchId) {
  showDeleteConfirmModal({
    title: `Delete match ${matchId}?`,
    body: 'This removes its log directory permanently.',
    expectedText: matchId,
    onConfirm: async (ctx) => {
      ctx.setBusy('Deleting…');
      const response = await fetch(`/api/matches/${matchId}`, { method: 'DELETE' });
      if (!response.ok) {
        ctx.setError('Delete Failed');
        console.error(`[matches.js] DELETE /api/matches/${matchId} → ${response.status}`);
        return;
      }
      ctx.close();
      await loadMatches();
      console.log(`[matches.js] Successfully deleted match: ${matchId}`);
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
  console.log('[matches.js] Activating with route:', route);

  // Show matches section, hide other sections
  const sectionsToHide = ['section-strategies', 'section-arena', 'section-config', 'section-cup', 'section-league'];
  const matchesSection = document.getElementById('section-matches');

  if (matchesSection) {
    matchesSection.removeAttribute('hidden');
  }

  sectionsToHide.forEach(sectionId => {
    const sectionEl = document.getElementById(sectionId);
    if (sectionEl) {
      sectionEl.setAttribute('hidden', '');
    }
  });

  // Parse route and render appropriate sub-view
  const { subView, matchId } = parseRoute(route);

  if (subView === 'list') {
    removeReplayBackButton();
    renderListSubView();
  } else if (subView === 'replay') {
    renderReplaySubView(matchId);
  } else if (subView === 'new') {
    removeReplayBackButton();
    renderNewSubView();
  }
}

function deactivate() {
  // Hide the matches section
  const matchesSection = document.getElementById('section-matches');
  if (matchesSection) {
    matchesSection.setAttribute('hidden', '');
  }

  // Clean up any modals
  dismissOpenDeleteConfirmModal();
  removeReplayBackButton();

  console.log('[matches.js] Deactivated matches section');
}

// ── Export Section Object ───────────────────────────────────────
window.matchesSection = {
  activate,
  deactivate
};

// Expose handlers that inline onclick="..." attributes call. Without these,
// `<script type="module">` keeps the functions in module scope and clicks
// silently fail because window.<name> is undefined.
window.navigateMatchesSubView = navigateToSubView;
window.loadMatches = loadMatches;
window.openMatchReplay = openMatchReplay;
window.openDeleteConfirm = openDeleteConfirm;
// closeDeleteModal / confirmDeleteMatch removed 2026-04-25 — the shared
// modals.js helper wires its own event listeners; no inline onclick refs
// remain to need a window-global.

// ── Event Feed collapse toggle ──────────────────────────────────
(function initEventFeedToggle() {
  const STORAGE_KEY = 'ap:event-feed-collapsed';
  const sidebar = document.getElementById('event-log-sidebar');
  const body = document.querySelector('#section-matches .body');
  const btn = document.getElementById('event-feed-toggle');
  if (!sidebar || !body || !btn) return;

  function setCollapsed(collapsed) {
    sidebar.classList.toggle('collapsed', collapsed);
    body.classList.toggle('event-feed-collapsed', collapsed);
    btn.setAttribute('aria-expanded', String(!collapsed));
    btn.title = collapsed ? 'Expand event feed' : 'Collapse event feed';
    btn.setAttribute('aria-label', collapsed ? 'Expand event feed' : 'Collapse event feed');
    try { localStorage.setItem(STORAGE_KEY, collapsed ? '1' : '0'); } catch (_) {}
  }

  btn.addEventListener('click', () => setCollapsed(!sidebar.classList.contains('collapsed')));

  // Restore persisted state
  try {
    if (localStorage.getItem(STORAGE_KEY) === '1') setCollapsed(true);
  } catch (_) {}
})();

console.log('[matches.js] Matches section module loaded (Phase 3a)');