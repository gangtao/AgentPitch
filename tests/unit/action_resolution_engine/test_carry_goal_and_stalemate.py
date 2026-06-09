"""ARE bugfix #22 — carried-ball goal detection + stalemate breaker.

Two defects surfaced by the canada-vs-bosnia match (ball frozen on the goal
line for the last ~132s):

1. A ball *dribbled/carried* over the goal line was never scored — the goal
   check only ran on the loose-ball / shot / pass physics path, while the
   carry branch of _resolve_phase7 snapped the ball to the carrier and
   returned early. A forward could stand on the goal line in the centre of
   the goal forever without scoring.

2. Nothing broke a stalemate: when the ball sat effectively motionless under
   a carrier (pinned at a boundary, no one pressuring), possession never
   changed and the match froze.
"""

import pytest
from unittest.mock import Mock

from src.foundation.action_resolution_engine.engine import ActionResolutionEngine


def _make_engine():
    engine = ActionResolutionEngine(Mock(), Mock(), Mock(), Mock(), Mock())
    engine._ball_just_passed = False
    engine._last_touching_team = None
    engine.gsm.state = Mock()
    return engine


# Geometric field used by the carry-path tests. team_a defends x=0,
# team_b defends x=100. Goal mouth spans y in [25, 35].
FIELD = {
    "width": 100.0, "height": 60.0,
    "team_a_goal_x": 0.0, "team_b_goal_x": 100.0,
    "goal_top": 35.0, "goal_bottom": 25.0,
}


class TestCarriedBallGoal:
    """Fix 1 — a carried ball over the goal line is a goal."""

    def _carry_snap(self, carrier_id, carrier_pos):
        return {
            "ball": {"position": carrier_pos, "velocity": (0.0, 0.0),
                     "carrier_id": carrier_id},
            "players": {
                carrier_id: {"player_id": carrier_id,
                             "team": carrier_id.rsplit("_", 1)[0],
                             "position": carrier_pos, "position_type": "FWD"},
            },
            "field": dict(FIELD),
        }

    def test_carried_ball_over_opponent_goal_line_scores(self):
        """A forward dribbling the ball onto the opponent goal line (within the
        goal mouth) scores for their team."""
        engine = _make_engine()
        # gsm.state.ball / players are Mocks (not dicts) → carry branch falls
        # back to the snap for carrier position.
        snap = self._carry_snap("team_a_9", (100.0, 30.0))

        engine._resolve_phase7(snap, tick=1700)

        engine.gsm.record_goal.assert_called_once_with("team_a")

    def test_carrying_ball_on_own_goal_line_is_not_a_goal(self):
        """A player in possession on their OWN goal line (keeper holding the
        ball, defender shielding on the line) is NOT an own goal. Real own
        goals come from a PLAYED ball with velocity via the ball-physics path,
        not from carrying — awarding one here made goal-line defending score
        own goals en masse (bugfix #22 regression)."""
        engine = _make_engine()
        snap = self._carry_snap("team_a_2", (0.0, 30.0))  # team_a defends x=0

        engine._resolve_phase7(snap, tick=1700)

        engine.gsm.record_goal.assert_not_called()

    def test_carried_ball_on_byline_outside_goal_mouth_is_not_a_goal(self):
        """Carrying the ball to the goal line but OUTSIDE the posts is not a
        goal (guards against over-firing)."""
        engine = _make_engine()
        snap = self._carry_snap("team_a_9", (100.0, 5.0))  # y outside [25,35]

        engine._resolve_phase7(snap, tick=1700)

        engine.gsm.record_goal.assert_not_called()

    def _carry_snap_with_keeper(self, carrier_id, carrier_pos,
                                keeper_id, keeper_pos):
        snap = self._carry_snap(carrier_id, carrier_pos)
        snap["players"][keeper_id] = {
            "player_id": keeper_id, "team": keeper_id.rsplit("_", 1)[0],
            "position": keeper_pos, "position_type": "GK",
        }
        return snap

    def test_keeper_in_position_saves_a_dribbled_in_ball(self):
        """A skilled keeper at the goal line smothers a point-blank dribble —
        no goal, keeper takes possession. Without this a slow dribble walks
        past the keeper into the net every time (bugfix #22 over-scored)."""
        engine = _make_engine()
        engine.gsm.seed = 42
        engine.gsm.build_player_state = lambda pid: {"save": 20, "skill": 20}
        # Carrier and a strong keeper both on the goal line (dist 0, ball
        # speed 0 → save probability ~1.0).
        snap = self._carry_snap_with_keeper(
            "team_a_9", (100.0, 30.0), "team_b_0", (100.0, 30.0))

        engine._resolve_phase7(snap, tick=1700)

        engine.gsm.record_goal.assert_not_called()
        engine.gsm.transfer_possession.assert_called_once_with("team_a_9", "team_b_0")

    def test_weak_keeper_far_from_ball_still_concedes(self):
        """The save is probabilistic by skill/distance: a weak, out-of-position
        keeper does NOT stop the dribble."""
        engine = _make_engine()
        engine.gsm.seed = 42
        engine.gsm.build_player_state = lambda pid: {"save": 1, "skill": 1}
        snap = self._carry_snap_with_keeper(
            "team_a_9", (100.0, 30.0), "team_b_0", (50.0, 30.0))  # far away

        engine._resolve_phase7(snap, tick=1700)

        engine.gsm.record_goal.assert_called_once_with("team_a")


class TestStalemateBreaker:
    """Fix 2 — a ball frozen under a carrier for too long forces a turnover."""

    def _stuck_state(self, gsm):
        gsm.state.ball = {"position": (100.0, 5.0), "carrier_id": "team_a_9",
                          "velocity": (0.0, 0.0)}
        gsm.state.players = {
            "team_a_9": {"player_id": "team_a_9", "team": "team_a",
                         "position": (100.0, 5.0)},
            "team_b_3": {"player_id": "team_b_3", "team": "team_b",
                         "position": (90.0, 8.0)},   # nearest opponent
            "team_b_5": {"player_id": "team_b_5", "team": "team_b",
                         "position": (55.0, 30.0)},  # far opponent
        }

    def test_static_ball_forces_turnover_to_nearest_opponent_after_50_ticks(self):
        engine = _make_engine()
        self._stuck_state(engine.gsm)

        # 49 ticks with the ball motionless: no turnover yet.
        for t in range(49):
            engine._check_stalemate(tick=t)
        engine.gsm.transfer_possession.assert_not_called()

        # 50th tick crosses the threshold → possession flips to the nearest
        # opposing player.
        engine._check_stalemate(tick=49)
        engine.gsm.transfer_possession.assert_called_once_with("team_a_9", "team_b_3")

    def test_moving_ball_does_not_trigger_turnover(self):
        engine = _make_engine()
        self._stuck_state(engine.gsm)

        # Ball advances well beyond the stuck radius every tick.
        for t in range(60):
            engine.gsm.state.ball["position"] = (float(t), 30.0)
            engine._check_stalemate(tick=t)

        engine.gsm.transfer_possession.assert_not_called()
