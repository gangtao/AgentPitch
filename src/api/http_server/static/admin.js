// Agent Pitch — Admin section (users + teams management)
//
// Two audiences share this section, gated by role (window.authState):
//   - Admin: full user CRUD, role changes, password resets, team CRUD, and
//            member/lead assignment on every team.
//   - Team lead (non-admin): sees only the teams they lead, and may add/remove
//            members and promote/demote leads within those teams. No user CRUD.
//
// All enforcement is server-side; this UI only hides controls the caller
// can't use, to avoid dead buttons. Uses design-system classes exclusively.

const ADMIN_ROOT = () => document.getElementById('admin-root');

let _usersCache = [];   // [{id, username, role, teams, leads, ...}]
let _teamsCache = [];   // [{slug, name, lead_user_ids, member_user_ids}]

// ── small helpers ───────────────────────────────────────────────

function _esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}

async function _api(path, opts = {}) {
  const res = await fetch(path, {
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  let body = null;
  try { body = await res.json(); } catch (_) {}
  return { ok: res.ok, status: res.status, body };
}

function _state() {
  return window.authState || { user: null, teams: [], isTeamLead: false };
}
function _isAdmin() { return _state().user && _state().user.role === 'admin'; }
function _username(userId) {
  const u = _usersCache.find(x => x.id === userId);
  return u ? u.username : userId.slice(0, 8);
}

// ── data loading ────────────────────────────────────────────────

async function _loadData() {
  // Teams are readable by any logged-in user; users list is admin-only.
  const teamsReq = _api('/api/teams');
  const usersReq = _isAdmin() ? _api('/api/users') : Promise.resolve({ ok: true, body: { users: [] } });
  const [teamsRes, usersRes] = await Promise.all([teamsReq, usersReq]);
  _teamsCache = (teamsRes.ok && teamsRes.body && teamsRes.body.teams) || [];
  _usersCache = (usersRes.ok && usersRes.body && usersRes.body.users) || [];
}

// ── rendering ───────────────────────────────────────────────────

function render() {
  const root = ADMIN_ROOT();
  if (!root) return;
  const admin = _isAdmin();

  const teamsForLead = admin
    ? _teamsCache
    : _teamsCache.filter(t => (_state().teams || []).some(mt => mt.slug === t.slug && mt.is_lead));

  root.innerHTML = `
    <div class="admin-wrap">
      ${admin ? _renderUsersPanel() : ''}
      ${_renderTeamsPanel(teamsForLead, admin)}
    </div>
  `;
  _wire(admin);
}

function _renderUsersPanel() {
  const rows = _usersCache.map(u => {
    const teamLabel = (u.teams && u.teams.length)
      ? u.teams.map(_esc).join(', ')
      : '<span class="dimer">no teams</span>';
    const leadBadge = (u.leads && u.leads.length)
      ? ` · leads ${u.leads.map(_esc).join(', ')}` : '';
    return `
      <div class="list-row" data-user-id="${_esc(u.id)}">
        <div class="list-row-content">
          <div class="list-row-line-1">
            ${_esc(u.username)}
            <span class="admin-role-tag admin-role-${_esc(u.role)}">${_esc(u.role)}</span>
          </div>
          <div class="list-row-line-2">${teamLabel}${leadBadge}</div>
        </div>
        <div class="list-row-actions">
          <select class="sel admin-role-sel" data-user-id="${_esc(u.id)}" aria-label="Role for ${_esc(u.username)}">
            <option value="user" ${u.role === 'user' ? 'selected' : ''}>user</option>
            <option value="admin" ${u.role === 'admin' ? 'selected' : ''}>admin</option>
          </select>
          <button class="btn btn-sm" data-action="reset-pw" data-user-id="${_esc(u.id)}">Reset PW</button>
          <button class="btn btn-sm btn-danger" data-action="del-user" data-user-id="${_esc(u.id)}">Delete</button>
        </div>
      </div>`;
  }).join('');

  return `
    <section class="admin-panel">
      <div class="ap-section"><span>Users</span><span class="rule"></span></div>

      <div class="admin-create-row">
        <input class="ipt" id="admin-new-username" placeholder="username" autocomplete="off" spellcheck="false">
        <input class="ipt" id="admin-new-password" type="password" placeholder="password (min 8)" autocomplete="new-password">
        <select class="sel" id="admin-new-role">
          <option value="user" selected>user</option>
          <option value="admin">admin</option>
        </select>
        <button class="btn btn-primary" id="admin-create-user-btn">+ Create user</button>
      </div>
      <div id="admin-user-error" class="form-error" hidden role="alert"></div>

      <div class="list-body">
        ${rows || '<div class="list-row skeleton">No users yet.</div>'}
      </div>
    </section>`;
}

function _renderTeamsPanel(teams, admin) {
  const teamCards = teams.map(t => _renderTeamCard(t, admin)).join('');
  return `
    <section class="admin-panel">
      <div class="ap-section"><span>Teams</span><span class="rule"></span></div>

      ${admin ? `
      <div class="admin-create-row">
        <input class="ipt" id="admin-new-team-slug" placeholder="slug (a-z0-9-_)" autocomplete="off" spellcheck="false">
        <input class="ipt" id="admin-new-team-name" placeholder="Display name">
        <button class="btn btn-primary" id="admin-create-team-btn">+ Create team</button>
      </div>
      <div id="admin-team-error" class="form-error" hidden role="alert"></div>
      ` : '<div class="field-help">You can manage members of the teams you lead.</div>'}

      <div class="admin-team-grid">
        ${teamCards || '<div class="list-row skeleton">No teams.</div>'}
      </div>
    </section>`;
}

function _renderTeamCard(t, admin) {
  const members = (t.member_user_ids || []).map(uid => {
    const isLead = (t.lead_user_ids || []).includes(uid);
    return `
      <div class="admin-member-row">
        <span class="admin-member-name">
          ${_esc(_username(uid))}
          ${isLead ? '<span class="admin-lead-tag">LEAD</span>' : ''}
        </span>
        <span class="admin-member-actions">
          ${isLead
            ? `<button class="btn btn-sm" data-action="demote" data-slug="${_esc(t.slug)}" data-user-id="${_esc(uid)}">Demote</button>`
            : `<button class="btn btn-sm" data-action="promote" data-slug="${_esc(t.slug)}" data-user-id="${_esc(uid)}">Make lead</button>`}
          <button class="btn btn-sm btn-danger" data-action="remove-member" data-slug="${_esc(t.slug)}" data-user-id="${_esc(uid)}">Remove</button>
        </span>
      </div>`;
  }).join('');

  // Candidate users to add (admins have the full list; leads only see it if
  // the users list was returned — which it isn't for non-admins, so leads add
  // by picking from all known members across teams is not possible; admins do
  // the heavy lifting of user creation). We still render an add control for
  // admins.
  const addControl = admin ? `
    <div class="admin-add-member-row">
      <select class="sel admin-add-member-sel" data-slug="${_esc(t.slug)}">
        <option value="">+ add member…</option>
        ${_usersCache
          .filter(u => !(t.member_user_ids || []).includes(u.id))
          .map(u => `<option value="${_esc(u.id)}">${_esc(u.username)}</option>`)
          .join('')}
      </select>
    </div>` : '';

  return `
    <div class="admin-team-card" data-slug="${_esc(t.slug)}">
      <div class="admin-team-head">
        <span class="admin-team-name">${_esc(t.name)}</span>
        <span class="admin-team-slug">${_esc(t.slug)}</span>
        ${admin ? `<button class="btn btn-sm btn-danger admin-team-del" data-action="del-team" data-slug="${_esc(t.slug)}">Delete</button>` : ''}
      </div>
      <div class="admin-member-list">
        ${members || '<div class="dimer admin-empty">No members.</div>'}
      </div>
      ${addControl}
    </div>`;
}

// ── actions ─────────────────────────────────────────────────────

function _err(id, msg) {
  const el = document.getElementById(id);
  if (!el) return;
  if (msg) { el.textContent = msg; el.hidden = false; }
  else { el.textContent = ''; el.hidden = true; }
}

async function _reload() {
  await _loadData();
  render();
}

function _wire(admin) {
  const root = ADMIN_ROOT();
  if (!root) return;

  if (admin) {
    const createUserBtn = document.getElementById('admin-create-user-btn');
    if (createUserBtn) createUserBtn.addEventListener('click', _createUser);
    const createTeamBtn = document.getElementById('admin-create-team-btn');
    if (createTeamBtn) createTeamBtn.addEventListener('click', _createTeam);

    root.querySelectorAll('.admin-role-sel').forEach(sel =>
      sel.addEventListener('change', _changeRole));
    root.querySelectorAll('.admin-add-member-sel').forEach(sel =>
      sel.addEventListener('change', _addMember));
  }

  // Click-delegated actions (present for both admin + lead where allowed).
  root.querySelectorAll('[data-action]').forEach(btn =>
    btn.addEventListener('click', _handleAction));
}

async function _createUser() {
  _err('admin-user-error', '');
  const username = document.getElementById('admin-new-username').value.trim();
  const password = document.getElementById('admin-new-password').value;
  const role = document.getElementById('admin-new-role').value;
  if (!username || !password) { _err('admin-user-error', 'Username and password are required.'); return; }
  const { ok, body } = await _api('/api/users', {
    method: 'POST',
    body: JSON.stringify({ username, password, role, must_change_password: true }),
  });
  if (!ok) { _err('admin-user-error', (body && body.detail) || 'Could not create user.'); return; }
  await _reload();
}

async function _changeRole(e) {
  const userId = e.target.dataset.userId;
  const role = e.target.value;
  const { ok, body } = await _api(`/api/users/${userId}/role`, {
    method: 'PUT', body: JSON.stringify({ role }),
  });
  if (!ok) { _err('admin-user-error', (body && body.detail) || 'Could not change role.'); await _reload(); return; }
  await _reload();
}

async function _createTeam() {
  _err('admin-team-error', '');
  const slug = document.getElementById('admin-new-team-slug').value.trim();
  const name = document.getElementById('admin-new-team-name').value.trim();
  if (!slug || !name) { _err('admin-team-error', 'Slug and name are required.'); return; }
  const { ok, body } = await _api('/api/teams', {
    method: 'POST', body: JSON.stringify({ slug, name }),
  });
  if (!ok) { _err('admin-team-error', (body && body.detail) || 'Could not create team.'); return; }
  await _reload();
}

async function _addMember(e) {
  const slug = e.target.dataset.slug;
  const userId = e.target.value;
  if (!userId) return;
  const { ok, body } = await _api(`/api/teams/${slug}/members`, {
    method: 'POST', body: JSON.stringify({ user_id: userId }),
  });
  if (!ok) { _err('admin-team-error', (body && body.detail) || 'Could not add member.'); }
  await _reload();
}

async function _handleAction(e) {
  const btn = e.currentTarget;
  const action = btn.dataset.action;
  const slug = btn.dataset.slug;
  const userId = btn.dataset.userId;

  let res;
  switch (action) {
    case 'del-user':
      if (!confirm(`Delete user "${_username(userId)}"? This cannot be undone.`)) return;
      res = await _api(`/api/users/${userId}`, { method: 'DELETE' });
      break;
    case 'reset-pw': {
      const pw = prompt('New password for this user (min 8 chars):');
      if (!pw) return;
      res = await _api(`/api/users/${userId}/password`, {
        method: 'PUT', body: JSON.stringify({ new_password: pw, must_change_password: true }),
      });
      break;
    }
    case 'del-team':
      if (!confirm(`Delete team "${slug}"? Member accounts are kept.`)) return;
      res = await _api(`/api/teams/${slug}`, { method: 'DELETE' });
      break;
    case 'remove-member':
      res = await _api(`/api/teams/${slug}/members/${userId}`, { method: 'DELETE' });
      break;
    case 'promote':
      res = await _api(`/api/teams/${slug}/leads`, {
        method: 'POST', body: JSON.stringify({ user_id: userId }),
      });
      break;
    case 'demote':
      res = await _api(`/api/teams/${slug}/leads/${userId}`, { method: 'DELETE' });
      break;
    default:
      return;
  }
  if (res && !res.ok) {
    const where = (action.includes('team') || action === 'remove-member'
      || action === 'promote' || action === 'demote') ? 'admin-team-error' : 'admin-user-error';
    _err(where, (res.body && res.body.detail) || 'Action failed.');
  }
  await _reload();
}

// ── section lifecycle ───────────────────────────────────────────

const ALL_SECTION_IDS = [
  'section-matches', 'section-strategies', 'section-arena',
  'section-config', 'section-cup', 'section-league', 'section-admin',
];

window.adminSection = {
  async activate() {
    ALL_SECTION_IDS.forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      if (id === 'section-admin') el.removeAttribute('hidden');
      else el.setAttribute('hidden', '');
    });
    const root = ADMIN_ROOT();
    if (root) root.innerHTML = '<div class="section-placeholder">Loading…</div>';
    try {
      await _loadData();
      render();
    } catch (err) {
      console.error('[admin] load failed', err);
      if (root) root.innerHTML = '<div class="section-placeholder">Failed to load admin data.</div>';
    }
  },
  deactivate() {
    const el = document.getElementById('section-admin');
    if (el) el.setAttribute('hidden', '');
  },
};

console.log('[admin.js] loaded');
