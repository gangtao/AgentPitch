"""
Formation & Role System for Agent Pitch soccer simulation.

This module implements the static formation anchoring system that computes
home positions for all players based on their roles. Each player has a
formation anchor (x, y) that acts as their home zone on the field.

Key components:
- Role-based longitudinal (x) anchor zones
- Team mirroring (Team B attacks opposite direction)
- Lateral (y) distribution formula for role groups
- Advisory warnings for unusual formations

TR-FRS-001, TR-FRS-002, TR-FRS-004, TR-FRS-005
"""

from __future__ import annotations

import logging
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from src.foundation.config_models import MatchConfig


# Module-level constants (UPPER_SNAKE_CASE per technical-preferences.md)
GK_ANCHOR_X: float = 8.0
DEF_ANCHOR_X: float = 25.0
MID_ANCHOR_X: float = 50.0
FWD_ANCHOR_X: float = 75.0

# Aggregated table (TR-FRS-001) — keyed by role for Team A's attack direction
FORMATION_ANCHORS: dict[str, float] = {
    "GK": GK_ANCHOR_X,
    "DEF": DEF_ANCHOR_X,
    "MID": MID_ANCHOR_X,
    "FWD": FWD_ANCHOR_X,
}

# Snap force constants for discipline conversion (TR-FRS-003).
# Soft-preference design per ADR-0013 (2026-04-22): discipline is a
# preference on top of the LLM's intended motion, not a force that overrides it.
# Even at max discipline=20 the snap accounts for only 20% of final motion;
# the LLM's Move() retains ≥80% of its intent.
SNAP_FORCE_CAP: float = 0.20
SNAP_FORCE_DIVISOR: float = 100.0


def get_anchor(role: Literal["GK", "DEF", "MID", "FWD"], team_id: str, field_width: float) -> float:
    """Return the longitudinal (x) anchor for a role on a given team.

    Team A attacks toward x=field_width; Team B attacks toward x=0 — Team B's
    anchor is mirrored: ``field_width - team_a_anchor``.

    Note: MID at x=50 with field_width=100 mirrors to x=50 (same value).
    This is correct per AC-2 — MID centerline does NOT mirror.

    Args:
        role: Player role (GK, DEF, MID, FWD)
        team_id: Team identifier ("team_a" or "team_b")
        field_width: Field width from match configuration

    Returns:
        Longitudinal anchor x-coordinate for the role/team combination

    TR-FRS-002.
    """
    base_x = FORMATION_ANCHORS[role]
    return base_x if team_id == "team_a" else field_width - base_x


def compute_anchors(config: MatchConfig) -> dict[str, tuple[float, float]]:
    """Compute the static formation anchor for every player in the match.

    Runs once at match initialization (called by GSM before any tick executes).
    Returns a dict keyed by ``player_id`` ("team_a_0", "team_b_3", ...) with
    ``(x, y)`` anchor tuples. Anchors are never mutated after this call
    (TR-FRS-004).

    Algorithm:
    1. For each team, group players by role preserving config-file order
    2. For each role group, compute anchor_x via get_anchor()
    3. For each role group of size N, distribute anchor_y as:
       field_height × (i + 1) / (N + 1) for i = 0 .. N-1
    4. Log advisory warnings for non-GK roles with N == 0 or N >= 4

    Args:
        config: Validated MatchConfig from the Configuration System.

    Returns:
        Mapping ``{player_id: (anchor_x, anchor_y)}`` for all 10 players.
        Y-distribution emerges implicitly from config-file order within
        each role group (TR-FRS-005).

    Side effects:
        Logs advisory warnings for 0 or 4+ non-GK role counts (per FRS
        Rule 8). Match proceeds regardless.
    """
    logger = logging.getLogger(__name__)
    anchors: dict[str, tuple[float, float]] = {}

    field_width = config.match.field_width
    field_height = config.match.field_height

    # Process both teams
    for team_id in ["team_a", "team_b"]:
        team_config = config.team_a if team_id == "team_a" else config.team_b

        # Group players by role, preserving config-file order
        role_groups: dict[str, list[tuple[int, str]]] = {"GK": [], "DEF": [], "MID": [], "FWD": []}
        for i, player in enumerate(team_config.players):
            role_groups[player.role].append((i, player.player_id))

        # Process each role group
        for role, players_in_role in role_groups.items():
            N = len(players_in_role)

            # Log advisory warnings for unusual formations
            if role == "GK" and N != 1:
                logger.warning(f"WARNING: {team_id} has {N} GK — exactly 1 required. Match will proceed.")
            elif role != "GK" and N == 0:
                logger.warning(f"WARNING: {team_id} has 0 {role} — {role.lower()} zone unoccupied. Match will proceed.")
            elif role != "GK" and N >= 4:
                logger.warning(f"WARNING: {team_id} has {N} {role} — formation may be unbalanced. Match will proceed.")

            # Skip empty role groups
            if N == 0:
                continue

            # Compute anchor_x for this role/team
            anchor_x = get_anchor(role, team_id, field_width)  # type: ignore

            # Distribute anchor_y values using the formula
            for i, (_, player_id) in enumerate(players_in_role):
                anchor_y = field_height * (i + 1) / (N + 1)
                anchors[player_id] = (anchor_x, anchor_y)

    return anchors


