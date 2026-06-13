"""Pydantic models for team-config HTTP validation.

API-layer-local; mirrors src/foundation/config_models TeamConfig constraints
but lives independently here per ADR-0006.
"""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class TeamPlayerPayload(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)
    name: Optional[str] = Field(default=None, max_length=64)
    role: Literal["GK", "DEF", "MID", "FWD"]
    speed: Optional[int] = Field(default=None, ge=1, le=20)
    skill: Optional[int] = Field(default=None, ge=1, le=20)
    strength: Optional[int] = Field(default=None, ge=1, le=20)
    discipline: Optional[int] = Field(default=None, ge=1, le=20)
    dribbling: Optional[int] = Field(default=None, ge=1, le=20)
    save: Optional[int] = Field(
        default=None, ge=0, le=20,
        validation_alias=AliasChoices("save", "save_reach"),
    )
    passing: Optional[int] = Field(default=None, ge=1, le=20)
    shooting: Optional[int] = Field(default=None, ge=1, le=20)
    stamina: Optional[int] = Field(default=None, ge=1, le=20)
    number: Optional[int] = Field(default=None, ge=0, le=99)
    # Issue #38 (IFAB Law 12/14): aggression + penalty-conversion ratings.
    offensive: Optional[int] = Field(default=None, ge=1, le=20)
    penalty: Optional[int] = Field(default=None, ge=1, le=20)


class TeamConfigPayload(BaseModel):
    """Root payload for PUT /api/config/teams/<slug>."""
    model_config = ConfigDict(frozen=True, extra="forbid")
    team_id: str = Field(pattern=r"^[a-z0-9_-]+$")
    name: str = Field(min_length=1, max_length=64)
    players: list[TeamPlayerPayload] = Field(min_length=5, max_length=11)
