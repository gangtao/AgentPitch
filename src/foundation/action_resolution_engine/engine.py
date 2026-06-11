"""Action Resolution Engine — 7-phase tick orchestrator.

Implements the Feature-layer integration hub that coordinates GameStateManager,
Player Movement System, Ball Physics System, Sandbox, and FallbackHandler to
resolve one simulation tick through 7 phases per ADR-0009.

This story implements only the class scaffold + Phase 1 (snapshot collection).
Stories 002-008 will add the remaining phases.
"""

from __future__ import annotations
import logging
from typing import Any

from src.foundation.sandbox import ExecutionStatus
from src.foundation.simulation_utils import hash_01
import src.core.ball_physics_system as bps

logger = logging.getLogger(__name__)

# GK save tuning (2026-06-08, spec gk-save-rate-tuning). Weights the keeper's
# effective save skill in the save-probability formula so realistic keepers stop
# the majority of on-target shots. 1.0 ≈ legacy behavior; raise to suppress goals.
# Calibrated against ~1-3 goals per 5-minute match. Code constant by design — no
# SimulationConfig/UI knob (see spec).
GK_SAVE_WEIGHT = 2.0


def _is_finite_number(value: Any) -> bool:
    """True only for a real, finite int/float.

    Action fields originate in untrusted, LLM-generated sandbox code and may be
    any type (e.g. a (dx, dy) tuple mistakenly passed as a scalar angle). Guard
    numeric validation with this before math.isfinite(), which raises TypeError
    on non-real inputs. bool is excluded — it is not a meaningful coordinate.
    """
    import math
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


