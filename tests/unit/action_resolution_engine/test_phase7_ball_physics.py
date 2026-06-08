"""ARE Story 007 — Phase 7 Ball Physics + Rule 16 + Goal Attempts.

Test suite for the ball physics phase including BPS integration,
offside-equivalent Rule 16, passer exclusion, and goalkeeper save attempts.
"""

import pytest
from unittest.mock import Mock, patch

from src.foundation.action_resolution_engine.engine import ActionResolutionEngine
from src.foundation.simulation_utils import hash_01


class TestPhase7BallPhysics:
    """Test ARE Story 007 Phase 7 implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_gsm = Mock()
        self.mock_pms = Mock()
        self.mock_bps = Mock()
        self.mock_sandbox = Mock()
        self.mock_fallback = Mock()

        self.engine = ActionResolutionEngine(
            self.mock_gsm, self.mock_pms, self.mock_bps, self.mock_sandbox, self.mock_fallback
        )
        # Initialize tick-local state for testing
        self.engine._ball_just_passed = False
        self.engine._last_touching_team = None

        # Common test data
        self.snap = {
            "ball": {"position": (50.0, 30.0), "velocity": (2.0, 0.0), "carrier_id": None},
            "players": {
                "team_a_0": {"player_id": "team_a_0", "team": "team_a", "position": (45.0, 30.0), "position_type": "FWD"},
                "team_a_1": {"player_id": "team_a_1", "team": "team_a", "position": (30.0, 30.0), "position_type": "DEF"},
                "team_b_0": {"player_id": "team_b_0", "team": "team_b", "position": (55.0, 30.0), "position_type": "FWD"},
                "team_b_1": {"player_id": "team_b_1", "team": "team_b", "position": (70.0, 30.0), "position_type": "DEF"},
                "team_b_2": {"player_id": "team_b_2", "team": "team_b", "position": (85.0, 30.0), "position_type": "GK"},
            },
            "field": {
                "width": 100.0, "height": 60.0,
                "team_a_goal_x": 0.0, "team_b_goal_x": 100.0,
                "goal_top": 35.0, "goal_bottom": 25.0
            }
        }

        self.mock_gsm.seed = 42
        self.mock_gsm.state = Mock()
        self.mock_gsm.state._pass_landing_zone = None

        # Default BPS return shape — tests override per scenario
        self.mock_bps.advance_ball.return_value = {
            "new_position": (52.0, 30.0),
            "new_velocity": (2.0, 0.0),
            "out_of_bounds": False,
            "controlled_by": None,
        }

    # AC-BPS-01: Ball motion delegation to BPS
    def test_calls_bps_advance_ball_with_correct_parameters(self):
        """AC-BPS-01: Phase 7 calls BPS advance_ball with game_state, seed, tick, field dimensions."""
        # Configure mock BPS to return proper dict structure
        self.mock_bps.advance_ball.return_value = {
            "new_position": (52.0, 30.0),
            "new_velocity": (2.0, 0.0),
            "out_of_bounds": False,
            "controlled_by": None
        }

        self.engine._resolve_phase7(self.snap, 10)

        self.mock_bps.advance_ball.assert_called_once()
        args = self.mock_bps.advance_ball.call_args[0]
        assert args[1] == 42  # seed
        assert args[2] == 10  # tick
        assert args[3] == 100.0  # field_width
        assert args[4] == 60.0  # field_height

    # AC-BPS-02: BPS motion results committed to GSM
    def test_commits_bps_motion_results_to_gsm(self):
        """AC-BPS-02: Phase 7 commits BPS new_position and new_velocity to GSM."""
        # Configure mock BPS to return proper dict structure
        self.mock_bps.advance_ball.return_value = {
            "new_position": (52.0, 30.0),
            "new_velocity": (1.8, 0.0),
            "out_of_bounds": False,
            "controlled_by": None
        }

        self.engine._resolve_phase7(self.snap, 10)

        self.mock_gsm.update_ball_position.assert_called_once_with((52.0, 30.0))
        self.mock_gsm.update_ball_velocity.assert_called_once_with((1.8, 0.0))

    # AC-BPS-03: Out of bounds handling
    def test_out_of_bounds_clears_landing_zone_no_contest(self):
        """AC-BPS-03: When BPS returns out_of_bounds=True OUTSIDE the goal mouth,
        clear landing zone, skip contest, and emit a system OOB record.

        Per ADR-0016: a ball reaching the end line within goal extents is now
        classified as a goal (not OOB). This test exercises the side-line OOB
        path — y=10 is outside goal_top=35 / goal_bottom=25.

        Per 2026-04-22 (post-ADR-0018 follow-up): OOB now produces a
        `system` record so the Event Log can show OOB rows. Was silent
        previously.
        """
        # Configure mock BPS to return proper dict structure
        self.mock_bps.advance_ball.return_value = {
            "new_position": (0.0, 10.0),  # Side OOB at y=10 (outside goal mouth)
            "new_velocity": (0.0, 0.0),  # Stopped
            "out_of_bounds": True,
            "controlled_by": None
        }

        bp_records, goal_records = self.engine._resolve_phase7(self.snap, 10)

        self.mock_gsm.set_pass_landing_zone.assert_called_once_with(None)
        # System OOB record is emitted for Event Log surfacing.
        assert "system" in bp_records
        assert bp_records["system"]["out_of_bounds"] is True
        assert bp_records["system"]["position"] == (0.0, 10.0)
        assert goal_records == {}  # No goal records

    # NOTE: tests for Rule 16 with _ball_just_passed=True were removed
    # 2026-04-22. Phase 7 has an early-return on _ball_just_passed (per
    # ADR-0009 phase ordering — when a Pass happened this tick, ball state
    # is in flux and pickup contests defer to next tick). That return
    # makes the offside check unreachable in production: by the time
    # Phase 7 is allowed to run again (next tick), _ball_just_passed has
    # been reset and `_is_offside_violation` returns False unconditionally.
    # The previously-failing tests exercised this unreachable code path.
    # ADR-0015 amendment supersedes Rule 16 anyway: the passer is on
    # cooldown, so they can't pickup their own pass regardless of role.

    # AC-R16-02: No violation when ball not just passed (still meaningful)
    def test_rule16_no_violation_when_ball_not_just_passed(self):
        """AC-R16-02: No Rule 16 violation when _ball_just_passed=False."""
        self.engine._ball_just_passed = False  # No recent pass

        # Configure mock BPS to return proper dict structure
        self.mock_bps.advance_ball.return_value = {
            "new_position": (85.0, 30.0),
            "new_velocity": (0.0, 0.0),
            "out_of_bounds": False,
            "controlled_by": "team_a_0"  # FWD picks up ball
        }

        bp_records, _ = self.engine._resolve_phase7(self.snap, 10)

        # Should allow pickup since no recent pass
        self.mock_gsm.transfer_possession.assert_called_with(None, "team_a_0")
        assert bp_records["team_a_0"]["ball_pickup"] == "success"
        assert bp_records["team_a_0"]["reason"] == "ok"

    # AC-CD-01: Cooldown-active player pre-excluded from pickup contest
    def test_cooldown_active_player_excluded_from_pickup(self):
        """Per ADR-0015 amendment (2026-04-22): a player on action cooldown
        is added to excluded_pids before BPS runs, so they cannot win the
        pickup contest. Replaces the old _passer_exclusion behavior."""
        # Mock GSM so the configured cooldown is 10 ticks and team_a_0 last
        # acted at tick=5 (so at tick=10 they have 5 ticks remaining).
        self.mock_gsm.config = Mock()
        self.mock_gsm.config.simulation = Mock()
        self.mock_gsm.config.simulation.action_cooldown_ticks = 10

        def fake_last_tick(pid):
            return 5 if pid == "team_a_0" else -10**9
        self.mock_gsm.get_last_action_tick.side_effect = fake_last_tick

        self.mock_bps.advance_ball.return_value = {
            "new_position": (45.0, 30.0),
            "new_velocity": (0.0, 0.0),
            "out_of_bounds": False,
            "controlled_by": None,  # BPS honors exclusion → no winner
        }

        self.engine._resolve_phase7(self.snap, 10)

        excluded = self.mock_bps.advance_ball.call_args.kwargs.get("excluded_pids")
        assert excluded is not None and "team_a_0" in excluded
        # And other (non-cooldown) players should NOT be excluded.
        assert "team_b_0" not in excluded

    # AC-CD-02: Pickup off cooldown succeeds + records new cooldown
    def test_successful_pickup_records_cooldown(self):
        """Per ADR-0015 amendment (2026-04-22): on successful pickup, the
        picker's cooldown timer is started so they must "settle" before
        immediately Pass/Shoot/Tackle next tick."""
        self.mock_bps.advance_ball.return_value = {
            "new_position": (55.0, 30.0),
            "new_velocity": (0.0, 0.0),
            "out_of_bounds": False,
            "controlled_by": "team_b_0",
        }

        self.engine._resolve_phase7(self.snap, 10)

        self.mock_gsm.transfer_possession.assert_called_with(None, "team_b_0")
        # New per-amendment behavior: pickup triggers the cooldown.
        self.mock_gsm.record_action_cooldown.assert_called_with("team_b_0", 10)

    # AC-CD-03: Successful pickup clears _last_ball_action_pid (goal attribution)
    def test_successful_pickup_clears_last_ball_action_pid(self):
        """Per ADR-0016 + ADR-0015 amendment: _last_ball_action_pid is the
        goal-attribution pointer; it's cleared once a player collects the
        ball (the previous passer/shooter no longer owns attribution)."""
        self.engine._last_ball_action_pid = "team_a_0"

        self.mock_bps.advance_ball.return_value = {
            "new_position": (55.0, 30.0),
            "new_velocity": (0.0, 0.0),
            "out_of_bounds": False,
            "controlled_by": "team_b_0",
        }

        self.engine._resolve_phase7(self.snap, 10)

        assert self.engine._last_ball_action_pid is None

    # AC-GK-01: Goal line crossing detection
    def test_goal_line_crossing_detection(self):
        """AC-GK-01: Detects when ball crosses goal line in goal area."""
        self.mock_bps.advance_ball.return_value = {
            "new_position": (101.0, 30.0),  # Past Team B goal line
            "new_velocity": (2.0, 0.0),
            "out_of_bounds": False,
            "controlled_by": None
        }

        # Mock goalkeeper save attempt
        self.mock_gsm.build_player_state.return_value = {"skill": 10}

        with patch.object(self.engine, '_attempt_goalkeeper_save') as mock_save:
            mock_save.return_value = (False, "skill_insufficient")

            bp_records, goal_records = self.engine._resolve_phase7(self.snap, 10)

            mock_save.assert_called_once()
            assert "team_b_2" in goal_records  # GK attempted save
            assert goal_records["team_b_2"]["goalkeeper_save"] == "failed"
            assert goal_records["team_b_2"]["goal_scored"] == "team_a"

    # AC-GK-02: Successful goalkeeper save
    def test_successful_goalkeeper_save(self):
        """AC-GK-02: Successful goalkeeper save stops ball and transfers possession."""
        self.mock_bps.advance_ball.return_value = {
            "new_position": (101.0, 30.0),
            "new_velocity": (2.0, 0.0),
            "out_of_bounds": False,
            "controlled_by": None
        }

        self.mock_gsm.build_player_state.return_value = {"skill": 20}

        with patch.object(self.engine, '_attempt_goalkeeper_save') as mock_save:
            # ADR-0018 (2026-04-22): _attempt_goalkeeper_save now returns
            # (outcome_str, reason). "caught" is the clean-catch path.
            mock_save.return_value = ("caught", "skill_sufficient")

            bp_records, goal_records = self.engine._resolve_phase7(self.snap, 10)

            # Should stop ball and give to GK
            self.mock_gsm.update_ball_velocity.assert_called_with((0.0, 0.0))
            self.mock_gsm.transfer_possession.assert_called_with(None, "team_b_2")
            assert goal_records["team_b_2"]["goalkeeper_save"] == "success"

    # AC-GK-03: Failed goalkeeper save allows goal
    def test_failed_goalkeeper_save_allows_goal(self):
        """AC-GK-03: Failed goalkeeper save results in goal scored."""
        self.mock_bps.advance_ball.return_value = {
            "new_position": (101.0, 30.0),
            "new_velocity": (2.0, 0.0),
            "out_of_bounds": False,
            "controlled_by": None
        }

        self.mock_gsm.build_player_state.return_value = {"skill": 5}

        with patch.object(self.engine, '_attempt_goalkeeper_save') as mock_save:
            # ADR-0018: "missed" is the goal-conceded path (was: False bool).
            mock_save.return_value = ("missed", "skill_insufficient")

            bp_records, goal_records = self.engine._resolve_phase7(self.snap, 10)

            # Should stop ball and record goal
            self.mock_gsm.update_ball_velocity.assert_called_with((0.0, 0.0))
            self.mock_gsm.set_pass_landing_zone.assert_called_with(None)
            assert goal_records["team_b_2"]["goalkeeper_save"] == "failed"
            assert goal_records["team_b_2"]["goal_scored"] == "team_a"

    # AC-GK-04: No goalkeeper automatic goal
    def test_no_goalkeeper_automatic_goal(self):
        """AC-GK-04: Goal automatically scored when no goalkeeper present."""
        # Remove goalkeeper from snap
        snap = self.snap.copy()
        snap["players"] = {k: v for k, v in snap["players"].items() if v["position_type"] != "GK"}

        self.mock_bps.advance_ball.return_value = {
            "new_position": (101.0, 30.0),
            "new_velocity": (2.0, 0.0),
            "out_of_bounds": False,
            "controlled_by": None
        }

        bp_records, goal_records = self.engine._resolve_phase7(snap, 10)

        # Should stop ball and record automatic goal
        self.mock_gsm.update_ball_velocity.assert_called_with((0.0, 0.0))
        self.mock_gsm.set_pass_landing_zone.assert_called_with(None)
        assert goal_records["system"]["goal_scored"] == "team_a"
        assert goal_records["system"]["reason"] == "no_goalkeeper"

    # AC-GK-05: Ball outside goal area no goal detection
    def test_ball_outside_goal_area_no_goal_detection(self):
        """AC-GK-05: Ball crossing goal line outside goal area doesn't trigger goal."""
        self.mock_bps.advance_ball.return_value = {
            "new_position": (101.0, 40.0),  # Outside goal area (y=40 > goal_top=35)
            "new_velocity": (2.0, 0.0),
            "out_of_bounds": False,
            "controlled_by": None
        }

        bp_records, goal_records = self.engine._resolve_phase7(self.snap, 10)

        assert goal_records == {}  # No goal attempt

    def test_save_probability_formula(self):
        """Save prob now uses the keeper's `save` attr (blended) weighted by
        GK_SAVE_WEIGHT. With only `skill` present, `save` falls back to skill.
        Outcome split (gk_caught_share=0.60) is unchanged:
          draw < save_prob * 0.60 → "caught"
          draw < save_prob        → "blocked"
          else                    → "missed"
        """
        from src.foundation.action_resolution_engine.engine import GK_SAVE_WEIGHT

        self.mock_gsm.build_player_state.return_value = {"skill": 15}

        outcome, reason = self.engine._attempt_goalkeeper_save(
            "team_b_2", (90.0, 30.0), (3.0, 0.0), self.snap, 10
        )

        # gk_save falls back to skill=15 → eff_save = (2*15 + 15)/3 = 15
        eff_save = (2.0 * 15 + 15) / 3.0
        save_prob = (GK_SAVE_WEIGHT * eff_save) / (GK_SAVE_WEIGHT * eff_save + 3.0 + 5.0)
        caught_threshold = save_prob * 0.60  # default gk_caught_share
        draw = hash_01(42, 10, "team_b_2", "goalkeeper_save")
        if draw < caught_threshold:
            assert outcome == "caught"
            assert reason == "skill_sufficient"
        elif draw < save_prob:
            assert outcome == "blocked"
            assert reason == "parried"
        else:
            assert outcome == "missed"
            assert reason == "skill_insufficient"

    def test_save_uses_save_attribute_and_weight(self):
        """A keeper's dedicated `save` rating drives the save prob (blended
        with skill, weighted by GK_SAVE_WEIGHT), not generic `skill` alone."""
        from src.foundation.action_resolution_engine.engine import GK_SAVE_WEIGHT

        self.mock_gsm.build_player_state.return_value = {"skill": 10, "save": 18}

        outcome, reason = self.engine._attempt_goalkeeper_save(
            "team_b_2", (90.0, 30.0), (3.0, 0.0), self.snap, 10
        )

        eff_save = (2.0 * 18 + 10) / 3.0  # uses save=18, not skill=10
        save_prob = (GK_SAVE_WEIGHT * eff_save) / (GK_SAVE_WEIGHT * eff_save + 3.0 + 5.0)
        caught_threshold = save_prob * 0.60
        draw = hash_01(42, 10, "team_b_2", "goalkeeper_save")
        if draw < caught_threshold:
            assert outcome == "caught"
        elif draw < save_prob:
            assert outcome == "blocked"
        else:
            assert outcome == "missed"

    def test_save_falls_back_to_skill_when_no_save_attr(self):
        """When player_state has no `save` key, the formula falls back to
        generic skill so old fixtures keep working."""
        from src.foundation.action_resolution_engine.engine import GK_SAVE_WEIGHT

        self.mock_gsm.build_player_state.return_value = {"skill": 12}  # no `save`

        outcome, reason = self.engine._attempt_goalkeeper_save(
            "team_b_2", (90.0, 30.0), (3.0, 0.0), self.snap, 10
        )

        eff_save = (2.0 * 12 + 12) / 3.0  # = 12 (save falls back to skill)
        save_prob = (GK_SAVE_WEIGHT * eff_save) / (GK_SAVE_WEIGHT * eff_save + 3.0 + 5.0)
        caught_threshold = save_prob * 0.60
        draw = hash_01(42, 10, "team_b_2", "goalkeeper_save")
        if draw < caught_threshold:
            assert outcome == "caught"
        elif draw < save_prob:
            assert outcome == "blocked"
        else:
            assert outcome == "missed"


