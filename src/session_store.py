"""Session store — server-side login sessions backed by a 0600 JSON file.

Companion pure-I/O module (like `user_store.py`): no engine code, safe for
the API layer under the ADR-0006 boundary.

A session maps an opaque, cryptographically-random token to a user id with an
absolute expiry. Tokens are stored HASHED (sha256) so a leaked sessions file
cannot be replayed directly — same rationale as never storing raw passwords.
The raw token lives only in the client's HttpOnly cookie.

Storage: `<data_home>/.sessions.json`, mode 0600, shape:
    {"sessions": [ {token_hash, user_id, created_at, expires_at}, ... ]}

Expired sessions are pruned lazily on every load/validate so the file does
not grow without bound.

Atomicity: temp + os.replace + fsync, same primitive as the other stores.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import stat
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class SessionStoreError(Exception):
    """Base class for session store failures."""


class SessionStoreWriteError(SessionStoreError):
    """Filesystem error during a write."""


# ---------------------------------------------------------------------------
# Schema / constants
# ---------------------------------------------------------------------------


DEFAULT_TTL_SECONDS = 7 * 24 * 3600  # one week
_TOKEN_BYTES = 32  # 256-bit token


@dataclass(frozen=True)
class Session:
    """A persisted session record (token stored hashed)."""

    token_hash: str
    user_id: str
    created_at: str
    expires_at: str  # ISO 8601 UTC


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(s: str) -> datetime:
    # Stored format is always "...Z"; tolerate a trailing Z or +00:00.
    s = s.replace("Z", "+00:00")
    return datetime.fromisoformat(s)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def sessions_path(data_home: Path | str) -> Path:
    """Return `<data_home>/.sessions.json`."""
    return Path(data_home) / ".sessions.json"


# ---------------------------------------------------------------------------
# Load / save (with lazy expiry pruning)
# ---------------------------------------------------------------------------


def _load_raw(data_home: Path | str) -> list[Session]:
    path = sessions_path(data_home)
    if not path.exists():
        return []

    current_mode = stat.S_IMODE(path.stat().st_mode)
    if current_mode != 0o600:
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise SessionStoreError(f"sessions file unreadable at {path}: {e}") from e
    if not isinstance(raw, dict) or not isinstance(raw.get("sessions"), list):
        raise SessionStoreError(
            f"sessions file at {path} is malformed (expected {{'sessions': [...]}})"
        )

    out: list[Session] = []
    for s in raw["sessions"]:
        try:
            out.append(
                Session(
                    token_hash=s["token_hash"],
                    user_id=s["user_id"],
                    created_at=s["created_at"],
                    expires_at=s["expires_at"],
                )
            )
        except (KeyError, TypeError):
            # Skip malformed individual rows rather than failing the whole load.
            continue
    return out


def _save(data_home: Path | str, sessions: list[Session]) -> None:
    data_home = Path(data_home)
    data_home.mkdir(parents=True, exist_ok=True)
    path = sessions_path(data_home)
    payload = {"sessions": [asdict(s) for s in sessions]}
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", dir=data_home, prefix=".sessions.json.tmp",
            delete=False, encoding="utf-8",
        ) as tmp:
            json.dump(payload, tmp, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = Path(tmp.name)
    except OSError as e:
        raise SessionStoreWriteError(f"failed to write temp sessions file: {e}") from e
    try:
        os.chmod(tmp_path, 0o600)
        os.replace(tmp_path, path)
        os.chmod(path, 0o600)
    except OSError as e:
        tmp_path.unlink(missing_ok=True)
        raise SessionStoreWriteError(f"atomic replace failed for {path}: {e}") from e


def _prune_expired(sessions: list[Session], now: datetime) -> list[Session]:
    keep: list[Session] = []
    for s in sessions:
        try:
            if _parse_iso(s.expires_at) > now:
                keep.append(s)
        except ValueError:
            # Unparseable expiry → treat as expired/corrupt, drop it.
            continue
    return keep


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_session(
    data_home: Path | str,
    user_id: str,
    *,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
) -> str:
    """Create a session for `user_id`; return the RAW token for the cookie.

    Only the token's hash is persisted. The raw token is returned once and
    must be stored client-side (HttpOnly cookie) — it cannot be recovered
    from the store afterwards.
    """
    now = _now()
    token = secrets.token_urlsafe(_TOKEN_BYTES)
    session = Session(
        token_hash=_hash_token(token),
        user_id=user_id,
        created_at=_iso(now),
        expires_at=_iso(now + timedelta(seconds=ttl_seconds)),
    )
    sessions = _prune_expired(_load_raw(data_home), now)
    sessions.append(session)
    _save(data_home, sessions)
    return token


def resolve_session(data_home: Path | str, token: str) -> str | None:
    """Return the user_id for a valid, non-expired token, else None.

    Prunes expired sessions as a side effect when any are found.
    """
    if not token:
        return None
    now = _now()
    sessions = _load_raw(data_home)
    pruned = _prune_expired(sessions, now)
    if len(pruned) != len(sessions):
        # Persist the pruning so the file stays bounded.
        try:
            _save(data_home, pruned)
        except SessionStoreError:
            pass
    token_hash = _hash_token(token)
    for s in pruned:
        if secrets.compare_digest(s.token_hash, token_hash):
            return s.user_id
    return None


def destroy_session(data_home: Path | str, token: str) -> bool:
    """Invalidate a single session by its raw token. Returns True if removed."""
    if not token:
        return False
    token_hash = _hash_token(token)
    sessions = _load_raw(data_home)
    remaining = [s for s in sessions if not secrets.compare_digest(s.token_hash, token_hash)]
    if len(remaining) == len(sessions):
        return False
    _save(data_home, remaining)
    return True


def destroy_user_sessions(data_home: Path | str, user_id: str) -> int:
    """Invalidate ALL sessions for a user (e.g. on delete / password change).

    Returns the number of sessions removed.
    """
    sessions = _load_raw(data_home)
    remaining = [s for s in sessions if s.user_id != user_id]
    removed = len(sessions) - len(remaining)
    if removed:
        _save(data_home, remaining)
    return removed
