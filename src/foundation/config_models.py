"""
Configuration models for Agent Pitch soccer simulation.

This module defines the Pydantic v2 models that represent the complete
configuration structure for running a match simulation.
"""

from __future__ import annotations

import warnings
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class PlayerConfig(BaseModel):
    """
    Player configuration model.

    Contains all player attributes used in the configuration system:
    - Identification: player_id, role
    - Physical: speed, skill, strength, save
    - Tactical: discipline, dribbling
    - Specialised (added 2026-04-23): passing, shooting — dominate
      the pass / shoot deviation formulas, while `skill` continues to
      cover tackle / ball-control / save / generic checks.
    """

    # populate_by_name = True so YAML can use `pass` (the natural soccer term)
    # which would otherwise collide with Python's reserved keyword.
    model_config = ConfigDict(frozen=True, strict=True, populate_by_name=True)

    player_id: str
    name: str = Field(default="", max_length=64)
    role: Literal["GK", "DEF", "MID", "FWD"]
    speed: int = Field(ge=1, le=20)
    skill: int = Field(ge=1, le=20)
    strength: int = Field(ge=1, le=20)
    save: int = Field(ge=0, le=20)
    discipline: int = Field(ge=1, le=20)
    dribbling: int = Field(ge=1, le=20)
    # Stamina (added 2026-04-23): 1-20 endurance rating. Drives the
    # health-drain formula `drain = base_cost × (1 - stamina/20)` —
    # stamina=20 burns no health, stamina=1 burns nearly full base
    # cost per action. Defaults to 10 (mid-range) so existing fixtures
    # keep working without migration; one balanced player can still
    # play a full match without falling apart.
    stamina: int = Field(default=10, ge=1, le=20)
    # Specialised pass / shoot ratings. Effective skill in those formulas
    # is `(2 * specialised + skill) / 3` — specialist dominates, skill
    # still cushions. Default `None` means "fall back to skill" so old
    # configs and test fixtures need no migration.
    passing: Optional[int] = Field(default=None, ge=1, le=20, alias="pass")
    shooting: Optional[int] = Field(default=None, ge=1, le=20, alias="shoot")
    # Jersey number for display (per-team unique). 0 = auto-assign from
    # roster index (1-5) at GSM init. Range [0, 99] matches real soccer.
    number: int = Field(default=0, ge=0, le=99)

    @model_validator(mode="after")
    def validate_save_gk_only(self) -> "PlayerConfig":
        """save is GK-only — non-GK players must have save == 0."""
        if self.role != "GK" and self.save != 0:
            raise ValueError(f"{self.player_id}: save is GK-only")
        return self


class TeamConfig(BaseModel):
    """
    Team configuration model.

    Contains team-level configuration and the complete roster of players.

    Note: llm_provider and llm_model fields are deprecated as of ADR-0021.
    LLM settings are now managed globally via the Config UX LLM tab.
    """

    model_config = ConfigDict(frozen=True, strict=True)

    team_id: str = Field(pattern=r"^[a-z0-9_-]+$")
    name: str = Field(min_length=1, max_length=64)
    # Post-ADR-0021: api_key may be empty when llm_provider is None (LLM
    # settings now live in <DATA_HOME>/llm-providers.yaml + .secrets.json).
    # Provider-call sites validate non-empty before actually calling the LLM.
    api_key: str = Field(default="", exclude=True)
    # Roster size: 5 (small-side) up to 11 (full FIFA team). Strict
    # min_length=5 / max_length=11 catches typos at config load.
    players: list[PlayerConfig] = Field(min_length=5, max_length=11)

    # Deprecated fields (ADR-0021 v1 migration: accept with warning, ignore values)
    # Widened from Literal["openai", "anthropic"] to str to support gemini and custom providers
    llm_provider: Optional[str] = Field(default=None, deprecated=True)
    llm_model: Optional[str] = Field(default=None, deprecated=True)

    @model_validator(mode="after")
    def validate_exactly_one_gk(self) -> "TeamConfig":
        """Validate that exactly one player has role GK."""
        gk_count = sum(1 for p in self.players if p.role == "GK")
        if gk_count != 1:
            raise ValueError(f"{gk_count} GK players found — exactly 1 required")
        return self

    @model_validator(mode="after")
    def warn_deprecated_llm_fields(self) -> "TeamConfig":
        """Warn about deprecated llm_provider and llm_model fields."""
        if self.llm_provider is not None or self.llm_model is not None:
            warnings.warn(
                "llm_provider and llm_model in TeamConfig are deprecated. "
                "LLM settings should be configured globally via the Config UX LLM tab.",
                DeprecationWarning,
                stacklevel=2
            )
        return self


