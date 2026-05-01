"""Ball Physics System (BPS).

Pure-compute module that advances the ball state by exactly one tick. Implements
a constant-velocity model (no acceleration), three-state machine (IN_FLIGHT,
AT_REST, CARRIED), dot-product overshoot detection, and a per-tick ball control
contest using deterministic SHA-256-based draws (hash_01).

BPS owns the canonical ball control formula (BPS F2 supersedes PAM F6). BPS
never mutates GameState — ARE commits the return values per ADR-0009 (phase 5).

Stories:
    001 — advance_ball_position: motion + overshoot + OOB + near-zero guard
    002 — compute_ball_control_prob, did_control_succeed, euclidean_distance
    003 — advance_ball: full public API composing motion + ball control contest
"""

from __future__ import annotations

import math

from src.foundation.simulation_utils import hash_01

# Field constants (defaults; loaded from config in production).
FIELD_WIDTH = 100.0
FIELD_HEIGHT = 60.0

# Ball control contest activation radius (default; loaded from config in production).
BALL_CONTROL_RANGE = 1.5

# Numerical safety threshold for near-zero velocity (EC-BPS-08).
_VELOCITY_EPSILON = 1e-6


# -----------------------------------------------------------------------------
# Story 001 — Ball motion
# -----------------------------------------------------------------------------


def advance_ball_position(
    ball_position: tuple[float, float],
    ball_velocity: tuple[float, float],
    pass_landing_zone: tuple[float, float] | None,
    field_width: float = FIELD_WIDTH,
    field_height: float = FIELD_HEIGHT,
) -> tuple[tuple[float, float], tuple[float, float], bool]:
    """Advance the ball one tick. Pure compute — no GameState mutation.

    Args:
        ball_position: current ball position (x, y).
        ball_velocity: current ball velocity (vx, vy).
        pass_landing_zone: optional landing zone (x, y) — None for shot path.
        field_width: pitch width (default FIELD_WIDTH=100.0).
        field_height: pitch height (default FIELD_HEIGHT=60.0).

    Returns:
        (new_position, new_velocity, out_of_bounds)

    Behavior:
        - AT_REST or near-zero velocity (‖v‖ < 1e-6): no-op, returns (position, (0,0), False).
        - IN_FLIGHT + landing_zone: advance by velocity, dot-product overshoot snap.
          OOB takes priority over overshoot (per AC-BPS-07).
        - IN_FLIGHT + no landing_zone (shot path): advance by velocity only;
          OOB triggers if applicable.
    """
    vx, vy = ball_velocity
    speed_sq = vx * vx + vy * vy

    # AC-BPS-02 + AC-BPS-15: AT_REST or near-zero velocity → no-op.
    if speed_sq < _VELOCITY_EPSILON * _VELOCITY_EPSILON:
        return (ball_position, (0.0, 0.0), False)

    # AC-BPS-03: advance by velocity (constant-velocity model).
    next_x = ball_position[0] + vx
    next_y = ball_position[1] + vy
    next_pos = (next_x, next_y)

    # AC-BPS-06 + AC-BPS-07: OOB check (priority over overshoot).
    oob = (
        next_x < 0.0
        or next_x > field_width
        or next_y < 0.0
        or next_y > field_height
    )
    if oob:
        clamped_x = max(0.0, min(field_width, next_x))
        clamped_y = max(0.0, min(field_height, next_y))
        return ((clamped_x, clamped_y), (0.0, 0.0), True)

    # AC-BPS-04 + AC-BPS-05: dot-product overshoot (only if landing zone set).
    if pass_landing_zone is not None:
        to_lz_x = pass_landing_zone[0] - ball_position[0]
        to_lz_y = pass_landing_zone[1] - ball_position[1]
        dot = vx * to_lz_x + vy * to_lz_y
        if dot <= 0.0:
            # Ball has overshot (or starts at landing zone exactly) → snap.
            return (pass_landing_zone, (0.0, 0.0), False)

    # Normal IN_FLIGHT advance — no overshoot, no OOB.
    return (next_pos, (vx, vy), False)


