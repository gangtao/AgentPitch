// Agent Pitch — Auth UI
// Gates the whole shell behind a login overlay and manages the current-user
// chrome (header user chip + logout). Talks to /api/auth/* only.
//
// Flow:
//   1. On load, GET /api/auth/me.
//   2. If 401 → show login overlay. (setup_required shows a first-run hint.)
//   3. If authenticated but must_change_password → show change-password form.
//   4. If fully authenticated → hide overlay, reveal role-gated nav, render
//      the user chip + logout in the header right-cap.
//
// The session cookie is HttpOnly and handled by the browser automatically;
// this module never sees the raw token.

const overlay = () => document.getElementById('auth-overlay');
const loginForm = () => document.getElementById('auth-login-form');
const changeForm = () => document.getElementById('auth-change-form');

// Current user state, shared via window.authState so section modules
// (e.g. admin.js) can read role/teams without re-fetching.
window.authState = window.authState || { user: null, teams: [], isTeamLead: false };

function _show(el) { if (el) el.hidden = false; }
function _hide(el) { if (el) el.hidden = true; }

function _setError(id, msg) {
  const el = document.getElementById(id);
  if (!el) return;
  if (msg) { el.textContent = msg; el.hidden = false; }
  else { el.textContent = ''; el.hidden = true; }
}

