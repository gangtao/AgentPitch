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


class TestPhase5OffsideWiring:
    def _pass_actions(self):
        return {"team_a_0": Pass(target_pos=(85.0, 30.0), power=10)}

    def test_pass_resolution_populates_flag_set(self):
        eng = make_engine()
        snap = base_snap()
        eng._resolve_phase5(self._pass_actions(), snap, 10, "team_a_0")
        assert eng._offside_pids_at_pass == {"team_a_1"}

    def test_restart_kick_pass_is_exempt_and_consumes_marker(self):
        eng = make_engine()
        snap = base_snap()
        eng._restart_kick_pid = "team_a_0"   # e.g. corner kicker
        eng._resolve_phase5(self._pass_actions(), snap, 10, "team_a_0")
        assert eng._offside_pids_at_pass == set()
        assert eng._restart_kick_pid is None

    def test_non_restart_pass_clears_stale_marker(self):
        """A different player passing means the restart possession was lost;
        the exemption must not leak to later passes."""
        eng = make_engine()
        snap = base_snap()
        eng._restart_kick_pid = "team_b_2"
        eng._resolve_phase5(self._pass_actions(), snap, 10, "team_a_0")
        assert eng._offside_pids_at_pass == {"team_a_1"}  # judged normally
        assert eng._restart_kick_pid is None

    def test_shoot_clears_flag_set_and_marker(self):
        eng = make_engine()
        snap = base_snap()
        eng._offside_pids_at_pass = {"team_a_1"}
        eng._restart_kick_pid = "team_a_0"
        eng._resolve_phase5({"team_a_0": Shoot(angle=0.0, power=10)}, snap, 10, "team_a_0")
        assert eng._offside_pids_at_pass == set()
        assert eng._restart_kick_pid is None

    def test_disabled_pass_leaves_set_empty(self):
        eng = make_engine(offside_enabled=False)
        snap = base_snap()
        eng._resolve_phase5(self._pass_actions(), snap, 10, "team_a_0")
        assert eng._offside_pids_at_pass == set()


def make_phase7_engine():
    """Engine whose GSM carries REAL state dicts (players/field/ball) so the
    restart machinery (_select_restarter / _apply_offside_free_kick) runs the
    production path instead of the mock-bail path."""
    eng = make_engine()
    snap = base_snap()
    eng.gsm.state = Mock()
    eng.gsm.state._pass_landing_zone = None
    eng.gsm.state.players = {pid: dict(p) for pid, p in snap["players"].items()}
    eng.gsm.state.field = dict(snap["field"])
    eng.gsm.state.ball = {"position": (78.0, 30.0), "velocity": (1.0, 0.0),
                          "carrier_id": None}
    eng.gsm.get_last_action_tick.return_value = -10**9
    snap["ball"]["carrier_id"] = None
    return eng, snap


