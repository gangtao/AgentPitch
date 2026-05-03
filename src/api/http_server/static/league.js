// Agent Pitch — League Section Module
// Implements 3 sub-views: List, Detail, New
// Route pattern: #/league | #/league/new | #/league/<league_id>

// ── State ───────────────────────────────────────────────────────
let currentSubView = 'list';
let currentLeagueId = null;
let leagueListData = [];
let currentLeagueData = null;
let sseSource = null;

// ── Sub-view Routing ────────────────────────────────────────────

function parseRoute(route) {
  const { section, subsection } = route;
  if (section !== 'league') return { subView: 'list', leagueId: null };
  if (!subsection) return { subView: 'list', leagueId: null };
  if (subsection === 'new') return { subView: 'new', leagueId: null };
  return { subView: 'detail', leagueId: subsection };
}

function leagueNavigateSubView(subView, leagueId = null) {
  if (subView === 'detail' && leagueId) {
    window.location.hash = `#/league/${leagueId}`;
  } else if (subView === 'new') {
    window.location.hash = '#/league/new';
  } else {
    window.location.hash = '#/league';
  }
}

// ── Right-cap back button ───────────────────────────────────────

function mountLeagueBackButton(label, targetHash) {
  const rightCap = document.getElementById('right-cap');
  if (!rightCap) return;
  if (rightCap.querySelector('.league-back-btn')) return;
  const btn = document.createElement('button');
  btn.className = 'btn-link league-back-btn';
  btn.textContent = label;
  btn.onclick = () => { window.location.hash = targetHash; };
  rightCap.innerHTML = '';
  rightCap.appendChild(btn);
}

function unmountLeagueBackButton() {
  const rightCap = document.getElementById('right-cap');
  const btn = rightCap && rightCap.querySelector('.league-back-btn');
  if (btn) btn.remove();
}

// ── Sub-view visibility ─────────────────────────────────────────

function showOnlySubView(activeId) {
  ['league-list-view', 'league-detail-view', 'league-new-view'].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    id === activeId ? el.removeAttribute('hidden') : el.setAttribute('hidden', '');
  });
}

function updateSubtitle(text) {
  window.dispatchEvent(new CustomEvent('shell:subtitleChanged', {
    detail: { subtitle: text }
  }));
}

// ── Status badge ────────────────────────────────────────────────

function leagueStatusBadge(status) {
  if (status === 'running') return `<span class="league-status-badge running"><span class="league-running-dot">●</span> RUNNING</span>`;
  if (status === 'complete') return `<span class="league-status-badge complete">COMPLETE</span>`;
  if (status === 'errored') return `<span class="league-status-badge errored">ERRORED</span>`;
  return `<span class="league-status-badge pending">PENDING</span>`;
}

