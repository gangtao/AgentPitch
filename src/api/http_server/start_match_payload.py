"""Pydantic model for POST /api/matches request body validation."""
from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class StartMatchPayload(BaseModel):
    """Validates the request body for POST /api/matches endpoint.

    All fields validated according to the Matches Start sub-view
    requirements from design/ux/match.md.
    """
    model_config = ConfigDict(frozen=True)

    config_name: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]{1,64}$",
        description="Name of the match configuration file (without .yaml extension)"
    )
    strategy_a: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]{1,64}$",
        description="Name of Team A's strategy file (without .py extension)"
    )
    strategy_b: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]{1,64}$",
        description="Name of Team B's strategy file (without .py extension)"
    )
    match_id: str = Field(
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9_-]{1,128}$",
        description="Unique identifier for this match run"
    )
    seed_override: Optional[int] = Field(
        None,
        ge=0,
        le=2147483647,
        description="Optional seed override; if None, uses config's seed"
    )