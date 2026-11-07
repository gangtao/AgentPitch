"""Team membership store — organisational teams with leads and members.

Companion pure-I/O module (like `user_store.py` / `secrets_store.py`): no
engine code, safe for the API layer to import under the ADR-0006 boundary.

This models the ORGANISATIONAL team (who belongs to a team, who leads it),
which is distinct from the GAMEPLAY team roster in
`<data_home>/configs/teams/<slug>.yaml`. The two are linked by `slug`: an org
team's `slug` may (but need not) match a gameplay roster of the same name.

Roles recap:
  - Global role (user_store): "admin" | "user".
  - "Team lead" is NOT a global role — it is a per-team capability recorded
    here as membership in a team's `lead_user_ids`. A user can lead several
    teams and be a plain member of others. Multiple leads per team allowed.

Storage: `<data_home>/teams-membership.json`, shape:
    {"teams": [ {slug, name, lead_user_ids: [...], member_user_ids: [...],
                 created_at}, ... ]}

Invariants enforced on write:
  - `lead_user_ids` ⊆ `member_user_ids` (a lead is always also a member).
  - no duplicate user ids within a team.
  - slug unique, matches `^[a-z0-9_-]+$` (same shape as gameplay team slugs).

Atomicity: temp + os.replace + fsync, same primitive as the other stores.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class TeamStoreError(Exception):
    """Base class for all team store failures."""


class TeamNotFoundError(TeamStoreError):
    """No team matched the requested slug."""


class TeamAlreadyExistsError(TeamStoreError):
    """A team with the requested slug already exists."""


class InvalidTeamSlugError(TeamStoreError):
    """Slug failed format validation."""


class TeamStoreWriteError(TeamStoreError):
    """Filesystem error during a write or delete."""


# ---------------------------------------------------------------------------
# Schema / constants
# ---------------------------------------------------------------------------


_SLUG_RE = re.compile(r"^[a-z0-9_-]+$")


@dataclass(frozen=True)
class Team:
    """An organisational team.

    `lead_user_ids` is always a subset of `member_user_ids` (a lead is also a
    member). Both lists hold user_store user ids.
    """

    slug: str
    name: str
    lead_user_ids: tuple[str, ...] = field(default_factory=tuple)
    member_user_ids: tuple[str, ...] = field(default_factory=tuple)
    created_at: str = ""

    def is_lead(self, user_id: str) -> bool:
        return user_id in self.lead_user_ids

    def is_member(self, user_id: str) -> bool:
        return user_id in self.member_user_ids

    def to_dict(self) -> dict:
        """JSON-friendly dict (lists, not tuples). Safe for HTTP responses."""
        return {
            "slug": self.slug,
            "name": self.name,
            "lead_user_ids": list(self.lead_user_ids),
            "member_user_ids": list(self.member_user_ids),
            "created_at": self.created_at,
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Path helpers / validation
# ---------------------------------------------------------------------------


def teams_path(data_home: Path | str) -> Path:
    """Return `<data_home>/teams-membership.json`."""
    return Path(data_home) / "teams-membership.json"


def _validate_slug(slug: str) -> None:
    if not isinstance(slug, str) or not _SLUG_RE.fullmatch(slug):
        raise InvalidTeamSlugError(
            f"Invalid team slug {slug!r}: must match {_SLUG_RE.pattern}"
        )


def _normalize_members(
    lead_user_ids: list[str] | tuple[str, ...],
    member_user_ids: list[str] | tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """De-duplicate (order-preserving) and enforce leads ⊆ members."""
    def _dedup(seq) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for x in seq:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    members = _dedup(member_user_ids)
    leads = _dedup(lead_user_ids)
    # A lead is always a member.
    for lead in leads:
        if lead not in members:
            members.append(lead)
    return tuple(leads), tuple(members)


# ---------------------------------------------------------------------------
# (De)serialization
# ---------------------------------------------------------------------------


def _team_from_dict(data: dict) -> Team:
    if "slug" not in data or "name" not in data:
        raise TeamStoreError(f"Team record missing required fields: {data!r}")
    leads, members = _normalize_members(
        data.get("lead_user_ids", []) or [],
        data.get("member_user_ids", []) or [],
    )
    return Team(
        slug=data["slug"],
        name=data["name"],
        lead_user_ids=leads,
        member_user_ids=members,
        created_at=data.get("created_at", ""),
    )


# ---------------------------------------------------------------------------
# Atomic load / save
# ---------------------------------------------------------------------------


def load_teams(data_home: Path | str) -> list[Team]:
    """Load all org teams. Missing file → empty list."""
    path = teams_path(data_home)
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise TeamStoreError(f"teams file unreadable at {path}: {e}") from e
    if not isinstance(raw, dict) or not isinstance(raw.get("teams"), list):
        raise TeamStoreError(
            f"teams file at {path} is malformed (expected {{'teams': [...]}})"
        )
    return [_team_from_dict(t) for t in raw["teams"]]


def _save_teams(data_home: Path | str, teams: list[Team]) -> None:
    data_home = Path(data_home)
    data_home.mkdir(parents=True, exist_ok=True)
    path = teams_path(data_home)
    payload = {"teams": [t.to_dict() for t in teams]}
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", dir=data_home, prefix=".teams-membership.json.tmp",
            delete=False, encoding="utf-8",
        ) as tmp:
            json.dump(payload, tmp, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = Path(tmp.name)
    except OSError as e:
        raise TeamStoreWriteError(f"failed to write temp teams file: {e}") from e
    try:
        os.replace(tmp_path, path)
    except OSError as e:
        tmp_path.unlink(missing_ok=True)
        raise TeamStoreWriteError(f"atomic replace failed for {path}: {e}") from e


# ---------------------------------------------------------------------------
# Lookups
# ---------------------------------------------------------------------------


def get_team(data_home: Path | str, slug: str) -> Team:
    for t in load_teams(data_home):
        if t.slug == slug:
            return t
    raise TeamNotFoundError(f"No team with slug {slug!r}")


def team_exists(data_home: Path | str, slug: str) -> bool:
    try:
        get_team(data_home, slug)
        return True
    except TeamNotFoundError:
        return False


def teams_for_user(data_home: Path | str, user_id: str) -> list[Team]:
    """All teams where the user is a member (includes teams they lead)."""
    return [t for t in load_teams(data_home) if t.is_member(user_id)]


def teams_led_by(data_home: Path | str, user_id: str) -> list[Team]:
    """All teams where the user is a lead."""
    return [t for t in load_teams(data_home) if t.is_lead(user_id)]


def is_lead_of_any(data_home: Path | str, user_id: str) -> bool:
    return any(t.is_lead(user_id) for t in load_teams(data_home))


# ---------------------------------------------------------------------------
# Mutations
# ---------------------------------------------------------------------------


def create_team(
    data_home: Path | str,
    slug: str,
    name: str,
    *,
    lead_user_ids: list[str] | None = None,
    member_user_ids: list[str] | None = None,
) -> Team:
    """Create a new org team. Raises on duplicate slug."""
    _validate_slug(slug)
    if not isinstance(name, str) or not name.strip():
        raise TeamStoreError("Team name must be a non-empty string")

    teams = load_teams(data_home)
    if any(t.slug == slug for t in teams):
        raise TeamAlreadyExistsError(f"Team slug {slug!r} already exists")

    leads, members = _normalize_members(lead_user_ids or [], member_user_ids or [])
    team = Team(
        slug=slug,
        name=name.strip(),
        lead_user_ids=leads,
        member_user_ids=members,
        created_at=_now_iso(),
    )
    teams.append(team)
    _save_teams(data_home, teams)
    return team


def delete_team(data_home: Path | str, slug: str) -> None:
    teams = load_teams(data_home)
    remaining = [t for t in teams if t.slug != slug]
    if len(remaining) == len(teams):
        raise TeamNotFoundError(f"No team with slug {slug!r}")
    _save_teams(data_home, remaining)


def _replace_team(data_home: Path | str, updated: Team) -> Team:
    teams = load_teams(data_home)
    for i, t in enumerate(teams):
        if t.slug == updated.slug:
            teams[i] = updated
            _save_teams(data_home, teams)
            return updated
    raise TeamNotFoundError(f"No team with slug {updated.slug!r}")


def rename_team(data_home: Path | str, slug: str, name: str) -> Team:
    if not isinstance(name, str) or not name.strip():
        raise TeamStoreError("Team name must be a non-empty string")
    t = get_team(data_home, slug)
    return _replace_team(
        data_home,
        Team(slug=t.slug, name=name.strip(), lead_user_ids=t.lead_user_ids,
             member_user_ids=t.member_user_ids, created_at=t.created_at),
    )


def add_member(data_home: Path | str, slug: str, user_id: str) -> Team:
    """Add a user as a plain member (idempotent)."""
    t = get_team(data_home, slug)
    leads, members = _normalize_members(t.lead_user_ids, t.member_user_ids + (user_id,))
    return _replace_team(
        data_home,
        Team(slug=t.slug, name=t.name, lead_user_ids=leads,
             member_user_ids=members, created_at=t.created_at),
    )


def remove_member(data_home: Path | str, slug: str, user_id: str) -> Team:
    """Remove a user from the team entirely (also drops lead status)."""
    t = get_team(data_home, slug)
    leads = tuple(x for x in t.lead_user_ids if x != user_id)
    members = tuple(x for x in t.member_user_ids if x != user_id)
    return _replace_team(
        data_home,
        Team(slug=t.slug, name=t.name, lead_user_ids=leads,
             member_user_ids=members, created_at=t.created_at),
    )


def promote_lead(data_home: Path | str, slug: str, user_id: str) -> Team:
    """Make a user a lead of the team (also ensures membership)."""
    t = get_team(data_home, slug)
    leads, members = _normalize_members(
        t.lead_user_ids + (user_id,), t.member_user_ids + (user_id,)
    )
    return _replace_team(
        data_home,
        Team(slug=t.slug, name=t.name, lead_user_ids=leads,
             member_user_ids=members, created_at=t.created_at),
    )


def demote_lead(data_home: Path | str, slug: str, user_id: str) -> Team:
    """Remove lead status but keep the user as a plain member."""
    t = get_team(data_home, slug)
    leads = tuple(x for x in t.lead_user_ids if x != user_id)
    return _replace_team(
        data_home,
        Team(slug=t.slug, name=t.name, lead_user_ids=leads,
             member_user_ids=t.member_user_ids, created_at=t.created_at),
    )


def purge_user(data_home: Path | str, user_id: str) -> int:
    """Remove a user id from ALL teams (called when a user is deleted).

    Returns the number of teams that were modified.
    """
    teams = load_teams(data_home)
    changed = 0
    new_teams: list[Team] = []
    for t in teams:
        if user_id in t.member_user_ids or user_id in t.lead_user_ids:
            changed += 1
            leads = tuple(x for x in t.lead_user_ids if x != user_id)
            members = tuple(x for x in t.member_user_ids if x != user_id)
            new_teams.append(
                Team(slug=t.slug, name=t.name, lead_user_ids=leads,
                     member_user_ids=members, created_at=t.created_at)
            )
        else:
            new_teams.append(t)
    if changed:
        _save_teams(data_home, new_teams)
    return changed
