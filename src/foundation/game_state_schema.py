"""
Game State Schema for Agent Pitch soccer simulation.

This module defines the TypedDict structure and validator for the game_state
dict passed to player decide() callbacks. The schema describes the snapshot
of match state exposed to each player at their decision moment.

Key components:
- GameStateDict: Complete type definition for the game_state dict
- BallDict, PlayerRecordDict, FieldDict, ScoreDict: Substructure types
- validate_game_state(): Runtime validator for tests and debug assertions
- Role, TeamId: Literal type aliases for valid enum values

TR-ASCI-002, TR-ASCI-006
"""

from __future__ import annotations
import copy
from typing import TypedDict, Literal


# Type aliases for valid enum values
Role = Literal["GK", "DEF", "MID", "FWD"]
TeamId = Literal["team_a", "team_b"]


class ScoreDict(TypedDict):
    """Current match score."""
    team_a: int
    team_b: int


class BallDict(TypedDict):
    """Ball position and possession state."""
    position: tuple[float, float]
    possession: TeamId | None        # None = loose ball
    carrier_id: str | None           # ADR-0004: str format "{team_id}_{index}", or None


class PlayerRecordDict(TypedDict):
    """Per-player record in the game_state snapshot.

    This is the thin public view exposed in game_state.players[].
    Full player attributes (speed, skill, etc.) appear only in player_state.
    """
    team: TeamId
    role: Role
    position: tuple[float, float]
    has_ball: bool


class FieldDict(TypedDict):
    """Field dimensions and goal positioning.

    Convention: ``goal_top`` is the larger-y edge of the goal mouth and
    ``goal_bottom`` the smaller-y edge, so ``goal_top > goal_bottom`` always
    (e.g. 33.66 and 26.34 on a 60-tall field). The mouth spans
    ``y in [goal_bottom, goal_top]``; its height is ``goal_top - goal_bottom``
    (positive) and its center is ``(goal_top + goal_bottom) / 2``. Computing
    ``goal_bottom - goal_top`` yields a negative value and is always a bug.
    """
    width: float
    height: float
    team_a_goal_x: float
    team_b_goal_x: float
    goal_top: float
    goal_bottom: float


class GameStateDict(TypedDict):
    """Complete game state snapshot passed to decide() callbacks."""
    tick: int
    match_time_seconds: float
    half: int                                 # 1 or 2
    ticks_remaining: int
    score: ScoreDict
    ball: BallDict
    players: dict[str, PlayerRecordDict]      # keyed by str player_id (ADR-0004)
    field: FieldDict
    my_team: TeamId
    my_player_id: str                         # ADR-0004: str (corrected from int)


# Required key sets for validation (frozenset for fast comparison).
_REQUIRED_TOP_KEYS = frozenset({
    "tick", "match_time_seconds", "half", "ticks_remaining",
    "score", "ball", "players", "field", "my_team", "my_player_id",
})
# Keys that GSM injects into snapshots for agent convenience (not in GameStateDict TypedDict).
# free_kick_kicker (issue #38, Law 13): pid of the pending free-kick taker
# (or None) — injected per-player by ARE Phase 2 so strategies know the
# taker must Pass/Shoot (Move is blocked until the kick).
_EXTRA_ALLOWED_TOP_KEYS = frozenset({"team_phase", "free_kick_kicker"})

_REQUIRED_BALL_KEYS = frozenset({"position", "possession", "carrier_id"})
_REQUIRED_PLAYER_KEYS = frozenset({"team", "role", "position", "has_ball"})
_REQUIRED_FIELD_KEYS = frozenset({
    "width", "height", "team_a_goal_x", "team_b_goal_x", "goal_top", "goal_bottom",
})
_REQUIRED_SCORE_KEYS = frozenset({"team_a", "team_b"})
_VALID_ROLES = frozenset({"GK", "DEF", "MID", "FWD"})
_VALID_TEAMS = frozenset({"team_a", "team_b"})


