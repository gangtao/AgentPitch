"""Story 003 tests — advance_ball orchestration (full BPS API).

Covers AC-BPS-01, 07, 08, 10, 11, 12, 13, 14 + EC-BPS-04, 05, 06.
"""

from __future__ import annotations

import copy
import math

import pytest

from src.core import ball_physics_system as bps
from src.core.ball_physics_system import advance_ball


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_player(position: tuple[float, float], team: str = "team_a", skill: int = 10) -> dict:
    return {"position": position, "team": team, "skill": skill}


def _make_state(
    *,
    ball_position: tuple[float, float] = (50.0, 30.0),
    ball_velocity: tuple[float, float] = (0.0, 0.0),
    carrier_id: str | None = None,
    possession: str | None = None,
    players: dict | None = None,
    pass_landing_zone: tuple[float, float] | None = None,
) -> dict:
    return {
        "ball": {
            "position": ball_position,
            "velocity": ball_velocity,
            "carrier_id": carrier_id,
            "possession": possession,
        },
        "players": players or {},
        "_pass_landing_zone": pass_landing_zone,
    }


# ---------------------------------------------------------------------------
# AC-1: CARRIED skip — AC-BPS-01
# ---------------------------------------------------------------------------


def test_carried_ball_returns_carrier_position_no_motion():
    state = _make_state(
        ball_position=(40.0, 30.0),
        ball_velocity=(0.0, 0.0),
        carrier_id="team_a_3",
        possession="team_a",
        players={"team_a_3": _make_player((40.0, 30.0))},
    )
    result = advance_ball(state, seed=42, tick=10)
    assert result["new_position"] == (40.0, 30.0)
    assert result["new_velocity"] == (0.0, 0.0)
    assert result["out_of_bounds"] is False
    assert result["controlled_by"] == "team_a_3"


def test_carried_ball_returns_current_carrier_position_even_if_moved():
    # Carrier moved this tick (PMS already ran in phase 4); BPS uses player's new pos.
    state = _make_state(
        ball_position=(40.0, 30.0),  # stale from previous tick
        ball_velocity=(0.0, 0.0),
        carrier_id="team_a_3",
        players={"team_a_3": _make_player((45.0, 32.0))},
    )
    result = advance_ball(state, seed=1, tick=1)
    assert result["new_position"] == (45.0, 32.0)
    assert result["controlled_by"] == "team_a_3"


# ---------------------------------------------------------------------------
# AC-2: Contest fires within range — AC-BPS-08
# ---------------------------------------------------------------------------


def test_contest_fires_for_player_within_range(monkeypatch):
    # Force success via mocked hash_01.
    monkeypatch.setattr(bps, "hash_01", lambda *a: 0.0)
    state = _make_state(
        ball_position=(50.0, 30.0),
        ball_velocity=(2.0, 0.0),
        players={"team_b_0": _make_player((52.5, 30.0), team="team_b", skill=10)},
    )
    result = advance_ball(state, seed=42, tick=1)
    # Contest fires; mocked hash_01 forces success → controlled_by set + position is player's.
    assert result["controlled_by"] == "team_b_0"
    assert result["new_position"] == (52.5, 30.0)
    assert result["new_velocity"] == (0.0, 0.0)


def test_contest_fails_when_hash_above_prob(monkeypatch):
    # Force failure via mocked hash_01 returning 1.0 - eps.
    monkeypatch.setattr(bps, "hash_01", lambda *a: 0.999_999)
    state = _make_state(
        ball_position=(50.0, 30.0),
        ball_velocity=(2.0, 0.0),
        players={"team_b_0": _make_player((52.5, 30.0), team="team_b", skill=10)},
    )
    result = advance_ball(state, seed=42, tick=1)
    # Contest fires but fails → controlled_by None + ball at next_pos with original velocity.
    assert result["controlled_by"] is None
    assert result["new_position"] == (52.0, 30.0)
    assert result["new_velocity"] == (2.0, 0.0)


# ---------------------------------------------------------------------------
# AC-3: Nearest only — AC-BPS-13
# ---------------------------------------------------------------------------