def compute_snap_force(discipline: int) -> float:
    """Convert a player's discipline attribute into a per-tick snap force.

    The snap force is the fraction of the formation anchor pull applied per
    tick by the Player Movement System: ``final_pos = (1 - snap_force) *
    move_result + snap_force * anchor_pos``.

    Soft-preference semantics per ADR-0013: with cap=0.20 and divisor=100, even
    at discipline=20 the snap contributes only 20% to final motion. The
    LLM's Move() retains ≥80% of its intent. discipline distinguishes
    players' tendency to drift toward formation when intent is weak/absent,
    but does NOT override strong intent (e.g. chasing a loose ball).

    Args:
        discipline: Player attribute, integer in [1, 20].

    Returns:
        Snap force in [0.01, 0.20]. Pure function, deterministic.

    TR-FRS-003.
    """
    return min(discipline / SNAP_FORCE_DIVISOR, SNAP_FORCE_CAP)


# ── Dynamic phase-aware zones (ADR-0022, 2026-04-25) ────────────────────────
#
# The static FORMATION_ANCHORS above stay as kickoff/home-base positions used
# at match init. The functions below add a second layer: per-tick, the player's
# *runtime* anchor (formation_position) is the center of a phase-aware zone
# that shifts with team possession state. Real soccer teams have a shape that
# moves with the ball; this captures that.
#
# Three phases per team per tick: "attacking" / "transitioning" / "defending".
# See classify_team_phase below for the rules.
#
# PHASE_ZONES is intentionally simple: keyed only by (phase, role). Future
# work could add per-formation overrides (e.g. wingbacks in 3-5-2 have huge
# freedom) but that's out of scope for the first iteration.

PHASE_ATTACKING_THRESHOLD: float = 0.66  # ball in opponent's third (fraction of pitch from own goal)
PHASE_DEFENDING_THRESHOLD: float = 0.34  # ball in own third

