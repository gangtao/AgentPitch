"""Pydantic models for strategy creation endpoints."""
from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field


class StrategyMetaPayload(BaseModel):
    """Provenance fields the client may attach to POST /api/strategies.

    Mirrors the sidecar schema in ADR-0023 (`src/strategy_library.py`).
    `created_at` and `last_modified_at` are server-stamped — never sent by
    the client.
    """
    model_config = ConfigDict(frozen=True)

    provider: str = Field(default="manual", min_length=1, max_length=64)
    model: str = Field(default="hand-written", min_length=1, max_length=128)
    created_by: Literal["llm", "manual"] = "manual"
    # Required when created_by == "llm". Validation happens at the strategy_library layer.
    prompt: Optional[str] = Field(default=None, max_length=4096)
    template_version: Optional[str] = Field(default=None, max_length=32)
    language: Literal["python", "javascript", "rust"] = "python"
    # Generation performance metrics — sent by the UI after a successful generate call
    generation_latency_ms: Optional[float] = None
    generation_input_tokens: Optional[int] = None
    generation_output_tokens: Optional[int] = None


class StrategyCreatePayload(BaseModel):
    """Payload for POST /api/strategies - create new strategy."""
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    source: Optional[str] = None
    # Optional sidecar metadata. When omitted, server writes a manual sidecar
    # with provider="manual", model="hand-written", created_by="manual".
    meta: Optional[StrategyMetaPayload] = None
    language: Literal["python", "javascript", "rust"] = "python"


class StrategyGeneratePayload(BaseModel):
    """Payload for POST /api/strategies/generate - LLM strategy generation.

    Supports both built-in providers (openai, anthropic, gemini) and custom
    OpenAI-compatible providers (ollama, vllm, etc.) via provider_type and base_url.
    """
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    # Empty prompt is allowed — generation v2.5+ has a USER INTENT section
    # with a {% else %} fallback ("apply general best practices"). Empty
    # string lets the LLM use the system context only.
    prompt: str = Field(default="", max_length=4096)
    provider: Optional[str] = None  # Built-in (openai/anthropic/gemini) or custom name
    model: Optional[str] = None
    language: Literal["python", "javascript", "rust"] = "python"
    # Optional fields for custom providers (e.g., ollama, vllm)
    provider_type: Optional[str] = None  # "openai_compatible" for custom providers
    base_url: Optional[str] = None  # Custom API endpoint (e.g., http://localhost:11434/v1/)
