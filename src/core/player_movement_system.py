# src/core/player_movement_system.py

from __future__ import annotations
import math

# Single source of truth for the snap formula lives in FRS — re-exported here
# for callers that import from PMS. Per ADR-0013: discipline is a soft
# preference; previously this module also defined its own copy of the formula
# (drift risk), now it imports the canonical one.
from src.foundation.formation_and_role_system import compute_snap_force

# Field constants (defaults; loaded from config in production)
FIELD_WIDTH = 100.0
FIELD_HEIGHT = 60.0

# Numerical safety threshold for near-zero direction vectors (EC-PMS-01)
_DIRECTION_EPSILON = 1e-6

# Per ADR-0013 amendment (2026-04-22): snap is a passive drift force —
# applies only when the player is "idle". A Move action with speed_ratio
# at or above this threshold counts as ACTIVE intent and bypasses snap.
# Carriers (has_ball=True) always bypass snap regardless of speed.
ACTIVE_SPEED_THRESHOLD = 0.5

# Real-world speed calibration (per ADR-0014, 2026-04-22).
# Field is interpreted as 100m wide. At tick_rate=10/s, max player speed
# (attribute=20) maps to 10 m/s = 1 unit/tick (Olympic-sprinter range).
# Formula: move_dist_per_tick = speed_ratio * player_speed * MOVE_UNIT_PER_TICK.
# Assumes tick_rate=10. If ever made variable, this should become tick_rate-aware.
MOVE_UNIT_PER_TICK = 0.05


def compute_move_result(
    current_pos: tuple[float, float],
    action: dict,
    player_speed: int,
    field_width: float = FIELD_WIDTH,
    field_height: float = FIELD_HEIGHT,
) -> tuple[float, float]:
    """Compute the post-movement position before snap.

    Implements GDD Formula 1: move_dist = clamp(speed_ratio, 0, 1) * player.speed,
    move_result = current_pos + normalize(dx, dy) * move_dist, clamped to field bounds.

    Args:
        current_pos: player's current (x, y) position.
        action: action dict with at least "type" ("move" or "hold"). For "move",
                also contains "dx", "dy" (direction vector), "speed" (speed ratio 0-1).
        player_speed: player's speed attribute (1-20).
        field_width / field_height: pitch dimensions for boundary clamp.

    Returns:
        move_result tuple (x, y) — within field bounds.
    """
    # Hold() pass-through (Rule 5)
    if action.get("type") != "move":
        return current_pos

    dx = action.get("dx", 0.0)
    dy = action.get("dy", 0.0)
    speed_ratio = action.get("speed", 0.0)

    # EC-PMS-01: near-zero direction vector → no movement
    magnitude = math.sqrt(dx * dx + dy * dy)
    if magnitude < _DIRECTION_EPSILON:
        return current_pos

    # AC-PMS-02: clamp speed_ratio to [0, 1] as internal safety net
    clamped_ratio = max(0.0, min(1.0, speed_ratio))

    # Formula 1 (per ADR-0014): move_dist = clamp(speed_ratio, 0, 1) * player.speed * MOVE_UNIT_PER_TICK
    # MOVE_UNIT_PER_TICK = 0.05 calibrates so that at tick_rate=10, max speed=20
    # → 1 unit/tick → 10 m/s (real Olympic-sprinter top speed).
    move_dist = clamped_ratio * player_speed * MOVE_UNIT_PER_TICK

    # Normalize direction
    nx = dx / magnitude
    ny = dy / magnitude

    # Apply movement
    new_x = current_pos[0] + nx * move_dist
    new_y = current_pos[1] + ny * move_dist

    # AC-PMS-03: post-movement boundary clamp (functional)
    clamped_x = max(0.0, min(field_width, new_x))
    clamped_y = max(0.0, min(field_height, new_y))

    return (clamped_x, clamped_y)


# Tuning knob (default; loaded from config in production)
DRIBBLE_RANGE = 1.5
_DRIBBLE_RANGE_SQ = DRIBBLE_RANGE * DRIBBLE_RANGE  # squared, recomputed per module load


