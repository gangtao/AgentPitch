"""Issue #31 — IFAB Law 11 offside: position snapshot, exemptions,
offence-on-control, and free-kick restart.

Offside position (v1, x-axis only): at the moment a team-mate PASSES,
a player is flagged iff measured as distance-to-opponents'-goal-line they
are (a) strictly inside the opponents' half, (b) strictly nearer than the
ball (= the passer), and (c) strictly nearer than the SECOND-LAST opponent
(any role). Level = onside. The offence fires in Phase 7 when a flagged
player is the one who controls the passed ball.
"""

from unittest.mock import Mock

from src.foundation.action_resolution_engine.engine import ActionResolutionEngine
from src.foundation.action import Pass, Shoot


def make_engine(offside_enabled=True):
    gsm, pms, bps, sandbox, fallback = Mock(), Mock(), Mock(), Mock(), Mock()
    gsm.seed = 42
    gsm.state = Mock()
    gsm.state._pass_landing_zone = None
    gsm.config = Mock()
    gsm.config.simulation = Mock()
    gsm.config.simulation.offside_enabled = offside_enabled
    # cooldown disabled so Phase 7 exclusion logic stays out of the way
    gsm.config.simulation.action_cooldown_ticks = 0
    return ActionResolutionEngine(gsm, pms, bps, sandbox, fallback)


def base_snap():
    """team_a attacks team_b's goal at x=100. Second-last opponent line:
    GK at x=95 (dist 5), last outfield DEF at x=75 (dist 25) → second-last
    distance = 25 (i.e. the x=75 line)."""
    return {
        "ball": {"position": (60.0, 30.0), "velocity": (0.0, 0.0), "carrier_id": "team_a_0"},
        "players": {
            "team_a_0": {"player_id": "team_a_0", "team": "team_a", "role": "MID",
                         "position": (60.0, 30.0), "skill": 16},
            "team_a_1": {"player_id": "team_a_1", "team": "team_a", "role": "FWD",
                         "position": (80.0, 30.0), "skill": 12},
            "team_a_2": {"player_id": "team_a_2", "team": "team_a", "role": "DEF",
                         "position": (40.0, 30.0), "skill": 12},
            "team_b_0": {"player_id": "team_b_0", "team": "team_b", "role": "GK",
                         "position": (95.0, 30.0), "skill": 10},
            "team_b_1": {"player_id": "team_b_1", "team": "team_b", "role": "DEF",
                         "position": (75.0, 30.0), "skill": 10},
            "team_b_2": {"player_id": "team_b_2", "team": "team_b", "role": "MID",
                         "position": (55.0, 40.0), "skill": 10},
        },
        "field": {"width": 100.0, "height": 60.0,
                  "team_a_goal_x": 0.0, "team_b_goal_x": 100.0,
                  "goal_top": 33.66, "goal_bottom": 26.34},
    }


