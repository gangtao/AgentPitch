"""Pydantic model for POST /api/arena request body validation."""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class StartSeriesPayload(BaseModel):
    """Validates the request body for POST /api/arena endpoint.

    Starts a new Arena series by running N matches back-to-back via PMEP
    (post-match evolution pipeline). Only LLM-mode seasons evolve strategies
    between matches; baseline runs stay static.
    """
    model_config = ConfigDict(frozen=True, strict=True)

    config_name: str
    """Name of a saved match config (without .yaml extension), e.g. 'match_11v11'."""

    format: str
    """Series length: '3-match' or '5-match'."""

    team_a_provider: Optional[str] = None
    """LLM provider for Team A (e.g. 'openai', 'anthropic'). None = use global LLM config."""

    team_a_model: Optional[str] = None
    """LLM model for Team A (e.g. 'gpt-4o'). None = use global LLM config."""

    team_b_provider: Optional[str] = None
    """LLM provider for Team B. None = use global LLM config."""

    team_b_model: Optional[str] = None
    """LLM model for Team B. None = use global LLM config."""

    team_a_language: Optional[str] = None
    """Strategy language for Team A CGP generation: 'python', 'javascript', or 'rust'. None = python."""

    team_b_language: Optional[str] = None
    """Strategy language for Team B CGP generation: 'python', 'javascript', or 'rust'. None = python."""

    @field_validator("team_a_language", "team_b_language")
    @classmethod
    def _validate_language(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in {"python", "javascript", "rust"}:
            raise ValueError(f"language must be 'python', 'javascript', or 'rust', got {v!r}")
        return v

    @field_validator("format")
    @classmethod
    def _validate_format(cls, v: str) -> str:
        allowed = {"3-match", "5-match"}
        if v not in allowed:
            raise ValueError(f"format must be one of {sorted(allowed)}, got {v!r}")
        return v
