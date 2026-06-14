// Agent Pitch — Match Statistics Panel Module
// Fetches GET /api/match/stats and renders a team-summary + per-player table
// below the scrub bar when a completed match is viewed.
//
// Public API (window.matchStats):
//   load(matchId)  — fetch stats for matchId, show panel
//   hide()         — hide panel and toggle button
//   clear()        — reset to empty state (call on navigation away)

'use strict';

(function () {
  let _statsCache = null;
  let _visible = false;
  let _fetching = false;

  // ── Public API ────────────────────────────────────────────────────────────

  window.matchStats = {
    load(matchId) {
      _hidePanel();
      _statsCache = null;
      _visible = false;
      _showButton(matchId);
    },

    hide() {
      _hidePanel();
      _hideButton();
    },

    clear() {
      _statsCache = null;
      _visible = false;
      _fetching = false;
      _hidePanel();
      _hideButton();
    },
  };

  // ── Button wiring ─────────────────────────────────────────────────────────

  function _showButton(matchId) {
    const btn = document.getElementById('stats-toggle');
    if (!btn) return;
    btn.removeAttribute('hidden');
    btn.style.display = '';    // clear any inline style from hideAllLiveViewerDOM
    btn.classList.remove('active');
    // Re-wire click on each load to bind the current matchId
    btn.onclick = () => _toggle(matchId);
  }

  function _hideButton() {
    const btn = document.getElementById('stats-toggle');
    if (btn) {
      btn.setAttribute('hidden', '');
      btn.classList.remove('active');
      btn.onclick = null;
    }
  }

  // ── Panel toggle ──────────────────────────────────────────────────────────

  async function _toggle(matchId) {
    if (_fetching) return;  // ignore clicks while fetch is in-flight

    const panel = document.getElementById('match-stats-panel');
    const btn = document.getElementById('stats-toggle');
    if (!panel) return;

    if (_visible) {
      _hidePanel();
      if (btn) btn.classList.remove('active');
      _visible = false;
      return;
    }

    _visible = true;
    if (btn) btn.classList.add('active');
    panel.removeAttribute('hidden');
    panel.style.display = '';   // clear inline style from hideAllLiveViewerDOM
    panel.classList.add('stats-fullview');

    // Hide the field area so the stats panel fills the vacated space
    const body = document.querySelector('#section-matches .body');
    if (body) body.style.display = 'none';

    if (_statsCache) {
      _renderStats(panel, _statsCache);
      return;
    }

    _fetching = true;
    _renderLoading(panel);
    try {
      const resp = await fetch(`/api/match/stats?match_id=${encodeURIComponent(matchId)}`);
      if (resp.status === 409) {
        _renderError(panel, 'Match still in progress — stats available after completion.');
        return;
      }
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      _statsCache = await resp.json();
      _renderStats(panel, _statsCache);
    } catch (err) {
      console.error('[match-stats.js] fetch failed:', err);
      _renderError(panel, 'Could not load match statistics.');
    } finally {
      _fetching = false;
    }
  }

  function _hidePanel() {
    const panel = document.getElementById('match-stats-panel');
    if (panel) {
      panel.setAttribute('hidden', '');
      panel.classList.remove('stats-fullview');
    }
    // Restore the field area when leaving fullview stats
    const body = document.querySelector('#section-matches .body');
    if (body) body.style.display = '';
  }

  // ── Rendering ─────────────────────────────────────────────────────────────

  function _renderLoading(panel) {
    panel.innerHTML = '<div class="stats-loading">Computing statistics…</div>';
  }

  function _renderError(panel, msg) {
    panel.innerHTML = `<div class="stats-error">${_esc(msg)}</div>`;
  }

  function _renderStats(panel, stats) {
    const teams = stats.teams || {};
    const players = stats.players || {};
    const ta = teams.team_a || {};
    const tb = teams.team_b || {};

    panel.innerHTML = `
      <div class="stats-panel-header">
        <span>MATCH STATISTICS</span>
      </div>
      <div class="stats-panel-body">
        ${_teamSummaryHtml(ta, tb)}
        ${_playerSectionHtml(players, { team_a: ta.name, team_b: tb.name })}
      </div>
    `;
  }

  function _teamSummaryHtml(ta, tb) {
    const rows = [
      ['Possession',    _pct(ta.possession_pct),       _pct(tb.possession_pct)],
      ['Goals',         ta.goals ?? 0,                  tb.goals ?? 0],
      ['Assists',       ta.assists ?? 0,                tb.assists ?? 0],
      ['Shots',         ta.shots ?? 0,                  tb.shots ?? 0],
      ['Shots on target', ta.shots_on_target ?? 0,      tb.shots_on_target ?? 0],
      ['Passes (attempted)', ta.passes_attempted ?? 0,   tb.passes_attempted ?? 0],
      ['Tackles',       ta.tackles_attempted ?? 0,       tb.tackles_attempted ?? 0],
      ['Tackles won',   ta.tackles_successful ?? 0,      tb.tackles_successful ?? 0],
      ['Dribbles',      ta.dribbles_attempted ?? 0,      tb.dribbles_attempted ?? 0],
      ['Dribbles won',  ta.dribbles_successful ?? 0,     tb.dribbles_successful ?? 0],
      ['GK saves (caught)', ta.gk_saves_caught ?? 0,    tb.gk_saves_caught ?? 0],
      ['GK saves (parried)', ta.gk_saves_parried ?? 0,  tb.gk_saves_parried ?? 0],
      ['Corners',       ta.oob_corners ?? 0,             tb.oob_corners ?? 0],
      ['Throw-ins',     ta.oob_throw_ins ?? 0,           tb.oob_throw_ins ?? 0],
      ['Goal kicks',    ta.oob_goal_kicks ?? 0,          tb.oob_goal_kicks ?? 0],
      ['Offsides',      ta.offsides ?? 0,                tb.offsides ?? 0],
      // Issue #38 (IFAB Law 12): fouls, cards, penalties.
      ['Fouls',         ta.fouls ?? 0,                   tb.fouls ?? 0],
      ['Yellow cards',  ta.yellow_cards ?? 0,            tb.yellow_cards ?? 0],
      ['Red cards',     ta.red_cards ?? 0,               tb.red_cards ?? 0],
      ['Penalties (scored)',
        `${ta.penalties_scored ?? 0}/${ta.penalties_awarded ?? 0}`,
        `${tb.penalties_scored ?? 0}/${tb.penalties_awarded ?? 0}`],
      // Engine-specific metrics
      ['Callback failures', _engineVal(ta.callback_failures ?? 0), _engineVal(tb.callback_failures ?? 0), true],
    ];

    const rowsHtml = rows.map(([label, aVal, bVal, isEngine]) => `
      <tr>
        <td>${_esc(label)}</td>
        <td class="${isEngine ? 'val-engine' : 'val-a'}">${_esc(String(aVal))}</td>
        <td class="${isEngine ? 'val-engine' : 'val-b'}">${_esc(String(bVal))}</td>
      </tr>
    `).join('');

    return `
      <div class="stats-team-section">
        <div class="stats-section-label">Team Summary</div>
        <table class="stats-team-table" aria-label="Team statistics">
          <thead>
            <tr>
              <th></th>
              <th class="col-a">TEAM A</th>
              <th class="col-b">TEAM B</th>
            </tr>
          </thead>
          <tbody>${rowsHtml}</tbody>
        </table>
      </div>
    `;
  }

  function _playerSectionHtml(players, teamLabels) {
    const teamAPlayers = Object.entries(players)
      .filter(([, p]) => p.team === 'team_a')
      .sort(([, a], [, b]) => a.number - b.number);
    const teamBPlayers = Object.entries(players)
      .filter(([, p]) => p.team === 'team_b')
      .sort(([, a], [, b]) => a.number - b.number);

    return `
      <div class="stats-players-section">
        <div class="stats-section-label">Per Player</div>
        ${_teamPlayerTableHtml('team_a', teamLabels.team_a || 'TEAM A', teamAPlayers)}
        ${_teamPlayerTableHtml('team_b', teamLabels.team_b || 'TEAM B', teamBPlayers)}
      </div>
    `;
  }

  function _teamPlayerTableHtml(teamId, label, entries) {
    const isA = teamId === 'team_a';
    const labelClass = isA ? 'team-label-a' : 'team-label-b';
    label = label.toUpperCase();

    const rowsHtml = entries.map(([pid, p]) => {
      const numTag = p.number ? `#${p.number}` : pid.replace('team_a_', '#').replace('team_b_', '#');
      const shortPid = p.name ? `${p.name} ${numTag}` : numTag;
      const gkCols = p.role === 'GK'
        ? `<td>${p.gk_saves_caught ?? 0}/${(p.gk_saves_caught ?? 0) + (p.gk_saves_parried ?? 0)}</td>`
        : `<td class="val-dim">—</td>`;
      return `
        <tr>
          <td class="pid-cell">${_esc(shortPid)}</td>
          <td class="role-cell">${_esc(p.role)}</td>
          <td>${p.goals ?? 0}</td>
          <td>${p.assists ?? 0}</td>
          <td>${p.shots ?? 0}</td>
          <td>${p.shots_on_target ?? 0}</td>
          <td>${p.passes_attempted ?? 0}</td>
          <td>${p.tackles_attempted ?? 0}/${p.tackles_successful ?? 0}</td>
          <td>${p.dribbles_attempted ?? 0}/${p.dribbles_successful ?? 0}</td>
          ${gkCols}
          <td class="dist-cell">${p.distance_run?.toFixed(0) ?? '—'}m</td>
          <td>${p.callback_failures ?? 0}</td>
        </tr>
      `;
    }).join('');

    return `
      <details class="stats-team-detail" open>
        <summary><span class="${labelClass}">${label}</span> PLAYERS</summary>
        <table class="stats-player-table" aria-label="${label} player statistics">
          <thead>
            <tr>
              <th>#</th><th>Role</th><th>G</th><th title="Assists">A</th><th>Sh</th><th>SoT</th>
              <th>Pass</th><th>Tkl W/A</th><th>Drb W/A</th><th>GK Sv</th>
              <th>Dist</th><th title="Callback failures">CB Fail</th>
            </tr>
          </thead>
          <tbody>${rowsHtml}</tbody>
        </table>
      </details>
    `;
  }

  // ── Formatters ────────────────────────────────────────────────────────────

  function _pct(val) {
    if (val == null) return '—';
    return `${val.toFixed(1)}%`;
  }

  function _engineVal(val) {
    // Engine-specific metric — display as plain number
    return val;
  }

  function _esc(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
})();
