"""Tests for classify_team_phase (ADR-0022).

Pure 3-state classifier from ball position + possession. Symmetric for
both teams via the "distance from own defending goal" normalization.
"""
from __future__ import annotations

import pytest

from src.foundation.formation_and_role_system import (
    PHASE_ATTACKING_THRESHOLD,
    PHASE_DEFENDING_THRESHOLD,
    classify_team_phase,
)


FIELD_W = 100.0


# ── team_a tests (defends x=0; attacks toward x=field_width) ──────────────


def test_team_a_attacking_when_have_ball_in_opponent_third():
    """Ball deep in opponent third + team_a possesses → attacking."""
    phase = classify_team_phase(
        team_id="team_a",
        ball_position=(80.0, 30.0),  # x=0.80 of pitch from team_a's goal
        ball_possession="team_a",
        field_width=FIELD_W,
    )
    assert phase == "attacking"


def test_team_a_attacking_when_ball_loose_in_opponent_third():
    """Loose ball in opponent third → attacking (chase the loose ball deep)."""
    phase = classify_team_phase(
        team_id="team_a",
        ball_position=(75.0, 30.0),
        ball_possession=None,
        field_width=FIELD_W,
    )
    assert phase == "attacking"


def test_team_a_transitioning_when_opponent_has_ball_in_attacking_third():
    """Opponent has ball deep in our attacking third → transitioning (counter setup)."""
    phase = classify_team_phase(
        team_id="team_a",
        ball_position=(75.0, 30.0),
        ball_possession="team_b",
        field_width=FIELD_W,
    )
    assert phase == "transitioning"


def test_team_a_defending_when_opponent_has_ball_in_own_third():
    """Opponent has ball deep in our own third → defending."""
    phase = classify_team_phase(
        team_id="team_a",
        ball_position=(20.0, 30.0),  # x=0.20, our defensive third
        ball_possession="team_b",
        field_width=FIELD_W,
    )
    assert phase == "defending"


def test_team_a_defending_when_ball_loose_in_own_third():
    """Loose ball in our defensive third → defending (must close down)."""
    phase = classify_team_phase(
        team_id="team_a",
        ball_position=(15.0, 30.0),
        ball_possession=None,
        field_width=FIELD_W,
    )
    assert phase == "defending"


def test_team_a_transitioning_when_have_ball_in_own_third():
    """We have ball in our own third → transitioning (build out from back)."""
    phase = classify_team_phase(
        team_id="team_a",
        ball_position=(15.0, 30.0),
        ball_possession="team_a",
        field_width=FIELD_W,
    )
    assert phase == "transitioning"


def test_team_a_transitioning_when_ball_in_middle_third_regardless_of_possession():
    """Ball in middle third → transitioning, regardless of who has it."""
    middle_x = 50.0
    for poss in (None, "team_a", "team_b"):
        phase = classify_team_phase(
            team_id="team_a",
            ball_position=(middle_x, 30.0),
            ball_possession=poss,
            field_width=FIELD_W,
        )
        assert phase == "transitioning", f"middle-third should always be transitioning (poss={poss})"


# ── team_b symmetry: defends x=field_width; attacks toward x=0 ────────────


def test_team_b_attacking_mirrors_team_a():
    """Ball at x=20 from team_b's perspective (close to opponent goal) + possession → attacking."""
    phase = classify_team_phase(
        team_id="team_b",
        ball_position=(20.0, 30.0),  # team_b attacks toward x=0; this is opponent's third for them
        ball_possession="team_b",
        field_width=FIELD_W,
    )
    assert phase == "attacking"


def test_team_b_defending_mirrors_team_a():
    """Ball at x=80 (deep in team_b's own third) + opponent has it → defending."""
    phase = classify_team_phase(
        team_id="team_b",
        ball_position=(80.0, 30.0),
        ball_possession="team_a",
        field_width=FIELD_W,
    )
    assert phase == "defending"


def test_team_b_middle_third_transitioning():
    """Middle third stays transitioning for team_b too."""
    phase = classify_team_phase(
        team_id="team_b",
        ball_position=(50.0, 30.0),
        ball_possession="team_b",
        field_width=FIELD_W,
    )
    assert phase == "transitioning"