class TestPhase7OffsideOffence:
    def _bps_pickup(self, eng, pid, pos=(80.0, 30.0)):
        eng.bps.advance_ball.return_value = {
            "new_position": pos, "new_velocity": (0.0, 0.0),
            "out_of_bounds": False, "controlled_by": pid,
        }

    def test_flagged_player_controlling_pass_concedes_free_kick(self):
        eng, snap = make_phase7_engine()
        eng._offside_pids_at_pass = {"team_a_1"}
        self._bps_pickup(eng, "team_a_1")
        bp_records, goal_records = eng._resolve_phase7(snap, 20)

        sys_rec = bp_records["system"]
        assert sys_rec["offside"] is True
        assert sys_rec["restart_type"] == "free_kick_offside"
        assert sys_rec["restart_team"] == "team_b"
        assert sys_rec["offender_id"] == "team_a_1"
        # offender record for per-player event attribution
        assert bp_records["team_a_1"]["offside_offence"] is True
        # offender did NOT get possession; the team_b kicker did
        kicker = sys_rec["kicker_id"]
        assert kicker is not None and kicker.startswith("team_b")
        # GK never takes the offside free kick
        assert eng.gsm.state.players[kicker]["role"] != "GK"
        eng.gsm.transfer_possession.assert_called_once_with(None, kicker)
        # ball placed at the offence spot (offender's live position, in-field)
        placed = eng.gsm.update_ball_position.call_args_list[-1][0][0]
        assert placed == sys_rec["restart_spot"]
        assert goal_records == {}
        # flag set consumed
        assert eng._offside_pids_at_pass == set()

    def test_free_kick_is_not_offside_exempt(self):
        """Law 11 exempts only goal kicks / throw-ins / corners — NOT free
        kicks. The offside restart must not set the exemption marker."""
        eng, snap = make_phase7_engine()
        eng._offside_pids_at_pass = {"team_a_1"}
        self._bps_pickup(eng, "team_a_1")
        eng._resolve_phase7(snap, 20)
        assert eng._restart_kick_pid is None

    def test_unflagged_pickup_clears_flag_set(self):
        eng, snap = make_phase7_engine()
        eng._offside_pids_at_pass = {"team_a_1"}
        self._bps_pickup(eng, "team_b_1", pos=(76.0, 30.0))
        bp_records, _ = eng._resolve_phase7(snap, 20)
        assert bp_records["team_b_1"]["ball_pickup"] == "success"
        assert eng._offside_pids_at_pass == set()

    def test_flag_set_survives_untouched_ticks(self):
        eng, snap = make_phase7_engine()
        eng._offside_pids_at_pass = {"team_a_1"}
        eng.bps.advance_ball.return_value = {
            "new_position": (70.0, 30.0), "new_velocity": (2.0, 0.0),
            "out_of_bounds": False, "controlled_by": None,
        }
        eng._resolve_phase7(snap, 20)
        assert eng._offside_pids_at_pass == {"team_a_1"}

    def test_deflection_touch_clears_flag_set(self):
        eng, snap = make_phase7_engine()
        eng._offside_pids_at_pass = {"team_a_1"}
        eng.bps.advance_ball.return_value = {
            "new_position": (70.0, 30.0), "new_velocity": (1.0, 1.0),
            "out_of_bounds": False, "controlled_by": None,
            "deflected_by": "team_b_1",
        }
        eng._resolve_phase7(snap, 20)
        assert eng._offside_pids_at_pass == set()

    def test_oob_restart_clears_flag_set_and_arms_exemption(self):
        eng, snap = make_phase7_engine()
        eng._offside_pids_at_pass = {"team_a_1"}
        eng.bps.advance_ball.return_value = {
            "new_position": (50.0, 0.0), "new_velocity": (0.0, 0.0),
            "out_of_bounds": True, "controlled_by": None,
        }
        eng._last_touching_team = "team_a"
        bp_records, _ = eng._resolve_phase7(snap, 20)
        assert bp_records["system"]["restart_type"] == "throw_in"
        assert eng._offside_pids_at_pass == set()
        assert eng._restart_kick_pid == bp_records["system"]["kicker_id"]

    def test_established_carrier_clears_flag_set(self):
        """Possession via any non-pickup path (kickoff, tackle, save) voids
        pending flags."""
        eng, snap = make_phase7_engine()
        eng._offside_pids_at_pass = {"team_a_1"}
        eng.gsm.state.ball["carrier_id"] = "team_b_2"
        snap["ball"]["carrier_id"] = "team_b_2"
        eng._resolve_phase7(snap, 20)
        assert eng._offside_pids_at_pass == set()

    def test_pass_tick_early_return_preserves_flag_set(self):
        eng, snap = make_phase7_engine()
        eng._offside_pids_at_pass = {"team_a_1"}
        eng._ball_just_passed = True
        bp, gr = eng._resolve_phase7(snap, 20)
        assert (bp, gr) == ({}, {})
        assert eng._offside_pids_at_pass == {"team_a_1"}

    def test_restart_spot_clamped_inside_field(self):
        eng, snap = make_phase7_engine()
        eng._offside_pids_at_pass = {"team_a_1"}
        eng.gsm.state.players["team_a_1"]["position"] = (99.5, 0.2)
        self._bps_pickup(eng, "team_a_1", pos=(99.5, 0.2))
        bp_records, _ = eng._resolve_phase7(snap, 20)
        x, y = bp_records["system"]["restart_spot"]
        assert 2.0 <= x <= 98.0 and 0.5 <= y <= 59.5
