"""
Game State Manager for Agent Pitch soccer simulation.

This module provides the foundational GameState dataclass and GameStateManager
that owns the entire simulation state. Implements Story 001 requirements for
state initialization and basic access methods.
"""

from __future__ import annotations
from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING, Literal

from src.foundation.simulation_utils import hash_01
from src.foundation.formation_and_role_system import (
    classify_team_phase,
    compute_zone_for,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from typing import Any

# Type alias for game phases
Phase = Literal["PRE_MATCH", "KICK_OFF", "IN_PLAY", "GOAL_SCORED", "HALF_TIME", "FULL_TIME"]


@dataclass
class GameState:
    """
    Complete simulation state for a single match.

    Contains both static configuration (set at initialization) and mutable
    runtime state that changes throughout the match. Owned exclusively by
    GameStateManager.

    Static fields are computed once from MatchConfig during initialization.
    Runtime fields are modified through GameStateManager mutation methods.
    Internal fields support simulation logic but are not included in snapshots.
    """

    # Static configuration (set at initialization, never changed)
    seed: int
    tick_rate: int
    duration_minutes: int
    total_ticks: int
    half_1_end_tick: int
    field_width: float
    field_height: float

    # Mutable runtime state (modified during simulation)
    tick: int
    phase: Phase
    score: dict[str, int]
    half: int
    players: dict[str, dict[str, Any]]
    ball: dict[str, Any]
    field: dict[str, Any]

    # Internal state (private — never in snapshot)
    _anchors: dict[str, tuple[float, float]]
    _kickoff_team: str
    _last_touching_team: str | None
    _pass_landing_zone: tuple[float, float] | None


class GameStateManager:
    """
    Manages the complete simulation state for a single match.

    Responsibilities:
    - Initialize GameState from MatchConfig and formation anchors
    - Provide controlled access to state through methods and properties
    - Own the single source of truth for all simulation state
    - Ensure deterministic initialization (same inputs → same initial state)

    The GSM is the sole owner of GameState. No other system should hold
    simulation state between ticks.
    """

    def __init__(self, config: Any, anchors: dict[str, tuple[float, float]]) -> None:
        """
        Initialize GameStateManager with match configuration and player positions.

        Reads the real `MatchConfig` schema (`config.team_a.players`,
        `config.team_b.players`, `config.match.field_width/height`). Player team
        is derived from `player_id` per ADR-0004 — `PlayerConfig` itself has no
        `team` field.

        Args:
            config: MatchConfig instance from src.foundation.config_models
            anchors: Dict mapping player_id to (x, y) formation position

        Post-conditions:
            - All 10 players positioned at their formation anchors
            - Ball at field center with zero velocity
            - Kickoff team determined deterministically from seed
            - Total ticks and half-time computed from match duration
            - Phase set to PRE_MATCH, tick = 0, score = 0-0
        """
        seed = config.match.seed
        tick_rate = config.match.tick_rate
        duration_minutes = config.match.duration_minutes
        total_ticks = tick_rate * duration_minutes * 60
        half_1_end_tick = total_ticks // 2

        # Determine kickoff team deterministically using hash_01
        kickoff_team = "team_a" if hash_01(seed, 0, "kickoff") < 0.5 else "team_b"

        # Build flat player_id → PlayerConfig map across both teams.
        # MatchConfig holds players under team_a.players / team_b.players;
        # player_id encodes team + index per ADR-0004.
        team_players: dict[str, Any] = {
            f"team_a_{i}": p for i, p in enumerate(config.team_a.players)
        }
        team_players.update(
            {f"team_b_{i}": p for i, p in enumerate(config.team_b.players)}
        )

        field_width = config.match.field_width
        field_height = config.match.field_height

        # Initialize player states from config and anchors
        # Per ADR-0015 (amended 2026-04-22): each player carries a single
        # last_action_tick for the unified cooldown timer. Initialized to a
        # sentinel "never" (-10**9) so the first action always succeeds.
        _NEVER = -10**9
        players: dict[str, dict[str, Any]] = {}
        for player_id, anchor in anchors.items():
            attr = team_players[player_id]
            team_id = player_id.rsplit("_", 1)[0]  # "team_a_3" → "team_a"
            # Jersey number: use config value if set (>0), else auto-assign
            # from roster index+1 (so player_id "team_a_3" → number 4 default).
            number = attr.number if getattr(attr, "number", 0) > 0 else (
                int(player_id.rsplit("_", 1)[1]) + 1
            )
            # Specialised pass/shoot ratings (added 2026-04-23). When the
            # config doesn't set them, fall back to `skill` so old fixtures
            # behave exactly as before. ARE's effective-skill blend then
            # reduces to plain `skill` in those cases.
            passing = attr.passing if attr.passing is not None else attr.skill
            shooting = attr.shooting if attr.shooting is not None else attr.skill
            # Stamina + initial health (added 2026-04-23). `stamina` is the
            # endurance rating; `current_health` starts at the configured
            # max and drains/recovers per ARE drain logic.
            stamina = getattr(attr, "stamina", 10)
            sim_cfg = getattr(config, "simulation", None)
            health_max = getattr(sim_cfg, "health_max", 100.0) if sim_cfg else 100.0
            players[player_id] = {
                "team": team_id,
                "role": attr.role,
                "number": number,
                "position": anchor,
                "formation_position": anchor,
                "has_ball": False,
                "speed": attr.speed,
                "skill": attr.skill,
                "strength": attr.strength,
                "save": attr.save,
                "discipline": attr.discipline,
                "dribbling": attr.dribbling,
                "passing": passing,
                "shooting": shooting,
                "stamina": stamina,
                "current_health": float(health_max),
                "last_action_tick": _NEVER,
            }

        # Store the config so ARE can read the unified cooldown value via
        # `self.gsm.config.simulation.action_cooldown_ticks` (per ADR-0015
        # amended 2026-04-22). Stored before GameState so `self.config` is
        # available even if GameState construction were modified later.
        self.config = config

        # ADR-0022: cache (role_index, role_count) per player so the per-tick
        # phase-zone lookup in build_player_state is O(1). Mirrors the
        # role-group enumeration done by FRS.compute_anchors but stored on the
        # GSM instance for the lifetime of the match (rosters are immutable).
        # Per-tick team_phase is also cached here, refreshed by build_tick_snapshot.
        self._role_meta: dict[str, tuple[int, int]] = {}
        for team_id_str in ("team_a", "team_b"):
            team_cfg = config.team_a if team_id_str == "team_a" else config.team_b
            role_groups: dict[str, list[str]] = {"GK": [], "DEF": [], "MID": [], "FWD": []}
            for i, p in enumerate(team_cfg.players):
                pid = f"{team_id_str}_{i}"
                role_groups[p.role].append(pid)
            for _role, group in role_groups.items():
                count = len(group)
                for idx, pid in enumerate(group):
                    self._role_meta[pid] = (idx, count)
        # Default phase before the first build_tick_snapshot call: both teams
        # in the most conservative state. Defending → defending-zone center
        # matches the legacy static anchor for DEF, so build_player_state
        # called during pre-match diagnostics returns sensible coords.
        self._cached_team_phase: dict[str, str] = {
            "team_a": "defending",
            "team_b": "defending",
        }

        # Create complete game state
        self.state = GameState(
            # Static configuration
            seed=seed,
            tick_rate=tick_rate,
            duration_minutes=duration_minutes,
            total_ticks=total_ticks,
            half_1_end_tick=half_1_end_tick,
            field_width=field_width,
            field_height=field_height,

            # Mutable runtime state
            tick=0,
            phase="PRE_MATCH",
            score={"team_a": 0, "team_b": 0},
            half=1,
            players=players,
            ball={
                "position": (field_width / 2.0, field_height / 2.0),
                "velocity": (0.0, 0.0),
                "carrier_id": None,
                "possession": None,
            },
            field={
                "width": field_width,
                "height": field_height,
                "team_a_goal_x": 0.0,
                "team_b_goal_x": field_width,
                # Vertical goal extents (y-axis), centered on midfield.
                # Width = config.match.goal_height (default 7.32u, real
                # FIFA spec). Was hard-coded 10u before 2026-04-23.
                # Constant across half-time (goal height doesn't mirror).
                "goal_top": field_height / 2.0 + getattr(config.match, "goal_height", 7.32) / 2.0,
                "goal_bottom": field_height / 2.0 - getattr(config.match, "goal_height", 7.32) / 2.0,
            },

            # Internal state
            _anchors=dict(anchors),    # Defensive copy
            _kickoff_team=kickoff_team,
            _last_touching_team=None,
            _pass_landing_zone=None,
        )

    def build_tick_snapshot(self) -> dict[str, Any]:
        """
        Build the published per-tick callback contract — a fresh dict each call.

        ADR-0009 Phase 1: Tick Engine calls this exactly once per tick; the same
        base snapshot is passed to all 10 player callbacks. The Tick Engine
        injects `my_player_id` and `my_team` per player before passing into the
        sandbox; those fields are NOT included in the base snapshot.

        Returns a fresh dict each call (no caching). Nested dicts (`score`,
        `ball`, `field`, and per-player dicts inside `players`) are also rebuilt
        per call so callers cannot mutate internal state. Tuple values
        (positions, velocities) are inherently immutable so they don't need
        rebuilding.

        Returns:
            Dict containing exactly these top-level keys:
                - tick: int — current simulation tick
                - ticks_remaining: int — total_ticks − tick (includes paused phases)
                - match_phase: str — phase as lowercase string
                  ("pre_match" | "kick_off" | "in_play" | "goal_scored"
                   | "half_time" | "full_time")
                - half: int — 1 or 2
                - score: dict[str, int] — {"team_a": N, "team_b": N}
                - ball: dict — position, velocity, carrier_id, possession
                - players: dict[str, dict] — player_id → player state dict
                - field: dict — width, height, team_a_goal_x, team_b_goal_x

        Excluded:
            - Underscore-prefixed internal fields (_anchors, _kickoff_team,
              _last_touching_team, _pass_landing_zone) never leak into snapshot
            - my_player_id / my_team — Tick Engine injects per player
        """
        s = self.state

        # ADR-0022: classify both teams' phases from this tick's ball state and
        # cache the result so the same-tick build_player_state calls reuse it
        # (10 callbacks per tick × 2 teams = same value 5 times per team).
        # Pass each team's CURRENT defending goal x — these swap at halftime
        # via swap_attack_direction, so the classifier stays correct in H2.
        ball_pos = s.ball["position"]
        possession = s.ball.get("possession")
        self._cached_team_phase = {
            "team_a": classify_team_phase(
                "team_a", ball_pos, possession, s.field_width,
                defending_goal_x=s.field["team_a_goal_x"],
            ),
            "team_b": classify_team_phase(
                "team_b", ball_pos, possession, s.field_width,
                defending_goal_x=s.field["team_b_goal_x"],
            ),
        }

        return {
            "tick": s.tick,
            "ticks_remaining": s.total_ticks - s.tick,
            "match_phase": s.phase.lower(),
            "half": s.half,
            "score": dict(s.score),
            "team_phase": dict(self._cached_team_phase),
            "ball": {
                "position": s.ball["position"],
                "velocity": s.ball["velocity"],
                "carrier_id": s.ball["carrier_id"],
                "possession": s.ball["possession"],
            },
            "players": {
                # Inject player_id into each snapshot dict so consumers (ARE,
                # callbacks) can read it without indexing the outer key.
                # Stored pstate intentionally omits player_id; the dict key is
                # authoritative — this is a published-contract convenience only.
                pid: {**dict(pstate), "player_id": pid}
                for pid, pstate in s.players.items()
            },
            "field": dict(s.field),
        }

    def build_player_state(self, player_id: str) -> dict[str, Any]:
        """
        Build the per-player state dict — the second arg passed to decide().

        Returns a fresh dict each call so callers cannot mutate internal state.
        The dict shape is the published callback contract per GSM GDD Rule 5.

        Args:
            player_id: String identifier in format "team_{a|b}_{0-4}" (ADR-0004)

        Returns:
            Dict with these keys:
                - player_id: str — internal identifier (ADR-0004)
                - team: str — "team_a" or "team_b"
                - number: int — jersey number (1-99); for human-friendly display
                - role: str — GK / DEF / MID / FWD
                - position: tuple[float, float] — current (x, y)
                - formation_position: tuple[float, float] — anchor (x, y)
                - has_ball: bool
                - speed, skill, strength, save, discipline, dribbling: int
                - passing, shooting: int — specialised pass / shoot rating
                  (added 2026-04-23). Falls back to `skill` when the config
                  doesn't specify; ARE blends as `(2 * specialised + skill) / 3`.
                - stamina: int — endurance rating (1-20). Drives drain.
                - current_health: float — remaining health (0..health_max).
                  Drains on actions, recovers on Hold / low-speed Move,
                  fully restored at half-time. ARE multiplies pass/shoot/
                  tackle/save effective skill by `health_floor + (1 -
                  health_floor) × current_health/health_max`.
                - cooldown_remaining: int (ticks; 0 = ready) — per ADR-0015 amended
                  2026-04-22. While > 0 the player can only Move or Hold;
                  Pass / Shoot / Tackle / Pickup are all blocked.

        Raises:
            KeyError: If player_id is not present in state
        """
        p = self.state.players[player_id]
        # cooldown_remaining = max(0, last_action_tick + action_cooldown_ticks
        # - current_tick). Reads the configured cooldown via self.config so
        # the LLM can plan around blocked actions instead of discovering them
        # via silent Hold() substitution.
        current_tick = self.state.tick
        sim = getattr(getattr(self, "config", None), "simulation", None)
        cd = getattr(sim, "action_cooldown_ticks", 0) if sim is not None else 0
        if not isinstance(cd, int) or cd <= 0:
            cooldown_remaining = 0
        else:
            last = p.get("last_action_tick", -10**9)
            if not isinstance(last, int):
                cooldown_remaining = 0
            else:
                cooldown_remaining = max(0, last + cd - current_tick)

        # ADR-0022: per-tick dynamic formation_position from the team's
        # current phase zone. The zone center shifts in BOTH dimensions:
        #   x — by team possession state (attacking pushes defenders up)
        #   y — by ball y (compaction toward ball-side, strongest when defending)
        # Falls back to the static initial anchor if role_meta is missing
        # (defensive — should never happen in normal play but keeps legacy
        # unit tests that construct GSM with a single-player roster from
        # breaking).
        team_id = p["team"]
        phase = self._cached_team_phase.get(team_id, "defending")
        meta = self._role_meta.get(player_id)
        if meta is not None:
            role_index, role_count = meta
            ball_y = self.state.ball["position"][1]
            # Read the team's CURRENT defending goal x — this value swaps
            # at halftime (via swap_attack_direction), keeping the dynamic
            # zone correctly oriented for the current half.
            defending_goal_x = self.state.field[f"{team_id}_goal_x"]
            zone = compute_zone_for(
                p["role"], team_id, phase,
                self.state.field_width, self.state.field_height,
                role_index, role_count,
                ball_y=ball_y,
                defending_goal_x=defending_goal_x,
            )
            formation_position = zone["center"]
            formation_zone = {"x": zone["x"], "y": zone["y"]}
        else:
            formation_position = p["formation_position"]
            formation_zone = {
                "x": (formation_position[0], formation_position[0]),
                "y": (formation_position[1], formation_position[1]),
            }

        return {
            "player_id": player_id,
            "team": p["team"],
            "number": p.get("number", 0),
            "role": p["role"],
            "position": p["position"],
            "formation_position": formation_position,
            "formation_zone": formation_zone,
            "formation_zone_phase": phase,
            "has_ball": p["has_ball"],
            "speed": p["speed"],
            "skill": p["skill"],
            "strength": p["strength"],
            "save": p["save"],
            "discipline": p["discipline"],
            "dribbling": p["dribbling"],
            "passing": p.get("passing", p["skill"]),
            "shooting": p.get("shooting", p["skill"]),
            "stamina": p.get("stamina", 10),
            "current_health": p.get("current_health", 100.0),
            "cooldown_remaining": cooldown_remaining,
        }

    @property
    def seed(self) -> int:
        """
        Get the match seed used for deterministic random number generation.

        Returns:
            Integer seed value from MatchConfig
        """
        return self.state.seed

    @property
    def total_ticks(self) -> int:
        """
        Get the total number of ticks for the match.

        Returns:
            Total ticks computed from duration and tick rate
        """
        return self.state.total_ticks

    @property
    def tick(self) -> int:
        """
        Get the current tick number.

        Returns:
            Current simulation tick
        """
        return self.state.tick

    @property
    def half_1_end_tick(self) -> int:
        """Tick at which the first half ends (read by TickEngine for phase transition)."""
        return self.state.half_1_end_tick

    def apply_move(self, player_id: str, new_pos: tuple[float, float]) -> None:
        """Apply a single player's new position. Clamps to field boundaries silently."""
        x, y = new_pos
        clamped_x = max(0.0, min(self.state.field_width, x))
        clamped_y = max(0.0, min(self.state.field_height, y))
        self.state.players[player_id]["position"] = (clamped_x, clamped_y)

    def transfer_possession(
        self, from_id: str | None, to_id: str | None
    ) -> None:
        """Atomic possession transfer. Updates carrier_id, all has_ball flags, possession.

        EC-GSM-03: transfer(None, None) is a no-op (no warning).
        EC-GSM-04: stale from_id is tolerated (transfer applied) with WARNING.
        """
        if from_id is None and to_id is None:
            return  # EC-GSM-03 no-op

        # EC-GSM-04: warn on stale from_id but still apply
        actual_carrier = self.state.ball["carrier_id"]
        if from_id is not None and actual_carrier != from_id:
            logger.warning(
                "transfer_possession: from_id=%s but actual carrier=%s — applying anyway",
                from_id, actual_carrier,
            )

        # Reset all has_ball flags
        for pid in self.state.players:
            self.state.players[pid]["has_ball"] = False

        if to_id is None:
            self.state.ball["carrier_id"] = None
            self.state.ball["possession"] = None
        else:
            self.state.ball["carrier_id"] = to_id
            self.state.players[to_id]["has_ball"] = True
            # Possession derived from new carrier's team
            self.state.ball["possession"] = self.state.players[to_id]["team"]

    def update_ball_position(
        self,
        new_pos: tuple[float, float],
        last_touching_team: str | None = None,
    ) -> None:
        """Set the ball position. Pure setter — no OOB handling.

        The original (pre-2026-04-23) implementation auto-clamped OOB
        positions and awarded possession to the nearest opponent. That
        logic has moved to ARE Phase 7 `_apply_oob_restart` (FIFA Laws
        15-17 throw-in / goal kick / corner). With both layers handling
        OOB, callers that committed a deflected/parried ball position
        sometimes triggered the GSM auto-handler and got a spurious
        possession transfer that conflicted with the ARE restart logic
        (causing the carrier-ball mismatches surfaced in the 10-round
        iteration). Removing the GSM handler makes ARE Phase 7 the
        single source of truth.

        `last_touching_team` is still recorded for use by ARE's restart
        logic via `state._last_touching_team`.
        """
        if last_touching_team is not None:
            self.state._last_touching_team = last_touching_team
        # Field clamping is intentionally NOT done here — ARE Phase 7
        # handles OOB by detecting BPS's `out_of_bounds` flag and routing
        # through `_apply_oob_restart`. Setting an out-of-field value
        # transiently is fine; the restart logic will fix it.
        self.state.ball["position"] = new_pos

    def update_ball_velocity(self, velocity: tuple[float, float]) -> None:
        """Set ball velocity directly. Used by ARE on pass/shoot initiation."""
        self.state.ball["velocity"] = velocity

    def record_goal(self, scoring_team: str) -> None:
        """Increment score for the scoring team. EC-GSM-07: log ERROR if non-IN_PLAY."""
        if self.state.phase != "IN_PLAY":
            logger.error(
                "record_goal called in phase=%s (expected IN_PLAY) — applying score anyway",
                self.state.phase,
            )
        self.state.score[scoring_team] += 1

    def _nearest_player_of_team(
        self, team: str, target: tuple[float, float]
    ) -> str:
        """Returns player_id of nearest player on `team` to `target`.

        Tie-break: ascending player_id string (ADR-0004).
        """
        candidates = [
            (pid, pstate["position"])
            for pid, pstate in self.state.players.items()
            if pstate["team"] == team
        ]
        def dist_sq(pos: tuple[float, float]) -> float:
            return (pos[0] - target[0]) ** 2 + (pos[1] - target[1]) ** 2
        candidates.sort(key=lambda x: (dist_sq(x[1]), x[0]))
        return candidates[0][0]

    def swap_attack_direction(self) -> None:
        """Mirror attack directions at half-time.

        Formula 4: new_anchor_x = field_width − old_anchor_x; y unchanged.
        Applies to: field.team_a_goal_x, field.team_b_goal_x, every player's
        formation_position, and the internal _anchors dict.

        Live `position` values are NOT mirrored — players physically stay where
        they are when the swap fires; subsequent kick-off / reset will place them
        at the new anchors.

        EC-GSM-08: a second consecutive call re-applies the transform (double
        inversion = identity, restoring originals). Log a WARNING.
        """
        # Detect "second call" — track via internal counter
        self._swap_call_count = getattr(self, "_swap_call_count", 0) + 1
        if self._swap_call_count > 1 and self._swap_call_count % 2 == 0:
            logger.warning(
                "swap_attack_direction called %d times — even-call inverts back to original",
                self._swap_call_count,
            )

        fw = self.state.field_width

        # Field goals
        self.state.field["team_a_goal_x"] = fw - self.state.field["team_a_goal_x"]
        self.state.field["team_b_goal_x"] = fw - self.state.field["team_b_goal_x"]

        # Player formation positions
        for pid, pstate in self.state.players.items():
            old_x, y = pstate["formation_position"]
            pstate["formation_position"] = (fw - old_x, y)

        # Internal anchors
        for pid, (old_x, y) in self.state._anchors.items():
            self.state._anchors[pid] = (fw - old_x, y)

    def set_pass_landing_zone(self, pos: tuple[float, float] | None) -> None:
        """Set or clear the pass landing zone.

        ARE calls this on:
        - pass initiation, with the landing coordinates
        - shoot initiation, with None (BPS skips overshoot detection on shots)
        - ball control success, with None (the new carrier no longer 'expects' a landing zone)
        """
        self.state._pass_landing_zone = pos

    # -----------------------------------------------------------------
    # Action cooldown (per ADR-0015 amended 2026-04-22) — single per-player
    # timer. Triggered by any non-trivial action (Pass / Shoot / Tackle /
    # Pickup); blocks all of those for `action_cooldown_ticks`. Move and
    # Hold neither trigger nor are blocked. ARE Phase 3 reads via
    # get_last_action_tick(); ARE Phase 3/7 record via record_action_cooldown().
    # -----------------------------------------------------------------

    def record_action_cooldown(self, player_id: str, tick: int) -> None:
        """Mark this player as having taken a non-trivial action at `tick`.

        Single timer per player — see ADR-0015 (amended 2026-04-22).
        """
        self.state.players[player_id]["last_action_tick"] = tick

    def get_last_action_tick(self, player_id: str) -> int:
        """Return the tick when this player last took a non-trivial action.

        Returns -10**9 if never performed (or if the field is absent — defensive
        for tests that build player dicts manually without the cooldown field).
        """
        return self.state.players[player_id].get("last_action_tick", -10**9)

    def adjust_health(self, player_id: str, delta: float) -> float:
        """Add `delta` (positive or negative) to player's current_health.
        Clamps to [0, health_max]. Returns the new value.

        Added 2026-04-23 for the stamina/health system. ARE calls this
        once per actor per tick after the action is resolved (drain on
        ball actions, recovery on Hold / low-speed Move).
        """
        sim = getattr(self, "config", None)
        sim_cfg = getattr(sim, "simulation", None) if sim else None
        health_max = float(getattr(sim_cfg, "health_max", 100.0)) if sim_cfg else 100.0
        p = self.state.players[player_id]
        new_val = max(0.0, min(health_max, float(p.get("current_health", health_max)) + delta))
        p["current_health"] = new_val
        return new_val

    def restore_all_health(self) -> None:
        """Reset every player's current_health to health_max. Called by the
        tick engine when half-time begins so the second half starts fresh
        (matches real soccer's break)."""
        sim = getattr(self, "config", None)
        sim_cfg = getattr(sim, "simulation", None) if sim else None
        health_max = float(getattr(sim_cfg, "health_max", 100.0)) if sim_cfg else 100.0
        for p in self.state.players.values():
            p["current_health"] = health_max

    def get_pass_landing_zone(self) -> tuple[float, float] | None:
        """Read the current pass landing zone. BPS calls this every tick."""
        return self.state._pass_landing_zone

    def start_match(self) -> None:
        """Transition PRE_MATCH → KICK_OFF; designate kick-off player.

        AC-GSM-11: phase=KICK_OFF, ball at center, players at anchors, kick-off
        player has ball.
        """
        if self.state.phase != "PRE_MATCH":
            logger.error("start_match called in phase=%s (expected PRE_MATCH)", self.state.phase)
            return  # idempotent guard

        self._reset_positions_to_anchors()
        self._reset_ball_to_center()
        self._assign_kickoff_ball(self.state._kickoff_team)
        # Per FIFA Law 8 (added 2026-04-22): override anchor positions to
        # legal kickoff state — kicker at center spot, all other players in
        # their own half AND outside the center circle. Must run AFTER
        # _assign_kickoff_ball so we know who the kicker is.
        self._apply_kickoff_positions(self.state.ball["carrier_id"])
        self.state.phase = "KICK_OFF"

    def set_phase(self, new_phase: Phase) -> None:
        """Transition to new phase. Enforces FULL_TIME terminal + AC-GSM-22 guard."""
        # AC-GSM-15 / AC-GSM-22: once at end-of-match tick, only FULL_TIME is valid
        # CRITICAL: this check MUST run BEFORE the FULL_TIME-terminal guard
        if self.state.tick >= self.state.total_ticks and new_phase != "FULL_TIME":
            logger.error(
                "set_phase(%s) at tick=%d >= total_ticks=%d — clamping to FULL_TIME",
                new_phase, self.state.tick, self.state.total_ticks,
            )
            self.state.phase = "FULL_TIME"
            return

        # Terminal-state guard
        if self.state.phase == "FULL_TIME" and new_phase != "FULL_TIME":
            logger.error("set_phase(%s) after FULL_TIME — refusing", new_phase)
            return

        # Half-counter increment on HALF_TIME → KICK_OFF
        if self.state.phase == "HALF_TIME" and new_phase == "KICK_OFF":
            self.state.half = 2

        self.state.phase = new_phase

    def advance_tick(self) -> None:
        """Increment tick counter. AC-GSM-15: cannot exceed total_ticks."""
        if self.state.tick >= self.state.total_ticks:
            logger.warning(
                "advance_tick called at tick=%d == total_ticks=%d — no-op",
                self.state.tick, self.state.total_ticks,
            )
            return
        self.state.tick += 1

    def get_phase(self) -> Phase:
        return self.state.phase

    def reset_to_kickoff(self, kickoff_team: str) -> None:
        """Reset positions/ball after a goal. Caller (Tick Engine) calls this then
        set_phase('KICK_OFF') to complete the GOAL_SCORED → KICK_OFF transition.

        AC-GSM-13: positions back to anchors; ball at center; conceding team kicks off.
        Story 006 amendment: ALSO clears _pass_landing_zone (in-flight pass invalidated by goal).
        """
        self._reset_positions_to_anchors()
        self._reset_ball_to_center()
        self._assign_kickoff_ball(kickoff_team)
        # Per FIFA Law 8 (added 2026-04-22): see start_match comment.
        self._apply_kickoff_positions(self.state.ball["carrier_id"])
        self.state._pass_landing_zone = None  # ← Story 006 amendment

    # Internal helpers
    def _reset_positions_to_anchors(self) -> None:
        for pid, anchor in self.state._anchors.items():
            self.state.players[pid]["position"] = anchor
            self.state.players[pid]["formation_position"] = anchor
            self.state.players[pid]["has_ball"] = False

    def _reset_ball_to_center(self) -> None:
        self.state.ball["position"] = (
            self.state.field_width / 2.0,
            self.state.field_height / 2.0,
        )
        self.state.ball["velocity"] = (0.0, 0.0)
        self.state.ball["carrier_id"] = None
        self.state.ball["possession"] = None

    def _assign_kickoff_ball(self, kickoff_team: str) -> None:
        """Pick the kick-off player and give them the ball.

        Per FIFA Law 8: GK never takes kickoff. We pick the non-GK player
        whose formation anchor x is closest to the field center (typically
        the central midfielder), with lexicographic player_id as deterministic
        tie-break. _apply_kickoff_positions then snaps them to the center spot.
        Falls back to the lowest-id team member if the team has only a GK
        (malformed config — match will still proceed).
        """
        center_x = self.state.field_width / 2.0
        candidates = [
            (abs(pstate["formation_position"][0] - center_x), pid)
            for pid, pstate in self.state.players.items()
            if pstate["team"] == kickoff_team and pstate["role"] != "GK"
        ]
        if candidates:
            candidates.sort(key=lambda c: (c[0], c[1]))
            kickoff_player = candidates[0][1]
        else:
            fallback = sorted(
                pid for pid, pstate in self.state.players.items()
                if pstate["team"] == kickoff_team
            )
            if not fallback:
                return  # team is empty — shouldn't happen for valid configs
            kickoff_player = fallback[0]
        self.transfer_possession(None, kickoff_player)

    def _apply_kickoff_positions(self, kicker_id: str | None) -> None:
        """Per FIFA Law 8: snap players into legal kickoff positions.

        - Kicker is placed at the center spot.
        - Every other player is placed within their own half (the side of the
          halfway line their goal is on) AND outside the center circle
          (radius = 9.15% of field width — the FIFA-spec 9.15m on a 100m field).

        Each non-kicker is moved minimally:
          1. Start from the player's formation anchor.
          2. Clamp x into the player's own half (±0.5u margin from the line).
          3. If the result is still inside the center circle, push x further
             outward (along their own-half direction) to land exactly on the
             circle boundary at the same y.

        Called from start_match, reset_to_kickoff, and the Tick Engine's
        kickoff setup. No-op if `kicker_id` is None or the GSM state isn't a
        real dict (mock-based unit tests).
        """
        if kicker_id is None:
            return
        if not isinstance(self.state.players, dict) or not isinstance(self.state.field, dict):
            return  # mock GSM — skip silently so unit tests can still wire things

        fw = self.state.field_width
        fh = self.state.field_height
        center_x = fw / 2.0
        center_y = fh / 2.0
        # FIFA Law 8: center circle radius is 9.15m (10 yards). On our 100m
        # field that's 9.15u; scaling by field_width keeps the rule consistent
        # if the configured field is non-100m.
        circle_r = fw * 0.0915
        margin = 0.5  # keep non-kickers off the literal halfway line

        for pid, pstate in self.state.players.items():
            if pid == kicker_id:
                pstate["position"] = (center_x, center_y)
                continue
            # Determine this team's "own half" by which side their goal is on.
            # team_*_goal_x swaps at halftime, so reading the live field dict
            # automatically respects the current attack direction.
            team_id = pstate["team"]
            team_goal_x = self.state.field.get(f"{team_id}_goal_x", 0.0)
            own_half_low = team_goal_x < center_x

            ax, ay = pstate["formation_position"]
            # Step 1: clamp x into own half.
            if own_half_low:
                x = min(ax, center_x - margin)
            else:
                x = max(ax, center_x + margin)

            # Step 2: if (x, ay) is inside the center circle, push x further
            # outward so the player lands on the circle boundary at y = ay.
            dx = x - center_x
            dy = ay - center_y
            if dx * dx + dy * dy < circle_r * circle_r:
                # Solve (x' - center_x)^2 + dy^2 = circle_r^2 for x'.
                # If dy alone exceeds the radius, dx already does too — fall
                # back to a small offset (shouldn't happen for typical anchors).
                dy_sq = dy * dy
                if dy_sq < circle_r * circle_r:
                    x_offset = (circle_r * circle_r - dy_sq) ** 0.5
                else:
                    x_offset = circle_r
                x = center_x - x_offset if own_half_low else center_x + x_offset

            # Final clamp to field bounds (defensive; shouldn't be needed).
            x = max(0.0, min(fw, x))
            y = max(0.0, min(fh, ay))
            pstate["position"] = (x, y)