function escapeHtml(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// ── SSE ─────────────────────────────────────────────────────────

function closeSseSource() {
  if (sseSource) { sseSource.close(); sseSource = null; }
}

function openSseSource(leagueId) {
  closeSseSource();
  sseSource = new EventSource(`/api/leagues/${encodeURIComponent(leagueId)}/stream`);

  sseSource.addEventListener('league-match-completed', (e) => {
    try {
      const data = JSON.parse(e.data);
      updateMatchRow(data);
    } catch {}
  });

  sseSource.addEventListener('league-matchday-started', (e) => {
    try {
      const data = JSON.parse(e.data);
      updateMatchdayStatus(data.matchday_number, 'running');
    } catch {}
  });

  sseSource.addEventListener('league-match-started', (e) => {
    try {
      const data = JSON.parse(e.data);
      updateMatchRowStatus(data.match_slot, data.match_id, 'running');
    } catch {}
  });

  sseSource.addEventListener('league-matchday-completed', (e) => {
    try {
      const data = JSON.parse(e.data);
      updateMatchdayStatus(data.matchday_number, 'complete');
      if (currentLeagueData && data.standings) {
        currentLeagueData.standings = data.standings;
        renderStandings(currentLeagueData.standings);
      }
    } catch {}
  });

  sseSource.addEventListener('league-completed', (e) => {
    closeSseSource();
    loadLeagueDetail(leagueId);
  });

  sseSource.addEventListener('league-errored', () => {
    closeSseSource();
    loadLeagueDetail(leagueId);
  });
}

function updateMatchRow(data) {
  const { match_slot, result, score } = data;
  const rowEl = document.querySelector(`[data-match-slot="${escapeHtml(match_slot)}"]`);
  if (!rowEl) return;
  const scoreEl = rowEl.querySelector('.league-match-score');
  const resultEl = rowEl.querySelector('.league-match-result');
  const linkEl = rowEl.querySelector('.league-match-link');
  if (scoreEl) scoreEl.textContent = score ? `${score.team_a}–${score.team_b}` : '—';
  if (resultEl) resultEl.textContent = result ? result.replace('_', ' ').toUpperCase() : '';
  if (linkEl) linkEl.textContent = '▶ replay';
  rowEl.dataset.status = 'complete';
}

function updateMatchRowStatus(matchSlot, matchId, status) {
  const rowEl = document.querySelector(`[data-match-slot="${escapeHtml(matchSlot)}"]`);
  if (!rowEl) return;
  rowEl.dataset.status = status;
  if (matchId) {
    const linkEl = rowEl.querySelector('.league-match-link');
    if (linkEl) {
      linkEl.textContent = '▶ watching';
      linkEl.setAttribute('href', `#/matches/${encodeURIComponent(matchId)}`);
    }
  }
}

function updateMatchdayStatus(matchdayNumber, status) {
  const el = document.querySelector(`[data-matchday="${matchdayNumber}"]`);
  if (!el) return;
  el.dataset.status = status;
  const statusEl = el.querySelector('.league-matchday-status');
  if (statusEl) statusEl.textContent = status.toUpperCase();
}

// ── List Sub-view ────────────────────────────────────────────────

function renderLeagueListSubView() {
  currentSubView = 'list';
  currentLeagueId = null;
  closeSseSource();
  showOnlySubView('league-list-view');
  updateSubtitle('LEAGUE');
  unmountLeagueBackButton();
  loadLeagueList();
}

async function loadLeagueList() {
  const listEl = document.getElementById('league-list');
  const countEl = document.getElementById('league-count');
  if (listEl) listEl.innerHTML = '<div class="league-list-row skeleton"><div class="dimer">Loading leagues…</div></div>';

  try {
    const response = await fetch('/api/leagues');
    if (!response.ok) throw new Error(`${response.status}`);
    leagueListData = await response.json();
  } catch (err) {
    if (listEl) listEl.innerHTML = '<div class="league-list-error"><div class="league-error-message">Could not load leagues — server unreachable</div></div>';
    return;
  }

  if (countEl) countEl.textContent = `${leagueListData.length} league${leagueListData.length !== 1 ? 's' : ''}`;

  if (!listEl) return;
  if (leagueListData.length === 0) {
    listEl.innerHTML = `
      <div class="league-empty-state">
        <div class="league-empty-heading">No leagues yet — create your first league</div>
        <button class="btn btn-primary" onclick="window.leagueNavigateSubView('new')">+ Create a new league</button>
      </div>`;
    return;
  }
  listEl.innerHTML = leagueListData.map(renderLeagueRow).join('');
}

function renderLeagueRow(league) {
  const { league_id, name, status, team_count, num_rounds, created_iso, champion } = league;
  const date = created_iso ? new Date(created_iso).toLocaleDateString() : '—';
  const championHtml = champion ? ` <span class="league-champion-badge">🏆 ${escapeHtml(champion)}</span>` : '';
  return `
    <div class="league-list-row" role="listitem" data-league-id="${escapeHtml(league_id)}">
      <div class="league-row-content"
           tabindex="0" role="button"
           aria-label="League ${escapeHtml(name || league_id)}"
           onclick="window.leagueOpenDetail('${escapeHtml(league_id)}')"
           onkeydown="if (event.key==='Enter'||event.key===' '){event.preventDefault();window.leagueOpenDetail('${escapeHtml(league_id)}');}">
        <div class="league-row-line-1">${escapeHtml(name || league_id)}${championHtml}</div>
        <div class="league-row-line-2">${team_count} teams · ${num_rounds === 2 ? 'double' : 'single'} round-robin · ${date}</div>
      </div>
      <div class="league-row-meta">
        ${leagueStatusBadge(status)}
        <button class="btn btn-sm" onclick="window.leagueOpenDetail('${escapeHtml(league_id)}')" aria-label="View league ${escapeHtml(league_id)}">View</button>
      </div>
    </div>
  `;
}

// ── Detail Sub-view ──────────────────────────────────────────────

function renderLeagueDetailSubView(leagueId) {
  currentSubView = 'detail';
  currentLeagueId = leagueId;
  closeSseSource();
  showOnlySubView('league-detail-view');
  updateSubtitle('LEAGUE · DETAIL');
  mountLeagueBackButton('Back to list', '#/league');
  loadLeagueDetail(leagueId);
}

async function loadLeagueDetail(leagueId) {
  const headerEl = document.getElementById('league-detail-header');
  if (headerEl) headerEl.innerHTML = '<div class="dimer">Loading…</div>';

  try {
    const response = await fetch(`/api/leagues/${encodeURIComponent(leagueId)}`);
    if (!response.ok) {
      if (response.status === 404) {
        if (headerEl) headerEl.innerHTML = `<div class="league-error-message">League "${escapeHtml(leagueId)}" not found</div>`;
        return;
      }
      throw new Error(`${response.status}`);
    }
    currentLeagueData = await response.json();
    renderLeagueDetail(currentLeagueData);
    if (['running', 'pending'].includes(currentLeagueData.status) && !sseSource) {
      openSseSource(leagueId);
    }
  } catch (err) {
    if (headerEl) headerEl.innerHTML = `<div class="league-error-message">Could not load league — server unreachable</div>`;
  }
}

function renderLeagueDetail(league) {
  renderLeagueHeader(league);
  renderStandings(league.standings || []);
  renderMatchdays(league);
  renderLeagueResultBanner(league);
}

function renderLeagueHeader(league) {
  const headerEl = document.getElementById('league-detail-header');
  if (!headerEl) return;
  const totalMatchdays = (league.matchdays || []).length;
  const completedMatchdays = (league.matchdays || []).filter(md => md.status === 'complete').length;
  const progressText = league.status === 'complete'
    ? 'Complete'
    : `Matchday ${completedMatchdays + 1} of ${totalMatchdays}`;
  headerEl.innerHTML = `
    <div class="league-detail-title">${escapeHtml(league.name || league.league_id)}</div>
    <div class="league-detail-meta">
      ${leagueStatusBadge(league.status)}
      <span class="dimer">${escapeHtml(league.config_name)} · ${(league.teams || []).length} teams · ${league.num_rounds === 2 ? 'double' : 'single'} round-robin</span>
      <span class="dimer">${escapeHtml(progressText)}</span>
    </div>
  `;
}

function renderLeagueResultBanner(league) {
  const bannerEl = document.getElementById('league-result-banner');
  if (!bannerEl) return;
  if (league.status === 'complete' && league.champion) {
    bannerEl.innerHTML = `<span class="league-champion-text">🏆 Champion: ${escapeHtml(league.champion)}</span>`;
    bannerEl.removeAttribute('hidden');
  } else {
    bannerEl.setAttribute('hidden', '');
  }
}

function renderStandings(standings) {
  const container = document.getElementById('league-standings-container');
  if (!container) return;
  if (!standings || standings.length === 0) {
    container.innerHTML = '<div class="dimer">No standings yet</div>';
    return;
  }
  const rows = standings.map(s => `
    <tr class="league-standing-row ${s.rank === 1 ? 'league-leader' : ''}">
      <td class="league-rank">${s.rank}</td>
      <td class="league-team-name">${escapeHtml(s.strategy_name)}</td>
      <td>${s.played}</td>
      <td>${s.won}</td>
      <td>${s.drawn}</td>
      <td>${s.lost}</td>
      <td>${s.goals_for}</td>
      <td>${s.goals_against}</td>
      <td>${s.goal_diff >= 0 ? '+' : ''}${s.goal_diff}</td>
      <td class="league-pts"><strong>${s.points}</strong></td>
    </tr>
  `).join('');
  container.innerHTML = `
    <h3 class="league-section-heading">Standings</h3>
    <table class="league-standings-table">
      <thead>
        <tr>
          <th>#</th><th>Team</th><th>P</th><th>W</th><th>D</th><th>L</th>
          <th>GF</th><th>GA</th><th>GD</th><th>Pts</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderMatchdays(league) {
  const container = document.getElementById('league-matchdays-container');
  if (!container) return;
  const matchdays = league.matchdays || [];
  const slotToName = {};
  (league.teams || []).forEach(t => { slotToName[t.slot] = t.strategy_name; });

  const runningIdx = matchdays.findIndex(md => md.status === 'running');
  const firstPendingIdx = matchdays.findIndex(md => md.status === 'pending');
  const expandIdx = runningIdx >= 0 ? runningIdx : firstPendingIdx >= 0 ? firstPendingIdx : matchdays.length - 1;

  const sections = matchdays.map((md, idx) => {
    const isOpen = idx === expandIdx;
    const matchRows = (md.matches || []).map(m => {
      const nameA = escapeHtml(slotToName[m.team_a_slot] || `Slot ${m.team_a_slot}`);
      const nameB = escapeHtml(slotToName[m.team_b_slot] || `Slot ${m.team_b_slot}`);
      const score = m.final_score ? `${m.final_score.team_a}–${m.final_score.team_b}` : '—';
      const result = m.result ? m.result.replace('_', ' ').toUpperCase() : '';
      const linkLabel = m.status === 'running' ? '▶ watching' : m.status === 'complete' ? '▶ replay' : '';
      const linkHtml = (m.match_id && linkLabel)
        ? `<a href="#/matches/${encodeURIComponent(m.match_id)}" class="league-match-link">${linkLabel}</a>`
        : `<span class="league-match-link"></span>`;
      return `
        <div class="league-match-row" data-match-slot="${escapeHtml(m.match_slot)}" data-status="${m.status}">
          <span class="league-match-teams">${nameA} vs ${nameB}</span>
          <span class="league-match-score">${score}</span>
          <span class="league-match-result">${result}</span>
          ${linkHtml}
        </div>
      `;
    }).join('');
    return `
      <details class="league-matchday" data-matchday="${md.matchday_number}" data-status="${md.status}" ${isOpen ? 'open' : ''}>
        <summary class="league-matchday-summary">
          Matchday ${md.matchday_number}
          <span class="league-matchday-status">${md.status.toUpperCase()}</span>
        </summary>
        <div class="league-matchday-matches">${matchRows}</div>
      </details>
    `;
  }).join('');

  container.innerHTML = `<h3 class="league-section-heading">Matchdays</h3>${sections}`;
}

// ── New League Sub-view ──────────────────────────────────────────

function renderLeagueNewSubView() {
  currentSubView = 'new';
  closeSseSource();
  showOnlySubView('league-new-view');
  updateSubtitle('LEAGUE · NEW');
  mountLeagueBackButton('Back to list', '#/league');
  initLeagueNewForm();
}

async function initLeagueNewForm() {
  // Populate config dropdown
  const configSelect = document.getElementById('league-config-select');
  if (configSelect) {
    configSelect.innerHTML = '<option value="">— select a config —</option>';
    try {
      const resp = await fetch('/api/config/match');
      if (resp.ok) {
        const configs = await resp.json();
        configs.forEach(c => {
          const opt = document.createElement('option');
          opt.value = c.name;
          opt.textContent = c.name;
          configSelect.appendChild(opt);
        });
      }
    } catch {}
  }

  // Populate team picker from strategy library
  const pickerEl = document.getElementById('league-team-picker');
  if (pickerEl) {
    try {
      const resp = await fetch('/api/strategies');
      if (resp.ok) {
        const strategies = await resp.json();
        pickerEl.innerHTML = strategies.map(s => `
          <label class="league-team-checkbox">
            <input type="checkbox" name="league-team" value="${escapeHtml(s.name)}"
                   onchange="window._leagueUpdateTeamCount()">
            ${escapeHtml(s.name)}
          </label>
        `).join('');
      }
    } catch {}
  }

  // Form submission
  const form = document.getElementById('league-new-form');
  if (form) {
    form.onsubmit = async (e) => {
      e.preventDefault();
      await submitLeagueForm();
    };
  }

  // Cancel button
  const cancelBtn = document.getElementById('league-cancel-btn');
  if (cancelBtn) cancelBtn.onclick = () => leagueNavigateSubView('list');
}

window._leagueUpdateTeamCount = function() {
  const checked = document.querySelectorAll('input[name="league-team"]:checked');
  const label = document.getElementById('league-team-count-label');
  if (label) {
    const n = checked.length;
    const even = n % 2 === 0;
    label.textContent = `${n} selected${n > 0 && !even ? ' — must be even' : ''}`;
    label.className = `league-team-count-label ${!even && n > 0 ? 'league-count-error' : 'dimer'}`;
  }
};

async function submitLeagueForm() {
  const nameInput = document.getElementById('league-name-input');
  const configSelect = document.getElementById('league-config-select');
  const roundsRadio = document.querySelector('input[name="league-rounds"]:checked');
  const selectedTeams = Array.from(document.querySelectorAll('input[name="league-team"]:checked')).map(el => el.value);
  const errorEl = document.getElementById('league-form-error');

  if (errorEl) errorEl.setAttribute('hidden', '');

  const name = nameInput ? nameInput.value.trim() : '';
  const configName = configSelect ? configSelect.value : '';
  const numRounds = roundsRadio ? parseInt(roundsRadio.value, 10) : 1;

  if (!name) { showLeagueFormError('League name is required.'); return; }
  if (!configName) { showLeagueFormError('Please select a config.'); return; }
  if (selectedTeams.length < 2) { showLeagueFormError('Select at least 2 strategies.'); return; }
  if (selectedTeams.length % 2 !== 0) { showLeagueFormError('Number of strategies must be even.'); return; }
  if (selectedTeams.length > 32) { showLeagueFormError('Maximum 32 strategies.'); return; }

  const submitBtn = document.getElementById('league-submit-btn');
  if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Creating…'; }

  try {
    const response = await fetch('/api/leagues', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        config_name: configName,
        num_rounds: numRounds,
        strategies: selectedTeams,
      }),
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      const detail = body.detail || `Server error ${response.status}`;
      showLeagueFormError(detail);
      return;
    }
    const { league_id } = await response.json();
    leagueNavigateSubView('detail', league_id);
  } catch (err) {
    showLeagueFormError('Network error — could not reach server.');
  } finally {
    if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = 'Create League'; }
  }
}

function showLeagueFormError(msg) {
  const errorEl = document.getElementById('league-form-error');
  if (!errorEl) return;
  errorEl.textContent = msg;
  errorEl.removeAttribute('hidden');
}

// ── Route Handler (called by shell.js) ──────────────────────────

function leagueHandleRoute(route = {}) {
  // Show league section, hide all others
  const allSectionIds = [
    'section-matches', 'section-strategies', 'section-arena',
    'section-cup', 'section-config', 'section-league'
  ];
  allSectionIds.forEach(sectionId => {
    const el = document.getElementById(sectionId);
    if (!el) return;
    if (sectionId === 'section-league') {
      el.removeAttribute('hidden');
    } else {
      el.setAttribute('hidden', '');
    }
  });

  const { subView, leagueId } = parseRoute(route);
  if (subView === 'detail' && leagueId) {
    renderLeagueDetailSubView(leagueId);
  } else if (subView === 'new') {
    renderLeagueNewSubView();
  } else {
    renderLeagueListSubView();
  }
}

function leagueOnSectionEnter(route) {
  leagueHandleRoute(route);
}

function leagueOnSectionLeave() {
  closeSseSource();
  unmountLeagueBackButton();
}

// ── Export Section Object (matches shell.js router contract) ────
window.leagueSection = {
  activate: leagueHandleRoute,
  deactivate: leagueOnSectionLeave,
};

// ── Public API (window exports) ──────────────────────────────────

window.leagueHandleRoute    = leagueHandleRoute;
window.leagueOnSectionEnter = leagueOnSectionEnter;
window.leagueOnSectionLeave = leagueOnSectionLeave;
window.leagueNavigateSubView = leagueNavigateSubView;
window.leagueOpenDetail = (id) => leagueNavigateSubView('detail', id);
window.leagueRetryList  = loadLeagueList;
