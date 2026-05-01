# tests/unit/player_movement_system/test_dribble.py

from __future__ import annotations
import pytest
from src.core.player_movement_system import detect_dribble_target


class TestDetectDribbleTarget:
    """Test dribble contest detection per Story 002 acceptance criteria."""

    def test_contest_fires_for_ball_carrier_within_range(self):
        """AC-1: Ball carrier at (30.0, 30.0), opponent at (31.0, 30.0) → dribble_target == "team_b_0"."""
        final_pos = (30.0, 30.0)
        player_state = {"has_ball": True, "team": "team_a"}
        action = {"type": "move"}
        game_state_snapshot = {
            "players": {
                "team_a_0": {"position": (30.0, 30.0), "team": "team_a"},
                "team_b_0": {"position": (31.0, 30.0), "team": "team_b"}
            }
        }

        result = detect_dribble_target(final_pos, player_state, action, game_state_snapshot)
        assert result == "team_b_0"

    def test_no_contest_for_non_carrier(self):
        """AC-2: Player without ball at (30.0, 30.0), opponent at (30.5, 30.0) → returns None."""
        final_pos = (30.0, 30.0)
        player_state = {"has_ball": False, "team": "team_a"}
        action = {"type": "move"}
        game_state_snapshot = {
            "players": {
                "team_a_0": {"position": (30.0, 30.0), "team": "team_a"},
                "team_b_0": {"position": (30.5, 30.0), "team": "team_b"}
            }
        }

        result = detect_dribble_target(final_pos, player_state, action, game_state_snapshot)
        assert result is None

    def test_no_contest_on_hold_action(self):
        """AC-3: Ball carrier with Hold action → returns None."""
        final_pos = (30.0, 30.0)
        player_state = {"has_ball": True, "team": "team_a"}
        action = {"type": "hold"}
        game_state_snapshot = {
            "players": {
                "team_a_0": {"position": (30.0, 30.0), "team": "team_a"},
                "team_b_0": {"position": (30.5, 30.0), "team": "team_b"}
            }
        }

        result = detect_dribble_target(final_pos, player_state, action, game_state_snapshot)
        assert result is None

    def test_nearest_opponent_selected(self):
        """AC-4: Opponents A at d=1.0, B at d=0.2 → returns B's player_id."""
        final_pos = (30.0, 30.0)
        player_state = {"has_ball": True, "team": "team_a"}
        action = {"type": "move"}
        game_state_snapshot = {
            "players": {
                "team_a_0": {"position": (30.0, 30.0), "team": "team_a"},
                "team_b_0": {"position": (31.0, 30.0), "team": "team_b"},  # distance = 1.0
                "team_b_1": {"position": (30.2, 30.0), "team": "team_b"}   # distance = 0.2
            }
        }

        result = detect_dribble_target(final_pos, player_state, action, game_state_snapshot)
        assert result == "team_b_1"

    def test_lexicographic_tie_break(self):
        """AC-5: 2 opponents at exactly same position with player_ids team_b_3 and team_b_0 → returns team_b_0."""
        final_pos = (30.0, 30.0)
        player_state = {"has_ball": True, "team": "team_a"}
        action = {"type": "move"}
        game_state_snapshot = {
            "players": {
                "team_a_0": {"position": (30.0, 30.0), "team": "team_a"},
                "team_b_3": {"position": (30.5, 30.0), "team": "team_b"},  # same distance
                "team_b_0": {"position": (30.5, 30.0), "team": "team_b"}   # same distance
            }
        }

        result = detect_dribble_target(final_pos, player_state, action, game_state_snapshot)
        assert result == "team_b_0"  # lexicographically smallest

    def test_same_team_players_excluded(self):
        """AC-6: Same-team players excluded from consideration."""
        final_pos = (30.0, 30.0)
        player_state = {"has_ball": True, "team": "team_a"}
        action = {"type": "move"}
        game_state_snapshot = {
            "players": {
                "team_a_0": {"position": (30.0, 30.0), "team": "team_a"},
                "team_a_1": {"position": (30.1, 30.0), "team": "team_a"},  # same team, closer
                "team_b_0": {"position": (30.5, 30.0), "team": "team_b"}   # opponent, farther
            }
        }

        result = detect_dribble_target(final_pos, player_state, action, game_state_snapshot)
        assert result == "team_b_0"  # same-team player excluded

    def test_outside_range_returns_none(self):
        """AC-7: Opponent outside DRIBBLE_RANGE (1.5) returns None."""
        final_pos = (30.0, 30.0)
        player_state = {"has_ball": True, "team": "team_a"}
        action = {"type": "move"}
        game_state_snapshot = {
            "players": {
                "team_a_0": {"position": (30.0, 30.0), "team": "team_a"},
                "team_b_0": {"position": (35.0, 30.0), "team": "team_b"}   # distance = 5.0 > 1.5
            }
        }

        result = detect_dribble_target(final_pos, player_state, action, game_state_snapshot)
        assert result is None

    def test_exact_range_boundary_excluded(self):
        """AC-8: Opponent at exactly DRIBBLE_RANGE (1.5) distance → returns None (strict less-than)."""
        final_pos = (30.0, 30.0)
        player_state = {"has_ball": True, "team": "team_a"}
        action = {"type": "move"}
        game_state_snapshot = {
            "players": {
                "team_a_0": {"position": (30.0, 30.0), "team": "team_a"},
                "team_b_0": {"position": (31.5, 30.0), "team": "team_b"}   # distance exactly = 1.5
            }
        }

        result = detect_dribble_target(final_pos, player_state, action, game_state_snapshot)
        assert result is None  # 2.25 < 2.25 is False

    def test_pure_function_no_input_mutation(self):
        """AC-9: Function does not mutate input dictionaries."""
        final_pos = (30.0, 30.0)
        player_state = {"has_ball": True, "team": "team_a"}
        action = {"type": "move", "dx": 1.0, "dy": 0.0}
        game_state_snapshot = {
            "players": {
                "team_a_0": {"position": (30.0, 30.0), "team": "team_a"},
                "team_b_0": {"position": (30.5, 30.0), "team": "team_b"}
            }
        }

        # Make copies to verify no mutation
        original_player_state = player_state.copy()
        original_action = action.copy()
        original_snapshot = {
            "players": {k: v.copy() for k, v in game_state_snapshot["players"].items()}
        }

        detect_dribble_target(final_pos, player_state, action, game_state_snapshot)

        # Verify no mutation occurred
        assert player_state == original_player_state
        assert action == original_action
        assert game_state_snapshot == original_snapshot

    def test_empty_players_dict_returns_none(self):
        """AC-10: Empty players dict returns None."""
        final_pos = (30.0, 30.0)
        player_state = {"has_ball": True, "team": "team_a"}
        action = {"type": "move"}
        game_state_snapshot = {"players": {}}

        result = detect_dribble_target(final_pos, player_state, action, game_state_snapshot)
        assert result is None