"""player_state and history schemas for the decide() callback contract.

Defines the per-tick views passed to a player's decide() callback: the calling
player's full attribute view (PlayerStateDict, mirroring PAM's PlayerAttribute)
and the bounded history of recent ticks (list[HistoryEntryDict]).

Both schemas are plain TypedDicts so they cross the sandbox deep-copy boundary
cheaply (per ADR-0001). PAM's Pydantic model handles config-time validation;
this schema is the per-tick projection.
"""

from __future__ import annotations

import warnings
from typing import Literal, TypedDict


# Tuning knob (GDD): default 10, safe range 5-30. GSM owns the per-match value.
HISTORY_MAX_TICKS: int = 10


# Type aliases (Literal enums)
Role = Literal["GK", "DEF", "MID", "FWD"]
TeamId = Literal["team_a", "team_b"]
ActionName = Literal["move", "pass", "shoot", "tackle", "hold"]
ActionResult = Literal["success", "fail", "goal", "save", "out_of_bounds"]


class PlayerStateDict(TypedDict):
    """The calling player's full per-tick view, passed to decide().

    Mirrors PAM's PlayerAttribute schema for the 7 attribute fields (6 numeric
    + role), plus per-tick context (position, has_ball, formation_position).
    Per-call player_state is a flat dict (not a Pydantic instance) so it can
    cross the sandbox deep-copy boundary cheaply.
    """

    player_id: str  # ADR-0004: "{team_id}_{index}"
    team: TeamId
    role: Role
    position: tuple[float, float]
    has_ball: bool
    formation_position: tuple[float, float]
    formation_zone: dict          # {"x": float, "y": float} zone anchor
    formation_zone_phase: str     # e.g. "attack" / "defend"
    # 9 PAM attributes (mirrors PlayerAttribute):
    speed: int
    skill: int
    strength: int
    save: int
    discipline: int
    dribbling: int
    passing: int
    shooting: int
    stamina: int
    # Issue #38 (IFAB Law 12/14): aggression + penalty-conversion ratings
    # and the player's current caution count (2 yellows = sent off).
    offensive: int
    penalty: int
    yellow_cards: int
    # Health (float, 0..health_max):
    current_health: float


class ScoreDict(TypedDict):
    team_a: int
    team_b: int


class HistoryActionDict(TypedDict):
    """One action record per (tick, player). Part of history[].actions[]."""

    player_id: str  # ADR-0004: str
    team: TeamId
    action: ActionName  # "move" | "pass" | "shoot" | "tackle" | "hold"
    result: ActionResult  # "success" | "fail" | "goal" | "save" | "out_of_bounds"
    details: dict  # action-specific; not strictly typed here


class HistoryEntryDict(TypedDict):
    """One per-tick snapshot in history. List ordered oldest-first."""

    tick: int
    ball_position: tuple[float, float]
    score: ScoreDict
    actions: list[HistoryActionDict]


# Required-key frozensets.
# Cooldown_remaining (singular) added 2026-04-22 per ADR-0015 amendment:
# the LLM needs feedback about whether its non-trivial actions (Pass /
# Shoot / Tackle / Pickup) are currently allowed, so it can plan instead
# of attempting blocked actions and discovering via substituted Hold().
_COOLDOWN_KEYS = frozenset({"cooldown_remaining"})

_REQUIRED_PLAYER_STATE_KEYS = frozenset({
    "player_id", "team", "number", "role", "position", "has_ball", "formation_position",
    "formation_zone", "formation_zone_phase",
    "speed", "skill", "strength", "save", "discipline", "dribbling",
    "passing", "shooting", "stamina", "offensive", "penalty", "yellow_cards",
    "current_health",
}) | _COOLDOWN_KEYS

_PAM_ATTRIBUTE_KEYS = frozenset({
    "speed", "skill", "strength", "save", "discipline", "dribbling",
})

_EXTRA_INT_KEYS = frozenset({
    "passing", "shooting", "stamina", "offensive", "penalty", "yellow_cards",
})

_REQUIRED_HISTORY_ENTRY_KEYS = frozenset({"tick", "ball_position", "score", "actions"})
_REQUIRED_HISTORY_ACTION_KEYS = frozenset({"player_id", "team", "action", "result", "details"})
_REQUIRED_SCORE_KEYS = frozenset({"team_a", "team_b"})