# ── Boundary tests ────────────────────────────────────────────────────────


def test_attacking_threshold_boundary_inclusive():
    """At exactly the attacking threshold (x=66.0 of 100), still transitioning.
    Strictly greater than threshold required to flip to attacking."""
    boundary_x = PHASE_ATTACKING_THRESHOLD * FIELD_W  # 66.0
    phase = classify_team_phase(
        team_id="team_a",
        ball_position=(boundary_x, 30.0),
        ball_possession="team_a",
        field_width=FIELD_W,
    )
    assert phase == "transitioning"


def test_defending_threshold_boundary_inclusive():
    """At exactly the defending threshold (x=34.0), still transitioning.
    Strictly less than threshold required to flip to defending."""
    boundary_x = PHASE_DEFENDING_THRESHOLD * FIELD_W  # 34.0
    phase = classify_team_phase(
        team_id="team_a",
        ball_position=(boundary_x, 30.0),
        ball_possession="team_b",
        field_width=FIELD_W,
    )
    assert phase == "transitioning"


def test_just_above_attacking_threshold_flips():
    """Just above the attacking threshold flips to attacking."""
    just_above = (PHASE_ATTACKING_THRESHOLD + 0.001) * FIELD_W
    phase = classify_team_phase(
        team_id="team_a",
        ball_position=(just_above, 30.0),
        ball_possession="team_a",
        field_width=FIELD_W,
    )
    assert phase == "attacking"


# ── Field-size independence ───────────────────────────────────────────────


def test_phase_classification_scales_with_field_width():
    """5v5 uses field_width=60. Ball at x=48 → 0.80 of pitch → attacking."""
    phase = classify_team_phase(
        team_id="team_a",
        ball_position=(48.0, 20.0),  # 48/60 = 0.80
        ball_possession="team_a",
        field_width=60.0,
    )
    assert phase == "attacking"


# ── Halftime swap (defending_goal_x parameter, ADR-0022 amendment) ────────


def test_team_a_attacking_when_defends_high_x_and_ball_in_low_x():
    """After halftime swap team_a defends x=field_width. Ball at x=20 (low)
    is now in the OPPONENT's third for team_a → attacking when team_a has it."""
    phase = classify_team_phase(
        team_id="team_a",
        ball_position=(20.0, 30.0),
        ball_possession="team_a",
        field_width=FIELD_W,
        defending_goal_x=FIELD_W,  # H2: team_a defends the right goal
    )
    assert phase == "attacking"


def test_team_a_defending_when_defends_high_x_and_opponent_has_ball_at_high_x():
    """After halftime swap team_a defends x=field_width. Ball at x=80 (high)
    is now in team_a's OWN third — opponent attacking → defending."""
    phase = classify_team_phase(
        team_id="team_a",
        ball_position=(80.0, 30.0),
        ball_possession="team_b",
        field_width=FIELD_W,
        defending_goal_x=FIELD_W,
    )
    assert phase == "defending"


def test_team_b_post_swap_mirrors_team_a():
    """After halftime team_b defends x=0. Ball at x=80 is in team_b's
    attacking third (opp goal at x=0 was team_b's old defending goal in H1)."""
    phase = classify_team_phase(
        team_id="team_b",
        ball_position=(80.0, 30.0),
        ball_possession="team_b",
        field_width=FIELD_W,
        defending_goal_x=0.0,  # H2: team_b defends the left goal
    )
    assert phase == "attacking"


def test_default_defending_goal_x_preserves_h1_layout():
    """Backward-compat: omitting defending_goal_x assumes H1 (team_a defends 0)."""
    # Same as test_team_a_attacking_when_have_ball_in_opponent_third above
    phase = classify_team_phase(
        team_id="team_a",
        ball_position=(80.0, 30.0),
        ball_possession="team_a",
        field_width=FIELD_W,
        # No defending_goal_x → defaults to 0.0 for team_a
    )
    assert phase == "attacking"
