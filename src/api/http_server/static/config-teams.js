// Agent Pitch — Config Teams Tab Module
// Implements list / editor / new sub-views for /api/config/teams.

let rootElement = null;
let currentSubView = 'list';
let currentSlug = null;
let savedFormData = {};
let currentFormData = {};

const apiBase = () => (window.shell ? window.shell.getApiBase() : `${window.location.protocol}//${window.location.host}`);

// ── Sub-view routing ────────────────────────────────────────────
function parseTeamsSubRoute() {
  const hash = window.location.hash.slice(1);
  const parts = hash.split('/').filter(p => p);
  if (parts[0] !== 'config' || parts[1] !== 'teams') return { subView: 'list', slug: null };
  if (parts.length === 2) return { subView: 'list', slug: null };
  if (parts[2] === 'new') return { subView: 'new', slug: null };
  return { subView: 'editor', slug: parts[2] };
}

function navigateToSubView(subView, slug = null) {
  const route = slug ? `#/config/teams/${slug}` : (subView === 'new' ? '#/config/teams/new' : '#/config/teams');
  if (window.location.hash !== route) {
    window.location.hash = route;
  }
  renderSubView(subView, slug);
}

function renderSubView(subView, slug = null) {
  currentSubView = subView;
  currentSlug = slug;
  if (!rootElement) return;
  if (subView === 'list') {
    renderListSubView();
  } else if (subView === 'editor' && slug) {
    renderEditorSubView(slug);
  } else if (subView === 'new') {
    renderNewSubView();
  }
}

// ── List sub-view ───────────────────────────────────────────────
async function renderListSubView() {
  rootElement.innerHTML = `
    <div class="config-teams-list">
      <div class="config-teams-list-header">
        <h3>Teams</h3>
        <button class="btn btn-primary" id="new-team-btn">+ New team</button>
      </div>
      <div id="teams-table"></div>
    </div>
  `;
  document.getElementById('new-team-btn').onclick = () => navigateToSubView('new');
  await refreshList();
}

async function refreshList() {
  let data;
  try {
    const res = await fetch(`${apiBase()}/api/config/teams`);
    if (!res.ok) throw new Error(res.statusText);
    data = await res.json();
  } catch (e) {
    document.getElementById('teams-table').innerHTML = `<p class="error">Failed to load teams: ${e.message}</p>`;
    return;
  }
  const teams = data.teams || {};
  if (Object.keys(teams).length === 0) {
    document.getElementById('teams-table').innerHTML = `<p class="empty">No teams yet. Click "+ New team" to create one.</p>`;
    return;
  }
  const html = Object.entries(teams).map(([slug, t]) => `
    <div class="team-row" data-slug="${slug}">
      <span class="team-slug">${slug}</span>
      <span class="team-name">${t.name || ''}</span>
      <span class="team-size">${(t.players || []).length} players</span>
      <button class="btn" data-action="edit">Edit</button>
      <button class="btn btn-danger" data-action="delete">Delete</button>
    </div>
  `).join('');
  document.getElementById('teams-table').innerHTML = html;
  document.querySelectorAll('.team-row').forEach(row => {
    const slug = row.dataset.slug;
    row.querySelector('[data-action="edit"]').onclick = () => navigateToSubView('editor', slug);
    row.querySelector('[data-action="delete"]').onclick = () => handleDelete(slug);
  });
}

async function handleDelete(slug) {
  if (!confirm(`Delete team "${slug}"?`)) return;
  const res = await fetch(`${apiBase()}/api/config/teams/${slug}`, { method: 'DELETE' });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const err = await res.json();
      detail = err.detail || detail;
    } catch (_) { /* ignore */ }
    alert(`Delete failed: ${detail}`);
    return;
  }
  await refreshList();
}

// ── Editor / New sub-views ──────────────────────────────────────
async function renderEditorSubView(slug) {
  let data;
  try {
    const res = await fetch(`${apiBase()}/api/config/teams/${slug}`);
    if (!res.ok) throw new Error(res.statusText);
    data = await res.json();
  } catch (e) {
    rootElement.innerHTML = `<p class="error">Team not found: ${slug} (${e.message})</p>`;
    return;
  }
  savedFormData = data;
  currentFormData = JSON.parse(JSON.stringify(data));
  renderEditorForm(slug, /*isNew=*/false);
}

function renderNewSubView() {
  savedFormData = {
    team_id: '',
    name: '',
    players: [
      { role: 'GK', save: 16, name: 'Player 1' },
      { role: 'DEF', name: 'Player 2' },
      { role: 'DEF', name: 'Player 3' },
      { role: 'MID', name: 'Player 4' },
      { role: 'FWD', name: 'Player 5' },
    ],
  };
  currentFormData = JSON.parse(JSON.stringify(savedFormData));
  renderEditorForm(null, /*isNew=*/true);
}

