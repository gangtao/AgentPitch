"""User store — file-backed user accounts with argon2 password hashing.

Companion to `src/secrets_store.py` and `src/strategy_library.py`: pure file
I/O, no engine code, so the API layer may import it without violating the
ADR-0006 boundary (API must not import src/foundation|core|orchestration).

Storage: `<data_home>/users.json`, mode 0600 (contains password hashes).
Schema (per user):
    {
      "id":                   str,   # stable opaque id (uuid4 hex)
      "username":             str,   # unique, case-insensitive match
      "role":                 str,   # "admin" | "user"  (team-lead is a
                                     #   per-team capability, NOT a global
                                     #   role — see team_store.py)
      "password_hash":        str,   # argon2id PHC string
      "created_at":           str,   # ISO 8601 UTC
      "must_change_password": bool,  # force a password change on next login
    }

File shape: {"users": [ {...}, ... ]}.  A missing file reads as "no users"
(bootstrap state). Malformed JSON raises — the caller wrote it, corruption
should surface rather than silently wipe accounts.

Atomicity: temp file + os.replace + fsync, same primitive as secrets_store.
"""

from __future__ import annotations

import json
import os
import re
import stat
import tempfile
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError, VerificationError


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class UserStoreError(Exception):
    """Base class for all user store failures."""


class UserNotFoundError(UserStoreError):
    """No user matched the requested id or username."""


class UserAlreadyExistsError(UserStoreError):
    """A user with the requested username already exists."""


class InvalidUsernameError(UserStoreError):
    """Username failed format validation."""


class WeakPasswordError(UserStoreError):
    """Password failed the minimum policy check."""


class UserStoreWriteError(UserStoreError):
    """Filesystem error during a write or delete."""


# ---------------------------------------------------------------------------
# Schema / constants
# ---------------------------------------------------------------------------


_USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")
_VALID_ROLES = frozenset({"admin", "user"})
MIN_PASSWORD_LEN = 8

# Shared argon2 hasher. Defaults (argon2id, sensible time/memory cost) are
# fine for a small self-hosted tool; kept here so hash + verify always use
# the same configured instance.
_hasher = PasswordHasher()


@dataclass(frozen=True)
class User:
    """A user account record.

    `password_hash` is included for persistence but callers that return users
    over HTTP must strip it (see `to_public_dict`).
    """

    id: str
    username: str
    role: Literal["admin", "user"]
    password_hash: str
    created_at: str
    must_change_password: bool = False

    def to_public_dict(self) -> dict:
        """JSON-friendly dict WITHOUT the password hash — safe for HTTP."""
        d = asdict(self)
        d.pop("password_hash", None)
        return d


