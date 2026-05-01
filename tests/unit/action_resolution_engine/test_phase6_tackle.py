"""Test Phase 6: Tackle resolution.

Tests for ARE Story 006 — GDD Rule 12 tackle resolution phase.
Verifies range checks, carrier checks, PAM F4 formula, possession transfers,
and proper ordering of multiple tackles.
"""

import pytest
from unittest.mock import Mock, patch

from src.foundation.action_resolution_engine.engine import ActionResolutionEngine
from src.foundation.action import Tackle, Hold


class TestPhase6Tackle:
    """Test Phase 6 tackle resolution logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.gsm = Mock()
        self.pms = Mock()
        self.bps = Mock()
        self.sandbox = Mock()
        self.fallback_handler = Mock()

        self.engine = ActionResolutionEngine(
            gsm=self.gsm,
            pms=self.pms,
            bps=self.bps,
            sandbox=self.sandbox,
            fallback_handler=self.fallback_handler
        )

        # Standard test snapshot with players - position within TACKLE_RANGE (1.5)
        self.snap = {
            "players": {
                "team_a_1": {
                    "player_id": "team_a_1",
                    "team": "team_a",
                    "position": (50.0, 30.0),
                },
                "team_b_3": {
                    "player_id": "team_b_3",
                    "team": "team_b",
                    "position": (51.0, 30.0),  # Distance 1.0 < TACKLE_RANGE 1.5
                },
                "team_a_2": {
                    "player_id": "team_a_2",
                    "team": "team_a",
                    "position": (49.5, 30.0),  # Distance 1.5 = TACKLE_RANGE (edge case)
                },
            },
            "ball": {"carrier_id": "team_b_3"}
        }

        # Mock GSM state access and player states
        self.gsm.state.ball = {"carrier_id": "team_b_3"}
        self.gsm.build_player_state.return_value = {"strength": 10}

    @patch('src.foundation.action_resolution_engine.engine.hash_01')
    def test_tackle_controlled_transfers_possession(self, mock_hash):
        """AC-ARE (ADR-0018, 2026-04-22): a tackle whose hash_01 draw lands
        in the [0, controlled_prob) window is a clean take ("controlled").
        Equal-strength contest (10v10) → prob=0.5, default tackle_clean_share
        =0.55, so controlled_prob = 0.275. Draw 0.0 < 0.275 → controlled."""
        mock_hash.return_value = 0.0  # → controlled

        validated_actions = {
            "team_a_1": Tackle(target_player_id="team_b_3"),
            "team_b_3": Hold(),
        }

        # Set up engine state (mock Phase 4 having run)
        self.engine.dribble_consumed = set()
        self.engine.move_results = {}  # No moves, use snap positions

        result = self.engine._resolve_phase6(validated_actions, self.snap, tick=100)

        # Verify possession transfer was called
        self.gsm.transfer_possession.assert_called_once_with("team_b_3", "team_a_1")

        # Verify result record
        assert result == {
            "team_a_1": {"action": "Tackle", "result": "controlled"}
        }

    @patch('src.foundation.action_resolution_engine.engine.hash_01')
    def test_tackle_failure_no_transfer(self, mock_hash):
        """AC-ARE: Tackle failure does not transfer possession."""
        mock_hash.return_value = 0.9  # Guaranteed failure (draw >= prob)

        validated_actions = {
            "team_a_1": Tackle(target_player_id="team_b_3"),
            "team_b_3": Hold(),
        }

        self.engine.dribble_consumed = set()
        self.engine.move_results = {}

        result = self.engine._resolve_phase6(validated_actions, self.snap, tick=100)

        # Verify no possession transfer
        self.gsm.transfer_possession.assert_not_called()

        # Verify result record
        assert result == {
            "team_a_1": {"action": "Tackle", "result": "failed"}
        }

    def test_out_of_range_tackle(self):
        """AC-ARE-10: Tackler out of range gets out_of_range result."""
        # Position tackler far from target (TACKLE_RANGE = 1.5)
        snap = {
            "players": {
                "team_a_1": {
                    "player_id": "team_a_1",
                    "team": "team_a",
                    "position": (50.0, 30.0),  # Tackler
                },
                "team_b_3": {
                    "player_id": "team_b_3",
                    "team": "team_b",
                    "position": (60.0, 30.0),  # Target 10 units away > 1.5
                },
            },
            "ball": {"carrier_id": "team_b_3"}
        }

        validated_actions = {
            "team_a_1": Tackle(target_player_id="team_b_3"),
        }

        self.engine.dribble_consumed = set()
        self.engine.move_results = {}

        result = self.engine._resolve_phase6(validated_actions, snap, tick=100)

        # Verify no possession transfer attempted
        self.gsm.transfer_possession.assert_not_called()

        # Verify out-of-range result
        assert result == {
            "team_a_1": {"action": "Tackle", "result": "out_of_range"}
        }

    def test_tackle_non_carrier_no_op(self):
        """AC-ARE: Tackle on non-carrier is no-op."""
        # Ball carrier is someone else
        self.gsm.state.ball = {"carrier_id": "team_a_0"}  # Different from target

        validated_actions = {
            "team_a_1": Tackle(target_player_id="team_b_3"),  # Target doesn't have ball
        }

        self.engine.dribble_consumed = set()
        self.engine.move_results = {}

        result = self.engine._resolve_phase6(validated_actions, self.snap, tick=100)

        # Verify no possession transfer
        self.gsm.transfer_possession.assert_not_called()

        # Verify no-op result
        assert result == {
            "team_a_1": {"action": "Tackle", "result": "no_op_carrier_changed"}
        }

    def test_dribble_consumed_skip(self):
        """AC-ARE-06: Defenders in dribble_consumed are skipped entirely."""
        validated_actions = {
            "team_a_1": Tackle(target_player_id="team_b_3"),
            "team_a_2": Tackle(target_player_id="team_b_3"),
        }

        # team_a_2 was consumed by dribble contest in Phase 4
        self.engine.dribble_consumed = {"team_a_2"}
        self.engine.move_results = {}

        result = self.engine._resolve_phase6(validated_actions, self.snap, tick=100)

        # Only team_a_1 should be processed (team_a_2 skipped)
        # team_a_1 should get no_op_carrier_changed since no hash mock set up
        assert len(result) == 1
        assert "team_a_1" in result
        assert "team_a_2" not in result  # Skipped entirely

    @patch('src.foundation.action_resolution_engine.engine.hash_01')
    def test_multiple_tacklers_ascending_order(self, mock_hash):
        """AC-ARE-11: Multiple tacklers resolved in player_id ascending order."""
        # Set up two tacklers: team_a_2 and team_a_1 (test sorting)
        validated_actions = {
            "team_a_2": Tackle(target_player_id="team_b_3"),  # Should be processed second
            "team_a_1": Tackle(target_player_id="team_b_3"),  # Should be processed first
        }

        self.engine.dribble_consumed = set()
        self.engine.move_results = {}

        # First call (team_a_1) succeeds, second call (team_a_2) for different target
        mock_hash.side_effect = [0.0, 0.0]  # Both would succeed, but order matters

        # Mock transfer_possession to change carrier_id after first success
        def side_effect(from_id, to_id):
            if from_id == "team_b_3" and to_id == "team_a_1":
                self.gsm.state.ball["carrier_id"] = "team_a_1"

        self.gsm.transfer_possession.side_effect = side_effect

        result = self.engine._resolve_phase6(validated_actions, self.snap, tick=100)

        # Verify hash_01 called once with team_a_1 (ascending order; second tackler short-circuits on carrier change)
        from unittest.mock import call
        assert mock_hash.call_args_list[0] == call(self.gsm.seed, 100, "team_a_1", "team_b_3")
        assert mock_hash.call_count == 1  # Second tackler fails carrier check before hash_01

        # First tackle is controlled (clean take); second finds carrier
        # changed (no hash_01 call needed). Per ADR-0018 "success" → "controlled".
        assert result["team_a_1"]["result"] == "controlled"
        assert result["team_a_2"]["result"] == "no_op_carrier_changed"

    def test_range_check_uses_post_commit_positions(self):
        """AC-ARE-10: Range check uses post-Phase-4 committed positions."""
        # Set up move_results from Phase 4 with final positions
        self.engine.dribble_consumed = set()
        self.engine.move_results = {
            "team_a_1": ((51.0, 30.0), None),  # Moved to within range of team_b_3
            "team_b_3": ((52.0, 30.0), None),  # Moved slightly
        }

        # Snap has old positions that would be out of range
        snap = {
            "players": {
                "team_a_1": {
                    "player_id": "team_a_1",
                    "team": "team_a",
                    "position": (40.0, 30.0),  # Old position, out of range
                },
                "team_b_3": {
                    "player_id": "team_b_3",
                    "team": "team_b",
                    "position": (60.0, 30.0),  # Old position, out of range
                },
            },
            "ball": {"carrier_id": "team_b_3"}
        }

        validated_actions = {
            "team_a_1": Tackle(target_player_id="team_b_3"),
        }

        result = self.engine._resolve_phase6(validated_actions, snap, tick=100)

        # Should use post-commit positions (1.0 apart) not snap positions (20.0 apart)
        # Distance 1.0 < TACKLE_RANGE 1.5, so tackle should be attempted (not out_of_range)
        assert result["team_a_1"]["result"] != "out_of_range"

    @patch('src.foundation.action_resolution_engine.engine.hash_01')
    def test_pam_f4_formula(self, mock_hash):
        """AC-ARE (ADR-0018, 2026-04-22): F4 base prob = tackler.str /
        (tackler.str + target.str) is unchanged. The "controlled" threshold
        is prob * tackle_clean_share (default 0.55).

        15v10 → prob = 0.6, controlled_prob = 0.6 * 0.55 = 0.33.
        Draw 0.20 < 0.33 → controlled."""
        def mock_player_state(player_id):
            if player_id == "team_a_1":
                return {"strength": 15}  # Tackler
            elif player_id == "team_b_3":
                return {"strength": 10}  # Target
            return {"strength": 10}

        self.gsm.build_player_state.side_effect = mock_player_state
        mock_hash.return_value = 0.20  # < 0.33 controlled threshold

        validated_actions = {
            "team_a_1": Tackle(target_player_id="team_b_3"),
        }

        self.engine.dribble_consumed = set()
        self.engine.move_results = {}

        result = self.engine._resolve_phase6(validated_actions, self.snap, tick=100)

        assert result["team_a_1"]["result"] == "controlled"

        # Verify transfer_possession called
        self.gsm.transfer_possession.assert_called_once_with("team_b_3", "team_a_1")

    def test_ec_are_01_passer_tackled_same_tick(self):
        """EC-ARE-01: After Phase 5 pass, carrier_id is None, tackle is no-op."""
        # Ball carrier is None (passed in Phase 5)
        self.gsm.state.ball = {"carrier_id": None}

        validated_actions = {
            "team_a_1": Tackle(target_player_id="team_b_3"),  # Target was passer
        }

        self.engine.dribble_consumed = set()
        self.engine.move_results = {}

        result = self.engine._resolve_phase6(validated_actions, self.snap, tick=100)

        # Tackle should be no-op since carrier_id != target_id (None != "team_b_3")
        assert result == {
            "team_a_1": {"action": "Tackle", "result": "no_op_carrier_changed"}
        }