class MatchParams(BaseModel):
    """
    Match parameter configuration model.

    Contains simulation parameters that control match execution:
    timing, field dimensions, and random seed.
    """

    model_config = ConfigDict(frozen=True, strict=True)

    seed: int
    tick_rate: int = Field(ge=1, le=60)
    duration_minutes: int = Field(ge=1, le=120)
    field_width: float = Field(gt=0)
    field_height: float = Field(gt=0)
    # Goal mouth y-extent (centered on field_height/2). Default 7.32u
    # matches real FIFA goal width (7.32m on a 100m-wide field).
    # Was hard-coded to 10.0u before 2026-04-23; widened goals made
    # most shots score or get saved, suppressing goal kicks.
    goal_height: float = Field(default=7.32, gt=0, le=20.0)
    match_id: str = ""


class SimulationConfig(BaseModel):
    """
    Simulation parameter configuration model.

    Contains simulation timing, pause duration, and the unified per-player
    action cooldown setting. Per ADR-0015 (amended 2026-04-22): one cooldown
    timer per player, triggered by any non-trivial action (Pass / Shoot /
    Tackle / Pickup). While the timer is active the player can only Move or
    Hold. Move and Hold never trigger cooldown. Set to 0 to disable.
    """

    model_config = ConfigDict(frozen=True, strict=True)

    goal_reset_ticks: int = Field(default=30, ge=1, le=300)
    half_time_pause_ticks: int = Field(default=60, ge=1, le=600)

    # Unified per-player action cooldown (ticks). At tick_rate=10/s, default
    # 10 = 1s. Triggered by Pass / Shoot / Tackle attempts and successful
    # Pickup. Blocks all of those for the window. Move and Hold are unaffected.
    action_cooldown_ticks: int = Field(default=10, ge=0, le=120)

    # Minimum distance between any two players, enforced post-movement-commit
    # in ARE Phase 4 (per ADR-0017). Default 1.0u ≈ 1m on the 100m-wide field
    # — matches real footballer diameter. Set to 0.0 to disable separation.
    min_player_separation: float = Field(default=1.0, ge=0.0, le=5.0)

    # ADR-0018 (2026-04-22): realism-pass tuning knobs.
    # Pass landing deviation max at skill=1; scaled down for higher skill via
    # spread_factor = (1 - skill/20)**0.7. Larger value → more wide passes.
    pass_max_deviation: float = Field(default=8.0, ge=0.0, le=50.0)
    # Shot angular deviation max at skill=1 (radians). 0.30 ≈ 17° — at 25u
    # range that's ~7.5u of y-error potential before skill scaling.
    shot_max_angle: float = Field(default=0.30, ge=0.0, le=1.5)
    # Tackle outcome split: of contests where tackler "wins" (draw < base prob),
    # this fraction become clean takes; the rest become deflections (blocked).
    tackle_clean_share: float = Field(default=0.55, ge=0.0, le=1.0)
    # Floor probability of a deflection even when the tackler "loses" the
    # base contest — physical contact often dislodges the ball.
    tackle_blocked_floor: float = Field(default=0.15, ge=0.0, le=1.0)
    # Random ball speed (u/tick) range for tackle-blocked deflections.
    tackle_block_speed_min: float = Field(default=1.0, ge=0.0, le=5.0)
    tackle_block_speed_max: float = Field(default=3.0, ge=0.0, le=10.0)
    # GK save outcome split: of attempts where save_prob is exceeded, this
    # fraction become clean catches; the rest become parried deflections.
    gk_caught_share: float = Field(default=0.60, ge=0.0, le=1.0)
    # Multiplier applied to incoming ball speed when a save is parried.
    gk_block_speed_factor: float = Field(default=0.4, ge=0.0, le=1.0)

    # Tackle reach (was hard-coded 1.5u inside ARE Phase 6). Bumped to 2.0u
    # 2026-04-22 to match strategy "close-down" gates and to avoid the
    # 1.5u-2.0u dead zone where strategies tried to tackle but the engine
    # rejected as out_of_range. See tech-debt-register entry "Tackle
    # attempts too rare in match flow".
    tackle_range: float = Field(default=2.0, ge=0.0, le=10.0)

    # Settled-possession grace period (added 2026-04-23). After a player's
    # last "ball action" (Pass / Shoot / Tackle / Pickup / Deflection),
    # opponents cannot tackle them for this many ticks. Real soccer's
    # "give the carrier a moment to settle the ball" pattern. Reduces
    # the ~5x-too-high possession churn observed in the 10-round
    # iteration without disabling tackles entirely.
    tackle_settle_grace_ticks: int = Field(default=3, ge=0, le=30)

    # Ball control range per role (added 2026-04-23). GKs use the larger
    # range to model their reach (gloves + diving); outfield players use
    # a tighter range. With both at 1.5u (the previous single value),
    # 11v11 had 4 DEFs absorbing every wide shot before it crossed any
    # line — suppressing all goal kicks and corners. Splitting GK/outfield
    # lets wide shots actually reach end lines.
    ball_control_range_gk: float = Field(default=1.5, ge=0.0, le=10.0)
    ball_control_range_outfield: float = Field(default=1.0, ge=0.0, le=10.0)

    # Shot deflection by a defender in the pickup contest (added 2026-04-23).
    # When a fast-moving loose ball passes through a player's BALL_CONTROL_RANGE
    # but they fail to control (F2 contest fails), they get a second roll
    # for partial deflection. Deflected balls squirt off the defender at a
    # reduced fraction of incoming speed in a random cone. Mainly intended
    # to enable corners (defender deflects shot wide of their own end line).
    # `min_speed`: contest only deflects above this ball speed (slower passes
    # get cleanly picked up via F2). `factor_min/max`: range of speed
    # multipliers applied to the incoming ball speed on deflection.
    shot_deflection_min_speed: float = Field(default=2.0, ge=0.0, le=10.0)
    shot_deflection_speed_factor_min: float = Field(default=0.3, ge=0.0, le=1.0)
    shot_deflection_speed_factor_max: float = Field(default=0.5, ge=0.0, le=1.0)

    # Stamina / health system (added 2026-04-23).
    # Each player carries a `current_health` in [0, health_max] that
    # drains on actions and recovers on Hold / low-speed Move. Half-time
    # restores everyone to full. Formula success rates scale with
    # `health_factor = health_floor + (1 - health_floor) × health/max`,
    # so a tired player still has a non-zero chance.
    health_max: float = Field(default=100.0, gt=0.0, le=1000.0)
    # Multiplier on every action's base health cost. Tuning lever to
    # speed up or slow down exhaustion across a match without changing
    # individual action costs.
    health_drain_factor: float = Field(default=1.0, ge=0.0, le=10.0)
    # Floor on the health-derived skill multiplier. 0.6 means a totally
    # exhausted player still hits 60% of their fresh effectiveness;
    # drop to 0.4 if you want exhaustion to truly break a player.
    health_floor: float = Field(default=0.6, ge=0.0, le=1.0)

    # Formation snap toggle (added 2026-04-25 per ADR-0022 amendment d;
    # default flipped to False on 2026-04-25 per user decision — pure
    # strategy-driven positioning is the new baseline).
    # When True, the Player Movement System pulls idle players softly toward
    # their dynamic phase-aware anchor (cap=0.20, see ADR-0013).
    # When False (default), snap is skipped entirely — final_pos = move_result;
    # the strategy fully owns positioning. formation_position, formation_zone,
    # team_phase, and the discipline attribute are still computed and exposed
    # as informational data; only system-side enforcement is removed.
    formation_snap_enabled: bool = Field(default=False)

    # Offside rule toggle (issue #31, IFAB Law 11). When True, ARE judges
    # offside POSITIONS at the moment of each Pass (x-axis only: strictly
    # inside the opponents' half, strictly nearer their goal line than both
    # the ball and the second-last opponent — level = onside) and awards a
    # free kick to the opposing team where a flagged player first controls
    # the passed ball. No offside from goal kicks, throw-ins, or corners.
    # Default False until baseline calibration confirms sane behavior.
    offside_enabled: bool = Field(default=False)


class OutputConfig(BaseModel):
    """
    Output configuration model.

    Contains settings for match data output and logging.
    """

    model_config = ConfigDict(frozen=True, strict=True)

    log_dir: str = Field(min_length=1)


class MatchConfig(BaseModel):
    """
    Complete match configuration model.

    Root configuration object that contains all settings needed
    to run a complete match simulation.
    """

    model_config = ConfigDict(frozen=True, strict=True)

    match: MatchParams
    simulation: SimulationConfig = Field(default_factory=SimulationConfig)
    output: OutputConfig
    team_a: TeamConfig
    team_b: TeamConfig

    @property
    def teams(self) -> dict[str, TeamConfig]:
        """Return dict of team configurations keyed by team name."""
        return {"team_a": self.team_a, "team_b": self.team_b}

    @property
    def total_ticks(self) -> int:
        """Return total number of simulation ticks for the match."""
        return self.match.tick_rate * self.match.duration_minutes * 60