_VALID_ROLES = frozenset({"GK", "DEF", "MID", "FWD"})
_VALID_TEAMS = frozenset({"team_a", "team_b"})
_VALID_ACTION_NAMES = frozenset({"move", "pass", "shoot", "tackle", "hold"})
_VALID_ACTION_RESULTS = frozenset({"success", "fail", "goal", "save", "out_of_bounds"})


def _check_int_not_bool(value: object, field_path: str) -> None:
    """Raise ValueError if value is not int (or is bool, since bool is int subclass)."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field_path}: expected int, got {type(value).__name__}")


def _check_2tuple_float(value: object, field_path: str) -> None:
    """Raise ValueError if value is not a (float, float) 2-tuple."""
    if not isinstance(value, tuple) or len(value) != 2:
        raise ValueError(f"{field_path}: expected 2-tuple, got {type(value).__name__}")
    for i, v in enumerate(value):
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise ValueError(f"{field_path}[{i}]: expected float, got {type(v).__name__}")


def _validate_score(score: object, field_path: str) -> None:
    if not isinstance(score, dict):
        raise ValueError(f"{field_path}: expected dict")
    keys = set(score.keys())
    missing = _REQUIRED_SCORE_KEYS - keys
    extra = keys - _REQUIRED_SCORE_KEYS
    if missing:
        raise ValueError(f"{field_path}: missing keys {sorted(missing)}")
    if extra:
        raise ValueError(f"{field_path}: unexpected keys {sorted(extra)}")
    _check_int_not_bool(score["team_a"], f"{field_path}.team_a")
    _check_int_not_bool(score["team_b"], f"{field_path}.team_b")


def validate_player_state(state: dict) -> None:
    """Raise ValueError if state does not conform to PlayerStateDict.

    Used in unit tests and as a debug assertion. Range validation (1..20) is
    NOT this validator's job — that lives in PAM's PlayerAttribute Pydantic
    model. This validator is structural only.
    """
    if not isinstance(state, dict):
        raise ValueError(f"player_state: expected dict, got {type(state).__name__}")

    keys = set(state.keys())
    missing = _REQUIRED_PLAYER_STATE_KEYS - keys
    extra = keys - _REQUIRED_PLAYER_STATE_KEYS
    if missing:
        raise ValueError(f"player_state: missing keys {sorted(missing)}")
    if extra:
        raise ValueError(f"player_state: unexpected keys {sorted(extra)}")

    if not isinstance(state["player_id"], str):
        raise ValueError("player_state.player_id: expected str (ADR-0004)")
    if state["team"] not in _VALID_TEAMS:
        raise ValueError(
            f"player_state.team: must be one of {sorted(_VALID_TEAMS)}, "
            f"got {state['team']!r}"
        )
    if state["role"] not in _VALID_ROLES:
        raise ValueError(
            f"player_state.role: must be one of {sorted(_VALID_ROLES)}, "
            f"got {state['role']!r}"
        )

    _check_2tuple_float(state["position"], "player_state.position")
    _check_2tuple_float(state["formation_position"], "player_state.formation_position")
    if not isinstance(state["has_ball"], bool):
        raise ValueError(
            f"player_state.has_ball: expected bool, got {type(state['has_ball']).__name__}"
        )

    for attr in _PAM_ATTRIBUTE_KEYS:
        _check_int_not_bool(state[attr], f"player_state.{attr}")

    for attr in _EXTRA_INT_KEYS:
        _check_int_not_bool(state[attr], f"player_state.{attr}")

    # Jersey number — non-negative int (0 = auto-assign sentinel).
    _check_int_not_bool(state["number"], "player_state.number")
    if state["number"] < 0 or state["number"] > 99:
        raise ValueError(f"player_state.number: must be in [0, 99], got {state['number']}")

    # Cooldown remaining ticks must be non-negative ints.
    for cd in _COOLDOWN_KEYS:
        _check_int_not_bool(state[cd], f"player_state.{cd}")
        if state[cd] < 0:
            raise ValueError(
                f"player_state.{cd}: must be >= 0 (0 = action allowed), got {state[cd]}"
            )

    # Formation zone: dict with at minimum x/y keys.
    if not isinstance(state["formation_zone"], dict):
        raise ValueError(
            f"player_state.formation_zone: expected dict, got {type(state['formation_zone']).__name__}"
        )

    # Formation zone phase: str
    if not isinstance(state["formation_zone_phase"], str):
        raise ValueError(
            f"player_state.formation_zone_phase: expected str, got {type(state['formation_zone_phase']).__name__}"
        )

    # current_health: numeric (float or int), non-negative.
    if isinstance(state["current_health"], bool) or not isinstance(state["current_health"], (int, float)):
        raise ValueError(
            f"player_state.current_health: expected float, got {type(state['current_health']).__name__}"
        )


def _validate_history_action(action: object, field_path: str) -> None:
    if not isinstance(action, dict):
        raise ValueError(f"{field_path}: expected dict")
    keys = set(action.keys())
    missing = _REQUIRED_HISTORY_ACTION_KEYS - keys
    extra = keys - _REQUIRED_HISTORY_ACTION_KEYS
    if missing:
        raise ValueError(f"{field_path}: missing keys {sorted(missing)}")
    if extra:
        raise ValueError(f"{field_path}: unexpected keys {sorted(extra)}")
    if not isinstance(action["player_id"], str):
        raise ValueError(f"{field_path}.player_id: expected str (ADR-0004)")
    if action["team"] not in _VALID_TEAMS:
        raise ValueError(
            f"{field_path}.team: must be one of {sorted(_VALID_TEAMS)}, "
            f"got {action['team']!r}"
        )
    if action["action"] not in _VALID_ACTION_NAMES:
        raise ValueError(
            f"{field_path}.action: must be one of {sorted(_VALID_ACTION_NAMES)}, "
            f"got {action['action']!r}"
        )
    if action["result"] not in _VALID_ACTION_RESULTS:
        raise ValueError(
            f"{field_path}.result: must be one of {sorted(_VALID_ACTION_RESULTS)}, "
            f"got {action['result']!r}"
        )
    if not isinstance(action["details"], dict):
        raise ValueError(f"{field_path}.details: expected dict")


def _validate_history_entry(entry: object, field_path: str) -> None:
    if not isinstance(entry, dict):
        raise ValueError(f"{field_path}: expected dict")
    keys = set(entry.keys())
    missing = _REQUIRED_HISTORY_ENTRY_KEYS - keys
    extra = keys - _REQUIRED_HISTORY_ENTRY_KEYS
    if missing:
        raise ValueError(f"{field_path}: missing keys {sorted(missing)}")
    if extra:
        raise ValueError(f"{field_path}: unexpected keys {sorted(extra)}")
    _check_int_not_bool(entry["tick"], f"{field_path}.tick")
    _check_2tuple_float(entry["ball_position"], f"{field_path}.ball_position")
    _validate_score(entry["score"], f"{field_path}.score")
    if not isinstance(entry["actions"], list):
        raise ValueError(f"{field_path}.actions: expected list")
    for j, action in enumerate(entry["actions"]):
        _validate_history_action(action, f"{field_path}.actions[{j}]")


def validate_history(history: list) -> None:
    """Raise ValueError if history does not conform to list[HistoryEntryDict].

    Emits a warning (not error) if len(history) > HISTORY_MAX_TICKS, since
    GSM owns the bound enforcement at construction time. Validates strict-
    increasing tick order (oldest-first per GDD Rule 7).
    """
    if not isinstance(history, list):
        raise ValueError(f"history: expected list, got {type(history).__name__}")

    if len(history) > HISTORY_MAX_TICKS:
        warnings.warn(
            f"history length {len(history)} exceeds HISTORY_MAX_TICKS={HISTORY_MAX_TICKS} "
            "(GSM should bound this — schema-level warning only)",
            stacklevel=2,
        )

    prev_tick: int | None = None
    for i, entry in enumerate(history):
        _validate_history_entry(entry, f"history[{i}]")
        current_tick = entry["tick"]
        if prev_tick is not None and current_tick <= prev_tick:
            raise ValueError(
                f"history[{i}].tick={current_tick} not strictly greater than "
                f"history[{i - 1}].tick={prev_tick} (must be oldest-first)"
            )
        prev_tick = current_tick
