"""Tests for compute_zone_for + compute_dynamic_anchor (ADR-0022).

Phase × role → zone rectangle. Mirrored for team_b. y-component reuses the
canonical role-group y-distribution (same formula as the static
compute_anchors), so existing y values are preserved.
"""
from __future__ import annotations

import pytest

from src.foundation.formation_and_role_system import (
    PHASE_ZONES,
    compute_dynamic_anchor,
    compute_zone_for,
    get_anchor,
)


FIELD_W = 100.0
FIELD_H = 60.0


# ── Spawn position vs defending-phase anchor (post amendment c, 2026-04-25) ─


def test_legacy_spawn_anchor_unchanged():
    """compute_anchors() (used at match init for spawn positions) still
    returns the legacy DEF_ANCHOR_X=25 / GK_ANCHOR_X=8 / etc. The dynamic
    defending-phase anchor is now deeper, but kickoff positions are stable."""
    assert get_anchor("GK",  "team_a", FIELD_W) == 8.0
    assert get_anchor("DEF", "team_a", FIELD_W) == 25.0
    assert get_anchor("MID", "team_a", FIELD_W) == 50.0
    assert get_anchor("FWD", "team_a", FIELD_W) == 75.0


def test_defending_def_center_is_goal_side_of_attacking_opp_fwd():
    """Goal-side defending: team_a DEF in defending phase must be CLOSER
    to own goal (x=0) than team_b FWD in attacking phase. Real soccer rule.
    Pre-amendment c: DEF=25 was AHEAD of opp FWD at x=16 (wrong side)."""
    team_a_def = compute_zone_for(
        role="DEF", team_id="team_a", phase="defending",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
    )["center"]
    team_b_fwd = compute_zone_for(
        role="FWD", team_id="team_b", phase="attacking",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
    )["center"]
    # team_a defends x=0; team_a DEF should be at x < team_b FWD's x.
    assert team_a_def[0] < team_b_fwd[0], (
        f"team_a DEF (x={team_a_def[0]}) should be goal-side of "
        f"team_b FWD (x={team_b_fwd[0]}). Defending DEF is on the wrong side."
    )


def test_defending_gk_center_tucked_close_to_goal():
    """GK should be very close to own goal (x ≤ 10) when defending."""
    zone = compute_zone_for(
        role="GK", team_id="team_a", phase="defending",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
    )
    cx, _cy = zone["center"]
    assert cx <= 10.0


def test_defending_fwd_center_drops_to_midfield_to_track_back():
    """In defending phase the FWD must drop into midfield zone (x ≤ 50)
    to help the press — was 58 (too high) before amendment c."""
    zone = compute_zone_for(
        role="FWD", team_id="team_a", phase="defending",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
    )
    cx, _cy = zone["center"]
    assert cx <= 50.0


# ── Attacking phase pushes defenders up significantly ─────────────────────


def test_attacking_def_center_pushes_up_substantially():
    """The user-observed problem: defenders never push up. Attacking-phase
    DEF center must be at least 15 units higher than defending-phase center."""
    defending = compute_zone_for(
        role="DEF", team_id="team_a", phase="defending",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
    )["center"]
    attacking = compute_zone_for(
        role="DEF", team_id="team_a", phase="attacking",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
    )["center"]
    delta_x = attacking[0] - defending[0]
    assert delta_x >= 15.0, (
        f"Attacking-phase DEF should push up >= 15 units (got {delta_x}). "
        "If this fails, revisit PHASE_ZONES tuning."
    )


def test_attacking_fwd_center_presses_high():
    """Attacking-phase FWD center should reach the opponent's box (x>=75)."""
    zone = compute_zone_for(
        role="FWD", team_id="team_a", phase="attacking",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
    )
    cx, _cy = zone["center"]
    assert cx >= 75.0


# ── Team_b mirroring ──────────────────────────────────────────────────────


