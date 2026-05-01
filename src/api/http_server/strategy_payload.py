"""Strategy payload model for PUT /api/strategies/<name> endpoint."""
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field


class StrategyPayload(BaseModel):
    """Payload for PUT /api/strategies/<name> - contains Python source code."""
    model_config = ConfigDict(frozen=True)

    source: str = Field(min_length=1, description="Python source code for the strategy")