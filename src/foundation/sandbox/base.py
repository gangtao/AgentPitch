"""Sandbox Protocol — the contract every per-language sandbox must satisfy.

ADR-0024. Implementations live in sibling modules:
  - python_sandbox.RestrictedPythonSandbox  (ADR-0001)
  - quickjs_sandbox.QuickJSSandbox          (ADR-0025, future)
  - wasm_sandbox.WasmSandbox                (ADR-0026, future)
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from src.foundation.sandbox.result import SandboxResult


@runtime_checkable
class Sandbox(Protocol):
    """Language-agnostic sandbox protocol."""

    timeout_ms: float
    consecutive_failures_limit: int

    @property
    def language(self) -> str: ...

    def compile(self, player_id: str, source: str) -> SandboxResult: ...

    def execute(
        self,
        player_id: str,
        game_state,
        player_state,
        history,
    ) -> SandboxResult: ...

    def disable(self, player_id: str) -> None: ...