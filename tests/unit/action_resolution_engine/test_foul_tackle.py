"""Issue #38 — IFAB Law 12 foul roll in ARE Phase 6: probability scaling
with `offensive`, severity → cards, preemption of the tackle contest."""

from unittest.mock import Mock

from src.foundation.action import Tackle
from src.foundation.action_resolution_engine.engine import ActionResolutionEngine
from src.foundation.simulation_utils import hash_01


def make_engine(fouls_enabled=True, tackle_foul_base=0.10,
                foul_yellow_share=0.25, foul_red_share=0.05):
    gsm, pms, bps, sandbox, fallback = Mock(), Mock(), Mock(), Mock(), Mock()
    gsm.seed = 42
    gsm.state = Mock()
    gsm.state._pass_landing_zone = None
    gsm.config = Mock()
    sim = gsm.config.simulation
    sim.fouls_enabled = fouls_enabled
    sim.tackle_foul_base = tackle_foul_base
    sim.foul_yellow_share = foul_yellow_share
    sim.foul_red_share = foul_red_share
    sim.penalty_goal_base = 0.60
    sim.penalty_goal_per_point = 0.015
    sim.free_kick_exclusion_radius = 9.15
    sim.action_cooldown_ticks = 0
    sim.tackle_settle_grace_ticks = 0
    sim.tackle_clean_share = 0.55
    sim.tackle_blocked_floor = 0.15
    sim.tackle_range = 2.0
    return ActionResolutionEngine(gsm, pms, bps, sandbox, fallback)


def field_dict():
    return {"width": 100.0, "height": 60.0,
            "team_a_goal_x": 0.0, "team_b_goal_x": 100.0,
            "goal_top": 33.66, "goal_bottom": 26.34}


def base_snap(tackler_pos=(50.0, 30.0), target_pos=(50.5, 30.0)):
    """team_b_1 (defender) tackles team_a_0 (carrier) at midfield."""
    return {
        "ball": {"position": target_pos, "velocity": (0.0, 0.0),
                 "carrier_id": "team_a_0"},
        "players": {
            "team_a_0": {"player_id": "team_a_0", "team": "team_a", "role": "MID",
                         "position": target_pos, "skill": 10, "strength": 10,
                         "dribbling": 10, "speed": 10},
            "team_b_1": {"player_id": "team_b_1", "team": "team_b", "role": "DEF",
                         "position": tackler_pos, "skill": 10, "strength": 10,
                         "dribbling": 10, "speed": 10},
        },
        "field": field_dict(),
    }


def wire_gsm(eng, snap, offensive=10):
    """Wire the mock GSM so Phase 6 reads real values."""
    g = eng.gsm
    g.state.ball = dict(snap["ball"])
    g.state.players = {
        pid: {**p, "sent_off": False} for pid, p in snap["players"].items()
    }
    g.state.field = dict(snap["field"])

    def _player_state(pid):
        p = snap["players"][pid]
        return {**p, "offensive": offensive if pid == "team_b_1" else 10,
                "penalty": 10, "yellow_cards": 0, "current_health": 100.0}
    g.build_player_state.side_effect = _player_state
    g.get_last_action_tick.return_value = -10**9
    g.record_card.return_value = False
    return g


def find_foul_tick(offensive, max_tick=400):
    """First tick where the deterministic foul draw fires for team_b_1."""
    foul_prob = 0.10 * (offensive / 10.0)
    for t in range(max_tick):
        if hash_01(42, t, "team_b_1", "foul") < foul_prob:
            return t
    raise AssertionError("no foul draw under threshold in range")


class TestFoulRoll:
    def test_foul_preempts_tackle_contest(self):
        tick = find_foul_tick(offensive=10)
        eng = make_engine()
        snap = base_snap()
        wire_gsm(eng, snap)
        eng.dribble_consumed = set()
        eng.move_results = {}
        records = eng._resolve_phase6(
            {"team_b_1": Tackle(target_player_id="team_a_0")}, snap, tick)
        assert records["team_b_1"]["result"] == "foul"
        assert "foul_severity" in records["team_b_1"]
        assert "system" in records

    def test_no_foul_when_disabled(self):
        tick = find_foul_tick(offensive=10)
        eng = make_engine(fouls_enabled=False)
        snap = base_snap()
        wire_gsm(eng, snap)
        eng.dribble_consumed = set()
        eng.move_results = {}
        records = eng._resolve_phase6(
            {"team_b_1": Tackle(target_player_id="team_a_0")}, snap, tick)
        assert records["team_b_1"]["result"] != "foul"

    def test_low_offensive_does_not_foul_on_same_draw(self):
        # Pick a tick whose draw is in (0.01, 0.10]: fouls at offensive=10
        # but not at offensive=1.
        foul_prob_high, foul_prob_low = 0.10, 0.01
        tick = next(t for t in range(2000)
                    if foul_prob_low <= hash_01(42, t, "team_b_1", "foul") < foul_prob_high)
        eng = make_engine()
        snap = base_snap()
        wire_gsm(eng, snap, offensive=1)
        eng.dribble_consumed = set()
        eng.move_results = {}
        records = eng._resolve_phase6(
            {"team_b_1": Tackle(target_player_id="team_a_0")}, snap, tick)
        assert records["team_b_1"]["result"] != "foul"


class TestSeverityCards:
    def _run_foul_at(self, tick, eng=None):
        eng = eng or make_engine()
        snap = base_snap()
        wire_gsm(eng, snap)
        eng.dribble_consumed = set()
        eng.move_results = {}
        records = eng._resolve_phase6(
            {"team_b_1": Tackle(target_player_id="team_a_0")}, snap, tick)
        return eng, records

    def test_severity_matches_draw_thresholds(self):
        tick = find_foul_tick(offensive=10)
        sev_draw = hash_01(42, tick, "team_b_1", "foul_severity")
        if sev_draw < 0.05:
            expected = ("excessive_force", "red")
        elif sev_draw < 0.30:
            expected = ("reckless", "yellow")
        else:
            expected = ("careless", None)
        eng, records = self._run_foul_at(tick)
        rec = records["team_b_1"]
        assert rec["foul_severity"] == expected[0]
        assert rec.get("card") == expected[1]
        if expected[1] is not None:
            eng.gsm.record_card.assert_called_once_with("team_b_1", expected[1])
        else:
            eng.gsm.record_card.assert_not_called()

    def test_each_severity_reachable(self):
        """Sweep ticks until every severity class has occurred — guards the
        threshold arithmetic (red < red+yellow < 1)."""
        seen = set()
        for tick in range(3000):
            if hash_01(42, tick, "team_b_1", "foul") >= 0.10:
                continue
            _, records = self._run_foul_at(tick)
            seen.add(records["team_b_1"]["foul_severity"])
            if seen == {"careless", "reckless", "excessive_force"}:
                break
        assert seen == {"careless", "reckless", "excessive_force"}