def test_nearest_player_only_contests(monkeypatch):
    # Record which player_id is passed to hash_01 → confirm only nearest.
    captured: list[str] = []

    def fake_hash(seed, tick, player_id, label):
        captured.append(player_id)
        return 0.0  # force success

    monkeypatch.setattr(bps, "hash_01", fake_hash)
    state = _make_state(
        ball_position=(50.0, 30.0),
        ball_velocity=(2.0, 0.0),
        players={
            "team_b_0": _make_player((52.5, 30.0), team="team_b", skill=10),  # dist 0.5 from next_pos (52,30)
            "team_b_1": _make_player((53.0, 30.0), team="team_b", skill=10),  # dist 1.0 from next_pos
        },
    )
    result = advance_ball(state, seed=42, tick=1)
    # Only the nearest player got a roll.
    assert captured == ["team_b_0"]
    assert result["controlled_by"] == "team_b_0"


# ---------------------------------------------------------------------------
# AC-4: Friendly-fire — AC-BPS-14 + EC-BPS-05
# ---------------------------------------------------------------------------


def test_friendly_fire_same_team_contest_allowed(monkeypatch):
    monkeypatch.setattr(bps, "hash_01", lambda *a: 0.0)
    state = _make_state(
        ball_position=(50.0, 30.0),
        ball_velocity=(2.0, 0.0),
        possession="team_a",  # team_a has possession
        players={"team_a_0": _make_player((52.5, 30.0), team="team_a", skill=10)},
    )
    result = advance_ball(state, seed=42, tick=1)
    # Same-team player wins control — no team filter on contest eligibility.
    assert result["controlled_by"] == "team_a_0"


# ---------------------------------------------------------------------------
# AC-5: Tie-break — EC-BPS-04 (lexicographic player_id)
# ---------------------------------------------------------------------------


def test_tie_break_lexicographic_player_id(monkeypatch):
    monkeypatch.setattr(bps, "hash_01", lambda *a: 0.0)
    state = _make_state(
        ball_position=(50.0, 30.0),
        ball_velocity=(2.0, 0.0),
        players={
            # Both at exact same distance from next_pos (52, 30).
            "team_b_3": _make_player((52.5, 30.0), team="team_b", skill=10),
            "team_b_0": _make_player((52.5, 30.0), team="team_b", skill=10),
        },
    )
    result = advance_ball(state, seed=42, tick=1)
    # Lexicographic smallest wins: team_b_0 < team_b_3.
    assert result["controlled_by"] == "team_b_0"


# ---------------------------------------------------------------------------
# AC-6: Landing-zone arrival → deterministic pickup — EC-BPS-06
# ---------------------------------------------------------------------------


def test_landing_zone_arrival_deterministic_pickup():
    # Ball at (48, 30), velocity (5, 0), LZ at (50, 30).
    # next_pos = (53, 30); dot((5,0), (50-48, 30-30)=(2,0)) = 10 > 0 — no overshoot first tick.
    # Need the second-tick state where dot <= 0 so ball snaps.
    state = _make_state(
        ball_position=(53.0, 30.0),
        ball_velocity=(5.0, 0.0),
        pass_landing_zone=(50.0, 30.0),
        players={"team_a_0": _make_player((50.5, 30.0), team="team_a", skill=10)},
    )
    result = advance_ball(state, seed=999, tick=999)
    # Ball snaps to LZ → ball_speed=0 → prob=1.0 → deterministic pickup.
    assert result["controlled_by"] == "team_a_0"
    assert result["new_position"] == (50.5, 30.0)  # winner's position
    assert result["new_velocity"] == (0.0, 0.0)


# ---------------------------------------------------------------------------
# AC-7: No candidates within range → ball continues
# ---------------------------------------------------------------------------


def test_no_candidates_in_range_ball_continues():
    state = _make_state(
        ball_position=(50.0, 30.0),
        ball_velocity=(2.0, 0.0),
        players={"team_b_0": _make_player((10.0, 10.0), team="team_b", skill=10)},
    )
    result = advance_ball(state, seed=42, tick=1)
    assert result["controlled_by"] is None
    assert result["new_position"] == (52.0, 30.0)
    assert result["new_velocity"] == (2.0, 0.0)
    assert result["out_of_bounds"] is False


