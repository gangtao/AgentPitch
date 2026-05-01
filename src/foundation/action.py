"""
Player Action Classes for Agent Pitch soccer simulation.

This module defines the Action class hierarchy returned by player decide()
callbacks. Each action is an immutable frozen dataclass that the Action
Resolution Engine dispatches via isinstance() checks.

Key components:
- Action: Marker base class for isinstance discrimination
- Move: Move in direction (dx, dy) at speed ratio [0.0, 1.0]
- Pass: Kick ball toward target position with power [1, 20]
- Shoot: Shoot ball at goal with angle and power
- Tackle: Attempt to tackle target player by player_id
- Hold: Stay in current position (universal fallback)

TR-ASCI-001, TR-ASCI-004, TR-ASCI-005
"""

from __future__ import annotations
from dataclasses import dataclass


class Action:
    """Marker base class for all player actions returned from decide().

    Subclasses are immutable frozen dataclasses. The Action Resolution Engine
    dispatches on subclass via isinstance(); no virtual methods are required.
    """
    __slots__ = ()

    @classmethod
    def from_tagged(cls, payload: dict) -> "Action":
        """Construct an Action from a tagged dict like {"type": "Move", "dx": 1.0, ...}.

        Used by non-Python sandboxes (QuickJS, WASM) to normalize callback
        return values into the Action hierarchy. Returns Hold() for any
        unrecognized or malformed payload.
        """
        action_type = payload.get("type")
        try:
            if action_type == "Move":
                return Move(dx=float(payload["dx"]), dy=float(payload["dy"]), speed=float(payload["speed"]))
            if action_type == "Pass":
                tp = payload["target_pos"]
                return Pass(target_pos=(float(tp[0]), float(tp[1])), power=int(payload["power"]))
            if action_type == "Shoot":
                return Shoot(angle=float(payload["angle"]), power=int(payload["power"]))
            if action_type == "Tackle":
                return Tackle(target_player_id=str(payload["target_player_id"]))
            if action_type == "Hold":
                return Hold()
        except (KeyError, TypeError, IndexError, ValueError):
            return Hold()
        return Hold()


@dataclass(frozen=True)
class Move(Action):
    """Move the player in direction (dx, dy) at the given speed ratio.

    Args:
        dx: x-component of direction vector. Magnitude ignored; only direction used.
        dy: y-component of direction vector.
        speed: Speed ratio in [0.0, 1.0]. Clamped at resolution time.
                ARE computes move_dist = clamp(speed, 0, 1) * player.speed.
    """
    dx: float
    dy: float
    speed: float


@dataclass(frozen=True)
class Pass(Action):
    """Ball carrier kicks toward target_pos with the given power.

    Args:
        target_pos: (x, y) field coordinate of pass target.
        power: Pass power in [1, 20]. Capped by player's strength attribute
                at resolution (effective_power = min(power, player.strength)).
    """
    target_pos: tuple[float, float]
    power: int


@dataclass(frozen=True)
class Shoot(Action):
    """Ball carrier shoots at goal.

    Args:
        angle: Degrees relative to attack direction (0 = straight at goal).
        power: Shot power in [1, 20]. Capped by player's strength at resolution.
    """
    angle: float
    power: int


@dataclass(frozen=True)
class Tackle(Action):
    """Attempt to tackle the specified opponent.

    Args:
        target_player_id: Opponent player_id (str, format "{team_id}_{index}",
                            per ADR-0004). NEVER int. Out-of-range or invalid IDs
                            substituted with Hold() at resolution.
    """
    target_player_id: str


@dataclass(frozen=True)
class Hold(Action):
    """Stay in current position.

    With ball: braces against tackles (defender must win strength contest).
    Without ball: no-op. Also the universal fallback action (ADR-0012).
    """
    pass