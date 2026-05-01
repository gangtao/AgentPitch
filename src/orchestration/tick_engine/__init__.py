"""Tick Engine package — match orchestrator.

Re-exports the public surface defined across this subpackage.
"""

from src.orchestration.tick_engine.engine import TickEngine

__all__ = ["TickEngine"]