def test_team_b_zones_mirror_team_a_across_midfield():
    """team_b's defending DEF center should mirror team_a's: 100 - 25 = 75."""
    a_def = compute_zone_for(
        role="DEF", team_id="team_a", phase="defending",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
    )["center"]
    b_def = compute_zone_for(
        role="DEF", team_id="team_b", phase="defending",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
    )["center"]
    assert b_def[0] == FIELD_W - a_def[0]


def test_team_b_attacking_def_crosses_into_opp_half():
    """team_b attacks toward x=0; attacking-phase DEF center should mirror
    team_a's (which is in opp half post-amendment 2026-04-25 → 52.0).
    team_b's mirror is at 100 - 52 = 48, which is in team_a's half — i.e.
    team_b defenders cross halfway during attacks. This is the design
    intent of the retuning (user feedback: 'defenders never go to other half').
    """
    b_atk_def = compute_zone_for(
        role="DEF", team_id="team_b", phase="attacking",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
    )["center"]
    # Halfway is at x=50. team_b defenders attacking should cross it
    # (cx < 50 means they're in team_a's defending half).
    assert b_atk_def[0] < 50.0, (
        f"Attacking-phase team_b DEF should cross halfway (got x={b_atk_def[0]})"
    )


# ── y-distribution preserved from canonical FRS formula ───────────────────


def test_y_distribution_matches_canonical_formula_single_player():
    """1-of-1 player → y_center = field_height * 1/2 = 30."""
    zone = compute_zone_for(
        role="DEF", team_id="team_a", phase="defending",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
    )
    _cx, cy = zone["center"]
    assert cy == 30.0


def test_y_distribution_matches_canonical_formula_multiple_players():
    """3-of-3 DEF group → y centers at 15, 30, 45 (per FRS Rule)."""
    expected_y = [15.0, 30.0, 45.0]
    for i, expected in enumerate(expected_y):
        zone = compute_zone_for(
            role="DEF", team_id="team_a", phase="defending",
            field_width=FIELD_W, field_height=FIELD_H,
            role_index=i, role_count=3,
        )
        _cx, cy = zone["center"]
        assert cy == expected, f"DEF[{i}] of 3 expected y={expected}, got {cy}"


# ── Bounds + invariants ──────────────────────────────────────────────────


def test_zone_bounds_well_formed():
    """For every (role, phase) cell, x_min < x_max and y_min <= y_max."""
    for phase in PHASE_ZONES.keys():
        for role in ("GK", "DEF", "MID", "FWD"):
            zone = compute_zone_for(
                role=role, team_id="team_a", phase=phase,
                field_width=FIELD_W, field_height=FIELD_H,
                role_index=0, role_count=1,
            )
            x_min, x_max = zone["x"]
            y_min, y_max = zone["y"]
            assert x_min < x_max, f"({role},{phase}): x_min={x_min} >= x_max={x_max}"
            assert y_min <= y_max, f"({role},{phase}): y_min={y_min} > y_max={y_max}"


def test_zone_bounds_inside_pitch():
    """All zones must be within [0, field_width] × [0, field_height]."""
    for phase in PHASE_ZONES.keys():
        for role in ("GK", "DEF", "MID", "FWD"):
            for team in ("team_a", "team_b"):
                zone = compute_zone_for(
                    role=role, team_id=team, phase=phase,
                    field_width=FIELD_W, field_height=FIELD_H,
                    role_index=0, role_count=1,
                )
                x_min, x_max = zone["x"]
                y_min, y_max = zone["y"]
                assert 0.0 <= x_min <= FIELD_W and 0.0 <= x_max <= FIELD_W
                assert 0.0 <= y_min <= FIELD_H and 0.0 <= y_max <= FIELD_H


def test_compute_dynamic_anchor_matches_zone_center():
    """compute_dynamic_anchor is a convenience wrapper around compute_zone_for."""
    zone = compute_zone_for(
        role="MID", team_id="team_a", phase="attacking",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=1, role_count=3,
    )
    anchor = compute_dynamic_anchor(
        role="MID", team_id="team_a", phase="attacking",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=1, role_count=3,
    )
    assert anchor == zone["center"]