def detect_dribble_target(
    final_pos: tuple[float, float],
    player_state: dict,
    action: dict,
    game_state_snapshot: dict,
    dribble_range: float = DRIBBLE_RANGE,
) -> str | None:
    """Detect dribble contest eligibility — return target opponent's player_id or None.

    Implements GDD Formula 4: contest fires iff
    (action.type == "move") AND (player_state["has_ball"]) AND
    (at least one opponent within DRIBBLE_RANGE of final_pos).

    Tie-break (EC-PMS-08): ascending lexicographic player_id (ADR-0004).
    Distance comparison: squared Euclidean — no sqrt.

    Args:
        final_pos: ball carrier's POST-SNAP position (Story 003 ensures ordering).
        player_state: includes "has_ball" and "team".
        action: action dict; only "move" actions can trigger contests.
        game_state_snapshot: includes "players" dict with all 10 player positions/teams.
        dribble_range: contest radius (default DRIBBLE_RANGE=1.5).

    Returns:
        Opponent player_id with minimum squared distance, or None if no contest.
    """
    # Condition 1: action was Move (not Hold)
    if action.get("type") != "move":
        return None

    # Condition 2: player has the ball
    if not player_state.get("has_ball"):
        return None

    # Condition 3: at least one opponent within DRIBBLE_RANGE
    own_team = player_state.get("team")
    range_sq = dribble_range * dribble_range

    candidates = []  # list of (squared_distance, opponent_player_id)
    for opp_pid, opp_state in game_state_snapshot.get("players", {}).items():
        if opp_state.get("team") == own_team:
            continue  # skip same-team players
        opp_pos = opp_state.get("position")
        if opp_pos is None:
            continue
        dx = opp_pos[0] - final_pos[0]
        dy = opp_pos[1] - final_pos[1]
        dist_sq = dx * dx + dy * dy
        if dist_sq < range_sq:
            candidates.append((dist_sq, opp_pid))

    if not candidates:
        return None

    # Sort by (squared_distance, player_id) — lexicographic player_id tie-break (EC-PMS-08)
    candidates.sort(key=lambda c: (c[0], c[1]))
    return candidates[0][1]


def apply_snap(
    move_result: tuple[float, float],
    anchor_pos: tuple[float, float],
    snap_force: float,
    field_width: float = FIELD_WIDTH,
    field_height: float = FIELD_HEIGHT,
) -> tuple[float, float]:
    """Formula 3: final_pos = (1 - snap_force) * move_result + snap_force * anchor_pos.

    Post-snap boundary clamp is a safety net (snapping toward an interior anchor
    from a valid move_result cannot normally produce out-of-bounds final_pos).
    """
    final_x = (1.0 - snap_force) * move_result[0] + snap_force * anchor_pos[0]
    final_y = (1.0 - snap_force) * move_result[1] + snap_force * anchor_pos[1]

    # Safety-net clamp (Rule 6)
    final_x = max(0.0, min(field_width, final_x))
    final_y = max(0.0, min(field_height, final_y))

    return (final_x, final_y)


def resolve_movement(
    player_id: str,
    action: dict,
    player_state: dict,
    game_state_snapshot: dict,
    field_width: float = FIELD_WIDTH,
    field_height: float = FIELD_HEIGHT,
    dribble_range: float = DRIBBLE_RANGE,
    snap_enabled: bool = True,
) -> tuple[tuple[float, float], str | None]:
    """Public PMS entry point. Composes movement + snap + dribble detection.

    Per ADR-0009 compute-all-then-commit: this function reads from the snapshot
    and returns positions; ARE commits via gsm.apply_move() after collecting all
    10 players' results.

    Args:
        player_id: the acting player's id (for documentation; not used in computation
                   except as input to dribble detection's tie-break).
        action: the validated action dict.
        player_state: dict with "position", "formation_position", "speed",
                      "discipline", "has_ball", "team".
        game_state_snapshot: dict with "players" subdict (all 10 players' positions/teams).
        field_width / field_height / dribble_range: tuning knobs (defaults from module).

    Returns:
        (final_pos, dribble_target) per GDD Rule 7.

    Determinism: pure function — same inputs always produce same output.
    """
    # Step 1: compute movement (Formula 1)
    current_pos = player_state["position"]
    player_speed = player_state["speed"]
    move_result = compute_move_result(
        current_pos, action, player_speed, field_width, field_height
    )

    # Step 2: apply snap (Formulas 2 + 3) — but ONLY when the player is "idle".
    # Per ADR-0013 amendment (2026-04-22): snap is a passive drift force.
    # Active intent — a Move at speed_ratio >= ACTIVE_SPEED_THRESHOLD or any
    # carrier action — bypasses snap. This fixes the "stuck-on-equilibrium"
    # pathology where intent toward a loose ball was cancelled tick-for-tick
    # by anchor pull on the opposite side. Real soccer: a player chasing a
    # ball doesn't get magically yanked back to formation; only a player
    # passively jogging back drifts toward their position.
    #
    # ADR-0022 amendment d (2026-04-25): snap_enabled=False short-circuits
    # this entire step — the strategy fully owns positioning when off.
    is_carrier = bool(player_state.get("has_ball", False))
    is_active_move = (
        action.get("type") == "move"
        and max(0.0, min(1.0, action.get("speed", 0.0))) >= ACTIVE_SPEED_THRESHOLD
    )
    if (not snap_enabled) or is_carrier or is_active_move:
        # Snap disabled, OR active intent: intent fully honored (modulo PMS
        # field clamp, which already happened in compute_move_result).
        final_pos = move_result
    else:
        # Idle / passive: drift toward formation anchor per the soft-preference
        # cap (max 0.20 per ADR-0013).
        anchor_pos = player_state["formation_position"]
        discipline = player_state["discipline"]
        snap_force = compute_snap_force(discipline)
        final_pos = apply_snap(move_result, anchor_pos, snap_force, field_width, field_height)

    # Step 3: detect dribble target (Formula 4) — uses POST-SNAP final_pos (EC-PMS-06)
    dribble_target = detect_dribble_target(
        final_pos, player_state, action, game_state_snapshot, dribble_range
    )

    return (final_pos, dribble_target)