# -----------------------------------------------------------------------------
# Story 002 — Ball control probability (Formula 2)
# -----------------------------------------------------------------------------


def compute_ball_control_prob(
    player_skill: int,
    distance_to_ball: float,
    ball_speed: float,
    ball_control_range: float = BALL_CONTROL_RANGE,
) -> float:
    """BPS Formula 2 — ball_control_prob = skill / (skill + ball_speed × (1 + distance_ratio)).

    Special case: ball_speed == 0 (AT_REST) → prob = 1.0 (deterministic pickup).

    Args:
        player_skill: PAM skill attribute in [1, 20].
        distance_to_ball: Euclidean distance from player to ball position.
        ball_speed: ‖ball.velocity‖.
        ball_control_range: contest activation radius (default BALL_CONTROL_RANGE=1.5).

    Returns:
        Probability in (0, 1]. AT_REST ball returns 1.0 exactly.
    """
    # AT_REST ball — formula naturally evaluates to 1.0; early-return for clarity.
    if ball_speed == 0.0:
        return 1.0

    # Distance ratio clamped to [0, 1] (per GDD: distance beyond range still capped).
    distance_ratio = min(1.0, max(0.0, distance_to_ball / ball_control_range))

    # F2 formula
    denominator = player_skill + ball_speed * (1.0 + distance_ratio)
    return player_skill / denominator


def did_control_succeed(
    seed: int,
    tick: int,
    player_id: str,
    ball_control_prob: float,
) -> bool:
    """Deterministic ball control roll using hash_01.

    Args:
        seed: match RNG seed.
        tick: current tick counter.
        player_id: contesting player's ID.
        ball_control_prob: F2 result in (0, 1].

    Returns:
        True iff hash_01(seed, tick, player_id, "ball_control") < ball_control_prob.
        Same inputs always produce same output (per AC-BPS-12).
    """
    draw = hash_01(seed, tick, player_id, "ball_control")
    return draw < ball_control_prob


def euclidean_distance(
    pos_a: tuple[float, float],
    pos_b: tuple[float, float],
) -> float:
    """Euclidean distance helper for distance_to_ball in F2."""
    dx = pos_a[0] - pos_b[0]
    dy = pos_a[1] - pos_b[1]
    return math.sqrt(dx * dx + dy * dy)


# -----------------------------------------------------------------------------
# Story 003 — advance_ball orchestration (full public API)
# -----------------------------------------------------------------------------