def _now_iso() -> str:
    """Current UTC time as ISO 8601 with Z suffix (matches strategy_library)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def users_path(data_home: Path | str) -> Path:
    """Return `<data_home>/users.json`. Pure path arithmetic."""
    return Path(data_home) / "users.json"


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate_username(username: str) -> None:
    if not isinstance(username, str) or not _USERNAME_RE.fullmatch(username):
        raise InvalidUsernameError(
            f"Invalid username {username!r}: must match {_USERNAME_RE.pattern}"
        )


def _validate_password(password: str) -> None:
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LEN:
        raise WeakPasswordError(
            f"Password must be at least {MIN_PASSWORD_LEN} characters"
        )


def _validate_role(role: str) -> None:
    if role not in _VALID_ROLES:
        raise UserStoreError(
            f"Invalid role {role!r}; must be one of {sorted(_VALID_ROLES)}"
        )


# ---------------------------------------------------------------------------
# (De)serialization
# ---------------------------------------------------------------------------


def _user_from_dict(data: dict) -> User:
    required = ("id", "username", "role", "password_hash", "created_at")
    missing = [k for k in required if k not in data]
    if missing:
        raise UserStoreError(f"User record missing required fields: {missing}")
    return User(
        id=data["id"],
        username=data["username"],
        role=data["role"],
        password_hash=data["password_hash"],
        created_at=data["created_at"],
        must_change_password=bool(data.get("must_change_password", False)),
    )


# ---------------------------------------------------------------------------
# Atomic load / save
# ---------------------------------------------------------------------------


def load_users(data_home: Path | str) -> list[User]:
    """Load all users. Missing file → empty list (bootstrap state).

    Side effect: if the file exists with looser-than-0600 permissions, it is
    tightened (same defensive behaviour as secrets_store).
    """
    path = users_path(data_home)
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
        raise UserStoreError(f"users file unreadable at {path}: {e}") from e

    if not isinstance(raw, dict) or not isinstance(raw.get("users"), list):
        raise UserStoreError(f"users file at {path} is malformed (expected {{'users': [...]}})")

    return [_user_from_dict(u) for u in raw["users"]]


def _save_users(data_home: Path | str, users: list[User]) -> None:
    """Atomically persist the full user list with mode 0600."""
    data_home = Path(data_home)
    data_home.mkdir(parents=True, exist_ok=True)
    path = users_path(data_home)

    payload = {"users": [asdict(u) for u in users]}

    try:
        with tempfile.NamedTemporaryFile(
            mode="w", dir=data_home, prefix=".users.json.tmp", delete=False, encoding="utf-8"
        ) as tmp:
            json.dump(payload, tmp, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = Path(tmp.name)
    except OSError as e:
        raise UserStoreWriteError(f"failed to write temp users file: {e}") from e

    try:
        os.chmod(tmp_path, 0o600)
        os.replace(tmp_path, path)
        os.chmod(path, 0o600)
    except OSError as e:
        tmp_path.unlink(missing_ok=True)
        raise UserStoreWriteError(f"atomic replace failed for {path}: {e}") from e


# ---------------------------------------------------------------------------
# Lookups
# ---------------------------------------------------------------------------


def get_user_by_id(data_home: Path | str, user_id: str) -> User:
    for u in load_users(data_home):
        if u.id == user_id:
            return u
    raise UserNotFoundError(f"No user with id {user_id!r}")


def get_user_by_username(data_home: Path | str, username: str) -> User:
    """Case-insensitive username lookup."""
    lowered = username.lower()
    for u in load_users(data_home):
        if u.username.lower() == lowered:
            return u
    raise UserNotFoundError(f"No user with username {username!r}")


def username_exists(data_home: Path | str, username: str) -> bool:
    try:
        get_user_by_username(data_home, username)
        return True
    except UserNotFoundError:
        return False


def count_users(data_home: Path | str) -> int:
    return len(load_users(data_home))


def has_any_admin(data_home: Path | str) -> bool:
    return any(u.role == "admin" for u in load_users(data_home))


# ---------------------------------------------------------------------------
# Mutations
# ---------------------------------------------------------------------------


def create_user(
    data_home: Path | str,
    username: str,
    password: str,
    role: str = "user",
    *,
    must_change_password: bool = False,
) -> User:
    """Create a new user. Raises on duplicate username or policy failure.

    Username uniqueness is case-insensitive. Returns the created User
    (including hash — strip via `to_public_dict` before any HTTP response).
    """
    _validate_username(username)
    _validate_password(password)
    _validate_role(role)

    users = load_users(data_home)
    lowered = username.lower()
    if any(u.username.lower() == lowered for u in users):
        raise UserAlreadyExistsError(f"Username {username!r} already taken")

    user = User(
        id=uuid.uuid4().hex,
        username=username,
        role=role,  # type: ignore[arg-type]
        password_hash=_hasher.hash(password),
        created_at=_now_iso(),
        must_change_password=must_change_password,
    )
    users.append(user)
    _save_users(data_home, users)
    return user


def delete_user(data_home: Path | str, user_id: str) -> None:
    """Delete a user by id. Raises UserNotFoundError if absent."""
    users = load_users(data_home)
    remaining = [u for u in users if u.id != user_id]
    if len(remaining) == len(users):
        raise UserNotFoundError(f"No user with id {user_id!r}")
    _save_users(data_home, remaining)


def set_role(data_home: Path | str, user_id: str, role: str) -> User:
    """Change a user's global role. Returns the updated user."""
    _validate_role(role)
    users = load_users(data_home)
    updated: User | None = None
    for i, u in enumerate(users):
        if u.id == user_id:
            updated = User(
                id=u.id,
                username=u.username,
                role=role,  # type: ignore[arg-type]
                password_hash=u.password_hash,
                created_at=u.created_at,
                must_change_password=u.must_change_password,
            )
            users[i] = updated
            break
    if updated is None:
        raise UserNotFoundError(f"No user with id {user_id!r}")
    _save_users(data_home, users)
    return updated


def set_password(
    data_home: Path | str,
    user_id: str,
    new_password: str,
    *,
    must_change_password: bool = False,
) -> User:
    """Set a new password (re-hash) and clear/raise the change-required flag."""
    _validate_password(new_password)
    users = load_users(data_home)
    updated: User | None = None
    for i, u in enumerate(users):
        if u.id == user_id:
            updated = User(
                id=u.id,
                username=u.username,
                role=u.role,
                password_hash=_hasher.hash(new_password),
                created_at=u.created_at,
                must_change_password=must_change_password,
            )
            users[i] = updated
            break
    if updated is None:
        raise UserNotFoundError(f"No user with id {user_id!r}")
    _save_users(data_home, users)
    return updated


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


def verify_password(data_home: Path | str, username: str, password: str) -> User:
    """Verify credentials; return the User on success.

    Raises UserNotFoundError if the username is unknown, or UserStoreError
    (password mismatch) on bad password. On a successful verify where argon2
    signals the hash parameters are outdated, the stored hash is transparently
    upgraded.
    """
    user = get_user_by_username(data_home, username)
    try:
        _hasher.verify(user.password_hash, password)
    except VerifyMismatchError as e:
        raise UserStoreError("Invalid password") from e
    except (InvalidHashError, VerificationError) as e:
        raise UserStoreError(f"Stored password hash is unusable: {e}") from e

    # Transparent rehash when argon2 parameters have since changed.
    try:
        if _hasher.check_needs_rehash(user.password_hash):
            users = load_users(data_home)
            for i, u in enumerate(users):
                if u.id == user.id:
                    users[i] = User(
                        id=u.id,
                        username=u.username,
                        role=u.role,
                        password_hash=_hasher.hash(password),
                        created_at=u.created_at,
                        must_change_password=u.must_change_password,
                    )
                    break
            _save_users(data_home, users)
    except OSError:
        # Rehash is best-effort; a failed upgrade must not block a valid login.
        pass

    return user
