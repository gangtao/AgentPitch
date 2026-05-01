"""Pydantic model for POST /api/leagues request body validation."""
from __future__ import annotations
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_STRATEGY_NAME_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class StartLeaguePayload(BaseModel):
    """Validates the request body for POST /api/leagues endpoint.

    Starts a new Strategy League tournament by running a round-robin
    schedule of N teams (even count, 2-16). Each match uses the specified
    config and strategy files.
    """
    model_config = ConfigDict(frozen=True, strict=True)

    name: str
    """Display name for the league. Max 64 chars."""

    config_name: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]{1,64}$",
    )
    """Name of a saved match config (without .yaml extension)."""

    num_rounds: int = 1
    """1 = single round-robin, 2 = double round-robin."""

    strategies: list[str]
    """Strategy names (without extension). Must be even count, 2-16."""

    @field_validator("name")
    @classmethod
    def _validate_name(cls, v: str) -> str:
        if not v or len(v) > 64:
            raise ValueError("name must be 1-64 characters")
        return v

    @field_validator("num_rounds")
    @classmethod
    def _validate_num_rounds(cls, v: int) -> int:
        if v not in (1, 2):
            raise ValueError("num_rounds must be 1 or 2")
        return v

    @field_validator("strategies", mode="before")
    @classmethod
    def _validate_strategies(cls, v):
        for name in v:
            if not _STRATEGY_NAME_RE.fullmatch(name):
                raise ValueError(
                    f"strategy name {name!r} must match ^[A-Za-z0-9_-]{{1,64}}$"
                )
        return v

    @model_validator(mode="after")
    def _check_strategy_constraints(self) -> "StartLeaguePayload":
        n = len(self.strategies)
        if n < 2 or n > 16:
            raise ValueError("strategies must have 2-16 entries")
        if n % 2 != 0:
            raise ValueError("League requires an even number of teams")
        return self
