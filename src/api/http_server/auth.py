"""Authentication + authorization helpers for the HTTP server.

API-layer module (ADR-0006 compliant): imports only the top-level pure-I/O
stores (user_store, team_store, session_store) — never src/foundation|core|
orchestration.

Responsibilities:
  - resolve the current user from the session cookie
  - FastAPI dependencies that enforce "logged in" / "is admin" / "team lead"
  - cookie name + attribute helpers (HttpOnly, SameSite, Secure)

Security notes:
  - The session cookie holds the RAW token; only its hash is persisted
    (see session_store). The cookie is HttpOnly + SameSite=Lax.
  - `Secure` is enabled automatically for non-localhost requests so the
    cookie is not sent over plain HTTP in production (behind a TLS proxy),
    while local http://localhost dev still works.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import Depends, HTTPException, Request

from src import session_store, team_store, user_store
from src.user_store import User

SESSION_COOKIE = "ap_session"


# ── data_home resolution ──────────────────────────────────────────────────


def _data_home(request: Request) -> Path:
    """The server's process-scoped data dir (app.state.log_dir IS data_home)."""
    return Path(request.app.state.log_dir)


# ── cookie attribute helper ───────────────────────────────────────────────


def cookie_is_secure(request: Request) -> bool:
    """Decide whether to set the `Secure` flag.

    True for anything that isn't a localhost/loopback host, so production
    (served over HTTPS behind a proxy) gets Secure cookies while local
    http://localhost development still functions.
    """
    host = (request.url.hostname or "").lower()
    if host in ("localhost", "127.0.0.1", "::1"):
        return False
    # X-Forwarded-Proto lets us respect the proxy's scheme if present.
    fwd_proto = request.headers.get("x-forwarded-proto", "").lower()
    if fwd_proto:
        return fwd_proto == "https"
    return request.url.scheme == "https"


# ── current-user resolution ───────────────────────────────────────────────


def current_user_optional(request: Request) -> User | None:
    """Return the logged-in User, or None if no/invalid session.

    Never raises — use this when a missing session is acceptable
    (e.g. the bootstrap/login flow).
    """
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    data_home = _data_home(request)
    try:
        user_id = session_store.resolve_session(data_home, token)
    except session_store.SessionStoreError:
        return None
    if not user_id:
        return None
    try:
        return user_store.get_user_by_id(data_home, user_id)
    except user_store.UserNotFoundError:
        # Session points at a deleted user — treat as logged out.
        return None


# ── FastAPI dependencies (guards) ─────────────────────────────────────────


def require_user(request: Request) -> User:
    """Dependency: 401 unless a valid session resolves to a known user."""
    user = current_user_optional(request)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def require_admin(request: Request) -> User:
    """Dependency: 401 if not logged in, 403 unless the user is an admin."""
    user = require_user(request)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user


def require_lead_or_admin(request: Request) -> User:
    """Dependency: admin OR a lead of at least one team.

    Fine-grained "lead of THIS team" checks happen per-endpoint via
    `assert_leads_team`, because the team slug is only known there.
    """
    user = require_user(request)
    if user.role == "admin":
        return user
    if team_store.is_lead_of_any(_data_home(request), user.id):
        return user
    raise HTTPException(status_code=403, detail="Team-lead privileges required")


def assert_leads_team(request: Request, user: User, slug: str) -> None:
    """Raise 403 unless `user` is an admin or a lead of team `slug`.

    Call this inside team-scoped endpoints after resolving the slug.
    """
    if user.role == "admin":
        return
    data_home = _data_home(request)
    try:
        team = team_store.get_team(data_home, slug)
    except team_store.TeamNotFoundError:
        raise HTTPException(status_code=404, detail=f"team {slug} not found")
    if not team.is_lead(user.id):
        raise HTTPException(
            status_code=403,
            detail="You must be a lead of this team to manage its members",
        )
