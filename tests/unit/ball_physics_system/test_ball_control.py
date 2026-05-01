"""Story 002 tests — Ball control probability (Formula 2 + hash_01).

Covers AC-BPS-09, 12 + F2 known values from GDD examples.
"""

from __future__ import annotations

import pytest

from src.core.ball_physics_system import (
    BALL_CONTROL_RANGE,
    compute_ball_control_prob,
    did_control_succeed,
    euclidean_distance,
)


# ---------------------------------------------------------------------------
# AC-1: AT_REST → prob = 1.0 (AC-BPS-09 special case)
# ---------------------------------------------------------------------------


def test_at_rest_ball_returns_prob_one_exactly():
    prob = compute_ball_control_prob(
        player_skill=10, distance_to_ball=1.0, ball_speed=0.0
    )
    assert prob == 1.0


def test_at_rest_ball_skill_one_returns_one():
    # Even minimum skill returns 1.0 when ball is AT_REST.
    assert compute_ball_control_prob(1, 0.5, 0.0) == 1.0


# ---------------------------------------------------------------------------
# AC-2: F2 known value — elite (skill=18, ball_speed=2.0, dist_ratio=0.1)
# ---------------------------------------------------------------------------


def test_f2_known_value_elite_skill_low_speed():
    # distance_ratio = 0.15 / 1.5 = 0.1
    prob = compute_ball_control_prob(
        player_skill=18, distance_to_ball=0.15, ball_speed=2.0
    )
    # 18 / (18 + 2.0 * 1.1) = 18 / 20.2 ≈ 0.891
    assert prob == pytest.approx(0.891, abs=0.01)


# ---------------------------------------------------------------------------
# AC-3: F2 known value — average (skill=10, ball_speed=4.0, dist_ratio=0.5)
# ---------------------------------------------------------------------------


def test_f2_known_value_average_skill_medium_speed():
    # distance_ratio = 0.75 / 1.5 = 0.5
    prob = compute_ball_control_prob(
        player_skill=10, distance_to_ball=0.75, ball_speed=4.0
    )
    # 10 / (10 + 4.0 * 1.5) = 10 / 16 = 0.625
    assert prob == pytest.approx(0.625, abs=1e-9)


# ---------------------------------------------------------------------------
# AC-4: F2 known value — poor (skill=4, ball_speed=6.0, dist_ratio=1.0)
# ---------------------------------------------------------------------------


def test_f2_known_value_poor_skill_fast_ball():
    # distance_ratio = 1.5 / 1.5 = 1.0
    prob = compute_ball_control_prob(
        player_skill=4, distance_to_ball=1.5, ball_speed=6.0
    )
    # 4 / (4 + 6.0 * 2.0) = 4 / 16 = 0.25
    assert prob == pytest.approx(0.25, abs=1e-9)


# ---------------------------------------------------------------------------
# AC-5: Distance ratio clamped at 1.0 (when distance > range)
# ---------------------------------------------------------------------------


def test_distance_ratio_clamped_at_one_when_distance_exceeds_range():
    # distance=10.0 > range=1.5 → distance_ratio clamps to 1.0
    prob = compute_ball_control_prob(
        player_skill=4, distance_to_ball=10.0, ball_speed=6.0
    )
    # Same result as if distance were exactly 1.5: 4 / 16 = 0.25
    assert prob == pytest.approx(0.25, abs=1e-9)


# ---------------------------------------------------------------------------
# AC-6: F2 range — always in (0, 1] for valid inputs (AC-BPS-09)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("skill", [1, 5, 10, 15, 20])
@pytest.mark.parametrize("distance", [0.0, 0.5, 1.0, 1.5])
@pytest.mark.parametrize("ball_speed", [0.0, 1.0, 5.0, 10.0])
def test_f2_always_in_zero_one_range(skill, distance, ball_speed):
    prob = compute_ball_control_prob(skill, distance, ball_speed)
    assert 0.0 < prob <= 1.0


# ---------------------------------------------------------------------------
# AC-7: Determinism — same inputs return same bool (AC-BPS-12)
# ---------------------------------------------------------------------------


def test_did_control_succeed_is_deterministic():
    result1 = did_control_succeed(seed=42, tick=5, player_id="team_a_0", ball_control_prob=0.5)
    result2 = did_control_succeed(seed=42, tick=5, player_id="team_a_0", ball_control_prob=0.5)
    assert result1 == result2


def test_did_control_succeed_with_prob_one_always_true():
    # AT_REST scenario: prob=1.0 → any draw < 1.0 → always True
    assert did_control_succeed(seed=42, tick=5, player_id="team_a_0", ball_control_prob=1.0) is True


def test_did_control_succeed_with_prob_zero_always_false():
    # No draw is < 0.0 → always False
    assert did_control_succeed(seed=42, tick=5, player_id="team_a_0", ball_control_prob=0.0) is False


# ---------------------------------------------------------------------------
# AC-8: Cross-machine pin — locks hash_01 output for regression tests
# ---------------------------------------------------------------------------


def test_hash_01_ball_control_cross_machine_pin():
    """Pin the deterministic ball_control hash_01 output.

    If this test ever fails, either hash_01 changed or the call signature
    changed — both would break determinism across machines and across versions.
    """
    from src.foundation.simulation_utils import hash_01

    # Pinned at 2026-04-21 for (seed=42, tick=5, "team_a_0", "ball_control").
    assert hash_01(42, 5, "team_a_0", "ball_control") == 0.6102178851142526


def test_did_control_succeed_uses_correct_hash_input():
    # With prob just above the pinned draw → True
    assert did_control_succeed(42, 5, "team_a_0", 0.6102178851142527) is True
    # With prob just below the pinned draw → False
    assert did_control_succeed(42, 5, "team_a_0", 0.6102178851142525) is False


# ---------------------------------------------------------------------------
# AC-9: euclidean_distance helper sanity
# ---------------------------------------------------------------------------


def test_euclidean_distance_classic_3_4_5():
    assert euclidean_distance((0.0, 0.0), (3.0, 4.0)) == 5.0


def test_euclidean_distance_zero_when_same_point():
    assert euclidean_distance((50.0, 30.0), (50.0, 30.0)) == 0.0


def test_euclidean_distance_symmetric():
    a = euclidean_distance((1.0, 2.0), (4.0, 6.0))
    b = euclidean_distance((4.0, 6.0), (1.0, 2.0))
    assert a == b == 5.0


# ---------------------------------------------------------------------------
# AC-10: Pure function — no side effects
# ---------------------------------------------------------------------------


def test_compute_ball_control_prob_no_side_effects_on_repeated_calls():
    p1 = compute_ball_control_prob(10, 0.75, 4.0)
    p2 = compute_ball_control_prob(10, 0.75, 4.0)
    assert p1 == p2


def test_default_ball_control_range_constant_used_when_not_specified():
    # BALL_CONTROL_RANGE = 1.5 is the default
    prob_default = compute_ball_control_prob(10, 0.75, 4.0)
    prob_explicit = compute_ball_control_prob(10, 0.75, 4.0, ball_control_range=BALL_CONTROL_RANGE)
    assert prob_default == prob_explicit