def validate_game_state(snapshot: dict) -> None:
    """Raise ValueError if snapshot does not conform to GameStateDict.

    Used in unit tests and as a debug assertion. Not called on the per-tick
    hot path — GSM's build_tick_snapshot() produces conformant dicts by
    construction.

    Args:
        snapshot: Dict to validate against GameStateDict schema

    Raises:
        ValueError: If snapshot structure, types, or values are invalid
    """
    if not isinstance(snapshot, dict):
        raise ValueError(f"game_state: expected dict, got {type(snapshot).__name__}")

    keys = set(snapshot.keys())
    missing = _REQUIRED_TOP_KEYS - keys
    if missing:
        raise ValueError(f"game_state: missing keys {sorted(missing)}")
    extra = keys - _REQUIRED_TOP_KEYS - _EXTRA_ALLOWED_TOP_KEYS
    if extra:
        raise ValueError(f"game_state: unexpected keys {sorted(extra)}")

    # Type checks for top-level fields
    # AC-4: bool exclusion for int fields (bool is subclass of int in Python)
    if not isinstance(snapshot["tick"], int) or isinstance(snapshot["tick"], bool):
        raise ValueError("game_state.tick: expected int")
    if not isinstance(snapshot["match_time_seconds"], (int, float)) or isinstance(snapshot["match_time_seconds"], bool):
        raise ValueError("game_state.match_time_seconds: expected float")
    if not isinstance(snapshot["half"], int) or isinstance(snapshot["half"], bool):
        raise ValueError("game_state.half: expected int")
    if not isinstance(snapshot["ticks_remaining"], int) or isinstance(snapshot["ticks_remaining"], bool):
        raise ValueError("game_state.ticks_remaining: expected int")

    # AC-5: my_player_id must be str (ADR-0004)
    if not isinstance(snapshot["my_player_id"], str):
        raise ValueError("game_state.my_player_id: expected str (ADR-0004)")

    # my_team must be valid TeamId
    if snapshot["my_team"] not in _VALID_TEAMS:
        raise ValueError(f"game_state.my_team: expected one of {sorted(_VALID_TEAMS)}, got {snapshot['my_team']!r}")

    # Validate score substructure
    _validate_score_dict(snapshot["score"])

    # Validate ball substructure
    _validate_ball_dict(snapshot["ball"])

    # Validate players substructure
    _validate_players_dict(snapshot["players"])

    # Validate field substructure
    _validate_field_dict(snapshot["field"])


def _validate_score_dict(score: dict) -> None:
    """Validate score substructure."""
    if not isinstance(score, dict):
        raise ValueError(f"game_state.score: expected dict, got {type(score).__name__}")

    keys = set(score.keys())
    missing = _REQUIRED_SCORE_KEYS - keys
    extra = keys - _REQUIRED_SCORE_KEYS
    if missing:
        raise ValueError(f"game_state.score: missing keys {sorted(missing)}")
    if extra:
        raise ValueError(f"game_state.score: unexpected keys {sorted(extra)}")

    # Type checks
    if not isinstance(score["team_a"], int) or isinstance(score["team_a"], bool):
        raise ValueError("game_state.score.team_a: expected int")
    if not isinstance(score["team_b"], int) or isinstance(score["team_b"], bool):
        raise ValueError("game_state.score.team_b: expected int")


def _validate_ball_dict(ball: dict) -> None:
    """Validate ball substructure."""
    if not isinstance(ball, dict):
        raise ValueError(f"game_state.ball: expected dict, got {type(ball).__name__}")

    keys = set(ball.keys())
    missing = _REQUIRED_BALL_KEYS - keys
    extra = keys - _REQUIRED_BALL_KEYS
    if missing:
        raise ValueError(f"game_state.ball: missing keys {sorted(missing)}")
    if extra:
        raise ValueError(f"game_state.ball: unexpected keys {sorted(extra)}")

    # Type checks
    if not isinstance(ball["position"], tuple) or len(ball["position"]) != 2:
        raise ValueError("game_state.ball.position: expected 2-tuple")
    if not all(isinstance(coord, (int, float)) and not isinstance(coord, bool) for coord in ball["position"]):
        raise ValueError("game_state.ball.position: expected tuple of float")

    # AC-7: possession must be valid TeamId or None
    if ball["possession"] is not None and ball["possession"] not in _VALID_TEAMS:
        raise ValueError(f"game_state.ball.possession: expected one of {sorted(_VALID_TEAMS)} or None, got {ball['possession']!r}")

    # AC-6: carrier_id must be str or None (ADR-0004)
    if ball["carrier_id"] is not None and not isinstance(ball["carrier_id"], str):
        raise ValueError("game_state.ball.carrier_id: expected str or None (ADR-0004)")