class TestGoalkeeperSaveFormula:
    """Test ARE GDD Rule 14a goalkeeper save formula."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_gsm = Mock()
        self.engine = ActionResolutionEngine(Mock(), Mock(), Mock(), Mock(), Mock())
        self.engine.gsm = self.mock_gsm
        self.mock_gsm.seed = 42

        self.snap = {
            "players": {
                "team_b_2": {"player_id": "team_b_2", "team": "team_b", "position": (85.0, 30.0), "position_type": "GK"}
            }
        }

    # AC-F3-01: Save probability formula (post-ADR-0018: 3-state, post-2026-06-08: GK_SAVE_WEIGHT)
    def test_save_probability_formula(self):
        """AC-F3-01 (ADR-0018, 2026-04-22 + spec gk-save-rate-tuning, 2026-06-08):
        F3 now uses eff_save (blended save+skill) weighted by GK_SAVE_WEIGHT.
        Returns (outcome_str, reason). With default gk_caught_share=0.60:
          draw < save_prob * 0.60          → "caught"
          draw < save_prob                 → "blocked" (parry)
          else                             → "missed" (goal)
        """
        from src.foundation.action_resolution_engine.engine import GK_SAVE_WEIGHT

        self.mock_gsm.build_player_state.return_value = {"skill": 15}

        outcome, reason = self.engine._attempt_goalkeeper_save(
            "team_b_2", (90.0, 30.0), (3.0, 0.0), self.snap, 10
        )

        # gk_save falls back to skill=15 → eff_save = (2*15 + 15)/3 = 15
        eff_save = (2.0 * 15 + 15) / 3.0
        save_prob = (GK_SAVE_WEIGHT * eff_save) / (GK_SAVE_WEIGHT * eff_save + 3.0 + 5.0)
        caught_threshold = save_prob * 0.60  # default gk_caught_share
        draw = hash_01(42, 10, "team_b_2", "goalkeeper_save")
        if draw < caught_threshold:
            assert outcome == "caught"
            assert reason == "skill_sufficient"
        elif draw < save_prob:
            assert outcome == "blocked"
            assert reason == "parried"
        else:
            assert outcome == "missed"
            assert reason == "skill_insufficient"

    # AC-F3-02: Deterministic hash_01 usage
    def test_deterministic_hash01_usage(self):
        """AC-F3-02: Same inputs produce same save result due to hash_01."""
        self.mock_gsm.build_player_state.return_value = {"skill": 10}

        result1 = self.engine._attempt_goalkeeper_save(
            "team_b_2", (90.0, 30.0), (2.0, 0.0), self.snap, 5
        )
        result2 = self.engine._attempt_goalkeeper_save(
            "team_b_2", (90.0, 30.0), (2.0, 0.0), self.snap, 5
        )

        assert result1 == result2  # Deterministic


class TestPhase7RecordStructure:
    """Test Phase 7 record structure and merging."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_gsm = Mock()
        self.engine = ActionResolutionEngine(Mock(), Mock(), Mock(), Mock(), Mock())
        self.engine.gsm = self.mock_gsm
        self.mock_gsm.seed = 42

    # AC-REC-01: Ball pickup success record
    def test_ball_pickup_success_record_structure(self):
        """AC-REC-01: Successful ball pickup creates correct record structure."""
        # Setup mock BPS for this test
        mock_bps = Mock()
        self.engine.bps = mock_bps

        snap = {
            "ball": {"position": (50.0, 30.0), "velocity": (0.0, 0.0), "carrier_id": None},
            "players": {"team_a_0": {"player_id": "team_a_0", "team": "team_a", "position": (50.0, 30.0)}},
            "field": {
                "width": 100.0, "height": 60.0,
                "team_a_goal_x": 0.0, "team_b_goal_x": 100.0,
                "goal_top": 35.0, "goal_bottom": 25.0
            }
        }

        mock_bps.advance_ball.return_value = {
            "new_position": (50.0, 30.0),
            "new_velocity": (0.0, 0.0),
            "out_of_bounds": False,
            "controlled_by": "team_a_0"
        }

        bp_records, goal_records = self.engine._resolve_phase7(snap, 10)

        expected = {
            "team_a_0": {
                "ball_pickup": "success",
                "reason": "ok"
            }
        }
        assert bp_records == expected
        assert goal_records == {}

    # AC-REC-02: No-pickup tick produces no record
    def test_no_pickup_when_bps_returns_no_winner(self):
        """Post-2026-04-22: ball_pickup "failed" records no longer exist —
        cooldown / offside filtering happens via BPS pre-exclusion, so when
        the contest has no eligible winner BPS simply returns
        controlled_by=None and Phase 7 emits no ball_physics record."""
        mock_bps = Mock()
        self.engine.bps = mock_bps

        snap = {
            "ball": {"position": (50.0, 30.0), "velocity": (0.0, 0.0), "carrier_id": None},
            "players": {"team_a_0": {"player_id": "team_a_0", "team": "team_a", "position": (50.0, 30.0)}},
            "field": {
                "width": 100.0, "height": 60.0,
                "team_a_goal_x": 0.0, "team_b_goal_x": 100.0,
                "goal_top": 35.0, "goal_bottom": 25.0,
            },
        }

        mock_bps.advance_ball.return_value = {
            "new_position": (50.0, 30.0),
            "new_velocity": (0.0, 0.0),
            "out_of_bounds": False,
            "controlled_by": None,
        }

        bp_records, goal_records = self.engine._resolve_phase7(snap, 10)
        assert bp_records == {}
        assert goal_records == {}

    # AC-REC-03: Goalkeeper save success record
    def test_goalkeeper_save_success_record_structure(self):
        """AC-REC-03: Successful goalkeeper save creates correct record structure."""
        # Setup mock BPS for this test
        mock_bps = Mock()
        self.engine.bps = mock_bps

        snap = {
            "ball": {"position": (50.0, 30.0), "velocity": (0.0, 0.0), "carrier_id": None},
            "players": {
                "team_b_2": {"player_id": "team_b_2", "team": "team_b", "position": (85.0, 30.0), "position_type": "GK"}
            },
            "field": {
                "width": 100.0, "height": 60.0,
                "team_a_goal_x": 0.0, "team_b_goal_x": 100.0,
                "goal_top": 35.0, "goal_bottom": 25.0
            }
        }

        self.mock_gsm.build_player_state.return_value = {"skill": 20}

        mock_bps.advance_ball.return_value = {
            "new_position": (101.0, 30.0),  # Goal line crossed
            "new_velocity": (2.0, 0.0),
            "out_of_bounds": False,
            "controlled_by": None
        }

        with patch.object(self.engine, '_attempt_goalkeeper_save') as mock_save:
            # ADR-0018: 3-state outcome. "caught" is the clean-catch path
            # (returned as ("caught", reason) instead of (True, reason)).
            mock_save.return_value = ("caught", "skill_sufficient")

            bp_records, goal_records = self.engine._resolve_phase7(snap, 10)

            # Per ADR-0016: successful saves include `saved_from` for
            # attribution (None when no shooter pid was tracked).
            expected = {
                "team_b_2": {
                    "goalkeeper_save": "success",
                    "reason": "skill_sufficient",
                    "saved_from": None,
                }
            }
            assert goal_records == expected