async function _api(path, opts = {}) {
  const res = await fetch(path, {
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  let body = null;
  try { body = await res.json(); } catch (_) { /* no body */ }
  return { ok: res.ok, status: res.status, body };
}

// ── Overlay visibility ────────────────────────────────────────────────────

function showLogin({ setupRequired = false } = {}) {
  _show(overlay());
  _show(loginForm());
  _hide(changeForm());
  document.getElementById('auth-subtitle').textContent = 'SIGN IN';
  const hint = document.getElementById('auth-setup-hint');
  if (setupRequired) {
    hint.innerHTML =
      'First run: an <b>admin</b> account was created at startup. ' +
      'Check the server log for the generated password (or use ' +
      'AGENTPITCH_ADMIN_PASSWORD).';
    hint.hidden = false;
  } else {
    hint.hidden = true;
  }
  const u = document.getElementById('auth-username');
  if (u) u.focus();
}

function showChangePassword({ forced = true } = {}) {
  _show(overlay());
  _hide(loginForm());
  _show(changeForm());
  document.getElementById('auth-subtitle').textContent = 'SET NEW PASSWORD';
  document.getElementById('auth-change-intro').textContent = forced
    ? 'You must set a new password before continuing.'
    : 'Change your password.';
  const c = document.getElementById('auth-current-password');
  if (c) c.focus();
}

function hideOverlay() {
  _hide(overlay());
}

// ── Role-gated chrome ──────────────────────────────────────────────────────

function applyRoleChrome(state) {
  // Reveal the Admin nav for admins (full user/team management) and for team
  // leads (they get a scoped members view inside the same section).
  const navAdmin = document.getElementById('nav-admin');
  const showAdmin = state.user && (state.user.role === 'admin' || state.isTeamLead);
  if (navAdmin) navAdmin.hidden = !showAdmin;

  renderUserChip(state);
}

function renderUserChip(state) {
  // The shell owns #right-cap; we only populate it when a user is present.
  const cap = document.getElementById('right-cap');
  if (!cap || !state.user) return;
  const roleLabel = state.user.role === 'admin'
    ? 'ADMIN'
    : (state.isTeamLead ? 'TEAM LEAD' : 'USER');
  cap.innerHTML = `
    <div class="auth-userchip">
      <span class="auth-userchip-name">${_escape(state.user.username)}</span>
      <span class="auth-userchip-role">${roleLabel}</span>
      <button type="button" class="btn btn-sm btn-ghost" id="auth-logout-btn">Logout</button>
    </div>`;
  const btn = document.getElementById('auth-logout-btn');
  if (btn) btn.addEventListener('click', handleLogout);
}

function _escape(s) {
  return String(s).replace(/[&<>"']/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}

// ── Actions ────────────────────────────────────────────────────────────────

async function refresh() {
  const { ok, status, body } = await _api('/api/auth/me');
  if (!ok || status === 401) {
    window.authState = { user: null, teams: [], isTeamLead: false };
    applyRoleChrome(window.authState);
    showLogin({ setupRequired: !!(body && body.setup_required) });
    return window.authState;
  }
  window.authState = {
    user: body.user,
    teams: body.teams || [],
    isTeamLead: !!body.is_team_lead,
  };
  if (body.must_change_password) {
    showChangePassword({ forced: true });
    applyRoleChrome(window.authState);
    return window.authState;
  }
  hideOverlay();
  applyRoleChrome(window.authState);
  // Let the rest of the app know auth is ready (sections can refetch).
  window.dispatchEvent(new CustomEvent('auth:ready', { detail: window.authState }));
  return window.authState;
}

async function handleLogin(e) {
  e.preventDefault();
  _setError('auth-login-error', '');
  const username = document.getElementById('auth-username').value.trim();
  const password = document.getElementById('auth-password').value;
  if (!username || !password) {
    _setError('auth-login-error', 'Enter a username and password.');
    return;
  }
  const btn = document.getElementById('auth-login-btn');
  btn.disabled = true; btn.textContent = 'Signing in…';
  try {
    const { ok, body } = await _api('/api/auth/login', {
      method: 'POST', body: JSON.stringify({ username, password }),
    });
    if (!ok) {
      _setError('auth-login-error', (body && body.detail) || 'Sign in failed.');
      return;
    }
    document.getElementById('auth-password').value = '';
    if (body && body.must_change_password) {
      showChangePassword({ forced: true });
    } else {
      await refresh();
    }
  } catch (_) {
    _setError('auth-login-error', 'Network error — is the server reachable?');
  } finally {
    btn.disabled = false; btn.textContent = 'Sign in';
  }
}

async function handleChangePassword(e) {
  e.preventDefault();
  _setError('auth-change-error', '');
  const current = document.getElementById('auth-current-password').value;
  const next = document.getElementById('auth-new-password').value;
  const next2 = document.getElementById('auth-new-password-2').value;
  if (next.length < 8) {
    _setError('auth-change-error', 'New password must be at least 8 characters.');
    return;
  }
  if (next !== next2) {
    _setError('auth-change-error', 'New passwords do not match.');
    return;
  }
  const btn = document.getElementById('auth-change-btn');
  btn.disabled = true; btn.textContent = 'Updating…';
  try {
    const { ok, body } = await _api('/api/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({ current_password: current, new_password: next }),
    });
    if (!ok) {
      _setError('auth-change-error', (body && body.detail) || 'Could not change password.');
      return;
    }
    // Clear fields and continue into the app.
    ['auth-current-password', 'auth-new-password', 'auth-new-password-2']
      .forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
    await refresh();
  } catch (_) {
    _setError('auth-change-error', 'Network error — try again.');
  } finally {
    btn.disabled = false; btn.textContent = 'Update password';
  }
}

async function handleLogout() {
  try {
    await _api('/api/auth/logout', { method: 'POST' });
  } catch (_) { /* ignore */ }
  window.authState = { user: null, teams: [], isTeamLead: false };
  // Clear header chip + re-gate the UI.
  const cap = document.getElementById('right-cap');
  if (cap) cap.innerHTML = '';
  applyRoleChrome(window.authState);
  showLogin();
}

// ── Public API + bootstrap ──────────────────────────────────────────────────

window.authUI = { refresh, handleLogout, getState: () => window.authState };

document.addEventListener('DOMContentLoaded', () => {
  const lf = loginForm();
  const cf = changeForm();
  if (lf) lf.addEventListener('submit', handleLogin);
  if (cf) cf.addEventListener('submit', handleChangePassword);
  // The shell clears #right-cap whenever the section changes, which would
  // wipe our user chip — re-render it after each section switch.
  window.addEventListener('app:sectionChanged', () => {
    if (window.authState && window.authState.user) renderUserChip(window.authState);
  });
  // Initial gate. Show the overlay immediately (pre-check) to avoid a flash
  // of the app, then reconcile with the server.
  _show(overlay());
  refresh();
});

console.log('[auth-ui] loaded');
