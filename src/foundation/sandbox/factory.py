"""SandboxFactory — dispatch strategy file extensions to the correct Sandbox impl.

ADR-0024. Siblings registered:
  .py   → RestrictedPythonSandbox  (ADR-0001)
  .js   → QuickJSSandbox           (ADR-0025)
  .rs   → WasmtimeSandbox          (ADR-0026, Rust source compiled per match)
  .wasm → not yet registered — pre-compiled blob support deferred.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.foundation.sandbox.python_sandbox import RestrictedPythonSandbox


class UnknownStrategyLanguage(Exception):
    """No sandbox registered for the given file extension."""


def _load_quickjs_sandbox():
    from src.foundation.sandbox.quickjs_sandbox import QuickJSSandbox
    return QuickJSSandbox


def _load_wasmtime_sandbox():
    from src.foundation.sandbox.wasm_sandbox import WasmtimeSandbox
    return WasmtimeSandbox


class SandboxFactory:
    """Dispatch strategy file extensions to the correct Sandbox impl."""

    _registry: dict[str, type] = {
        ".py": RestrictedPythonSandbox,
    }

    _lazy_registry: dict[str, callable] = {
        ".js": _load_quickjs_sandbox,
        ".rs": _load_wasmtime_sandbox,
    }

    @classmethod
    def for_strategy_path(cls, path: Path, **kwargs: Any) -> Any:
        ext = path.suffix.lower()
        impl = cls._registry.get(ext)
        if impl is None:
            loader = cls._lazy_registry.get(ext)
            if loader is not None:
                impl = loader()
                cls._registry[ext] = impl
            else:
                raise UnknownStrategyLanguage(f"No sandbox registered for {ext!r}")
        return impl(**kwargs)
