"""Issue #38 follow-up — IFAB Law 13: a free-kick taker must put the ball
in play with Pass or Shoot. Move/Tackle are blocked while the kick is
pending, opponents cannot tackle the taker (ball not in play), and after
restart_auto_kick_ticks of stalling the engine kicks for them."""

from unittest.mock import Mock

from src.foundation.action import Hold, Move, Pass, Shoot, Tackle
from src.foundation.action_resolution_engine.engine import ActionResolutionEngine


def make_engine(auto_kick_ticks=20):
    gsm, pms, bps, sandbox, fallback = Mock(), Mock(), Mock(), Mock(), Mock()
    gsm.seed = 42
    gsm.state = Mock()
    gsm.state._pass_landing_zone = None
    gsm.config = Mock()
    sim = gsm.config.simulation
    sim.fouls_enabled = True
    sim.action_cooldown_ticks = 0
    sim.restart_auto_kick_ticks = auto_kick_ticks
    return ActionResolutionEngine(gsm, pms, bps, sandbox, fallback)


def base_snap():
    """team_a_3 is the pending free-kick taker and carrier at (50, 30)."""
    return {
        "ball": {"position": (50.0, 30.0), "velocity": (0.0, 0.0),
                 "carrier_id": "team_a_3"},
        "players": {
            "team_a_3": {"player_id": "team_a_3", "team": "team_a", "role": "MID",
                         "position": (50.0, 30.0), "skill": 10, "strength": 14,
                         "dribbling": 10, "speed": 10},
            "team_a_4": {"player_id": "team_a_4", "team": "team_a", "role": "FWD",
                         "position": (62.0, 30.0), "skill": 10, "strength": 10,
                         "dribbling": 10, "speed": 10},
            "team_b_1": {"player_id": "team_b_1", "team": "team_b", "role": "DEF",
                         "position": (59.4, 30.0), "skill": 10, "strength": 10,
                         "dribbling": 10, "speed": 10},
        },
        "field": {"width": 100.0, "height": 60.0,
                  "team_a_goal_x": 0.0, "team_b_goal_x": 100.0,
                  "goal_top": 33.66, "goal_bottom": 26.34},
    }


def wire_player_state(eng, snap):
    def _player_state(pid):
        return {**snap["players"][pid], "offensive": 10, "penalty": 10,
                "yellow_cards": 0, "current_health": 100.0}
    eng.gsm.build_player_state.side_effect = _player_state
    eng.gsm.get_last_action_tick.return_value = -10**9


class TestMustKickGate:
    def test_move_substituted_with_hold(self):
        eng = make_engine()
        snap = base_snap()
        wire_player_state(eng, snap)
        eng._pending_kick = ("team_a_3", 5)
        validated, reasons = eng._validate_actions(
            {"team_a_3": Move(dx=1.0, dy=0.0, speed=1.0)}, snap, tick=7)
        assert isinstance(validated["team_a_3"], Hold)
        assert reasons["team_a_3"] == "restart_must_kick"

    def test_pass_allowed(self):
        eng = make_engine()
        snap = base_snap()
        wire_player_state(eng, snap)
        eng._pending_kick = ("team_a_3", 5)
        validated, reasons = eng._validate_actions(
            {"team_a_3": Pass(target_pos=(62.0, 30.0), power=10)}, snap, tick=7)
        assert isinstance(validated["team_a_3"], Pass)

    def test_shoot_allowed(self):
        eng = make_engine()
        snap = base_snap()
        wire_player_state(eng, snap)
        eng._pending_kick = ("team_a_3", 5)
        validated, reasons = eng._validate_actions(
            {"team_a_3": Shoot(angle=0.0, power=10)}, snap, tick=7)
        assert isinstance(validated["team_a_3"], Shoot)

    def test_kick_bypasses_cooldown(self):
        eng = make_engine()
        snap = base_snap()
        wire_player_state(eng, snap)
        eng.gsm.config.simulation.action_cooldown_ticks = 10
        eng.gsm.get_last_action_tick.return_value = 6  # acted 1 tick ago
        eng._pending_kick = ("team_a_3", 5)
        validated, reasons = eng._validate_actions(
            {"team_a_3": Pass(target_pos=(62.0, 30.0), power=10)}, snap, tick=7)
        assert isinstance(validated["team_a_3"], Pass)
        assert reasons.get("team_a_3") != "cooldown_blocked"

    def test_other_players_unaffected(self):
        eng = make_engine()
        snap = base_snap()
        wire_player_state(eng, snap)
        eng._pending_kick = ("team_a_3", 5)
        validated, _ = eng._validate_actions(
            {"team_b_1": Move(dx=-1.0, dy=0.0, speed=1.0)}, snap, tick=7)
        assert isinstance(validated["team_b_1"], Move)