class TestOffsidePositionSnapshot:
    def test_player_beyond_second_last_opponent_is_flagged(self):
        eng = make_engine()
        snap = base_snap()
        eng._capture_offside_at_pass(snap["players"]["team_a_0"], snap)
        assert eng._offside_pids_at_pass == {"team_a_1"}  # x=80 beyond x=75 line

    def test_level_with_second_last_opponent_is_onside(self):
        eng = make_engine()
        snap = base_snap()
        snap["players"]["team_a_1"]["position"] = (75.0, 10.0)  # exactly level
        eng._capture_offside_at_pass(snap["players"]["team_a_0"], snap)
        assert eng._offside_pids_at_pass == set()

    def test_own_half_is_exempt_even_beyond_opponents(self):
        """Opponents pushed into team_a's half: candidate at x=49 (own half,
        dist 51) is nearer the opponents' goal than the second-last opponent
        (x=40, dist 60) and the ball (x=30, dist 70) — every clause except
        own-half says offside. Law 11: own half is exempt → onside."""
        eng = make_engine()
        snap = base_snap()
        snap["players"]["team_b_0"]["position"] = (45.0, 30.0)  # dist 55
        snap["players"]["team_b_1"]["position"] = (40.0, 30.0)  # dist 60
        snap["players"]["team_b_2"]["position"] = (35.0, 30.0)  # dist 65
        snap["players"]["team_a_0"]["position"] = (30.0, 30.0)  # ball dist 70
        snap["ball"]["position"] = (30.0, 30.0)
        snap["players"]["team_a_2"]["position"] = (49.0, 30.0)  # dist 51 ≥ 50 → own half
        snap["players"]["team_a_1"]["position"] = (40.0, 30.0)  # also own half
        eng._capture_offside_at_pass(snap["players"]["team_a_0"], snap)
        assert eng._offside_pids_at_pass == set()

    def test_halfway_line_counts_as_own_half(self):
        eng = make_engine()
        snap = base_snap()
        snap["players"]["team_a_1"]["position"] = (50.0, 30.0)  # exactly on halfway line
        # make opponents deep so only the half test can save the player
        snap["players"]["team_b_1"]["position"] = (90.0, 30.0)
        eng._capture_offside_at_pass(snap["players"]["team_a_0"], snap)
        assert eng._offside_pids_at_pass == set()

    def test_player_behind_ball_is_onside(self):
        eng = make_engine()
        snap = base_snap()
        # Passer carries the ball deeper than the receiver: ball dist 10
        snap["players"]["team_a_0"]["position"] = (90.0, 30.0)
        snap["ball"]["position"] = (90.0, 30.0)
        # Receiver beyond second-last opponent (dist 20 < 25) but BEHIND the ball
        snap["players"]["team_a_1"]["position"] = (80.0, 30.0)
        eng._capture_offside_at_pass(snap["players"]["team_a_0"], snap)
        assert eng._offside_pids_at_pass == set()

    def test_second_last_opponent_is_any_role_not_role_based(self):
        eng = make_engine()
        snap = base_snap()
        # GK upfield at x=60 (dist 40); outfielders at x=75 (25) and x=85 (15).
        # Sorted dists: 15, 25, 40 → second-last = 25 → line x=75.
        snap["players"]["team_b_0"]["position"] = (60.0, 30.0)   # GK upfield
        snap["players"]["team_b_2"]["position"] = (85.0, 30.0)
        snap["players"]["team_a_1"]["position"] = (80.0, 30.0)   # beyond x=75 line
        eng._capture_offside_at_pass(snap["players"]["team_a_0"], snap)
        assert eng._offside_pids_at_pass == {"team_a_1"}

    def test_half_time_side_swap_judged_correctly(self):
        eng = make_engine()
        snap = base_snap()
        # Second half: goals swap — team_a now attacks x=0.
        snap["field"]["team_a_goal_x"] = 100.0
        snap["field"]["team_b_goal_x"] = 0.0
        snap["players"]["team_a_0"]["position"] = (40.0, 30.0)
        snap["ball"]["position"] = (40.0, 30.0)
        snap["players"]["team_b_0"]["position"] = (5.0, 30.0)    # GK, dist 5
        snap["players"]["team_b_1"]["position"] = (25.0, 30.0)   # DEF, dist 25
        snap["players"]["team_b_2"]["position"] = (45.0, 30.0)
        snap["players"]["team_a_1"]["position"] = (20.0, 30.0)   # beyond x=25 line
        snap["players"]["team_a_2"]["position"] = (60.0, 30.0)   # own half now
        eng._capture_offside_at_pass(snap["players"]["team_a_0"], snap)
        assert eng._offside_pids_at_pass == {"team_a_1"}

    def test_disabled_toggle_never_flags(self):
        eng = make_engine(offside_enabled=False)
        snap = base_snap()
        eng._capture_offside_at_pass(snap["players"]["team_a_0"], snap)
        assert eng._offside_pids_at_pass == set()

    def test_passer_is_never_flagged(self):
        eng = make_engine()
        snap = base_snap()
        snap["players"]["team_a_0"]["position"] = (80.0, 30.0)
        snap["ball"]["position"] = (80.0, 30.0)
        eng._capture_offside_at_pass(snap["players"]["team_a_0"], snap)
        assert "team_a_0" not in eng._offside_pids_at_pass
