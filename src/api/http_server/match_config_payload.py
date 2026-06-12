"""Pydantic models for match-config HTTP validation per ADR-0019.

API-layer-local; do NOT import these from src/foundation. The constraints
mirror config_models.py field constraints but live independently here so
the API layer satisfies ADR-0006 import isolation.
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class MatchSection(BaseModel):
    model_config = ConfigDict(frozen=True)
    seed: int = Field(ge=0, le=2**31 - 1)
    tick_rate: int = Field(ge=1, le=60)
    duration_minutes: int = Field(ge=1, le=60)
    field_width: float = Field(ge=50.0, le=200.0)
    field_height: float = Field(ge=30.0, le=120.0)
    # match_id is per-run, not per-config — it's supplied at match-start time
    # (Matches' Start sub-view), not stored in saved configs. Accept optional
    # for backward-compat with old yaml files but never required.
    match_id: str = Field(default="", max_length=64)


class SimulationSection(BaseModel):
    model_config = ConfigDict(frozen=True)
    goal_reset_ticks: int = Field(ge=0, le=300, default=30)
    half_time_pause_ticks: int = Field(ge=0, le=300, default=60)
    action_cooldown_ticks: int = Field(ge=0, le=100, default=10)
    # ADR-0022 amendment d: system-side formation enforcement toggle.
    # Default flipped to False on 2026-04-25 — strategies fully own
    # positioning out of the box; turn on to enable the soft snap helper.
    formation_snap_enabled: bool = Field(default=False)
    # Issue #31: IFAB Law 11 offside toggle (mirrors SimulationConfig).
    # Default flipped to True on 2026-06-11 in lockstep with SimulationConfig.
    offside_enabled: bool = Field(default=True)
    # Issue #38: IFAB Law 12 foul-system toggle (mirrors SimulationConfig).
    fouls_enabled: bool = Field(default=True)


class OutputSection(BaseModel):
    model_config = ConfigDict(frozen=True)
    log_dir: str = Field(min_length=1)


class MatchConfigPayload(BaseModel):
    """Root payload for PUT /api/config/match/<name>.

    Schema is post-ADR-0021: NO llm_provider / llm_model fields anywhere.

    `team_a` / `team_b` are team-id slugs referencing
    ``<data_home>/configs/teams/<slug>.yaml`` (per the team-config split).
    Roster details live entirely in those team YAMLs; the match config only
    points at them. The PUT handler additionally verifies that both slugs
    exist on disk before saving.

    `simulation` and `output` are Optional. Both are runtime concerns supplied
    at match-start time:
      - `simulation` — overlaid from the global Game tab via --global-defaults
      - `output` — overridden by --log-dir (the API always passes it)
    They live in the saved YAML only as defaults for direct CLI use; the UI
    does not edit them. The PUT handler auto-fills `output` with a default
    when the UI omits it, so the saved YAML stays loadable by the engine.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")  # rejects llm_provider as an unknown field
    match: MatchSection
    simulation: Optional[SimulationSection] = None
    output: Optional[OutputSection] = None
    team_a: str = Field(pattern=r"^[a-z0-9_-]+$")
    team_b: str = Field(pattern=r"^[a-z0-9_-]+$")