# Tuning table — third-pass values (amended 2026-04-25 per user feedback that
# defenders sat in front of opponent forwards instead of goal-side, and that
# forwards never tracked back to defend). Tuple is (x_min_pct, x_max_pct,
# y_spread_pct). x is fraction of field_width for team_a; oriented per the
# team's defending direction in compute_zone_for (handles halftime swap).
#
# Defending row is now realistic for actual defending:
#   DEF center 0.125 — deep enough to be GOAL-SIDE of opp FWD (whose attacking
#                      zone center, mirrored, is at 0.16 of our pitch).
#   MID center 0.30  — covers in front of defenders (was 0.425, too high).
#   FWD center 0.45  — drops into midfield to help press (was 0.58, didn't help).
# Spawn positions are NOT changed — compute_anchors() still produces the
# legacy DEF=25 / MID=50 / FWD=75 baseline used at match init.
PHASE_ZONES: dict[str, dict[str, tuple[float, float, float]]] = {
    "defending": {
        "GK":  (0.03, 0.10, 0.05),  # center 0.065 = 6.5  — tucked closer to goal
        "DEF": (0.05, 0.20, 0.15),  # center 0.125 = 12.5 — GOAL-SIDE of opp FWD
        "MID": (0.20, 0.40, 0.20),  # center 0.30 = 30.0  — covers defenders
        "FWD": (0.35, 0.55, 0.25),  # center 0.45 = 45.0  — tracks back to midfield
    },
    "transitioning": {
        "GK":  (0.06, 0.12, 0.07),
        "DEF": (0.28, 0.45, 0.18),  # center 0.365 = 36.5
        "MID": (0.45, 0.62, 0.22),  # center 0.535 = 53.5
        "FWD": (0.65, 0.80, 0.25),  # center 0.725 = 72.5
    },
    "attacking": {
        "GK":  (0.08, 0.16, 0.10),
        "DEF": (0.42, 0.62, 0.20),  # center 0.52 = 52.0 — INTO OPP HALF
        "MID": (0.58, 0.78, 0.22),  # center 0.68 = 68.0
        "FWD": (0.75, 0.93, 0.20),  # center 0.84 = 84.0 — press high
    },
}

# Ball-side y-compaction. Real soccer teams shift their entire block
# laterally toward the ball — strongly when defending (compactness), weakly
# when attacking (preserve width to stretch opponent). Each player's y_center
# shifts by ``factor * (ball_y - field_height/2)``.
# Bumped 2026-04-25 from (0.40 / 0.20 / 0.05) for more visible lateral movement.
Y_COMPACTION_FACTOR: dict[str, float] = {
    "defending": 0.55,       # strong shift toward ball-side
    "transitioning": 0.30,   # moderate
    "attacking": 0.10,       # slight; mostly preserve width
}


def classify_team_phase(
    team_id: str,
    ball_position: tuple[float, float],
    ball_possession: str | None,
    field_width: float,
    defending_goal_x: float | None = None,
) -> Literal["attacking", "transitioning", "defending"]:
    """Classify a team's current phase from ball position + possession.

    Per ADR-0022, intentionally a coarse 3-state classifier — pure function on
    a single tick's snapshot, no history, no hysteresis (yet). Called once per
    team per tick by GameStateManager.build_tick_snapshot.

    The "distance from own defending goal" normalization makes the rules
    symmetric for both teams AND survives halftime swap (per GSM
    swap_attack_direction): just pass the team's CURRENT defending goal x.

    Args:
        team_id: "team_a" or "team_b".
        ball_position: (x, y) tuple. Only x is used.
        ball_possession: "team_a" / "team_b" / None (loose ball).
        field_width: Pitch width in units.
        defending_goal_x: x-coordinate of the team's CURRENT defending goal
            (read live from field["{team}_goal_x"] each tick — those values
            swap at halftime). When None (default), assume H1 layout
            (team_a defends x=0, team_b defends x=field_width).

    Returns:
        One of "attacking", "transitioning", "defending".
    """
    # Backward-compat default: H1 layout.
    if defending_goal_x is None:
        defending_goal_x = 0.0 if team_id == "team_a" else field_width

    # Symmetric "distance from own defending goal" — works for both halves.
    dist = abs(ball_position[0] - defending_goal_x) / field_width

    have_ball = ball_possession == team_id
    loose = ball_possession is None

    if dist > PHASE_ATTACKING_THRESHOLD:
        # Ball in opponent's third
        return "attacking" if (have_ball or loose) else "transitioning"
    if dist < PHASE_DEFENDING_THRESHOLD:
        # Ball in own third
        return "transitioning" if have_ball else "defending"
    # Ball in middle third
    return "transitioning"