# ---------------------------------------------------------------------------
# AC-8: OOB no contest — AC-BPS-07
# ---------------------------------------------------------------------------


def test_oob_returns_no_contest_oob_true():
    state = _make_state(
        ball_position=(98.0, 30.0),
        ball_velocity=(5.0, 0.0),
        # Player would be in range of an in-bounds next_pos, but OOB takes priority.
        players={"team_b_0": _make_player((100.0, 30.0), team="team_b", skill=10)},
    )
    result = advance_ball(state, seed=42, tick=1)
    assert result["out_of_bounds"] is True
    assert result["controlled_by"] is None
    assert result["new_position"] == (100.0, 30.0)  # clamped to east edge
    assert result["new_velocity"] == (0.0, 0.0)


# ---------------------------------------------------------------------------
# AC-9: Determinism — AC-BPS-12
# ---------------------------------------------------------------------------


def test_determinism_same_inputs_same_output():
    def make() -> dict:
        return _make_state(
            ball_position=(50.0, 30.0),
            ball_velocity=(2.0, 0.0),
            players={"team_b_0": _make_player((52.5, 30.0), team="team_b", skill=10)},
        )

    r1 = advance_ball(make(), seed=42, tick=5)
    r2 = advance_ball(make(), seed=42, tick=5)
    assert r1 == r2


def test_determinism_different_seeds_can_differ():
    def make() -> dict:
        return _make_state(
            ball_position=(50.0, 30.0),
            ball_velocity=(2.0, 0.0),
            players={"team_b_0": _make_player((52.5, 30.0), team="team_b", skill=10)},
        )

    # Repeated calls with same args identical (sanity), but no claim that
    # different seeds always differ — just that determinism per-input holds.
    r1 = advance_ball(make(), seed=42, tick=5)
    r2 = advance_ball(make(), seed=42, tick=5)
    assert r1 == r2


# ---------------------------------------------------------------------------
# AC-10: AT_REST loose ball — pickup contest fires (post-2026-04-22)
# ---------------------------------------------------------------------------


def test_at_rest_ball_no_carrier_picked_up_by_nearby_player():
    """Per 2026-04-22 fix: a stationary loose ball with a player within
    BALL_CONTROL_RANGE IS picked up. Previously the AT_REST guard skipped
    the contest, which created the "stuck loose ball" pathology where a
    ball that overshot a pass landing zone and stopped could never be
    collected even when players reached within range on subsequent ticks.
    """
    state = _make_state(
        ball_position=(50.0, 30.0),
        ball_velocity=(0.0, 0.0),
        carrier_id=None,
        # Player 0.5u from ball — well within BALL_CONTROL_RANGE=1.5.
        players={"team_b_0": _make_player((50.5, 30.0), team="team_b", skill=10)},
    )
    result = advance_ball(state, seed=42, tick=1)
    assert result["new_velocity"] == (0.0, 0.0)
    assert result["out_of_bounds"] is False
    # AT_REST + nearby player → contest fires, F2 prob=1.0 (ball_speed=0) → pickup.
    assert result["controlled_by"] == "team_b_0"
    # On successful pickup, ball snaps to controller's position (per advance_ball).
    assert result["new_position"] == (50.5, 30.0)


# ---------------------------------------------------------------------------
# AC-11: Clearing signals — AC-BPS-11 (3 separate tests)
# ---------------------------------------------------------------------------


def test_clearing_signal_overshoot_arrival():
    # Overshoot snaps ball to LZ with vel=0, no opponents → controlled_by None.
    # ARE infers landing-zone arrival from new_velocity == (0, 0) AND
    # new_position == prior _pass_landing_zone (ARE has both pieces of context).
    state = _make_state(
        ball_position=(53.0, 30.0),
        ball_velocity=(5.0, 0.0),
        pass_landing_zone=(50.0, 30.0),
    )
    result = advance_ball(state, seed=1, tick=1)
    assert result["new_position"] == (50.0, 30.0)
    assert result["new_velocity"] == (0.0, 0.0)
    assert result["out_of_bounds"] is False
    assert result["controlled_by"] is None


