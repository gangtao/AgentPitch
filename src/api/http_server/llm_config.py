"""LLM configuration Pydantic models for HTTP validation."""
from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class LLMProviderConfig(BaseModel):
    """LLM provider configuration for HTTP requests."""
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)  # Built-in (openai/anthropic/gemini) or custom provider name
    url: str = Field(min_length=1)
    model: str = Field(min_length=1)
    key: Optional[str] = Field(default=None)  # Optional: omit=no change, null=clear, string=set
    type: Optional[str] = Field(default=None)  # "openai_compatible" for custom; None for built-in


class LLMConfigPayload(BaseModel):
    """Wrapper for PUT /api/config/llm request body."""
    model_config = ConfigDict(frozen=True)

    providers: list[LLMProviderConfig]


class TestConnectionRequest(BaseModel):
    """Request body for POST /api/config/llm/test.

    Optional ``key`` lets the UI test an unsaved key the user just typed,
    without round-tripping through the secrets file. When omitted/empty the
    server falls back to the env-var > secrets-file resolution path
    (ADR-0020 amendment 2026-04-25).

    For custom providers, ``url`` and ``type`` are required to test the connection.
    """
    model_config = ConfigDict(frozen=True)

    provider: str = Field(min_length=1)  # Built-in or custom provider name
    key: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)  # Required for custom providers
    type: Optional[str] = Field(default=None)  # "openai_compatible" for custom