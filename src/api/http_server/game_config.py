"""
Game Configuration model for Agent Pitch Config UI.

Defines the GameConfig Pydantic model that represents the subset of
simulation parameters that can be tuned through the Game tab interface.
This is a projection of the existing MatchParams and SimulationConfig models,
exposing only the fields that researchers commonly tune.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class GameConfig(BaseModel):
    """
    Game configuration model for Config UI Game tab.

    This is a subset projection of MatchParams + SimulationConfig that exposes
    only the commonly-tuned simulation parameters. Field constraints mirror
    those in the parent models to maintain validation consistency.
    """

    model_config = ConfigDict(frozen=True, strict=True)

    # ── A. Match defaults ──
    # Source: MatchParams.tick_rate. Default 10 matches every real config in
    # the codebase + SimulationConfig.action_cooldown_ticks=10 (designed as
    # "1 second of cooldown at tick_rate=10"). The previous scaffold default
    # of 30 was inconsistent with engine reality.
    tick_rate: int = Field(default=10, ge=1, le=60, description="Simulation ticks per second")

    # Source: MatchParams.duration_minutes
    duration_minutes: int = Field(default=5, ge=1, le=120, description="Match duration in minutes")

    # Source: MatchParams.field_width
    field_width: float = Field(default=100.0, gt=0, le=200, description="Field width in game units")

    # Source: MatchParams.field_height
    field_height: float = Field(default=60.0, gt=0, le=120, description="Field height in game units")

    # Source: MatchParams.goal_height
    goal_height: float = Field(default=7.32, gt=0, le=12, description="Goal mouth height in game units")

    # Source: MatchParams.seed (mapped to default_seed for clarity in Config UI)
    default_seed: int = Field(default=42, description="Default random seed for matches")

    # ── B. Action mechanics ──
    # Source: SimulationConfig.action_cooldown_ticks
    action_cooldown_ticks: int = Field(default=10, ge=0, le=100, description="Cooldown ticks after actions")

    # Source: SimulationConfig.pass_max_deviation
    pass_max_deviation: float = Field(default=8.0, ge=0.0, le=30.0, description="Maximum pass deviation at skill=1")

    # Source: SimulationConfig.shot_max_angle
    shot_max_angle: float = Field(default=0.30, ge=0.0, le=1.0, description="Maximum shot angle deviation (radians)")

    # Source: SimulationConfig.tackle_clean_share
    tackle_clean_share: float = Field(default=0.55, ge=0.0, le=1.0, description="Fraction of successful tackles that are clean")

    # Source: SimulationConfig.tackle_blocked_floor
    tackle_blocked_floor: float = Field(default=0.15, ge=0.0, le=1.0, description="Minimum deflection probability on failed tackles")

    # Source: SimulationConfig.tackle_block_speed_min
    tackle_block_speed_min: float = Field(default=1.0, ge=0.0, le=10.0, description="Minimum deflection speed on blocked tackles")

    # Source: SimulationConfig.tackle_block_speed_max
    tackle_block_speed_max: float = Field(default=3.0, ge=0.0, le=10.0, description="Maximum deflection speed on blocked tackles")

    # Source: SimulationConfig.tackle_range
    tackle_range: float = Field(default=2.0, ge=0.0, le=10.0, description="Maximum tackle reach distance")

    # Source: SimulationConfig.tackle_settle_grace_ticks
    tackle_settle_grace_ticks: int = Field(default=3, ge=0, le=30, description="Grace period ticks after ball actions")

    # ── C. Goalkeeper / ball physics ──
    # Source: SimulationConfig.gk_caught_share
    gk_caught_share: float = Field(default=0.60, ge=0.0, le=1.0, description="Fraction of successful GK saves that are catches")

    # Source: SimulationConfig.gk_block_speed_factor
    gk_block_speed_factor: float = Field(default=0.4, ge=0.0, le=1.0, description="Speed multiplier for GK parries")

    # Source: SimulationConfig.ball_control_range_gk
    ball_control_range_gk: float = Field(default=1.5, ge=0.0, le=5.0, description="Ball control range for goalkeepers")

    # Source: SimulationConfig.ball_control_range_outfield
    ball_control_range_outfield: float = Field(default=1.0, ge=0.0, le=5.0, description="Ball control range for outfield players")

    # Source: SimulationConfig.shot_deflection_min_speed
    shot_deflection_min_speed: float = Field(default=2.0, ge=0.0, le=10.0, description="Minimum speed for shot deflections")

    # Source: SimulationConfig.shot_deflection_speed_factor_min
    shot_deflection_speed_factor_min: float = Field(default=0.3, ge=0.0, le=1.0, description="Minimum speed multiplier for deflections")

    # Source: SimulationConfig.shot_deflection_speed_factor_max
    shot_deflection_speed_factor_max: float = Field(default=0.5, ge=0.0, le=1.0, description="Maximum speed multiplier for deflections")

    # ── D. Stamina / health ──
    # Source: SimulationConfig.health_max
    health_max: float = Field(default=100.0, gt=0.0, le=1000.0, description="Maximum player health/stamina")

    # Source: SimulationConfig.health_drain_factor
    health_drain_factor: float = Field(default=1.0, ge=0.0, le=10.0, description="Global multiplier for health drain")

    # Source: SimulationConfig.health_floor
    health_floor: float = Field(default=0.6, ge=0.0, le=1.0, description="Minimum effectiveness when exhausted")

    # ── E. Match-flow timing ──
    # Source: SimulationConfig.goal_reset_ticks
    goal_reset_ticks: int = Field(default=30, ge=0, le=300, description="Ticks to pause after goals")

    # Source: SimulationConfig.half_time_pause_ticks
    half_time_pause_ticks: int = Field(default=60, ge=0, le=300, description="Ticks to pause at half-time")

    # Source: SimulationConfig.min_player_separation
    min_player_separation: float = Field(default=1.0, ge=0.0, le=5.0, description="Minimum distance between players")

    # ── F. Formation system (ADR-0022 amendment d) ──
    # Source: SimulationConfig.formation_snap_enabled
    # Default flipped to False on 2026-04-25 — strategies fully own
    # positioning out of the box. Turn on to enable the soft snap toward
    # each player's dynamic phase-aware anchor (system-assisted helper).
    formation_snap_enabled: bool = Field(
        default=False,
        description="Enable soft snap toward dynamic formation anchor (ADR-0022)"
    )

    # ── G. Match rules ──
    # Source: SimulationConfig.offside_enabled (issue #31, IFAB Law 11)
    # Default flipped to True on 2026-06-11 in lockstep with SimulationConfig.
    offside_enabled: bool = Field(
        default=True,
        description="Enforce IFAB Law 11 offside (free-kick restart on offence)"
    )