def _validate_players_dict(players: dict) -> None:
    """Validate players substructure."""
    if not isinstance(players, dict):
        raise ValueError(f"game_state.players: expected dict, got {type(players).__name__}")

    # AC-8: All player_id keys must be str and properly formatted
    for player_id in players.keys():
        if not isinstance(player_id, str):
            raise ValueError(f"game_state.players: player_id key {player_id!r} is not str (ADR-0004)")

        # Validate player_id format: {team_id}_{index}
        if "_" not in player_id:
            raise ValueError(f"game_state.players: malformed player_id {player_id!r} (expected format team_id_index)")

        team_part, index_part = player_id.rsplit("_", 1)
        if team_part not in _VALID_TEAMS:
            raise ValueError(f"game_state.players: invalid team in player_id {player_id!r} (expected team_a or team_b)")

        try:
            int(index_part)
        except ValueError:
            raise ValueError(f"game_state.players: non-numeric index in player_id {player_id!r}")

    # Validate each player record
    for player_id, player_record in players.items():
        _validate_player_record_dict(player_record, player_id)


def _validate_player_record_dict(player_record: dict, player_id: str) -> None:
    """Validate individual player record."""
    if not isinstance(player_record, dict):
        raise ValueError(f"game_state.players[{player_id}]: expected dict, got {type(player_record).__name__}")

    keys = set(player_record.keys())
    missing = _REQUIRED_PLAYER_KEYS - keys
    extra = keys - _REQUIRED_PLAYER_KEYS
    if missing:
        raise ValueError(f"game_state.players[{player_id}]: missing keys {sorted(missing)}")
    if extra:
        raise ValueError(f"game_state.players[{player_id}]: unexpected keys {sorted(extra)}")

    # Type checks
    if player_record["team"] not in _VALID_TEAMS:
        raise ValueError(f"game_state.players[{player_id}].team: expected one of {sorted(_VALID_TEAMS)}, got {player_record['team']!r}")

    # AC-10: role must be valid enum
    if player_record["role"] not in _VALID_ROLES:
        raise ValueError(f"game_state.players[{player_id}].role: expected one of {sorted(_VALID_ROLES)}, got {player_record['role']!r}")

    if not isinstance(player_record["position"], tuple) or len(player_record["position"]) != 2:
        raise ValueError(f"game_state.players[{player_id}].position: expected 2-tuple")
    if not all(isinstance(coord, (int, float)) and not isinstance(coord, bool) for coord in player_record["position"]):
        raise ValueError(f"game_state.players[{player_id}].position: expected tuple of float")

    if not isinstance(player_record["has_ball"], bool):
        raise ValueError(f"game_state.players[{player_id}].has_ball: expected bool")


def _validate_field_dict(field: dict) -> None:
    """Validate field substructure."""
    if not isinstance(field, dict):
        raise ValueError(f"game_state.field: expected dict, got {type(field).__name__}")

    keys = set(field.keys())
    missing = _REQUIRED_FIELD_KEYS - keys
    extra = keys - _REQUIRED_FIELD_KEYS
    if missing:
        raise ValueError(f"game_state.field: missing keys {sorted(missing)}")
    if extra:
        raise ValueError(f"game_state.field: unexpected keys {sorted(extra)}")

    # Type checks - all should be float
    for field_name in ["width", "height", "team_a_goal_x", "team_b_goal_x", "goal_top", "goal_bottom"]:
        value = field[field_name]
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"game_state.field.{field_name}: expected float")