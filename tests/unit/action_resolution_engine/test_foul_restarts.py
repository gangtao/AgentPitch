"""Issue #38 — foul restarts: direct free kick with 9.15 u exclusion
(Law 13) and instant penalty-kick resolution (Law 14)."""

from unittest.mock import Mock

from src.foundation.action_resolution_engine.engine import ActionResolutionEngine
from src.foundation.simulation_utils import hash_01


def make_engine():
    gsm, pms, bps, sandbox, fallback = Mock(), Mock(), Mock(), Mock(), Mock()
    gsm.seed = 42
    gsm.state = Mock()
    gsm.config = Mock()
    sim = gsm.config.simulation
    sim.fouls_enabled = True
    sim.penalty_goal_base = 0.60
    sim.penalty_goal_per_point = 0.015
    sim.penalty_save_per_point = 0.01
    sim.free_kick_exclusion_radius = 9.15
    return ActionResolutionEngine(gsm, pms, bps, sandbox, fallback)


def live_players():
    """Live gsm.state.players — team_a attacks x=100, team_b defends x=100."""
    return {
        "team_a_0": {"team": "team_a", "role": "MID", "position": (50.0, 30.0),
                     "penalty": 10, "shooting": 10, "skill": 10, "sent_off": False},
        "team_a_4": {"team": "team_a", "role": "FWD", "position": (60.0, 28.0),
                     "penalty": 18, "shooting": 12, "skill": 10, "sent_off": False},
        "team_a_1": {"team": "team_a", "role": "GK", "position": (5.0, 30.0),
                     "penalty": 3, "shooting": 5, "skill": 10, "sent_off": False},
        "team_b_0": {"team": "team_b", "role": "GK", "position": (95.0, 30.0),
                     "penalty": 5, "shooting": 5, "skill": 10, "save": 12,
                     "sent_off": False},
        "team_b_1": {"team": "team_b", "role": "DEF", "position": (52.0, 30.0),
                     "penalty": 5, "shooting": 5, "skill": 10, "sent_off": False},
        "team_b_2": {"team": "team_b", "role": "MID", "position": (53.0, 31.0),
                     "penalty": 5, "shooting": 5, "skill": 10, "sent_off": False},
    }


def snap_from(players):
    return {
        "ball": {"position": (50.0, 30.0), "velocity": (0.0, 0.0),
                 "carrier_id": "team_a_0"},
        "players": {pid: {**p, "player_id": pid} for pid, p in players.items()},
        "field": {"width": 100.0, "height": 60.0,
                  "team_a_goal_x": 0.0, "team_b_goal_x": 100.0,
                  "goal_top": 33.66, "goal_bottom": 26.34},
    }


def wire(eng, players):
    eng.gsm.state.players = players
    eng.gsm.state.field = {"width": 100.0, "height": 60.0,
                           "team_a_goal_x": 0.0, "team_b_goal_x": 100.0,
                           "goal_top": 33.66, "goal_bottom": 26.34}
    eng.gsm.state.ball = {"position": (50.0, 30.0), "velocity": (0.0, 0.0),
                          "carrier_id": "team_a_0", "possession": "team_a"}

    def _apply_move(pid, pos):
        players[pid]["position"] = pos
    eng.gsm.apply_move.side_effect = _apply_move

    def _player_state(pid):
        p = players[pid]
        return {**p, "player_id": pid}
    eng.gsm.build_player_state.side_effect = _player_state


class TestPenaltyAreaDetection:
    def test_inside_own_area(self):
        eng = make_engine()
        snap = snap_from(live_players())
        # team_b defends x=100: a spot at (90, 30) is inside their area
        assert eng._is_in_penalty_area((90.0, 30.0), "team_b", snap) is True

    def test_outside_depth(self):
        eng = make_engine()
        snap = snap_from(live_players())
        assert eng._is_in_penalty_area((80.0, 30.0), "team_b", snap) is False

    def test_outside_y_extent(self):
        eng = make_engine()
        snap = snap_from(live_players())
        # goal_bottom 26.34 - 16.5 = 9.84 → y=5 is outside
        assert eng._is_in_penalty_area((95.0, 5.0), "team_b", snap) is False