class TestAutoKick:
    def test_stalling_past_threshold_forces_pass_to_nearest_teammate(self):
        eng = make_engine(auto_kick_ticks=20)
        snap = base_snap()
        wire_player_state(eng, snap)
        eng._pending_kick = ("team_a_3", 5)
        validated, reasons = eng._validate_actions(
            {"team_a_3": Hold()}, snap, tick=25)  # 25 - 5 >= 20
        v = validated["team_a_3"]
        assert isinstance(v, Pass)
        assert v.target_pos == (62.0, 30.0)  # team_a_4, the only teammate
        assert reasons["team_a_3"] == "restart_auto_kick"

    def test_below_threshold_hold_passes_through(self):
        eng = make_engine(auto_kick_ticks=20)
        snap = base_snap()
        wire_player_state(eng, snap)
        eng._pending_kick = ("team_a_3", 5)
        validated, reasons = eng._validate_actions(
            {"team_a_3": Hold()}, snap, tick=10)
        assert isinstance(validated["team_a_3"], Hold)
        assert reasons.get("team_a_3") is None


class TestBallNotInPlay:
    def test_tackle_on_pending_kicker_is_no_op(self):
        eng = make_engine()
        snap = base_snap()
        wire_player_state(eng, snap)
        eng.gsm.state.ball = dict(snap["ball"])
        eng.gsm.config.simulation.tackle_settle_grace_ticks = 0
        eng.gsm.config.simulation.tackle_range = 2.0
        # Defender adjacent to the kicker.
        snap["players"]["team_b_1"]["position"] = (50.5, 30.0)
        eng._pending_kick = ("team_a_3", 5)
        eng.dribble_consumed = set()
        eng.move_results = {}
        records = eng._resolve_phase6(
            {"team_b_1": Tackle(target_player_id="team_a_3")}, snap, tick=7)
        assert records["team_b_1"]["result"] == "no_op_restart_pending"


class TestPendingLifecycle:
    def test_foul_free_kick_sets_pending(self):
        eng = make_engine()
        players = {pid: {**p, "sent_off": False}
                   for pid, p in base_snap()["players"].items()}
        eng.gsm.state.players = players
        eng.gsm.state.field = dict(base_snap()["field"])
        eng._apply_foul_free_kick("team_b", "team_a", (50.0, 30.0),
                                  "team_b_1", base_snap(), 9, {})
        assert eng._pending_kick is not None
        assert eng._pending_kick[0].startswith("team_a")
        assert eng._pending_kick[1] == 9

    def test_offside_free_kick_sets_pending(self):
        eng = make_engine()
        snap = base_snap()
        players = {pid: {**p, "sent_off": False}
                   for pid, p in snap["players"].items()}
        eng.gsm.state.players = players
        eng.gsm.state.field = dict(snap["field"])
        eng._apply_offside_free_kick("team_a_4", snap, {}, tick=11)
        assert eng._pending_kick is not None
        assert eng._pending_kick[1] == 11

    def test_oob_restart_sets_pending(self):
        """Throw-ins / corners / goal kicks get the same must-kick rule
        (Laws 15/16/17 — the ball is in play only once thrown/kicked)."""
        eng = make_engine()
        snap = base_snap()
        players = {pid: {**p, "sent_off": False}
                   for pid, p in snap["players"].items()}
        eng.gsm.state.players = players
        eng.gsm.state.field = dict(snap["field"])
        eng._last_touching_team = "team_b"
        # Ball over the top side line at x=40 → throw-in to team_a.
        eng._apply_oob_restart((40.0, 0.0), snap, {}, tick=13)
        assert eng._pending_kick is not None
        assert eng._pending_kick[0].startswith("team_a")
        assert eng._pending_kick[1] == 13

    def test_pass_by_kicker_clears_pending(self):
        eng = make_engine()
        snap = base_snap()
        wire_player_state(eng, snap)
        eng._pending_kick = ("team_a_3", 5)
        eng._resolve_phase5(
            {"team_a_3": Pass(target_pos=(62.0, 30.0), power=10)},
            snap, tick=7, current_carrier="team_a_3")
        assert eng._pending_kick is None

    def test_game_state_injection_field(self):
        """Phase 2 injects restart_kicker into each player's game_state."""
        from src.foundation.game_state_schema import _EXTRA_ALLOWED_TOP_KEYS
        assert "restart_kicker" in _EXTRA_ALLOWED_TOP_KEYS