def test_zone_scales_with_field_width():
    """5v5 uses field_width=60. Defending DEF center scales: 0.125 * 60 = 7.5
    (post amendment c — DEF is now goal-side defending)."""
    zone = compute_zone_for(
        role="DEF", team_id="team_a", phase="defending",
        field_width=60.0, field_height=40.0,
        role_index=0, role_count=1,
    )
    cx, _cy = zone["center"]
    assert cx == 7.5


# ── Ball-side y-compaction (ADR-0022 amendment 2026-04-25) ────────────────


def test_no_ball_y_means_no_y_shift():
    """Backward-compat: if ball_y is omitted, y_center is the canonical base."""
    zone = compute_zone_for(
        role="DEF", team_id="team_a", phase="defending",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
    )
    _cx, cy = zone["center"]
    # Canonical y for 1-of-1 player on 60-tall pitch = 30
    assert cy == 30.0


def test_defending_phase_compacts_toward_ball_strongly():
    """In defending phase the y_center shifts toward ball_y by 55% (post-amend)."""
    # Ball at y=10, player base y_center=30, defending → factor 0.55
    # offset = (10 - 30) * 0.55 = -11
    # y_center = 30 - 11 = 19
    zone = compute_zone_for(
        role="DEF", team_id="team_a", phase="defending",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
        ball_y=10.0,
    )
    _cx, cy = zone["center"]
    assert cy == 19.0


def test_attacking_phase_compacts_toward_ball_weakly():
    """In attacking phase the y_center shifts only 10% toward ball_y (preserve width)."""
    # Ball at y=10, base=30, attacking → factor 0.10
    # offset = (10 - 30) * 0.10 = -2.0
    # y_center = 28.0
    zone = compute_zone_for(
        role="DEF", team_id="team_a", phase="attacking",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
        ball_y=10.0,
    )
    _cx, cy = zone["center"]
    assert cy == 28.0


def test_transitioning_phase_compaction_is_intermediate():
    """Transitioning factor 0.30 sits between attacking (0.10) and defending (0.55)."""
    # Ball at y=10, base=30 → offset = -20 * 0.30 = -6.0
    zone = compute_zone_for(
        role="MID", team_id="team_a", phase="transitioning",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
        ball_y=10.0,
    )
    _cx, cy = zone["center"]
    assert cy == 24.0


def test_ball_at_pitch_center_produces_no_y_shift():
    """If ball_y == field_height/2 exactly, no shift in any phase."""
    for phase in ("defending", "transitioning", "attacking"):
        zone = compute_zone_for(
            role="DEF", team_id="team_a", phase=phase,
            field_width=FIELD_W, field_height=FIELD_H,
            role_index=0, role_count=1,
            ball_y=FIELD_H / 2.0,  # exactly center
        )
        _cx, cy = zone["center"]
        assert cy == 30.0, f"Phase {phase}: ball at center should produce no y-shift"


def test_y_compaction_preserves_team_width_relative_spread():
    """All players on a team shift by the SAME y-offset, so their relative
    spread (formation width) is preserved — only the center moves."""
    # 3 defenders, ball at y=10
    centers_no_ball = []
    centers_with_ball = []
    for i in range(3):
        cy_no_ball = compute_zone_for(
            role="DEF", team_id="team_a", phase="defending",
            field_width=FIELD_W, field_height=FIELD_H,
            role_index=i, role_count=3,
        )["center"][1]
        cy_with_ball = compute_zone_for(
            role="DEF", team_id="team_a", phase="defending",
            field_width=FIELD_W, field_height=FIELD_H,
            role_index=i, role_count=3,
            ball_y=10.0,
        )["center"][1]
        centers_no_ball.append(cy_no_ball)
        centers_with_ball.append(cy_with_ball)

    # Relative spread (gap between adjacent players) preserved
    no_ball_gaps = [centers_no_ball[i+1] - centers_no_ball[i] for i in range(2)]
    with_ball_gaps = [centers_with_ball[i+1] - centers_with_ball[i] for i in range(2)]
    assert no_ball_gaps == with_ball_gaps

    # All 3 shifted by the same offset (compaction is uniform across the team)
    deltas = [centers_with_ball[i] - centers_no_ball[i] for i in range(3)]
    assert all(d == deltas[0] for d in deltas)


