"""Pydantic model for POST /api/cups request body validation."""
from __future__ import annotations
import json
import re
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_STRATEGY_NAME_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class StartCupPayload(BaseModel):
    """Validates the request body for POST /api/cups endpoint.

    Starts a new Strategy Cup tournament by running a single-elimination
    bracket of N teams (4, 8, 16, or 32). Each match uses the specified
    config and strategy files provided in the strategies list.
    """
    model_config = ConfigDict(frozen=True, strict=True)

    name: str
    """Display name for the cup, e.g. 'Spring Cup 2026'. Max 64 chars."""

    config_name: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]{1,64}$",
    )
    """Name of a saved match config (without .yaml extension), e.g. '5v5'."""

    bracket_size: int
    """Number of teams: must be 4, 8, 16, or 32."""

    strategies: list[str]
    """Strategy names (without extension), one per team slot. len must equal bracket_size."""

    @field_validator("bracket_size")
    @classmethod
    def _validate_bracket_size(cls, v: int) -> int:
        if v not in {4, 8, 16, 32}:
            raise ValueError("bracket_size must be 4, 8, 16, or 32")
        return v

    @field_validator("name")
    @classmethod
    def _validate_name(cls, v: str) -> str:
        if not v or len(v) > 64:
            raise ValueError("name must be 1-64 characters")
        return v

    @field_validator("strategies", mode="before")
    @classmethod
    def _validate_strategies(cls, v):
        if not isinstance(v, list):
            raise ValueError("strategies must be a list")
        for name in v:
            if not isinstance(name, str) or not _STRATEGY_NAME_RE.fullmatch(name):
                raise ValueError(
                    f"strategy name {name!r} must match ^[A-Za-z0-9_-]{{1,64}}$"
                )
        return v

    @model_validator(mode="after")
    def _check_strategy_count(self) -> "StartCupPayload":
        if len(self.strategies) != self.bracket_size:
            raise ValueError(
                f"strategies list length {len(self.strategies)} must equal bracket_size {self.bracket_size}"
            )
        return self


def team_names_for_match(match_dir: Path) -> dict:
    """Read meta.json from a match dir and return team display names.

    Returns {"team_a": str, "team_b": str}. Falls back to "Team A" / "Team B"
    when meta.json is missing, unreadable, or lacks the new teams block.
    """
    fallback = {"team_a": "Team A", "team_b": "Team B"}
    meta_path = match_dir / "meta.json"
    if not meta_path.exists():
        return fallback
    try:
        meta = json.loads(meta_path.read_text())
    except Exception:
        return fallback
    teams = meta.get("teams") or {}

    def _name(slot, default):
        td = teams.get(slot)
        if isinstance(td, dict):
            return td.get("name") or default
        # legacy bare-list shape -> no name available
        return default

    return {
        "team_a": _name("team_a", "Team A"),
        "team_b": _name("team_b", "Team B"),
    }