function renderEditorForm(slug, isNew) {
  const tid = currentFormData.team_id ?? '';
  const tname = currentFormData.name ?? '';
  const idDisabled = isNew ? '' : 'disabled';
  rootElement.innerHTML = `
    <div class="config-teams-editor">
      <label class="config-field">
        <span>Team ID (slug)</span>
        <input id="team-id-input" value="${tid}" ${idDisabled} pattern="^[a-z0-9_-]+$" maxlength="64">
      </label>
      <label class="config-field">
        <span>Display name</span>
        <input id="team-name-input" value="${tname}" maxlength="64">
      </label>
      <h4>Roster</h4>
      <div class="players-header-row">
        <span class="hdr-name">Name</span>
        <span class="hdr-num">#</span>
        <span class="hdr-role">Role</span>
        <span class="hdr-attr" title="Speed">SPD</span>
        <span class="hdr-attr" title="Skill">SKL</span>
        <span class="hdr-attr" title="Strength">STR</span>
        <span class="hdr-attr" title="Save (GK only)">SAV</span>
        <span class="hdr-attr" title="Discipline">DIS</span>
        <span class="hdr-attr" title="Dribbling">DRB</span>
        <span class="hdr-attr" title="Passing (blank = skill)">PAS</span>
        <span class="hdr-attr" title="Shooting (blank = skill)">SHO</span>
        <span class="hdr-attr" title="Stamina (blank = 10)">STA</span>
        <span class="hdr-del"></span>
      </div>
      <div id="players-table"></div>
      <button class="btn" id="add-player-btn">+ Add player</button>
    </div>
  `;
  document.getElementById('team-id-input').oninput = (e) => {
    currentFormData.team_id = e.target.value;
    markDirty();
  };
  document.getElementById('team-name-input').oninput = (e) => {
    currentFormData.name = e.target.value;
    markDirty();
  };
  document.getElementById('add-player-btn').onclick = () => {
    if (currentFormData.players.length >= 11) {
      alert('Maximum 11 players per team');
      return;
    }
    currentFormData.players.push({ role: 'DEF', name: `Player ${currentFormData.players.length + 1}` });
    renderPlayersTable();
    markDirty();
  };
  renderPlayersTable();
}

function renderPlayersTable() {
  const tbl = document.getElementById('players-table');
  if (!tbl) return;

  const attrHtml = (p, key, min, max, placeholder = '') => {
    const v = p[key];
    const value = (v === undefined || v === null) ? '' : v;
    return `<input class="p-attr p-${key}" type="number" min="${min}" max="${max}" placeholder="${placeholder}" value="${value}">`;
  };

  tbl.innerHTML = currentFormData.players.map((p, i) => {
    const isGK = p.role === 'GK';
    const saveCell = isGK
      ? `<input class="p-attr p-save" type="number" min="0" max="20" placeholder="0" value="${p.save ?? ''}">`
      : `<input class="p-attr p-save" type="number" min="0" max="20" placeholder="—" value="" disabled>`;
    return `
      <div class="player-row" data-i="${i}">
        <input class="p-name" placeholder="Name" value="${(p.name ?? '').replace(/"/g, '&quot;')}" maxlength="64">
        <input class="p-num" type="number" min="0" max="99" placeholder="#" value="${p.number ?? ''}">
        <select class="p-role">
          ${['GK','DEF','MID','FWD'].map(r => `<option value="${r}" ${p.role===r?'selected':''}>${r}</option>`).join('')}
        </select>
        ${attrHtml(p, 'speed', 1, 20)}
        ${attrHtml(p, 'skill', 1, 20)}
        ${attrHtml(p, 'strength', 1, 20)}
        ${saveCell}
        ${attrHtml(p, 'discipline', 1, 20)}
        ${attrHtml(p, 'dribbling', 1, 20)}
        ${attrHtml(p, 'passing', 1, 20, '—')}
        ${attrHtml(p, 'shooting', 1, 20, '—')}
        ${attrHtml(p, 'stamina', 1, 20, '10')}
        <button class="btn btn-danger p-del" ${currentFormData.players.length <= 5 ? 'disabled' : ''}>×</button>
      </div>
    `;
  }).join('');

  // Wire up per-row handlers
  tbl.querySelectorAll('.player-row').forEach(row => {
    const i = +row.dataset.i;
    row.querySelector('.p-name').oninput = (e) => {
      currentFormData.players[i].name = e.target.value;
      markDirty();
    };
    row.querySelector('.p-num').oninput = (e) => {
      const v = e.target.value === '' ? null : +e.target.value;
      if (v === null) delete currentFormData.players[i].number;
      else currentFormData.players[i].number = v;
      markDirty();
    };
    row.querySelector('.p-role').onchange = (e) => {
      currentFormData.players[i].role = e.target.value;
      if (e.target.value === 'GK') {
        if (currentFormData.players[i].save === undefined) {
          currentFormData.players[i].save = 16;
        }
      } else {
        delete currentFormData.players[i].save;
      }
      renderPlayersTable();  // re-render to flip the save cell enabled/disabled
      markDirty();
    };

    const wireAttr = (key, isInt = true) => {
      const el = row.querySelector(`.p-${key}`);
      if (!el) return;
      el.oninput = (e) => {
        const raw = e.target.value;
        if (raw === '') {
          delete currentFormData.players[i][key];
        } else {
          currentFormData.players[i][key] = isInt ? parseInt(raw, 10) : parseFloat(raw);
        }
        markDirty();
      };
    };
    wireAttr('speed');
    wireAttr('skill');
    wireAttr('strength');
    wireAttr('save');
    wireAttr('discipline');
    wireAttr('dribbling');
    wireAttr('passing');
    wireAttr('shooting');
    wireAttr('stamina');

    row.querySelector('.p-del').onclick = () => {
      if (currentFormData.players.length <= 5) {
        alert('Minimum 5 players per team');
        return;
      }
      currentFormData.players.splice(i, 1);
      renderPlayersTable();
      markDirty();
    };
  });
}