def compute_zone_for(
    role: Literal["GK", "DEF", "MID", "FWD"],
    team_id: str,
    phase: Literal["attacking", "transitioning", "defending"],
    field_width: float,
    field_height: float,
    role_index: int,
    role_count: int,
    ball_y: float | None = None,
    defending_goal_x: float | None = None,
) -> dict[str, tuple[float, float]]:
    """Compute the (role × phase) zone for one player on the pitch.

    The y-component starts from the canonical FRS y-distribution
    (``field_height * (i+1) / (N+1)``) and, when ``ball_y`` is supplied,
    shifts toward the ball by Y_COMPACTION_FACTOR[phase] (real-soccer
    "ball-side compaction" — the whole block slides laterally to the
    ball-side). Then expands by ``y_spread_pct * field_height / 2`` on each
    side. The x-component comes from PHASE_ZONES, oriented per the team's
    defending direction (which swaps at halftime per GSM
    swap_attack_direction).

    Args:
        role: Player role.
        team_id: "team_a" or "team_b".
        phase: Output of classify_team_phase for this team.
        field_width / field_height: Pitch dimensions.
        role_index: 0-based index of this player within their team's role group
                    (preserves config-file order, same as compute_anchors).
        role_count: Total players of this role on this team.
        ball_y: Ball y-coordinate. When provided, y_center shifts toward
                ball.y by Y_COMPACTION_FACTOR[phase]. When None (default),
                y_center is the canonical y-distribution value.
        defending_goal_x: x-coordinate of the team's CURRENT defending goal
                (read live from field["{team}_goal_x"] each tick — those
                values swap at halftime). When None (default), assume H1
                layout (team_a defends x=0, team_b defends x=field_width).

    Returns:
        Dict with keys:
            "x":      (x_min, x_max) — bounding rectangle x-range
            "y":      (y_min, y_max) — bounding rectangle y-range
            "center": (cx, cy)       — center of the rectangle (cy includes
                                       ball-side shift if ball_y was given)
    """
    # Backward-compat default: H1 layout.
    if defending_goal_x is None:
        defending_goal_x = 0.0 if team_id == "team_a" else field_width

    x_min_pct, x_max_pct, y_spread_pct = PHASE_ZONES[phase][role]

    # PHASE_ZONES x_min_pct/x_max_pct are "fraction of pitch from defending
    # goal toward opponent goal". Orient them based on which goal this team
    # is defending — works for both halves (defending_goal_x is the live
    # value, swapped by GSM at halftime).
    if defending_goal_x < field_width / 2.0:
        # Team defends low-x; attacks toward +x
        x_min = x_min_pct * field_width
        x_max = x_max_pct * field_width
    else:
        # Team defends high-x; attacks toward -x → mirror across midfield
        x_min = (1.0 - x_max_pct) * field_width
        x_max = (1.0 - x_min_pct) * field_width

    # y: canonical role-group y-distribution as the BASE center.
    y_base = field_height * (role_index + 1) / (role_count + 1)

    # Ball-side compaction (ADR-0022 amendment 2026-04-25): shift toward ball-y
    # by phase-dependent factor. All players on a team shift by the same
    # offset so their relative spread (formation width) is preserved.
    if ball_y is not None:
        ball_offset = (ball_y - field_height / 2.0) * Y_COMPACTION_FACTOR[phase]
        y_center = y_base + ball_offset
        y_center = max(0.0, min(field_height, y_center))  # clamp to pitch
    else:
        y_center = y_base

    y_half = y_spread_pct * field_height / 2.0
    y_min = max(0.0, y_center - y_half)
    y_max = min(field_height, y_center + y_half)

    cx = (x_min + x_max) / 2.0
    return {
        "x": (x_min, x_max),
        "y": (y_min, y_max),
        "center": (cx, y_center),
    }


def compute_dynamic_anchor(
    role: Literal["GK", "DEF", "MID", "FWD"],
    team_id: str,
    phase: Literal["attacking", "transitioning", "defending"],
    field_width: float,
    field_height: float,
    role_index: int,
    role_count: int,
    ball_y: float | None = None,
    defending_goal_x: float | None = None,
) -> tuple[float, float]:
    """Convenience wrapper: returns the zone center as the per-tick anchor.

    Equivalent to ``compute_zone_for(...)["center"]`` — provided so callers
    that don't need the bounds can avoid the dict allocation.
    """
    return compute_zone_for(
        role, team_id, phase, field_width, field_height, role_index, role_count,
        ball_y=ball_y,
        defending_goal_x=defending_goal_x,
    )["center"]