class ActionResolutionEngine:
    """GDD Rule 1 — stateless 7-phase tick orchestrator.

    The Action Resolution Engine (ARE) is the central coordinator that orchestrates
    all gameplay systems to resolve one simulation tick. It follows a stateless
    design where no tick-level data persists between resolve_tick() calls.

    The ARE implements ADR-0009's 7-phase resolution order:
    1. Snapshot collection (this story)
    2. Player action generation (story 002)
    3. Action validation (story 003)
    4. Player movement (story 004)
    5. Ball physics (story 005)
    6. Goal detection (story 006)
    7. Phase transitions (story 007)

    Each phase operates on the snapshot from Phase 1, maintaining consistency
    throughout the tick resolution process.
    """

    def __init__(self, gsm: Any, pms: Any, bps: Any, sandbox: Any, fallback_handler: Any) -> None:
        """Initialize Action Resolution Engine with injected dependencies.

        Args:
            gsm: GameStateManager instance for state access and mutations
            pms: Player Movement System for computing movement results
            bps: Ball Physics System for ball motion and control contests
            sandbox: Sandbox for safe LLM code execution
            fallback_handler: FallbackHandler for handling execution failures
        """
        self.gsm = gsm
        self.pms = pms
        self.bps = bps
        self.sandbox = sandbox
        self.fallback_handler = fallback_handler
        # Tracks the most-recent player to Pass or Shoot — used for goal
        # attribution when the ball later crosses the goal line. Per the
        # ADR-0015 amendment (2026-04-22) this no longer blocks pickup;
        # the unified per-player cooldown handles that role.
        self._last_ball_action_pid: str | None = None
        # Tick-local state variables
        self._ball_just_passed = False
        self._last_touching_team: str | None = None
        # Bugfix #22 stalemate breaker — persists across ticks. Counts
        # consecutive ticks the carried ball has stayed within
        # _STUCK_RADIUS of an anchor point; at _STUCK_MAX_TICKS the ball is
        # turned over to the nearest opponent so the match can't freeze.
        self._stuck_anchor_pos: tuple[float, float] | None = None
        self._stuck_ticks = 0
        # Issue #31 (IFAB Law 11): player ids flagged in an OFFSIDE POSITION
        # at the moment of the most recent Pass. Persists across ticks while
        # the pass travels; the offence fires in Phase 7 only if a flagged
        # player is the one who controls the ball. Cleared on any touch,
        # restart, or possession change.
        self._offside_pids_at_pass: set[str] = set()
        # Law 11 exemption: no offside directly from a goal kick, throw-in,
        # or corner. _apply_oob_restart records the kicker here; their next
        # Pass skips the offside snapshot, then the marker clears.
        self._restart_kick_pid: str | None = None

    # Stalemate breaker tuning (bugfix #22). 50 ticks at the default 10
    # ticks/sec rate = 5s of an effectively motionless carried ball. The
    # radius tolerates a pinned ball that wobbles in place without ever
    # making net progress, while a genuinely dribbled ball clears it.
    _STUCK_MAX_TICKS = 50
    _STUCK_RADIUS = 2.0

    def resolve_tick(self, tick: int, history: list[dict]) -> dict[str, dict]:
        """Resolve one simulation tick through 7-phase orchestration.

        This is the only public method of the Action Resolution Engine. It coordinates
        all gameplay systems to advance the simulation state by exactly one tick.

        Phase 1 (this story): Collect the tick snapshot from GameStateManager
        Phases 2-7 (future stories): Player actions, validation, movement, ball physics,
        goal detection, and phase transitions.

        Args:
            tick: Current simulation tick number
            history: List of previous tick snapshots for context

        Returns:
            Dict mapping player_id to ActionRecord dict. Each ActionRecord contains:
                - action: str — the action taken ("Hold", "Move", "Pass", etc.)
                - result: str — execution result ("ok", "failed", "fallback")
                - tick: int — the tick this action was resolved

        Note:
            This implementation returns placeholder records until phases 2-7 are added.
            The tick-local state variables are initialized fresh each call to maintain
            statelessness between ticks.
        """
        # Tick-local state — initialized fresh each call (Rule 1 statelessness)
        self._ball_just_passed = False
        # NOTE: _last_touching_team is intentionally PERSISTENT across ticks
        # (initialised in __init__). The 2026-04-23 OOB-restart code reads it
        # to award throw-ins to the opposing team — resetting it per tick
        # made every restart attribute to the default fallback.
        # Per ADR-0015 (amended 2026-04-22): tracks pids whose Pass/Shoot/
        # Tackle was blocked by the unified cooldown so the action_record
        # can restore the LLM's intent name (otherwise it would show as
        # "Hold" after substitution). Replaces the old _last_ball_action_pid
        # mechanism — cooldown subsumes passer self-collect prevention.
        self._cooldown_blocked: dict[str, str] = {}

        # Phase 1: build snapshot once
        snap = self.gsm.build_tick_snapshot()

        # Phase 2: callback invocation + fallback routing
        actions: dict[str, Any] = {}

        for player in snap["players"].values():
            pid = player["player_id"]
            team = player["team"]

            # Build per-player game_state with my_player_id and my_team injected
            game_state = {**snap, "my_player_id": pid, "my_team": team}
            player_state = self.gsm.build_player_state(pid)
            result = self.sandbox.execute(pid, game_state, player_state, history)

            if result.status != ExecutionStatus.SUCCESS:
                # Route to fallback handler
                provider = self._provider_for_team(team)
                fr = self.fallback_handler.handle(result, pid, team, provider, tick)
                actions[pid] = fr.action
            else:
                # Use sandbox result action
                actions[pid] = result.action

        # Phase 3: Action validation + normalization (Story 003)
        # Pass `tick` per ADR-0015 so cooldown checks can compare against
        # gsm.get_last_action_tick(pid, action_type).
        validated_actions, validation_reasons = self._validate_actions(actions, snap, tick)

        # Phase 4: Movement compute-all-then-commit + dribble contest (Story 004)
        dribble_consumed = self._resolve_phase4(validated_actions, snap, tick)

        # Phase 5: Ball action (Pass + Shoot resolution) (Story 005)
        # Phase 4 may have changed possession via dribble contests. Since GSM doesn't expose
        # get_carrier_id(), we find current carrier by checking who has has_ball=True after Phase 4.
        current_carrier = None
        for pid in snap["players"]:
            player_state = self.gsm.build_player_state(pid)
            if player_state.get("has_ball", False):
                current_carrier = pid
                break

        ball_action_records = self._resolve_phase5(validated_actions, snap, tick, current_carrier)

        # Phase 6: Tackle resolution (Story 006)
        tackle_records = self._resolve_phase6(validated_actions, snap, tick)

        # Phase 7: Ball physics + Rule 16 + Goal attempt (Story 007)
        ball_physics_records, goal_records = self._resolve_phase7(snap, tick)

        # Convert validated actions to action records.
        action_records = {}
        for pid, action in validated_actions.items():
            record = {
                "action": type(action).__name__,
                "result": validation_reasons.get(pid, "ok"),
                "tick": tick
            }
            # Add effective_power for Pass/Shoot actions when capped
            if hasattr(action, 'power') and validation_reasons.get(pid) == "power_capped":
                record["effective_power"] = action.power
            # Per ADR-0015: cooldown-blocked actions were substituted with
            # Hold(). Keep action="Hold" (effective action) and surface the
            # LLM's intent as intended_action so the event log can distinguish
            # "system cooldown" from "blocked by opponent".
            if pid in self._cooldown_blocked:
                record["intended_action"] = self._cooldown_blocked[pid]
            action_records[pid] = record

        # Merge dribble records from Phase 4 (per-carrier outcome of any
        # dribble contest that fired during their move). The carrier's base
        # action stays "Move" — we add `dribble_result` + `dribble_target`
        # alongside, and the tick-engine classifier surfaces the event.
        for pid, drib_record in getattr(self, "_dribble_records", {}).items():
            if pid in action_records:
                action_records[pid].update(drib_record)

        # Merge ball action records from Phase 5
        for pid, ball_record in ball_action_records.items():
            action_records[pid].update(ball_record)

        # Merge tackle records from Phase 6
        for pid, tackle_record in tackle_records.items():
            action_records[pid].update(tackle_record)

        # Merge ball physics records from Phase 7
        for pid, bp_record in ball_physics_records.items():
            if pid not in action_records:
                action_records[pid] = {"action": "Hold", "result": "ok", "tick": tick}
            action_records[pid].update(bp_record)

        # Merge goal records from Phase 7
        for pid, goal_record in goal_records.items():
            if pid not in action_records:
                action_records[pid] = {"action": "Hold", "result": "ok", "tick": tick}
            action_records[pid].update(goal_record)

        # Stamina / health drain + recovery (added 2026-04-23). Runs
        # AFTER all phases so the formulas this tick used the players'
        # pre-tick health.
        self._apply_health_drain(validated_actions, snap, tick)

        # Bugfix #22: break a frozen match (ball pinned under a carrier with
        # no pressure). Runs last, on the ball position settled this tick.
        self._check_stalemate(tick)

        return action_records

    def _validate_actions(self, actions: dict[str, Any], snap: dict, tick: int = 0) -> tuple[dict[str, Any], dict[str, str]]:
        """GDD Rule 5 — per-action-type validation/normalization.

        Per ADR-0015 (amended 2026-04-22): unified per-player cooldown.
        Pass/Shoot/Tackle on cooldown are substituted with Hold() and the
        player_id is added to self._cooldown_blocked so the action_record
        can restore the intended action type. Pass/Shoot/Tackle that survive
        validation record the cooldown via gsm.record_action_cooldown(pid, tick).

        Args:
            actions: Dict mapping player_id to Action objects from Phase 2
            snap: Game state snapshot from Phase 1
            tick: Current tick (for cooldown comparisons). Default 0 for
                backward compatibility with tests that pre-date ADR-0015.

        Returns:
            Tuple of (validated_actions, validation_reasons) where:
            - validated_actions: Dict mapping player_id to validated Action objects
            - validation_reasons: Dict mapping player_id to reason string for logging
        """
        import math
        from src.foundation.action import Move, Pass, Shoot, Tackle, Hold

        validated: dict[str, Any] = {}
        reasons: dict[str, str] = {}
        carrier_id = snap["ball"].get("carrier_id")

        # Build player lookup for strength and team info
        # Since the snapshot players dict doesn't include strength, we need to get it
        # via build_player_state for each player as needed
        players_by_id = {p["player_id"]: p for p in snap["players"].values()}

        # Pids to record on successful Pass/Shoot/Tackle. Collected here,
        # applied at end of validation (intent-based pacing — the cooldown
        # clock starts when the player attempts the action, regardless of
        # whether downstream phases succeed).
        to_record_cooldowns: list[str] = []

        for pid, action in actions.items():
            player_record = players_by_id[pid]

            # Unified cooldown check (per ADR-0015 amended 2026-04-22): any
            # of Pass/Shoot/Tackle is blocked while the player's single
            # action cooldown is active. Substitute Hold() but preserve
            # intent for the action_record.
            if isinstance(action, (Pass, Shoot, Tackle)):
                action_type = type(action).__name__
                if self._is_on_cooldown(pid, tick):
                    validated[pid] = Hold()
                    reasons[pid] = "cooldown_blocked"
                    self._cooldown_blocked[pid] = action_type
                    continue

            if isinstance(action, Move):
                # Reject non-real / non-finite values from sandbox output
                if not (_is_finite_number(action.dx) and _is_finite_number(action.dy) and _is_finite_number(action.speed)):
                    validated[pid] = Hold()
                    reasons[pid] = "non_finite_move"
                    continue
                # Clamp speed to [0.0, 1.0]
                speed = max(0.0, min(1.0, action.speed))
                # If speed becomes 0.0 OR direction is zero, substitute Hold
                if speed == 0.0 or (action.dx == 0.0 and action.dy == 0.0):
                    validated[pid] = Hold()
                    reasons[pid] = "zero_move_substituted"
                else:
                    # Replace with clamped Move (frozen dataclass — construct new)
                    validated[pid] = Move(dx=action.dx, dy=action.dy, speed=speed)

            elif isinstance(action, Pass):
                if pid != carrier_id:
                    validated[pid] = Hold()
                    reasons[pid] = "not_carrier"
                elif not (
                    isinstance(action.target_pos, (tuple, list))
                    and len(action.target_pos) == 2
                    and _is_finite_number(action.target_pos[0])
                    and _is_finite_number(action.target_pos[1])
                ):
                    validated[pid] = Hold()
                    reasons[pid] = "invalid_target_pos"
                else:
                    # Get player strength from player_state
                    player_state = self.gsm.build_player_state(pid)
                    player_strength = player_state["strength"]

                    # Floor power to 1, then cap by strength
                    floored_power = max(1, action.power)
                    effective_power = min(floored_power, player_strength)

                    validated[pid] = Pass(target_pos=action.target_pos, power=effective_power)

                    # Track reason if power was capped
                    if effective_power < action.power:
                        reasons[pid] = "power_capped"

            elif isinstance(action, Shoot):
                if pid != carrier_id:
                    validated[pid] = Hold()
                    reasons[pid] = "not_carrier"
                elif not _is_finite_number(action.angle):
                    validated[pid] = Hold()
                    reasons[pid] = "invalid_angle"
                else:
                    # Get player strength from player_state
                    player_state = self.gsm.build_player_state(pid)
                    player_strength = player_state["strength"]

                    # Floor power to 1, then cap by strength
                    floored_power = max(1, action.power)
                    effective_power = min(floored_power, player_strength)

                    validated[pid] = Shoot(angle=action.angle, power=effective_power)

                    # Track reason if power was capped
                    if effective_power < action.power:
                        reasons[pid] = "power_capped"

            elif isinstance(action, Tackle):
                target_player = players_by_id.get(action.target_player_id)
                if target_player is None:
                    # Unknown target
                    validated[pid] = Hold()
                    reasons[pid] = "unknown_target"
                elif target_player["team"] == player_record["team"]:
                    # Same team tackle
                    validated[pid] = Hold()
                    reasons[pid] = "same_team_tackle"
                else:
                    # Valid opposing team target - pass through (range check in Phase 6)
                    validated[pid] = action

            else:  # Hold or other actions
                validated[pid] = action

            # Per ADR-0015 amended: queue cooldown recording for any
            # Pass/Shoot/Tackle that survived validation (not Hold()).
            v = validated.get(pid)
            if isinstance(v, (Pass, Shoot, Tackle)):
                to_record_cooldowns.append(pid)

        # Apply cooldown recordings after the loop so we don't conflict with
        # iteration. Even Pass/Shoot/Tackle that fails downstream (e.g.
        # Phase 6 out_of_range) still counts toward cooldown — the player
        # attempted the action and that's what the cooldown tracks.
        for pid in to_record_cooldowns:
            self.gsm.record_action_cooldown(pid, tick)

        return validated, reasons

    def _is_on_cooldown(self, player_id: str, current_tick: int) -> bool:
        """Per ADR-0015 amended (2026-04-22): True if the player took any
        non-trivial action within `action_cooldown_ticks`. Reads the unified
        cooldown value from gsm.config.simulation."""
        cooldown = self._action_cooldown()
        if cooldown <= 0:
            return False  # cooldown disabled
        last_tick = self.gsm.get_last_action_tick(player_id)
        if not isinstance(last_tick, int):
            return False  # mocked GSM in tests; treat as never-performed
        return current_tick - last_tick < cooldown

    def _min_player_separation(self) -> float:
        """Per ADR-0017: read configured min separation. Defensive: returns 0
        (= disabled) if config or simulation block is missing (mock-based tests)."""
        sim = getattr(getattr(self.gsm, "config", None), "simulation", None)
        if sim is None:
            return 0.0
        v = getattr(sim, "min_player_separation", 0.0)
        return v if isinstance(v, (int, float)) else 0.0

    def _enforce_player_separation(
        self,
        positions: dict,
        min_sep: float,
        field_w: float,
        field_h: float,
    ) -> dict:
        """Per ADR-0017: single-pass pairwise separation. Players within
        min_sep of each other are pushed apart equally along the
        center-to-center vector. Field-boundary clamp applied per push.

        Deterministic: iterates pairs in sorted player_id order. For 10
        players in a sparse 100x60 field, single pass converges; rare
        cascade edges self-correct on the next tick.
        """
        out = {pid: pos for pid, pos in positions.items()}
        pids = sorted(out.keys())

        for i in range(len(pids)):
            pid_i = pids[i]
            for j in range(i + 1, len(pids)):
                pid_j = pids[j]
                xi, yi = out[pid_i]
                xj, yj = out[pid_j]
                dx = xj - xi
                dy = yj - yi
                d = (dx * dx + dy * dy) ** 0.5
                if d >= min_sep:
                    continue
                # Compute push direction; handle exact-overlap edge case
                if d < 1e-6:
                    ux, uy = 1.0, 0.0
                    d = 1e-6
                else:
                    ux = dx / d
                    uy = dy / d
                overlap = min_sep - d
                push = overlap / 2.0
                # Push apart, clamp to field
                out[pid_i] = (
                    max(0.0, min(field_w, xi - ux * push)),
                    max(0.0, min(field_h, yi - uy * push)),
                )
                out[pid_j] = (
                    max(0.0, min(field_w, xj + ux * push)),
                    max(0.0, min(field_h, yj + uy * push)),
                )
        return out

    def _action_cooldown(self) -> int:
        """Resolve the configured unified action cooldown (ticks).

        Defensive: if gsm.config is unavailable or returns non-int (mock-based
        unit tests where gsm is a MagicMock), return 0 so cooldowns are inert.
        Real GSM (post-ADR-0015 amendment init) always has the int value.
        """
        sim = getattr(getattr(self.gsm, "config", None), "simulation", None)
        if sim is None:
            return 0
        value = getattr(sim, "action_cooldown_ticks", 0)
        # Mock-friendly: only honor real ints. MagicMock attributes return
        # other MagicMocks which would crash arithmetic comparisons.
        return value if isinstance(value, int) else 0

    # --- ADR-0018 realism knob accessors (defensive vs mock GSM) ----------
    def _sim_float(self, name: str, default: float) -> float:
        sim = getattr(getattr(self.gsm, "config", None), "simulation", None)
        if sim is None:
            return default
        v = getattr(sim, name, default)
        return v if isinstance(v, (int, float)) and not isinstance(v, bool) else default

    def _pass_max_deviation(self) -> float:
        return self._sim_float("pass_max_deviation", 8.0)

    def _shot_max_angle(self) -> float:
        return self._sim_float("shot_max_angle", 0.30)

    def _tackle_clean_share(self) -> float:
        return self._sim_float("tackle_clean_share", 0.55)

    def _tackle_blocked_floor(self) -> float:
        return self._sim_float("tackle_blocked_floor", 0.15)

    def _tackle_block_speed_min(self) -> float:
        return self._sim_float("tackle_block_speed_min", 1.0)

    def _tackle_block_speed_max(self) -> float:
        return self._sim_float("tackle_block_speed_max", 3.0)

    def _gk_caught_share(self) -> float:
        return self._sim_float("gk_caught_share", 0.60)

    def _gk_block_speed_factor(self) -> float:
        return self._sim_float("gk_block_speed_factor", 0.4)

    def _tackle_range(self) -> float:
        return self._sim_float("tackle_range", 2.0)

    def _tackle_settle_grace(self) -> int:
        sim = getattr(getattr(self.gsm, "config", None), "simulation", None)
        if sim is None:
            return 3
        v = getattr(sim, "tackle_settle_grace_ticks", 3)
        return v if isinstance(v, int) and not isinstance(v, bool) else 3

    def _offside_enabled(self) -> bool:
        """Issue #31: IFAB Law 11 toggle. Defensive vs mock GSM — only an
        explicit True enables the rule (MagicMock attrs are truthy but not
        `is True`), so legacy mock-based tests stay on the old behavior."""
        sim = getattr(getattr(self.gsm, "config", None), "simulation", None)
        if sim is None:
            return False
        return getattr(sim, "offside_enabled", False) is True

    def _capture_offside_at_pass(self, passer: dict, snap: dict) -> None:
        """Issue #31 — snapshot team-mates in an OFFSIDE POSITION at the
        moment the ball is played (IFAB Law 11, x-axis judgement).

        A team-mate is flagged iff, measured as distance to the opponents'
        goal line (abs(x - opp_goal_x), half-time-swap safe):
          - strictly inside the opponents' half (on the halfway line = own
            half = onside), and
          - strictly nearer the goal line than the ball (= the passer), and
          - strictly nearer than the SECOND-LAST opponent, any role
            (level = onside).
        Being in an offside position is NOT an offence — Phase 7 penalises
        only the flagged player who actually controls this pass.
        """
        self._offside_pids_at_pass.clear()
        if not self._offside_enabled():
            return
        field = snap.get("field", {})
        width = field.get("width")
        goal_key = "team_b_goal_x" if passer["team"] == "team_a" else "team_a_goal_x"
        opp_goal_x = field.get(goal_key)
        if not isinstance(width, (int, float)) or not isinstance(opp_goal_x, (int, float)):
            return  # sparse test fixture — cannot judge geometry
        team = passer["team"]
        ball_dist = abs(passer["position"][0] - opp_goal_x)
        opp_dists = sorted(
            abs(p["position"][0] - opp_goal_x)
            for p in snap["players"].values() if p["team"] != team
        )
        # Degenerate rosters (<2 opponents) can't define a second-last
        # opponent; treat the line as infinitely deep (only ball + half
        # clauses apply). Real rosters are always 5-11 a side.
        second_last = opp_dists[1] if len(opp_dists) >= 2 else float("inf")
        half_width = width / 2.0
        for p in snap["players"].values():
            if p["team"] != team or p["player_id"] == passer["player_id"]:
                continue
            d = abs(p["position"][0] - opp_goal_x)
            if d < half_width and d < ball_dist and d < second_last:
                self._offside_pids_at_pass.add(p["player_id"])

    # ── Stamina / health (added 2026-04-23) ────────────────────────
    def _health_max(self) -> float:
        return self._sim_float("health_max", 100.0)

    def _health_drain_factor(self) -> float:
        return self._sim_float("health_drain_factor", 1.0)

    def _health_floor(self) -> float:
        return self._sim_float("health_floor", 0.6)

    def _health_factor(self, player_state_or_snap: dict) -> float:
        """Skill multiplier from current_health.

        floor + (1-floor) × current_health/max. Returns 1.0 if either
        field is missing — keeps mock-based unit tests behaving as before.
        """
        ch = player_state_or_snap.get("current_health")
        if ch is None:
            return 1.0
        floor = self._health_floor()
        max_h = max(1e-6, self._health_max())
        return floor + (1.0 - floor) * (ch / max_h)

    # Per-action base health cost. Positive = drain, applied as
    # `-base × (1 - stamina/20) × drain_factor`. Recovery values
    # (Hold, low-Move) are flat positive amounts.
    _BASE_DRAIN = {"Move": 0.3, "Pass": 2.0, "Shoot": 4.0, "Tackle": 4.0}
    _RECOVER_HOLD = 1.5
    _RECOVER_MOVE_LOW = 0.5
    _MOVE_LOW_SPEED = 0.5  # Move actions with speed ≤ this are jogging

    def _apply_health_drain(self, validated_actions, snap, tick):
        """Walk every actor and adjust current_health based on what they
        chose this tick. Called once at the end of resolve_tick.

        Cooldown-blocked players get the substituted Hold's recovery
        (they didn't actually pass/shoot), which is intentional —
        cooldown already throttles them; piling on health drain would
        over-punish.
        """
        if not hasattr(self.gsm, "adjust_health"):
            return  # mock GSM in tests
        drain_factor = self._health_drain_factor()
        for pid, action in validated_actions.items():
            pstate = snap.get("players", {}).get(pid, {})
            stamina = pstate.get("stamina", 10)
            drain_mod = max(0.0, 1.0 - stamina / 20.0)
            name = type(action).__name__
            if name == "Hold":
                delta = self._RECOVER_HOLD
            elif name == "Move":
                speed = float(getattr(action, "speed", 1.0))
                if speed <= self._MOVE_LOW_SPEED:
                    delta = self._RECOVER_MOVE_LOW
                else:
                    delta = -self._BASE_DRAIN["Move"] * drain_mod * drain_factor
            elif name in ("Pass", "Shoot", "Tackle"):
                delta = -self._BASE_DRAIN[name] * drain_mod * drain_factor
            else:
                delta = 0.0
            if delta != 0.0:
                try:
                    self.gsm.adjust_health(pid, delta)
                except Exception:
                    pass  # defensive: mock GSM with non-functional adjust_health

    def _resolve_phase4(self, validated_actions: dict[str, Any], snap: dict, tick: int) -> set[str]:
        """Phase 4: Movement compute-all-then-commit + dribble contest.

        Returns dribble_consumed_tacklers — defender ids consumed by dribble (Phase 6 skips them).

        Args:
            validated_actions: Dict mapping player_id to validated Action objects from Phase 3
            snap: Game state snapshot from Phase 1
            tick: Current simulation tick

        Returns:
            Set of defender player_ids that were targeted by dribble contests
        """
        from src.foundation.action import Hold, Move

        # ADR-0022 amendment d: read the snap-enabled toggle from
        # SimulationConfig (default True) — used for both Move and Hold paths.
        sim_cfg = getattr(getattr(self.gsm, "config", None), "simulation", None)
        snap_enabled = getattr(sim_cfg, "formation_snap_enabled", True)

        # Compute all moves first
        move_results: dict[str, tuple[tuple[float, float], str | None]] = {}
        for pid, action in validated_actions.items():
            if isinstance(action, Move):
                # Convert Action object to dict for PMS
                action_dict = {
                    "type": "move",
                    "dx": action.dx,
                    "dy": action.dy,
                    "speed": action.speed
                }
                player_state = self.gsm.build_player_state(pid)
                final_pos, dribble_target = self.pms.resolve_movement(
                    pid, action_dict, player_state, snap,
                    snap_enabled=snap_enabled,
                )
                move_results[pid] = (final_pos, dribble_target)

        # ADR-0022 amendment d (option B): also feed Hold actions through PMS
        # so the soft snap can drift idle players toward their dynamic anchor
        # (matches ADR-0013 original intent — "snap is for idle players").
        # Pass/Shoot/Tackle/Pickup are NOT routed through PMS — those are
        # explicit actions that pin the player's location. Only Hold means
        # "I'm not actively moving but I'm still on the field".
        for pid, action in validated_actions.items():
            if isinstance(action, Hold):
                action_dict = {"type": "hold"}
                player_state = self.gsm.build_player_state(pid)
                final_pos, dribble_target = self.pms.resolve_movement(
                    pid, action_dict, player_state, snap,
                    snap_enabled=snap_enabled,
                )
                # Only record the result if it actually changed — when snap
                # is disabled or the player is the carrier, final_pos ==
                # current_pos so there's nothing to commit. (Avoids a no-op
                # apply_move call when snap_enabled=False, keeping the
                # gsm.apply_move counts identical to the pre-amendment-d
                # behavior in tests that mock the GSM.)
                current_pos = player_state["position"]
                if final_pos != current_pos:
                    move_results[pid] = (final_pos, dribble_target)

        # Per ADR-0017: separation pass before commit. When enabled
        # (min_player_separation > 0), build the full set of 10 players'
        # final positions, apply pairwise separation, then commit ALL 10
        # (non-movers may have shifted from incoming pushes). When disabled
        # (or in mock-based unit tests), commit only the movers — old behavior.
        min_sep = self._min_player_separation()
        if min_sep > 0:
            all_pos: dict[str, tuple[float, float]] = {}
            for player in snap["players"].values():
                pid = player["player_id"]
                if pid in move_results:
                    all_pos[pid] = move_results[pid][0]
                else:
                    all_pos[pid] = player["position"]

            field = snap.get("field", {})
            field_w = field.get("width", 100.0)
            field_h = field.get("height", 60.0)
            all_pos = self._enforce_player_separation(all_pos, min_sep, field_w, field_h)
            # Update move_results so the dribble contest below uses the
            # post-separation positions for movers.
            for pid in list(move_results.keys()):
                _, dribble_target = move_results[pid]
                move_results[pid] = (all_pos[pid], dribble_target)

            # Commit ALL 10 — non-movers may have shifted from separation pushes
            for pid, pos in all_pos.items():
                self.gsm.apply_move(pid, pos)
        else:
            # Separation disabled: original behavior — commit only movers
            for pid, (final_pos, _) in move_results.items():
                self.gsm.apply_move(pid, final_pos)

        # Dribble contests (after all moves committed)
        dribble_consumed: set[str] = set()
        # Per-carrier dribble outcome records, surfaced via resolve_tick into
        # the merged action_records so the Event Log shows dribble moments.
        # Was silent before 2026-04-22 (only classifier wiring existed; no
        # actual records produced — every dribble contest invisible in logs).
        self._dribble_records: dict[str, dict] = {}
        players_by_id = {p["player_id"]: p for p in snap["players"].values()}
        seed = self.gsm.seed  # Get seed from GameStateManager

        for pid, (_, dribble_target) in move_results.items():
            if dribble_target is None:
                continue
            carrier = players_by_id[pid]
            defender = players_by_id[dribble_target]
            attacker_power = (carrier["dribbling"] + carrier["speed"]) / 2
            prob = attacker_power / (attacker_power + defender["strength"])
            draw = hash_01(seed, tick, pid, dribble_target)
            if draw >= prob:  # FAIL → defender steals
                self.gsm.transfer_possession(pid, dribble_target)
                self._dribble_records[pid] = {
                    "dribble_result": "failed",
                    "dribble_target": dribble_target,
                }
            else:  # SUCCESS → carrier dribbles past
                self._dribble_records[pid] = {
                    "dribble_result": "success",
                    "dribble_target": dribble_target,
                }
            dribble_consumed.add(dribble_target)

        # Store for Story 006 (Phase 6) to read
        self.dribble_consumed = dribble_consumed
        self.move_results = move_results
        return dribble_consumed

    def _resolve_phase5(self, validated_actions: dict[str, Any], snap: dict, tick: int, current_carrier: str | None) -> dict[str, dict]:
        """GDD Rule 9, 10, 11 — ball action by current carrier.

        Phase 5: Pass and Shoot resolution. Only the player who holds ball possession
        after Phase 4 can execute Pass or Shoot actions. Sets ball velocity, landing zone,
        and transfers possession to None.

        Args:
            validated_actions: Dict mapping player_id to validated Action objects from Phase 3
            snap: Game state snapshot from Phase 1
            tick: Current simulation tick
            current_carrier: Player ID who currently has the ball (None if no carrier)

        Returns:
            Dict mapping player_id to ball action record dict with action details
        """
        from src.foundation.action import Pass, Shoot
        import math

        if current_carrier is None:
            return {}

        action = validated_actions.get(current_carrier)
        if not isinstance(action, (Pass, Shoot)):
            return {}

        passer = next(p for p in snap["players"].values() if p["player_id"] == current_carrier)
        # BALL_SPEED_PER_POWER calibrated per ADR-0014 (2026-04-22): power=20
        # → 3.5 units/tick = 35 m/s (Roberto Carlos territory). Was 0.6.
        BALL_SPEED_PER_POWER = 0.175
        seed = self.gsm.seed
        skill = passer["skill"]
        # Specialised attributes (added 2026-04-23). Falls back to skill
        # when not set so old fixtures behave identically.
        passing_attr = passer.get("passing", skill)
        shooting_attr = passer.get("shooting", skill)
        # Effective skill = (2 * specialised + skill) / 3. Specialist
        # dominates the result while skill still cushions a poor specialist
        # / lifts a good generalist by ~33%.
        pass_eff_skill = (2.0 * passing_attr + skill) / 3.0
        shot_eff_skill = (2.0 * shooting_attr + skill) / 3.0
        # Health multiplier (added 2026-04-23): a tired passer/shooter
        # gets a wider spread. Compounds with the specialised blend so
        # a fresh specialist still beats an exhausted specialist by a
        # lot, but a tired specialist still beats a fresh generalist.
        h_factor = self._health_factor(passer)
        pass_eff_skill *= h_factor
        shot_eff_skill *= h_factor

        # Per ADR-0018 (2026-04-22): continuous skill-based deviation. The
        # spread_factor exponent (0.7) flattens the high-skill tail so a
        # rating of ≥15 feels precise but not robotic. eff_skill=20 → 0
        # deviation. Pass and Shoot use their specialised effective skill;
        # fall back is identical to the prior behaviour.
        pass_spread = max(0.0, 1.0 - pass_eff_skill / 20.0) ** 0.7
        shot_spread = max(0.0, 1.0 - shot_eff_skill / 20.0) ** 0.7

        if isinstance(action, Pass):
            # ADR-0018 F1: continuous deviation. magnitude in [0, max] modulated
            # by effective passing skill; direction uniform on the circle.
            dev_mag_draw = hash_01(seed, tick, current_carrier, "pass_dev_mag")
            dev_ang_draw = hash_01(seed, tick, current_carrier, "pass_dev_angle")
            mag = pass_spread * self._pass_max_deviation() * dev_mag_draw
            ang = dev_ang_draw * 2 * math.pi
            landing_pos = (
                action.target_pos[0] + math.cos(ang) * mag,
                action.target_pos[1] + math.sin(ang) * mag,
            )

            # F3 — ball velocity (toward landing_pos, at power-derived speed)
            passer_pos = (passer["position"][0], passer["position"][1])
            delta = (landing_pos[0] - passer_pos[0], landing_pos[1] - passer_pos[1])
            dist = math.sqrt(delta[0]**2 + delta[1]**2)

            if dist < 1e-6:
                # EC-ARE-05 — default direction toward opponent goal
                opp_goal_x = snap["field"]["team_b_goal_x"] if passer["team"] == "team_a" else snap["field"]["team_a_goal_x"]
                delta = (opp_goal_x - passer_pos[0], 0.0)
                dist = abs(opp_goal_x - passer_pos[0]) or 1.0

            unit_dir = (delta[0]/dist, delta[1]/dist)
            ball_speed = action.power * BALL_SPEED_PER_POWER
            ball_velocity = (unit_dir[0] * ball_speed, unit_dir[1] * ball_speed)

            self.gsm.update_ball_velocity(ball_velocity)
            self.gsm.set_pass_landing_zone(landing_pos)
            self.gsm.transfer_possession(current_carrier, None)
            self._ball_just_passed = True
            self._last_touching_team = passer["team"]
            self._last_ball_action_pid = current_carrier

            # Issue #31 (Law 11): no offside directly from a goal kick,
            # throw-in, or corner — the restart kicker's pass is exempt.
            # Any other pass snapshots offside positions at this moment;
            # the offence (if any) fires in Phase 7 when a flagged player
            # controls the ball.
            if current_carrier == self._restart_kick_pid:
                self._offside_pids_at_pass.clear()
            else:
                self._capture_offside_at_pass(passer, snap)
            self._restart_kick_pid = None

            # Per ADR-0018: drop the binary "inaccurate" label. Always "ok".
            # The landing_pos vs target_pos delta in the event log shows
            # how off the pass was.
            return {current_carrier: {"action": "Pass", "result": "ok", "landing_pos": landing_pos}}

        else:  # Shoot
            # ADR-0018: base direction toward goal MOUTH CENTER (not just
            # ±x-axis as before). Strategy can offset via action.angle (still
            # in degrees, still relative to base). Skill adds random spread.
            opp_goal_x = snap["field"]["team_b_goal_x"] if passer["team"] == "team_a" else snap["field"]["team_a_goal_x"]
            goal_top = snap["field"].get("goal_top", 35.0)
            goal_bottom = snap["field"].get("goal_bottom", 25.0)
            goal_center_y = (goal_top + goal_bottom) / 2.0
            passer_pos = (passer["position"][0], passer["position"][1])

            base_angle = math.atan2(goal_center_y - passer_pos[1], opp_goal_x - passer_pos[0])
            strategy_intent = math.radians(action.angle)  # contract: degrees relative to base

            # Skill-based symmetric angular spread driven by effective
            # shooting skill (added 2026-04-23). eff_skill=20 → no spread.
            shot_dev_draw = hash_01(seed, tick, current_carrier, "shot_dev_angle")
            angular_spread = shot_spread * self._shot_max_angle()
            skill_deviation = (shot_dev_draw - 0.5) * 2.0 * angular_spread

            final_angle = base_angle + strategy_intent + skill_deviation
            ball_speed = action.power * BALL_SPEED_PER_POWER
            ball_velocity = (math.cos(final_angle) * ball_speed, math.sin(final_angle) * ball_speed)

            self.gsm.update_ball_velocity(ball_velocity)
            self.gsm.set_pass_landing_zone(None)
            self.gsm.transfer_possession(current_carrier, None)
            self._ball_just_passed = True
            self._last_touching_team = passer["team"]
            self._last_ball_action_pid = current_carrier

            # Issue #31: a shot is a fresh touch — void any pending offside
            # flags (v1 judges offside only at Pass moments) and consume any
            # restart-kick exemption.
            self._offside_pids_at_pass.clear()
            self._restart_kick_pid = None

            return {current_carrier: {"action": "Shoot", "result": "ok"}}

    def _resolve_phase6(self, validated_actions: dict[str, Any], snap: dict, tick: int) -> dict[str, dict]:
        """GDD Rule 12 — Tackle resolution phase.

        Phase 6: For each player whose validated action is Tackle (excluding those in
        dribble_consumed from Phase 4), resolve in player_id ascending order:
        - Range check (post-move committed positions): > TACKLE_RANGE → out_of_range
        - If ball.carrier_id != target_player_id (ball changed hands): no-op
        - PAM F4: prob = tackler.strength / (tackler.strength + target.strength)
        - draw = hash_01(tick, tackler_id, target_id)
        - If draw < prob AND target has ball: transfer_possession(target_id, tackler_id)

        Args:
            validated_actions: Dict mapping player_id to validated Action objects from Phase 3
            snap: Game state snapshot from Phase 1
            tick: Current simulation tick

        Returns:
            Dict mapping player_id to tackle record dict with action details
        """
        from src.foundation.action import Tackle

        # Per simulation config (was hard-coded 1.5u). Default 2.0u — see
        # SimulationConfig.tackle_range comment + tech-debt register.
        TACKLE_RANGE = self._tackle_range()

        tackle_records: dict[str, dict] = {}

        # Get all tacklers, excluding those consumed by dribble in Phase 4
        tacklers = [
            (pid, action) for pid, action in validated_actions.items()
            if isinstance(action, Tackle) and pid not in self.dribble_consumed
        ]

        # Sort by player_id ascending (string sort works for "team_a_0"..."team_b_4")
        tacklers.sort(key=lambda x: x[0])

        players_by_id = {p["player_id"]: p for p in snap["players"].values()}

        for tackler_id, action in tacklers:
            target_id = action.target_player_id

            # Range check using POST-COMMIT positions from Phase 4
            # For movers: use move_results final_pos; for non-movers: use snap position
            if hasattr(self, 'move_results') and tackler_id in self.move_results:
                tackler_pos = self.move_results[tackler_id][0]  # (final_pos, dribble_target)
            else:
                tackler_pos = players_by_id[tackler_id].get("position", (0.0, 0.0))

            if hasattr(self, 'move_results') and target_id in self.move_results:
                target_pos = self.move_results[target_id][0]  # (final_pos, dribble_target)
            else:
                target_pos = players_by_id[target_id].get("position", (0.0, 0.0))

            # Calculate distance
            dist = ((tackler_pos[0] - target_pos[0])**2 + (tackler_pos[1] - target_pos[1])**2) ** 0.5

            if dist > TACKLE_RANGE:
                tackle_records[tackler_id] = {"action": "Tackle", "result": "out_of_range"}
                continue

            # Re-read carrier_id (may have changed in Phase 4 dribble or Phase 5 pass)
            current_carrier = self.gsm.state.ball["carrier_id"]

            if current_carrier != target_id:
                tackle_records[tackler_id] = {"action": "Tackle", "result": "no_op_carrier_changed"}
                continue

            # Settled-possession grace (added 2026-04-23). If the carrier
            # just touched the ball within the grace window, they get a
            # moment to act before opponents can challenge. Mimics the
            # real-soccer pattern of "give the carrier time to settle"
            # and reduces the ping-pong possession churn observed in the
            # 10-round iteration.
            grace = self._tackle_settle_grace()
            if grace > 0:
                last_action_tick = self.gsm.get_last_action_tick(target_id)
                if isinstance(last_action_tick, int) and tick - last_action_tick < grace:
                    tackle_records[tackler_id] = {"action": "Tackle", "result": "no_op_settled"}
                    continue

            # PAM F4: tackle contest
            tackler = players_by_id[tackler_id]
            target = players_by_id[target_id]

            # Get strength from player_state since it's not in snap
            tackler_state = self.gsm.build_player_state(tackler_id)
            target_state = self.gsm.build_player_state(target_id)

            tackler_strength = tackler_state["strength"]
            target_strength = target_state["strength"]
            # Health-factor multiplier (added 2026-04-23): a tired
            # tackler hits weaker; a tired carrier resists less. Both
            # sides of the contest get scaled.
            tackler_strength *= self._health_factor(tackler_state)
            target_strength *= self._health_factor(target_state)

            # Per ADR-0018 (2026-04-22): 3-outcome resolution.
            # Base contest unchanged: prob = tackler.str / (tackler.str + target.str).
            # Of that "win zone", `tackle_clean_share` is a clean take; the rest
            # is a deflection (ball squirts loose). Even on a "lose", a
            # `tackle_blocked_floor` chance of deflection accounts for physical
            # contact dislodging the ball without giving it cleanly.
            prob = tackler_strength / (tackler_strength + target_strength)
            clean_share = self._tackle_clean_share()
            blocked_floor = self._tackle_blocked_floor()
            controlled_prob = prob * clean_share
            blocked_prob = prob * (1.0 - clean_share) + blocked_floor
            # Clamp so we don't exceed 1.0 in extreme settings.
            if controlled_prob + blocked_prob > 1.0:
                blocked_prob = max(0.0, 1.0 - controlled_prob)

            draw = hash_01(self.gsm.seed, tick, tackler_id, target_id)

            if draw < controlled_prob:
                # CONTROLLED: clean take. Check that target still has ball
                # (an earlier tackle this tick may have already taken it).
                if self.gsm.state.ball["carrier_id"] == target_id:
                    self.gsm.transfer_possession(target_id, tackler_id)
                    # Track for OOB attribution (FIFA Laws 15-17 restarts).
                    self._last_touching_team = tackler["team"]
                    tackle_records[tackler_id] = {"action": "Tackle", "result": "controlled"}
                else:
                    tackle_records[tackler_id] = {"action": "Tackle", "result": "no_op_carrier_changed"}
            elif draw < controlled_prob + blocked_prob:
                # BLOCKED: ball squirts loose with random velocity. Skip if
                # the target no longer has the ball.
                if self.gsm.state.ball["carrier_id"] == target_id:
                    self.gsm.transfer_possession(target_id, None)
                    speed_min = self._tackle_block_speed_min()
                    speed_max = self._tackle_block_speed_max()
                    speed_draw = hash_01(self.gsm.seed, tick, tackler_id, "tackle_block_speed")
                    angle_draw = hash_01(self.gsm.seed, tick, tackler_id, "tackle_block_angle")
                    speed = speed_min + speed_draw * (speed_max - speed_min)
                    angle = angle_draw * 2.0 * 3.14159265358979
                    import math as _m
                    self.gsm.update_ball_velocity((_m.cos(angle) * speed, _m.sin(angle) * speed))
                    # Loose ball — clear any pending pass landing zone so BPS
                    # doesn't snap to it on the next tick.
                    self.gsm.set_pass_landing_zone(None)
                    # Tackler deflected the ball — they're the last toucher
                    # for OOB-restart attribution.
                    self._last_touching_team = tackler["team"]
                    tackle_records[tackler_id] = {"action": "Tackle", "result": "blocked"}
                else:
                    tackle_records[tackler_id] = {"action": "Tackle", "result": "no_op_carrier_changed"}
            else:
                tackle_records[tackler_id] = {"action": "Tackle", "result": "failed"}

        return tackle_records

    def _resolve_phase7(self, snap: dict, tick: int) -> tuple[dict[str, dict], dict[str, dict]]:
        """ARE Story 007 — Ball physics + Rule 16 + Goal attempts.

        Phase 7: Execute BPS advance_ball with ARE-supplied pre-exclusion set
        (cooldown-active players + offside-eligible FWDs after a pass), then
        handle goal scoring attempts per ARE GDD Rule 14a.

        Per ADR-0015 amendment (2026-04-22) and ADR-0016: pre-exclusion in
        BPS is the ONLY pickup filter — there is no post-BPS reversal of
        contested pickups. The previous post-filter approach snapped the
        ball to the rejected winner's position and pinned it there, creating
        an infinite "rejected pickup" loop (visible in playtest_003).

        Args:
            snap: Game state snapshot from Phase 1
            tick: Current simulation tick

        Returns:
            Tuple of (ball_physics_records, goal_records) where:
            - ball_physics_records: Dict mapping player_id to ball pickup record
            - goal_records: Dict mapping goalkeeper_id to save attempt record
        """
        # Phase 7 preconditions (per Rule 13): skip the pickup-contest path
        # when ball is carried, or just passed. Tolerate snapshots without
        # 'field' or 'ball' (defensive for sparse test fixtures).
        ball = snap.get("ball", {})
        # Prefer LIVE carrier from GSM — the snap is from Phase 1, but Phase 5
        # may have changed possession this tick (e.g. a successful Shoot
        # transfers carrier_id → None without setting _ball_just_passed).
        # Using only snap.ball.carrier_id here would snap an already-shot ball
        # back to the shooter's feet. Surfaced 2026-04-22 in playtest_007/008.
        # Fall back to snap when gsm.state.ball isn't a real dict — mock-based
        # unit tests have `Mock()` there and would otherwise lose the carrier
        # short-circuit entirely.
        if isinstance(self.gsm.state.ball, dict):
            cid = self.gsm.state.ball.get("carrier_id")
            live_carrier_id = cid if isinstance(cid, str) else None
        else:
            cid = ball.get("carrier_id")
            live_carrier_id = cid if isinstance(cid, str) else None
        if live_carrier_id is not None:
            # Carried ball — snap ball position to carrier so it follows them
            # as they move. (BPS's own carrier-handling does this, but we
            # short-circuit BPS here to avoid running the pickup contest on
            # an already-carried ball.) Bug surfaced 2026-04-22 in
            # playtest_006: ball stayed frozen at pickup location while
            # carrier dribbled away — visible as "shot from far away" in
            # the event log because the ball was nowhere near the shooter.
            #
            # Same live-vs-snap dance: production reads from GSM live state;
            # mock-based tests fall back to snap.
            carrier_pos = None
            if isinstance(self.gsm.state.players, dict):
                carrier_state = self.gsm.state.players.get(live_carrier_id, {})
                if isinstance(carrier_state, dict):
                    carrier_pos = carrier_state.get("position")
            if carrier_pos is None:
                snap_carrier = snap.get("players", {}).get(live_carrier_id, {})
                carrier_pos = snap_carrier.get("position") if isinstance(snap_carrier, dict) else None
            if isinstance(carrier_pos, tuple) and len(carrier_pos) == 2:
                self.gsm.update_ball_position(carrier_pos)
                # Bugfix #22: a ball *carried* over the goal line within the
                # goal mouth is a goal. The shot/pass physics path below has
                # its own _is_goal_line_crossed check, but a carried ball
                # short-circuits before reaching it — so a forward could stand
                # on the goal line dribbling forever without scoring (the
                # original frozen-match symptom).
                #
                # CRUCIAL: only a carrier ATTACKING this goal can score by
                # dribbling it in. A player in possession at their OWN goal
                # line — a keeper holding the ball, a defender shielding on
                # the line — is NOT an own goal; awarding one there made
                # normal goal-line defending catastrophic (10 bogus own goals
                # in one match during the first fix pass). Genuine own goals
                # come from a PLAYED ball (kick/deflection carrying velocity)
                # via the ball-physics goal check further below — not from
                # carrying. A carrier pinned at their own line instead falls
                # through to the stalemate breaker, which turns it over.
                if self._is_goal_line_crossed(carrier_pos, snap):
                    defending_team = self._get_defending_team(carrier_pos, snap)
                    carrier_player = snap.get("players", {}).get(live_carrier_id)
                    carrier_team = (carrier_player.get("team")
                                    if isinstance(carrier_player, dict) else None)
                    if carrier_team is not None and carrier_team != defending_team:
                        gk_id = self._find_goalkeeper(defending_team, snap)
                        # A keeper in position gets a save attempt — otherwise
                        # a slow dribble walks past them into the net every
                        # time. A carried ball is ~stationary, so a parry is
                        # treated as a smother: either save outcome hands the
                        # keeper possession, which also breaks any boundary pin
                        # realistically.
                        if gk_id is not None:
                            outcome, reason = self._attempt_goalkeeper_save(
                                gk_id, carrier_pos, (0.0, 0.0), snap, tick)
                            if outcome in ("caught", "blocked"):
                                self.gsm.update_ball_velocity((0.0, 0.0))
                                self.gsm.transfer_possession(live_carrier_id, gk_id)
                                self._snap_ball_to_carrier(gk_id)
                                self._last_ball_action_pid = None
                                self._last_touching_team = defending_team
                                return {}, {gk_id: {
                                    "goalkeeper_save": outcome,
                                    "reason": reason,
                                    "saved_from": live_carrier_id,
                                }}
                        # No keeper, or the save missed → goal.
                        self.gsm.update_ball_velocity((0.0, 0.0))
                        self.gsm.transfer_possession(live_carrier_id, None)
                        self._record_goal(defending_team, snap)
                        self._last_ball_action_pid = None
                        return {}, {"system": {
                            "goal_scored": self._get_attacking_team(defending_team),
                            "scored_by": live_carrier_id,
                            "reason": "dribbled_in",
                        }}
            return {}, {}
        # NOTE: previously had `if velocity == (0,0): return {},{}` here.
        # Removed 2026-04-22 — that guard prevented the pickup contest from
        # ever running for a stationary loose ball. BPS still has its own
        # contest logic; it should run every tick when there's no carrier.
        if self._ball_just_passed:
            return {}, {}
        if "field" not in snap:
            return {}, {}

        # Get current game state for BPS (includes private _pass_landing_zone)
        game_state_dict = self._build_bps_game_state(snap)

        # Build pickup exclusion set (ADR-0015 amendment + Rule 16):
        # - cooldown-active players (replaces _passer_exclusion blocking role)
        # - offside-eligible FWDs while _ball_just_passed is set
        excluded_pids: set[str] = set()
        if self._action_cooldown() > 0:
            for pid in snap.get("players", {}):
                if self._is_on_cooldown(pid, tick):
                    excluded_pids.add(pid)
        for player in snap.get("players", {}).values():
            pid = player["player_id"]
            if self._is_offside_violation(pid, snap):
                excluded_pids.add(pid)

        # Call BPS advance_ball (handles motion + ball control contest +
        # shot deflection). Use injected self.bps (MagicMock-friendly in
        # tests; real BPS in production). All optional kwargs flow as
        # kwargs so legacy mock-based tests with positional-only args
        # still work — Mock just records them.
        bps_kwargs = {
            "deflect_min_speed": self._sim_float("shot_deflection_min_speed", 2.0),
            "deflect_speed_factor_min": self._sim_float("shot_deflection_speed_factor_min", 0.3),
            "deflect_speed_factor_max": self._sim_float("shot_deflection_speed_factor_max", 0.5),
            "range_gk": self._sim_float("ball_control_range_gk", 1.5),
            "range_outfield": self._sim_float("ball_control_range_outfield", 1.0),
        }
        if excluded_pids:
            bps_kwargs["excluded_pids"] = excluded_pids
        ball_result = self.bps.advance_ball(
            game_state_dict,
            self.gsm.seed,
            tick,
            snap["field"]["width"],
            snap["field"]["height"],
            **bps_kwargs,
        )

        # Commit motion results to GSM
        self.gsm.update_ball_position(ball_result["new_position"])
        self.gsm.update_ball_velocity(ball_result["new_velocity"])

        ball_physics_records: dict[str, dict] = {}
        goal_records: dict[str, dict] = {}

        # If a defender deflected the ball (shot block), record the touch
        # for OOB attribution and emit an event-log row. Added 2026-04-23:
        # this is the new mechanism that produces corners (defender
        # deflects shot wide of own end line → ball goes over their end
        # line → corner to attacking team).
        #
        # Important: trigger the cooldown for the deflector so they can't
        # immediately re-pickup their own deflection on the very next
        # tick. Without this, deflections bounce 1u and get picked back
        # up — never reaching the end line.
        deflector = ball_result.get("deflected_by")
        if deflector is not None:
            deflector_state = (self.gsm.state.players.get(deflector, {})
                               if isinstance(self.gsm.state.players, dict)
                               else {})
            deflector_team = deflector_state.get("team")
            if deflector_team:
                self._last_touching_team = deflector_team
            self.gsm.record_action_cooldown(deflector, tick)
            ball_physics_records[deflector] = {
                "shot_deflection": True,
                "deflected_from": self._last_ball_action_pid,
            }

        # Per ADR-0016: goal-line crossing has PRECEDENCE over OOB. A ball
        # crossing the goal line within the goal mouth is BOTH out-of-bounds
        # AND a goal — but it must be handled by the goal logic, not the
        # generic OOB early-return. Capture the shooter from
        # self._last_ball_action_pid BEFORE the goal logic clears it.
        if self._is_goal_line_crossed(ball_result["new_position"], snap):
            shooter_id = self._last_ball_action_pid  # may be None for non-shot scenarios
            defending_team = self._get_defending_team(ball_result["new_position"], snap)
            goalkeeper_id = self._find_goalkeeper(defending_team, snap)

            if goalkeeper_id is not None:
                save_outcome, reason = self._attempt_goalkeeper_save(
                    goalkeeper_id, ball_result["new_position"], ball_result["new_velocity"],
                    snap, tick
                )

                if save_outcome == "caught":
                    # Clean catch — stop ball, give possession to GK.
                    self.gsm.update_ball_velocity((0.0, 0.0))
                    self.gsm.transfer_possession(None, goalkeeper_id)
                    self._snap_ball_to_carrier(goalkeeper_id)
                    self._last_ball_action_pid = None
                    self._last_touching_team = defending_team
                    goal_records[goalkeeper_id] = {
                        "goalkeeper_save": "success",
                        "reason": reason,
                        "saved_from": shooter_id,  # ADR-0016 attribution
                    }
                elif save_outcome == "blocked":
                    # ADR-0018 (revised 2026-04-23, fix-pass 2026-04-23):
                    # parries split into TWO outcomes — push wide (corner)
                    # or rebound back into the box. Two bugs fixed in this
                    # revision:
                    #   1. incoming_speed used `ball_result.new_velocity`,
                    #      which is (0,0) when BPS clamped the ball OOB at
                    #      the goal line. Result: parried ball had zero
                    #      velocity → stuck at the post forever.
                    #   2. Old code only ever pushed perpendicular, so the
                    #      ball never crossed the END line — corners
                    #      stayed at 0 across all 11v11 rounds.
                    # Now we use the pre-BPS velocity from the snap, and
                    # roll for "push wide → corner" vs "rebound in box",
                    # weighted by how close the shot was to a post.
                    import math as _m
                    field_w = snap["field"]["width"]
                    field_h = snap["field"]["height"]
                    team_goal_x = snap["field"][f"{defending_team}_goal_x"]
                    away_x_sign = 1.0 if team_goal_x < field_w / 2.0 else -1.0
                    goal_top = snap["field"]["goal_top"]
                    goal_bottom = snap["field"]["goal_bottom"]
                    goal_center_y = (goal_top + goal_bottom) / 2.0
                    goal_half_h = max(1e-6, (goal_top - goal_bottom) / 2.0)
                    ball_y = ball_result["new_position"][1]
                    # post_proximity: 0 at goal center, 1 at post.
                    post_proximity = min(1.0, abs(ball_y - goal_center_y) / goal_half_h)

                    # Push-wide chance scales with post proximity. Central
                    # shots are usually punched back into play; shots near
                    # a post are usually tipped around it for a corner.
                    push_wide_prob = 0.45 + 0.45 * post_proximity
                    oob_draw = hash_01(self.gsm.seed, tick, goalkeeper_id, "save_block_oob")
                    push_wide = oob_draw < push_wide_prob

                    if push_wide:
                        # Tip-around-post → corner. Place ball just past
                        # the end line, just outside the nearer post.
                        # _last_touching_team = defending_team makes the
                        # OOB restart award the corner to the attackers.
                        side_sign = 1.0 if ball_y >= goal_center_y else -1.0
                        post_y = goal_center_y + side_sign * goal_half_h
                        oob_y = post_y + side_sign * 0.5  # 0.5u outside post
                        oob_y = max(0.0, min(field_h, oob_y))
                        oob_x = 0.0 if team_goal_x <= 0.001 else field_w
                        oob_pos = (oob_x, oob_y)
                        self.gsm.update_ball_position(oob_pos)
                        self.gsm.update_ball_velocity((0.0, 0.0))
                        self.gsm.set_pass_landing_zone(None)
                        self._last_touching_team = defending_team
                        # Clear shooter attribution — parry-to-corner is a
                        # finished play; no rebound goal possible.
                        self._last_ball_action_pid = None
                        self._apply_oob_restart(oob_pos, snap, ball_physics_records)
                        goal_records[goalkeeper_id] = {
                            "goalkeeper_save": "blocked",
                            "reason": reason,
                            "saved_from": shooter_id,
                            "push_wide": True,
                        }
                    else:
                        # Rebound into the box. Use the PRE-BPS velocity
                        # (snap) for incoming_speed because BPS may have
                        # zeroed new_velocity when clamping OOB.
                        pre_vel = snap.get("ball", {}).get("velocity", (0.0, 0.0))
                        incoming_speed = (pre_vel[0] ** 2 + pre_vel[1] ** 2) ** 0.5
                        # Floor: ensure the rebound actually moves even on
                        # degenerate inputs (e.g. low-speed lob saves).
                        new_speed = max(2.0, incoming_speed * self._gk_block_speed_factor())
                        # Direction: REVERSE incoming (back toward midfield)
                        # with ±60° spread. Real GK punches send the ball
                        # back the way it came, not perpendicular.
                        incoming_angle = _m.atan2(pre_vel[1], pre_vel[0])
                        # Reverse = +π (180° flip).
                        reverse_angle = incoming_angle + _m.pi
                        cone_draw = hash_01(self.gsm.seed, tick, goalkeeper_id, "save_block_angle")
                        REBOUND_CONE_HALF = _m.pi / 3.0  # ±60°
                        angle = reverse_angle + (cone_draw - 0.5) * 2.0 * REBOUND_CONE_HALF
                        self.gsm.update_ball_velocity((_m.cos(angle) * new_speed,
                                                        _m.sin(angle) * new_speed))
                        # Nudge position back into the box along away axis,
                        # 3.0u so the rebound has room to fly clear before
                        # any goal-line re-check fires.
                        deflected_pos = (ball_result["new_position"][0] + away_x_sign * 3.0,
                                         ball_result["new_position"][1])
                        deflected_pos = (max(0.0, min(field_w, deflected_pos[0])),
                                         deflected_pos[1])
                        self.gsm.update_ball_position(deflected_pos)
                        self.gsm.set_pass_landing_zone(None)
                        # _last_ball_action_pid preserved → rebound goal still
                        # attributes to the original shooter.
                        self._last_touching_team = defending_team
                        goal_records[goalkeeper_id] = {
                            "goalkeeper_save": "blocked",
                            "reason": reason,
                            "saved_from": shooter_id,
                            "push_wide": False,
                        }
                else:  # "missed"
                    # Save failed — goal scored. Stop ball at goal line and
                    # actually increment the score (ADR-0016 closes the
                    # _record_goal stub).
                    self.gsm.update_ball_velocity((0.0, 0.0))
                    self.gsm.set_pass_landing_zone(None)
                    self._record_goal(defending_team, snap)
                    self._last_ball_action_pid = None
                    goal_records[goalkeeper_id] = {
                        "goalkeeper_save": "failed",
                        "reason": reason,
                        "goal_scored": self._get_attacking_team(defending_team),
                        "scored_by": shooter_id,  # ADR-0016 attribution
                    }
            else:
                # No goalkeeper — automatic goal
                self.gsm.update_ball_velocity((0.0, 0.0))
                self.gsm.set_pass_landing_zone(None)
                self._record_goal(defending_team, snap)
                self._last_ball_action_pid = None
                goal_records["system"] = {
                    "goal_scored": self._get_attacking_team(defending_team),
                    "scored_by": shooter_id,  # ADR-0016 attribution
                    "reason": "no_goalkeeper"
                }

            return ball_physics_records, goal_records

        # Handle out of bounds — FIFA Laws 15 (throw-in), 16 (goal kick),
        # 17 (corner kick). Only reached if NOT a goal-line crossing.
        # Implemented 2026-04-23 (was: ball just stopped at the boundary
        # and the nearest player picked it up, which gave no team a
        # restart advantage and looked nothing like real soccer).
        if ball_result["out_of_bounds"]:
            self.gsm.set_pass_landing_zone(None)
            self._apply_oob_restart(ball_result["new_position"], snap, ball_physics_records)
            return ball_physics_records, goal_records

        # Handle ball pickup. Cooldown + offside filtering is done upstream
        # via excluded_pids — anything BPS returns here is a valid pickup.
        pickup_player_id = ball_result.get("controlled_by")
        if pickup_player_id is not None:
            self.gsm.transfer_possession(None, pickup_player_id)
            # Per ADR-0015 amendment (2026-04-22): a successful pickup
            # triggers the unified action cooldown — the player must
            # "settle" before passing/shooting/tackling again.
            self.gsm.record_action_cooldown(pickup_player_id, tick)
            # BPS computed `new_position` from the snapshot's stale carrier
            # position (Phase 1, before Phase 4 movement). Re-snap to the
            # picker's LIVE position so the ball lands at their feet, not
            # 0.7-1.0u behind. Surfaced 2026-04-22 in playtest_009.
            self._snap_ball_to_carrier(pickup_player_id)
            # Clear _last_ball_action_pid: the most recent ball-action's
            # passer/shooter no longer owns goal attribution once the
            # ball has been collected. Update _last_touching_team for OOB
            # restart attribution (FIFA Laws 15-17).
            self._last_ball_action_pid = None
            picker_team = self.gsm.state.players.get(pickup_player_id, {}).get("team") \
                if isinstance(self.gsm.state.players, dict) else None
            if picker_team:
                self._last_touching_team = picker_team
            ball_physics_records[pickup_player_id] = {
                "ball_pickup": "success",
                "reason": "ok"
            }

        # (Goal-line check moved to the top of the function per ADR-0016.)
        return ball_physics_records, goal_records

    def _snap_ball_to_carrier(self, carrier_id: str) -> None:
        """Snap ball position to the named carrier's LIVE position. No-op if
        the carrier or position can't be read (mock-based unit tests).

        Used after pickup/save commits to enforce the ball-at-carrier
        invariant. Reading from gsm.state (live) instead of the snap avoids
        the lag introduced by Phase 4 movement happening AFTER the snap was
        built. Surfaced 2026-04-22 in playtest_009.
        """
        if not isinstance(self.gsm.state.players, dict):
            return  # mock GSM — nothing to snap
        carrier_state = self.gsm.state.players.get(carrier_id, {})
        if not isinstance(carrier_state, dict):
            return
        carrier_pos = carrier_state.get("position")
        if isinstance(carrier_pos, tuple) and len(carrier_pos) == 2:
            self.gsm.update_ball_position(carrier_pos)

    def _check_stalemate(self, tick: int) -> None:
        """Bugfix #22 — break a frozen match.

        Tracks how long the carried ball has stayed within _STUCK_RADIUS of
        an anchor point. Once it has been effectively motionless for
        _STUCK_MAX_TICKS consecutive ticks, force a turnover to the nearest
        opponent so play resumes (e.g. a ball pinned at a boundary that the
        defending side never pressures).

        Resets whenever the ball is loose (no carrier) or makes net progress.
        Defensive against mock GSMs whose state isn't a real dict.
        """
        ball = getattr(self.gsm.state, "ball", None)
        if not isinstance(ball, dict):
            return
        pos = ball.get("position")
        carrier_id = ball.get("carrier_id")
        if (carrier_id is None
                or not isinstance(pos, (tuple, list)) or len(pos) != 2):
            # Loose ball (or unreadable) — no stalemate to track.
            self._stuck_ticks = 0
            self._stuck_anchor_pos = None
            return

        anchor = self._stuck_anchor_pos
        if anchor is not None and (
            (pos[0] - anchor[0]) ** 2 + (pos[1] - anchor[1]) ** 2
            <= self._STUCK_RADIUS ** 2
        ):
            self._stuck_ticks += 1
        else:
            # Net progress (or first observation) — re-anchor and count this
            # tick as the first in the new window.
            self._stuck_anchor_pos = (float(pos[0]), float(pos[1]))
            self._stuck_ticks = 1

        if self._stuck_ticks >= self._STUCK_MAX_TICKS:
            self._force_turnover(carrier_id, (float(pos[0]), float(pos[1])))
            self._stuck_ticks = 0
            self._stuck_anchor_pos = None

    def _force_turnover(self, carrier_id: str, pos: tuple[float, float]) -> None:
        """Hand the ball to the nearest opponent of the stuck carrier."""
        players = getattr(self.gsm.state, "players", None)
        if not isinstance(players, dict):
            return
        carrier = players.get(carrier_id, {})
        carrier_team = carrier.get("team") if isinstance(carrier, dict) else None

        best_pid = None
        best_dist = None
        for pid, p in players.items():
            if not isinstance(p, dict) or p.get("team") == carrier_team:
                continue
            ppos = p.get("position")
            if not isinstance(ppos, (tuple, list)) or len(ppos) != 2:
                continue
            d = (ppos[0] - pos[0]) ** 2 + (ppos[1] - pos[1]) ** 2
            if best_dist is None or d < best_dist:
                best_dist = d
                best_pid = pid
        if best_pid is None:
            return

        logger.info(
            "stalemate breaker: ball static at %s under %s for %d ticks — "
            "turning over to nearest opponent %s",
            pos, carrier_id, self._STUCK_MAX_TICKS, best_pid,
        )
        self.gsm.transfer_possession(carrier_id, best_pid)
        self._snap_ball_to_carrier(best_pid)
        self.gsm.update_ball_velocity((0.0, 0.0))
        opponent = players.get(best_pid, {})
        if isinstance(opponent, dict):
            self._last_touching_team = opponent.get("team")

    def _apply_oob_restart(self, oob_pos: tuple[float, float], snap: dict,
                           ball_physics_records: dict) -> None:
        """Per FIFA Laws 15-17: classify OOB and award the appropriate
        restart (throw-in / goal kick / corner kick) to the correct team.

        Side line OOB (top/bottom of field) → throw-in by the team that
        did NOT touch the ball last.

        End line OOB (left/right of field, outside the goal mouth — goals
        are intercepted by ADR-0016 before reaching here):
          - Last touched by attacker → defending team's GK takes a goal
            kick from a spot 5.5u in front of their own goal.
          - Last touched by defender → attacking team takes a corner from
            the corner of the field nearest the OOB point.

        After classification, the ball is placed at the restart spot, the
        chosen kicker is teleported to the same spot, possession is given
        to them, and a `system` record is emitted with `restart_type`,
        `restart_team`, `kicker_id` for the Event Log.

        Defensive against mock GSMs: if `state.players` / `state.field`
        aren't real dicts (e.g. from MagicMock), fall back to the legacy
        "just record OOB" behaviour.
        """
        bx, by = oob_pos

        # Mock-tolerance: bail to the legacy behaviour if state isn't real.
        if (not isinstance(getattr(self.gsm.state, "players", None), dict)
                or not isinstance(getattr(self.gsm.state, "field", None), dict)):
            ball_physics_records["system"] = {
                "out_of_bounds": True,
                "position": (bx, by),
                "last_touched_by": self._last_ball_action_pid,
            }
            return

        field = self.gsm.state.field
        fw = field.get("width", 100.0)
        fh = field.get("height", 60.0)

        # Decide OOB type. Corners (both x and y at extremes) are
        # classified as END line — the corner kick / goal kick paths
        # treat them correctly via x-side anyway.
        end_oob = (bx <= 0.001 or bx >= fw - 0.001)
        side_oob = (by <= 0.001 or by >= fh - 0.001)

        last_team = self._last_touching_team
        if last_team is None:
            # No prior touch tracked — extremely unlikely (only happens at
            # match start before anyone has touched the ball). Default to
            # team_a so we always produce a deterministic restart.
            last_team = "team_a"
        other_team = "team_b" if last_team == "team_a" else "team_a"

        if end_oob:
            # Defending team is whoever defends THIS end of the field.
            # team_*_goal_x stores their defended goal's x-coord.
            team_a_goal_x = field.get("team_a_goal_x", 0.0)
            if (bx <= 0.001 and team_a_goal_x <= 0.001) or \
               (bx >= fw - 0.001 and team_a_goal_x >= fw - 0.001):
                defending_team = "team_a"
            else:
                defending_team = "team_b"
            attacking_team = "team_b" if defending_team == "team_a" else "team_a"

            if last_team == attacking_team:
                # Goal kick — defending GK restarts from the goal area.
                receiving_team = defending_team
                sign = 1.0 if bx <= 0.001 else -1.0
                restart_spot = (bx + sign * 5.5, fh / 2.0)
                restart_type = "goal_kick"
                kicker_id = self._select_restarter(receiving_team, restart_spot, prefer_role="GK")
            else:
                # Corner kick — attacking team restarts from the nearest
                # corner. Corners are exactly (0|fw, 0|fh).
                receiving_team = attacking_team
                corner_x = 0.0 if bx <= 0.001 else fw
                corner_y = 0.0 if by < fh / 2.0 else fh
                restart_spot = (corner_x, corner_y)
                restart_type = "corner_kick"
                kicker_id = self._select_restarter(receiving_team, restart_spot, exclude_role="GK")
        elif side_oob:
            # Throw-in — opposing team restarts from where the ball crossed.
            # Pull the restart spot just inside the field so subsequent
            # motion isn't immediately classified OOB again.
            receiving_team = other_team
            restart_y = 0.5 if by <= 0.001 else fh - 0.5
            restart_x = max(2.0, min(fw - 2.0, bx))
            restart_spot = (restart_x, restart_y)
            restart_type = "throw_in"
            kicker_id = self._select_restarter(receiving_team, restart_spot, exclude_role="GK")
        else:
            # Shouldn't happen — OOB without crossing any line. Emit the
            # legacy record and bail.
            ball_physics_records["system"] = {
                "out_of_bounds": True,
                "position": (bx, by),
                "last_touched_by": self._last_ball_action_pid,
            }
            return

        # Apply the restart: ball + kicker at the spot, possession transferred.
        self.gsm.update_ball_position(restart_spot)
        self.gsm.update_ball_velocity((0.0, 0.0))
        if kicker_id is not None:
            self.gsm.apply_move(kicker_id, restart_spot)
            self.gsm.transfer_possession(None, kicker_id)
            self._last_touching_team = receiving_team
            # Don't trigger cooldown for the restart — the kicker hasn't
            # ACTED yet, just been positioned. Their next-tick Pass/Shoot
            # will trigger cooldown normally.

        ball_physics_records["system"] = {
            "out_of_bounds": True,
            "position": (bx, by),
            "restart_spot": restart_spot,
            "restart_type": restart_type,
            "restart_team": receiving_team,
            "kicker_id": kicker_id,
            "last_touched_by": self._last_ball_action_pid,
        }

    def _select_restarter(self, team: str, spot: tuple[float, float],
                          exclude_role: str | None = None,
                          prefer_role: str | None = None) -> str | None:
        """Pick the team player nearest to `spot` to take a restart.

        - `prefer_role`: if any team player matches this role, choose the
          nearest of those (used for goal kicks → prefer GK).
        - `exclude_role`: skip players with this role (used for throw-ins
          and corners → exclude GK).
        - Falls back to "any team member nearest" if filters leave nobody.
        """
        if not isinstance(self.gsm.state.players, dict):
            return None
        candidates = []
        for pid, p in self.gsm.state.players.items():
            if p.get("team") != team:
                continue
            role = p.get("role")
            if exclude_role is not None and role == exclude_role:
                continue
            ppos = p.get("position", (0.0, 0.0))
            d = ((ppos[0] - spot[0]) ** 2 + (ppos[1] - spot[1]) ** 2) ** 0.5
            preferred = (prefer_role is not None and role == prefer_role)
            # Sort key: preferred role first, then nearest, then pid for stability.
            candidates.append(((0 if preferred else 1), d, pid))
        if not candidates:
            # Fallback: include excluded role too.
            for pid, p in self.gsm.state.players.items():
                if p.get("team") != team:
                    continue
                ppos = p.get("position", (0.0, 0.0))
                d = ((ppos[0] - spot[0]) ** 2 + (ppos[1] - spot[1]) ** 2) ** 0.5
                candidates.append((1, d, pid))
        if not candidates:
            return None
        candidates.sort()
        return candidates[0][2]

    def _build_bps_game_state(self, snap: dict) -> dict:
        """Build BPS-compatible game_state dict from ARE snapshot.

        BPS expects the private _pass_landing_zone key that's stripped from public snapshots.
        """
        # Get the private _pass_landing_zone from GSM
        pass_landing_zone = getattr(self.gsm.state, '_pass_landing_zone', None)

        game_state = snap.copy()
        if pass_landing_zone is not None:
            game_state["_pass_landing_zone"] = pass_landing_zone

        return game_state

    def _is_offside_violation(self, player_id: str, snap: dict) -> bool:
        """Check ARE GDD Rule 16 - offside-equivalent rule.

        A FWD player violates Rule 16 if:
        1. Player is a FWD (position == "FWD")
        2. Ball just passed this tick (_ball_just_passed == True)
        3. Player is closer to opponent goal line than any opponent DEF/GK
        """
        if not self._ball_just_passed:
            return False

        player = next((p for p in snap["players"].values() if p["player_id"] == player_id), None)
        # Real GSM snapshots use 'role' (per ADR-0004 / GSM init), not
        # 'position_type'. The latter only ever appeared in test fixtures.
        # Accept either for backward compat with the 5 advisory fixtures.
        if player is None:
            return False
        role = player.get("role") or player.get("position_type")
        if role != "FWD":
            return False

        player_team = player["team"]
        opponent_team = "team_b" if player_team == "team_a" else "team_a"

        # Find opponent goal x-coordinate
        opp_goal_x = snap["field"]["team_b_goal_x"] if player_team == "team_a" else snap["field"]["team_a_goal_x"]

        # Distance from player to opponent goal line
        player_pos = player["position"]
        player_dist_to_goal = abs(player_pos[0] - opp_goal_x)

        # Find closest opponent DEF/GK distance to their own goal
        min_defender_dist = float('inf')
        for p in snap["players"].values():
            p_role = p.get("role") or p.get("position_type")
            if (p["team"] == opponent_team and
                p_role in ["DEF", "GK"]):
                defender_pos = p["position"]
                defender_dist = abs(defender_pos[0] - opp_goal_x)
                min_defender_dist = min(min_defender_dist, defender_dist)

        # Violation if FWD is closer than any opponent DEF/GK
        return player_dist_to_goal < min_defender_dist

    def _is_goal_line_crossed(self, ball_pos: tuple[float, float], snap: dict) -> bool:
        """Check if ball has crossed a goal line.

        Goal lines are GEOMETRICALLY FIXED at x=0 and x=field_width — they do
        NOT swap at halftime. (Bug history 2026-04-22: this used to compare
        against team_a_goal_x / team_b_goal_x, but those swap at halftime per
        GSM.swap_attack_direction. After swap, team_a_goal_x=field_width and
        team_b_goal_x=0, so `x <= team_a_goal_x or x >= team_b_goal_x` was
        True for ANY x in the field — every tick fired a phantom goal.)

        Which team defends which side is determined separately by
        _get_defending_team via the team_*_goal_x attributes.
        """
        x, y = ball_pos
        field = snap["field"]

        # Check if ball is in goal area (y within goal bounds)
        goal_top = field["goal_top"]
        goal_bottom = field["goal_bottom"]

        if not (goal_bottom <= y <= goal_top):
            return False

        # Geometric goal lines, halftime-independent.
        field_width = field["width"]
        return x <= 0.0 or x >= field_width

    def _get_defending_team(self, ball_pos: tuple[float, float], snap: dict) -> str:
        """Determine which team is defending based on which side was crossed.

        Compares the crossed side (x=0 or x=field_width) to each team's
        current goal_x — which DOES swap at halftime. Whichever team's
        goal is at the crossed side is the defender.
        """
        x, _ = ball_pos
        field = snap["field"]
        field_width = field["width"]

        # Determine which physical side the ball crossed.
        crossed_x = 0.0 if x <= 0.0 else field_width
        # Match to the team whose goal is at that x (post-swap aware).
        if abs(field["team_a_goal_x"] - crossed_x) < 1e-6:
            return "team_a"
        return "team_b"

    def _get_attacking_team(self, defending_team: str) -> str:
        """Get the attacking team given the defending team."""
        return "team_b" if defending_team == "team_a" else "team_a"

    def _find_goalkeeper(self, team: str, snap: dict) -> str | None:
        """Find the goalkeeper for the specified team.

        Real GSM snapshots use 'role' (per ADR-0004 / GSM init); fixture
        snapshots in the 5 long-standing advisory tests use 'position_type'.
        Accept either so both paths work. Long-term cleanup: migrate the
        advisory test fixtures to 'role' and drop the alias.
        """
        for player in snap["players"].values():
            role = player.get("role") or player.get("position_type")
            if player["team"] == team and role == "GK":
                return player["player_id"]
        return None

    def _attempt_goalkeeper_save(self, gk_id: str, ball_pos: tuple[float, float],
                                ball_vel: tuple[float, float], snap: dict, tick: int
                                ) -> tuple[str, str]:
        """Execute ARE GDD Rule 14a + ADR-0018 goalkeeper save attempt.

        Per ADR-0018 (2026-04-22): 3-state outcome.
          - "caught": clean catch (current "success" path)
          - "blocked": parry — ball deflects with reduced speed, still loose
          - "missed": GK misses, goal scored (current "failed" path)

        Returns:
            (outcome, reason) where outcome is one of {"caught", "blocked", "missed"}.
            Backward note: ARE Phase 7 used to test `save_success: bool` —
            the call site is updated alongside this signature change.
        """
        gk_player = next(p for p in snap["players"].values() if p["player_id"] == gk_id)
        gk_pos = gk_player["position"]

        # Effective save skill (2026-06-08, spec gk-save-rate-tuning): use the
        # keeper's dedicated `save` rating (GK-only attr, already in
        # player_state) blended with generic skill via the engine's standard
        # (2*specialised + skill)/3 convention. Fall back to skill when `save`
        # is absent (mock fixtures / degenerate configs).
        gk_state = self.gsm.build_player_state(gk_id)
        gk_skill = gk_state.get("skill", 1)
        gk_save = gk_state.get("save", gk_skill)
        eff_save = (2.0 * gk_save + gk_skill) / 3.0
        # Health-factor multiplier (a tired GK has weaker reflexes).
        eff_save *= self._health_factor(gk_state)

        # ARE F1: distance from GK to ball
        dist_to_ball = ((gk_pos[0] - ball_pos[0])**2 + (gk_pos[1] - ball_pos[1])**2)**0.5

        # ARE F2: ball speed
        ball_speed = (ball_vel[0]**2 + ball_vel[1]**2)**0.5

        # ARE F3: save_prob weights the keeper term by GK_SAVE_WEIGHT so
        # realistic keepers stop most on-target shots (curbs the inflated
        # goal rate). GK_SAVE_WEIGHT=1.0 reproduces the legacy curve.
        save_prob = (GK_SAVE_WEIGHT * eff_save) / (GK_SAVE_WEIGHT * eff_save + ball_speed + dist_to_ball)

        # Single hash_01 roll, two thresholds:
        #   draw < save_prob * caught_share        → CAUGHT
        #   draw < save_prob                       → BLOCKED (parry)
        #   else                                   → MISSED (goal)
        caught_share = self._gk_caught_share()
        caught_threshold = save_prob * caught_share

        draw = hash_01(self.gsm.seed, tick, gk_id, "goalkeeper_save")
        if draw < caught_threshold:
            return "caught", "skill_sufficient"
        if draw < save_prob:
            return "blocked", "parried"
        return "missed", "skill_insufficient"

    def _record_goal(self, defending_team: str, snap: dict) -> None:
        """Record goal in GSM state by incrementing the attacking team's score.

        Per ADR-0016 (2026-04-22): closes the long-standing TODO. Calls
        gsm.record_goal(scoring_team) — the GSM mutation API has existed since
        GSM Story 003 but the ARE-side caller was never implemented, which
        caused every goal-line crossing to silently no-op (5 advisory tests
        flagged this for months).
        """
        attacking_team = self._get_attacking_team(defending_team)
        self.gsm.record_goal(attacking_team)
        pass

    def _provider_for_team(self, team: str) -> str:
        """Get LLM provider for the given team.

        TODO: Read from MatchConfig when available. For now returns 'unknown'.
        """
        return "unknown"