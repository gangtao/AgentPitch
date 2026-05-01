"""Pydantic models for match-config HTTP validation per ADR-0019.

API-layer-local; do NOT import these from src/foundation. The constraints
mirror config_models.py field constraints but live independently here so
the API layer satisfies ADR-0006 import isolation.
"""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class PlayerPayload(BaseModel):
    # populate_by_name lets the schema accept legacy YAMLs that still spell
    # `save` as `save_reach` (the previous API field name). New saves write
    # the canonical `save` so the YAML naturally migrates on next edit.
    model_config = ConfigDict(frozen=True, populate_by_name=True)
    role: Literal["GK", "DEF", "MID", "FWD"]
    speed: int = Field(ge=1, le=20)
    skill: int = Field(ge=1, le=20)
    strength: int = Field(ge=1, le=20)
    discipline: int = Field(ge=1, le=20, default=10)
    dribbling: int = Field(ge=1, le=20, default=10)
    # `save` is GK-only. Constraints mirror the engine's PlayerConfig.save
    # (ge=0 — non-GK rows are 0). `validation_alias` accepts both `save`
    # (canonical) and `save_reach` (legacy) on incoming YAML/JSON.
    save: Optional[int] = Field(
        default=None, ge=0, le=20,
        validation_alias=AliasChoices("save", "save_reach"),
    )
    passing: Optional[int] = Field(ge=1, le=20, default=None)
    shooting: Optional[int] = Field(ge=1, le=20, default=None)
    stamina: int = Field(ge=1, le=20, default=10)


class TeamPayload(BaseModel):
    model_config = ConfigDict(frozen=True)
    players: list[PlayerPayload] = Field(min_length=5, max_length=11)


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


class OutputSection(BaseModel):
    model_config = ConfigDict(frozen=True)
    log_dir: str = Field(min_length=1)


class MatchConfigPayload(BaseModel):
    """Root payload for PUT /api/config/match/<name>.

    Schema is post-ADR-0021: NO llm_provider / llm_model fields anywhere.

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
    team_a: TeamPayload
    team_b: TeamPayload