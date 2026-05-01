"""Fallback Handler package.

Re-exports the public surface defined across this subpackage. Story 003 will
add `reset_for_match()`.
"""

from src.foundation.fallback.handler import FallbackHandler
from src.foundation.fallback.types import (
    ExecutionStatus,
    FallbackEvent,
    FallbackResult,
)

__all__ = ["FallbackEvent", "FallbackHandler", "FallbackResult", "ExecutionStatus"]