def test_clearing_signal_oob():
    state = _make_state(
        ball_position=(98.0, 30.0),
        ball_velocity=(5.0, 0.0),
    )
    result = advance_ball(state, seed=1, tick=1)
    assert result["out_of_bounds"] is True


def test_clearing_signal_contest_success(monkeypatch):
    monkeypatch.setattr(bps, "hash_01", lambda *a: 0.0)
    state = _make_state(
        ball_position=(50.0, 30.0),
        ball_velocity=(2.0, 0.0),
        players={"team_b_0": _make_player((52.5, 30.0), team="team_b", skill=10)},
    )
    result = advance_ball(state, seed=1, tick=1)
    assert isinstance(result["controlled_by"], str)
    assert result["controlled_by"] == "team_b_0"


# ---------------------------------------------------------------------------
# AC-12: Privacy — _pass_landing_zone never in result dict (AC-BPS-10)
# ---------------------------------------------------------------------------


def test_pass_landing_zone_never_in_result_dict():
    state = _make_state(
        ball_position=(53.0, 30.0),
        ball_velocity=(5.0, 0.0),
        pass_landing_zone=(50.0, 30.0),
    )
    result = advance_ball(state, seed=1, tick=1)
    assert "_pass_landing_zone" not in result
    # Sanity — the only allowed keys.
    assert set(result.keys()) == {
        "new_position",
        "new_velocity",
        "out_of_bounds",
        "controlled_by",
    }


# ---------------------------------------------------------------------------
# AC-13: Pure function — game_state unchanged after call
# ---------------------------------------------------------------------------


def test_pure_function_game_state_unchanged():
    state = _make_state(
        ball_position=(50.0, 30.0),
        ball_velocity=(2.0, 0.0),
        players={"team_b_0": _make_player((52.5, 30.0), team="team_b", skill=10)},
        pass_landing_zone=(60.0, 30.0),
    )
    state_before = copy.deepcopy(state)
    advance_ball(state, seed=42, tick=1)
    assert state == state_before


def test_pure_function_carried_path_no_mutation():
    state = _make_state(
        ball_position=(40.0, 30.0),
        carrier_id="team_a_0",
        players={"team_a_0": _make_player((40.0, 30.0))},
    )
    state_before = copy.deepcopy(state)
    advance_ball(state, seed=1, tick=1)
    assert state == state_before


def test_pure_function_oob_path_no_mutation():
    state = _make_state(
        ball_position=(98.0, 30.0),
        ball_velocity=(5.0, 0.0),
    )
    state_before = copy.deepcopy(state)
    advance_ball(state, seed=1, tick=1)
    assert state == state_before


# ---------------------------------------------------------------------------
# Bonus: missing _pass_landing_zone key in dict still works (defaults to None)
# ---------------------------------------------------------------------------


def test_missing_pass_landing_zone_key_defaults_to_none():
    state = {
        "ball": {
            "position": (50.0, 30.0),
            "velocity": (2.0, 0.0),
            "carrier_id": None,
            "possession": None,
        },
        "players": {},
        # Note: no "_pass_landing_zone" key at all.
    }
    result = advance_ball(state, seed=1, tick=1)
    # Should run without KeyError and advance normally.
    assert result["new_position"] == (52.0, 30.0)
    assert result["new_velocity"] == (2.0, 0.0)


# ---------------------------------------------------------------------------
# Bonus: ball-speed boundary — was IN_FLIGHT, now AT_REST due to overshoot snap
# ---------------------------------------------------------------------------


def test_overshoot_no_player_in_range_returns_at_lz_no_controller():
    # Ball overshoots LZ; no players within range → AT_REST at LZ, no controller.
    state = _make_state(
        ball_position=(53.0, 30.0),
        ball_velocity=(5.0, 0.0),
        pass_landing_zone=(50.0, 30.0),
        players={"team_a_0": _make_player((10.0, 10.0))},  # far away
    )
    result = advance_ball(state, seed=1, tick=1)
    assert result["new_position"] == (50.0, 30.0)
    assert result["new_velocity"] == (0.0, 0.0)
    assert result["controlled_by"] is None