class TestFoulFreeKick:
    def test_ball_and_kicker_at_spot_possession_to_fouled_team(self):
        eng = make_engine()
        players = live_players()
        wire(eng, players)
        snap = snap_from(players)
        records = {}
        eng._apply_foul_free_kick("team_b", "team_a", (50.0, 30.0),
                                  "team_b_1", snap, 7, records)
        eng.gsm.update_ball_position.assert_called_with((50.0, 30.0))
        sysrec = records["system"]
        assert sysrec["foul"] is True
        assert sysrec["restart_type"] == "free_kick_foul"
        assert sysrec["restart_team"] == "team_a"
        assert sysrec["kicker_id"].startswith("team_a")

    def test_fouling_team_pushed_to_exclusion_radius(self):
        eng = make_engine()
        players = live_players()
        wire(eng, players)
        snap = snap_from(players)
        eng._apply_foul_free_kick("team_b", "team_a", (50.0, 30.0),
                                  "team_b_1", snap, 7, {})
        for pid in ("team_b_1", "team_b_2"):  # were within 9.15 of the spot
            px, py = players[pid]["position"]
            d = ((px - 50.0) ** 2 + (py - 30.0) ** 2) ** 0.5
            assert d >= 9.15 - 1e-6, f"{pid} only {d:.2f}u from spot"

    def test_fouled_team_not_moved(self):
        eng = make_engine()
        players = live_players()
        wire(eng, players)
        snap = snap_from(players)
        before = players["team_a_4"]["position"]
        eng._apply_foul_free_kick("team_b", "team_a", (50.0, 30.0),
                                  "team_b_1", snap, 7, {})
        assert players["team_a_4"]["position"] == before


class TestPenaltyKick:
    # team_a_4 penalty=18, team_b_0 GK save=12 →
    # p = 0.60 + 0.015*18 − 0.01*(12−10) = 0.87 − 0.02 = 0.85
    P_GOAL = 0.85

    def _run(self, tick, mutate=None):
        eng = make_engine()
        players = live_players()
        if mutate:
            mutate(players)
        wire(eng, players)
        snap = snap_from(players)
        records = {}
        # Foul by team_b at (90, 30) — inside team_b's own penalty area.
        eng._resolve_penalty_kick("team_b", "team_a", (90.0, 30.0),
                                  "team_b_1", snap, tick, records)
        return eng, players, records

    def test_taker_is_highest_penalty_attribute(self):
        eng, players, records = self._run(tick=3)
        assert records["system"]["kicker_id"] == "team_a_4"  # penalty=18

    def test_goal_when_draw_under_conversion(self):
        tick = next(t for t in range(200)
                    if hash_01(42, t, "team_a_4", "penalty_kick") < self.P_GOAL)
        eng, players, records = self._run(tick)
        assert records["system"]["penalty_outcome"] == "goal"
        assert records["system"]["goal_scored"] == "team_a"
        assert records["system"]["scored_by"] == "team_a_4"
        eng.gsm.record_goal.assert_called_once_with("team_a")

    def test_save_when_draw_over_conversion(self):
        tick = next(t for t in range(2000)
                    if hash_01(42, t, "team_a_4", "penalty_kick") >= self.P_GOAL)
        eng, players, records = self._run(tick)
        assert records["system"]["penalty_outcome"] == "saved"
        eng.gsm.record_goal.assert_not_called()
        # GK ends with the ball
        eng.gsm.transfer_possession.assert_called_with(None, "team_b_0")

    def test_gk_save_rating_shifts_conversion(self):
        # Pick a draw in [0.85, 0.87): saved against the save=12 keeper,
        # but a goal against an average (save=10) keeper on the SAME draw.
        tick = next(t for t in range(5000)
                    if 0.85 <= hash_01(42, t, "team_a_4", "penalty_kick") < 0.87)
        _, _, records_strong = self._run(tick)
        assert records_strong["system"]["penalty_outcome"] == "saved"

        def _average_gk(players):
            players["team_b_0"]["save"] = 10
        _, _, records_avg = self._run(tick, mutate=_average_gk)
        assert records_avg["system"]["penalty_outcome"] == "goal"

    def test_no_goalkeeper_means_automatic_goal(self):
        # GK sent off — Law 14 with no keeper: the kick always converts.
        # Pick a draw that would normally be SAVED to prove the bypass.
        tick = next(t for t in range(2000)
                    if hash_01(42, t, "team_a_4", "penalty_kick") >= self.P_GOAL)

        def _send_off_gk(players):
            players["team_b_0"]["sent_off"] = True
        eng, _, records = self._run(tick, mutate=_send_off_gk)
        assert records["system"]["penalty_outcome"] == "goal"
        assert records["system"]["reason"] == "no_goalkeeper"
        eng.gsm.record_goal.assert_called_once_with("team_a")

    def test_penalty_mark_position(self):
        eng, players, records = self._run(tick=3)
        # team_b defends x=100 → mark at (89, goal-center y = 30)
        assert records["system"]["restart_spot"] == (89.0, 30.0)