// ── Dirty / valid state ─────────────────────────────────────────
function markDirty() {
  const dirty = JSON.stringify(savedFormData) !== JSON.stringify(currentFormData);
  window.dispatchEvent(new CustomEvent('config:tabDirtyChanged', {
    detail: { tab: 'teams', dirty, valid: validateForm() }
  }));
}

function validateForm() {
  if (!currentFormData.team_id || !/^[a-z0-9_-]+$/.test(currentFormData.team_id)) return false;
  if (!currentFormData.name || currentFormData.name.length > 64) return false;
  if (!currentFormData.players || currentFormData.players.length < 5 || currentFormData.players.length > 11) return false;
  const gkCount = currentFormData.players.filter(p => p.role === 'GK').length;
  if (gkCount !== 1) return false;
  return true;
}

// ── Save / discard / reset ──────────────────────────────────────
async function save() {
  if (!validateForm()) {
    alert('Form invalid: check team_id (lowercase letters/digits/_-), name (1-64 chars), 5-11 players, exactly one GK.');
    return;
  }
  const slug = currentFormData.team_id;
  // Strip empty fields per player so role defaults apply server-side
  const body = {
    team_id: currentFormData.team_id,
    name: currentFormData.name,
    players: currentFormData.players.map(p => {
      const out = { role: p.role };
      if (p.name) out.name = p.name;
      if (p.number !== undefined && p.number !== null && p.number !== '') out.number = +p.number;
      if (p.role === 'GK' && p.save !== undefined) out.save = p.save;
      if (p.speed !== undefined) out.speed = +p.speed;
      if (p.skill !== undefined) out.skill = +p.skill;
      if (p.strength !== undefined) out.strength = +p.strength;
      if (p.discipline !== undefined) out.discipline = +p.discipline;
      if (p.dribbling !== undefined) out.dribbling = +p.dribbling;
      if (p.passing !== undefined) out.passing = +p.passing;
      if (p.shooting !== undefined) out.shooting = +p.shooting;
      if (p.stamina !== undefined) out.stamina = +p.stamina;
      return out;
    }),
  };
  const res = await fetch(`${apiBase()}/api/config/teams/${slug}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const err = await res.json();
      detail = err.detail || detail;
    } catch (_) { /* ignore */ }
    alert(`Save failed: ${detail}`);
    return;
  }
  savedFormData = JSON.parse(JSON.stringify(currentFormData));
  window.dispatchEvent(new CustomEvent('config:tabDirtyChanged', {
    detail: { tab: 'teams', dirty: false, valid: true }
  }));
  // After a successful save from "new", switch to editor view of the saved slug
  if (currentSubView === 'new') {
    navigateToSubView('editor', slug);
  }
}

function discard() {
  currentFormData = JSON.parse(JSON.stringify(savedFormData));
  renderEditorForm(currentFormData.team_id, currentSubView === 'new');
  window.dispatchEvent(new CustomEvent('config:tabDirtyChanged', {
    detail: { tab: 'teams', dirty: false, valid: validateForm() }
  }));
}

function reset() {
  // Teams have no "factory defaults" concept (each team is user content).
  // Reset to a clean new-team template.
  if (currentSubView === 'list') return;
  if (!confirm('Clear all fields in the current team form?')) return;
  renderNewSubView();
  markDirty();
}

// ── Mount ───────────────────────────────────────────────────────
function mount(root, _data) {
  rootElement = root;
  const route = parseTeamsSubRoute();
  renderSubView(route.subView, route.slug);
}

window.configTeamsTab = { mount, save, discard, reset };
console.log('[config-teams] module loaded');