def advance_ball(
    game_state: dict,
    seed: int,
    tick: int,
    field_width: float = FIELD_WIDTH,
    field_height: float = FIELD_HEIGHT,
    ball_control_range: float = BALL_CONTROL_RANGE,
    excluded_pids: set[str] | None = None,
    # ADR shot-deflection knobs (added 2026-04-23). Defaults match
    # SimulationConfig defaults; ARE passes the live config values.
    deflect_min_speed: float = 2.0,
    deflect_speed_factor_min: float = 0.3,
    deflect_speed_factor_max: float = 0.5,
    # Per-role pickup range (added 2026-04-23). GK keeps the larger
    # value; outfield gets a tighter one. Pass None to fall back to
    # the legacy single `ball_control_range` for both roles.
    range_gk: float | None = None,
    range_outfield: float | None = None,
) -> dict:
    """Public BPS API. Advances ball one tick + ball control contest.

    Composes Story 001 (motion) + Story 002 (ball control probability).

    Args:
        game_state: snapshot dict containing:
            - "ball": dict with "position" (x, y), "velocity" (vx, vy),
              "carrier_id" (str | None), "possession" (str | None).
            - "players": dict[player_id, {position, team, skill}].
            - "_pass_landing_zone": (x, y) | None — private snapshot key set by
              ARE/Tick Engine. NOT in the public snapshot (build_tick_snapshot
              strips this).
        seed: match RNG seed (for hash_01 determinism).
        tick: current tick counter (for hash_01 determinism).
        field_width / field_height / ball_control_range: tuning knobs.
        excluded_pids: optional set of player_ids to skip in the candidate
            scan. Per ADR-0015 amendment (2026-04-22), ARE pre-excludes
            cooldown-active players (and offside-eligible FWDs after a pass)
            so they cannot win the contest — preventing the position-snap
            loop where a rejected winner pinned the ball at their feet.

    Returns:
        {
            "new_position": (x, y),
            "new_velocity": (vx, vy),
            "out_of_bounds": bool,
            "controlled_by": str | None,  # winner's player_id, or None
        }

    BPS is pure compute — does NOT mutate game_state. ARE commits the result.
    """
    ball = game_state["ball"]

    # AC-BPS-01: CARRIED skip — return carrier's position, no motion.
    if ball.get("carrier_id") is not None:
        carrier_id = ball["carrier_id"]
        carrier = game_state["players"].get(carrier_id, {})
        carrier_pos = carrier.get("position", ball["position"])
        return {
            "new_position": carrier_pos,
            "new_velocity": (0.0, 0.0),
            "out_of_bounds": False,
            "controlled_by": carrier_id,
        }

    # Story 001: advance position.
    new_pos, new_vel, oob = advance_ball_position(
        ball["position"],
        ball["velocity"],
        game_state.get("_pass_landing_zone"),
        field_width,
        field_height,
    )

    # AC-BPS-07: OOB priority — no contest this tick.
    if oob:
        return {
            "new_position": new_pos,
            "new_velocity": new_vel,
            "out_of_bounds": True,
            "controlled_by": None,
        }

    # Compute new ball speed for F2 (AT_REST → ball_speed=0 → prob=1.0).
    new_speed = math.sqrt(new_vel[0] ** 2 + new_vel[1] ** 2)

    # NOTE: previously had `if not was_in_flight and new_speed == 0.0:
    # return controlled_by=None` — skipped the contest for a ball that was
    # AT_REST and stayed AT_REST. Removed 2026-04-22 because it created the
    # "stuck loose ball" pathology: a ball that overshot its landing zone
    # and stopped could never be picked up even when players reached
    # within BALL_CONTROL_RANGE on subsequent ticks. The contest is cheap
    # (~10 player distance checks per tick) and at-rest balls deserve
    # collection like any other loose ball.

    # Find candidates within their per-role BALL_CONTROL_RANGE of the new
    # ball position. GK uses a wider range (gloves + diving reach); outfield
    # uses a tighter one. Falling back to the single `ball_control_range`
    # value preserves the legacy behaviour for callers that don't pass
    # the per-role kwargs.
    gk_range = range_gk if range_gk is not None else ball_control_range
    out_range = range_outfield if range_outfield is not None else ball_control_range
    gk_range_sq = gk_range * gk_range
    out_range_sq = out_range * out_range

    excluded = excluded_pids or set()
    candidates: list[tuple[float, str, int, int]] = []
    for pid, pstate in game_state["players"].items():
        if pid in excluded:
            continue
        ppos = pstate.get("position")
        if ppos is None:
            continue
        dx = ppos[0] - new_pos[0]
        dy = ppos[1] - new_pos[1]
        dist_sq = dx * dx + dy * dy
        # Per-role range gate.
        is_gk = pstate.get("role") == "GK"
        eligible_range_sq = gk_range_sq if is_gk else out_range_sq
        if dist_sq <= eligible_range_sq:
            candidates.append((
                dist_sq, pid,
                pstate.get("skill", 1),
                pstate.get("strength", 1),
            ))

    # No candidates → no contest fires.
    if not candidates:
        return {
            "new_position": new_pos,
            "new_velocity": new_vel,
            "out_of_bounds": False,
            "controlled_by": None,
        }

    # AC-BPS-13 (nearest only) + EC-BPS-04 (lexicographic tie-break on player_id).
    candidates.sort(key=lambda c: (c[0], c[1]))
    contest_dist_sq, contest_pid, contest_skill, contest_strength = candidates[0]
    contest_distance = math.sqrt(contest_dist_sq)

    # F2 + hash_01 roll.
    prob = compute_ball_control_prob(
        contest_skill, contest_distance, new_speed, ball_control_range
    )
    success = did_control_succeed(seed, tick, contest_pid, prob)

    if success:
        # Ball stops at the contesting player's position (per GDD Rule 6).
        controller_pos = game_state["players"][contest_pid]["position"]
        return {
            "new_position": controller_pos,
            "new_velocity": (0.0, 0.0),
            "out_of_bounds": False,
            "controlled_by": contest_pid,
        }

    # Contest failed — but on a fast ball, defender may still partially
    # deflect it (added 2026-04-23). Real soccer: a defender often blocks
    # a shot without controlling it. Enables corners (deflected shot wide
    # of own end line) and adds chaos to fast-ball play.
    if new_speed >= deflect_min_speed:
        # Deflection probability: combined skill+strength vs ball speed.
        block_factor = (contest_skill + contest_strength) / 2.0
        deflect_prob = block_factor / (block_factor + new_speed * 4.0)
        deflect_draw = hash_01(seed, tick, contest_pid, "shot_deflect")
        if deflect_draw < deflect_prob:
            # DEFLECTED. Ball squirts off the defender at reduced speed,
            # biased TOWARD the incoming direction (added 2026-04-23).
            # Real soccer: a defender's leg/hip slows the ball but rarely
            # reverses it — the shot's momentum carries it past. So the
            # deflection direction is in a ±60° cone around incoming.
            # This is what produces corners: a defender in front of their
            # own goal deflects an incoming shot, ball keeps going past
            # them toward the end line.
            #
            # The earlier "fully random" cone produced lots of weird
            # bounces (sometimes back across midfield) but never
            # produced corners because direction was uncorrelated with
            # ball trajectory.
            speed_draw = hash_01(seed, tick, contest_pid, "shot_deflect_speed")
            angle_draw = hash_01(seed, tick, contest_pid, "shot_deflect_angle")
            new_ball_speed = new_speed * (
                deflect_speed_factor_min
                + speed_draw * (deflect_speed_factor_max - deflect_speed_factor_min)
            )
            incoming_angle = math.atan2(new_vel[1], new_vel[0])
            # Bias the cone CENTER toward "wide of goal mouth y" — i.e.
            # the side of the field the ball is already on. Real defender
            # blocks tend to deflect the ball outward (around the
            # defender's body), not straight through. Without this bias,
            # the uniform ±60° cone produced ~zero corners across 10
            # rounds of 11v11: deflections continued forward, hit the
            # goal line in the goal mouth, and triggered another save
            # attempt instead of going wide.
            ball_y = new_pos[1]
            goal_center_y = field_height / 2.0
            wide_sign = 1.0 if ball_y >= goal_center_y else -1.0
            WIDE_BIAS = math.pi / 6.0  # 30° toward sideline
            biased_center = incoming_angle + WIDE_BIAS * wide_sign
            # ±60° cone around biased center.
            DEFLECT_CONE_HALF = math.pi / 3.0
            deflect_angle = biased_center + (angle_draw - 0.5) * 2.0 * DEFLECT_CONE_HALF
            new_velocity = (
                math.cos(deflect_angle) * new_ball_speed,
                math.sin(deflect_angle) * new_ball_speed,
            )
            defender_pos = game_state["players"][contest_pid]["position"]
            return {
                "new_position": defender_pos,
                "new_velocity": new_velocity,
                "out_of_bounds": False,
                "controlled_by": None,
                "deflected_by": contest_pid,
            }

    # Contest failed and no deflection — ball continues at next_pos.
    return {
        "new_position": new_pos,
        "new_velocity": new_vel,
        "out_of_bounds": False,
        "controlled_by": None,
    }