def test_y_compaction_clamps_to_pitch_bounds():
    """Extreme ball position + strong factor must not drive y_center off-pitch."""
    # Ball at y=0 (top edge), defending phase, top defender (base y_center small)
    # offset = (0 - 30) * 0.40 = -12; y_center = base - 12. For role_index=0 of
    # 3 the base is 60*1/4 = 15, so y_center = 15 - 12 = 3 (still positive). OK.
    # For an edge case: confirm clamp at 0.
    zone = compute_zone_for(
        role="DEF", team_id="team_a", phase="defending",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=10,  # base = 60/11 ≈ 5.45
        ball_y=0.0,
    )
    _cx, cy = zone["center"]
    # base ≈ 5.45, offset = -12, raw = -6.55, clamped to 0
    assert cy == 0.0


def test_compute_dynamic_anchor_passes_ball_y_through():
    """The convenience wrapper must propagate ball_y to compute_zone_for."""
    anchor = compute_dynamic_anchor(
        role="DEF", team_id="team_a", phase="defending",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
        ball_y=10.0,
    )
    # Same as test_defending_phase_compacts_toward_ball_strongly above
    assert anchor[1] == 19.0


# ── Halftime swap (defending_goal_x parameter, ADR-0022 amendment) ────────


def test_team_a_post_swap_defending_def_mirrors_to_high_x():
    """After halftime swap team_a defends x=field_width. Defending DEF zone
    center should mirror to x=field_width-12.5 = 87.5 (post amendment c —
    deeper defensive line, now goal-side at high-x end)."""
    zone = compute_zone_for(
        role="DEF", team_id="team_a", phase="defending",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
        defending_goal_x=FIELD_W,  # H2 team_a defends right goal
    )
    cx, _cy = zone["center"]
    assert cx == 87.5


def test_team_a_post_swap_attacking_def_pushes_left_into_opp_half():
    """After swap team_a attacks toward x=0. Attacking DEF zone center
    should be at field_width - 52 = 48 (across halfway from the right side)."""
    zone = compute_zone_for(
        role="DEF", team_id="team_a", phase="attacking",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
        defending_goal_x=FIELD_W,
    )
    cx, _cy = zone["center"]
    assert cx == 48.0
    # Confirm it crosses halfway (now downward from team_a's defending side)
    assert cx < FIELD_W / 2.0


def test_team_b_post_swap_defending_def_at_low_x():
    """After halftime team_b defends x=0. Defending DEF zone center should
    be at x=12.5 (post amendment c — deeper defensive line; H1 was at
    field_width-12.5=87.5)."""
    zone = compute_zone_for(
        role="DEF", team_id="team_b", phase="defending",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
        defending_goal_x=0.0,
    )
    cx, _cy = zone["center"]
    assert cx == 12.5


def test_default_defending_goal_x_preserves_h1_layout_in_zones():
    """Backward-compat: omitting defending_goal_x for team_a yields the
    same result as defending_goal_x=0 (H1 layout). Regression guard for the
    optional-parameter contract."""
    zone_default = compute_zone_for(
        role="DEF", team_id="team_a", phase="defending",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
        # No defending_goal_x → defaults to 0.0 for team_a
    )
    zone_explicit = compute_zone_for(
        role="DEF", team_id="team_a", phase="defending",
        field_width=FIELD_W, field_height=FIELD_H,
        role_index=0, role_count=1,
        defending_goal_x=0.0,
    )
    assert zone_default["center"] == zone_explicit["center"]
