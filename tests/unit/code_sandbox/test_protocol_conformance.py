"""Protocol conformance tests for the Sandbox abstraction (ADR-0024)."""

from __future__ import annotations

import pytest

from src.foundation.sandbox.base import Sandbox


class _StubSandbox:
    """Minimal stub that satisfies the Protocol for isinstance checks."""

    timeout_ms: float = 5.0
    consecutive_failures_limit: int = 10

    @property
    def language(self) -> str:
        return "stub"

    def compile(self, player_id: str, source: str):
        pass

    def execute(self, player_id: str, game_state, player_state, history):
        pass

    def disable(self, player_id: str) -> None:
        pass


class _BadStub:
    """Missing required members — must NOT satisfy the Protocol."""

    timeout_ms: float = 5.0


def test_valid_stub_satisfies_protocol():
    assert isinstance(_StubSandbox(), Sandbox)


def test_invalid_stub_rejected():
    assert not isinstance(_BadStub(), Sandbox)


from src.foundation.sandbox.python_sandbox import RestrictedPythonSandbox


def test_restricted_python_sandbox_satisfies_protocol():
    sb = RestrictedPythonSandbox()
    assert isinstance(sb, Sandbox)


def test_restricted_python_sandbox_language():
    sb = RestrictedPythonSandbox()
    assert sb.language == "python"


from pathlib import Path

from src.foundation.sandbox.factory import SandboxFactory, UnknownStrategyLanguage


def test_factory_returns_python_sandbox_for_py():
    sb = SandboxFactory.for_strategy_path(Path("strategies/team_a/current.py"))
    assert isinstance(sb, RestrictedPythonSandbox)
    assert sb.language == "python"


def test_factory_passes_kwargs():
    sb = SandboxFactory.for_strategy_path(
        Path("foo.py"), timeout_ms=10.0, consecutive_failures_limit=5
    )
    assert sb.timeout_ms == 10.0
    assert sb.consecutive_failures_limit == 5


def test_factory_rejects_unknown_extension():
    with pytest.raises(UnknownStrategyLanguage):
        SandboxFactory.for_strategy_path(Path("foo.lua"))


quickjs_available = pytest.importorskip("quickjs", reason="quickjs not installed")


def test_quickjs_sandbox_satisfies_protocol():
    from src.foundation.sandbox.quickjs_sandbox import QuickJSSandbox
    sb = QuickJSSandbox()
    assert isinstance(sb, Sandbox)


def test_quickjs_sandbox_language():
    from src.foundation.sandbox.quickjs_sandbox import QuickJSSandbox
    sb = QuickJSSandbox()
    assert sb.language == "javascript"


def test_factory_returns_quickjs_sandbox_for_js():
    from src.foundation.sandbox.quickjs_sandbox import QuickJSSandbox
    sb = SandboxFactory.for_strategy_path(Path("strategies/team_b/current.js"))
    assert isinstance(sb, QuickJSSandbox)
    assert sb.language == "javascript"


# ── WasmtimeSandbox (ADR-0026) ────────────────────────────────────────────

wasmtime_available = pytest.importorskip("wasmtime", reason="wasmtime not installed")
msgpack_available = pytest.importorskip("msgpack", reason="msgpack not installed")


def test_wasmtime_sandbox_satisfies_protocol():
    from src.foundation.sandbox.wasm_sandbox import WasmtimeSandbox
    sb = WasmtimeSandbox()
    assert isinstance(sb, Sandbox)


def test_wasmtime_sandbox_language():
    from src.foundation.sandbox.wasm_sandbox import WasmtimeSandbox
    sb = WasmtimeSandbox()
    assert sb.language == "rust"


def test_factory_returns_wasmtime_sandbox_for_rs():
    from src.foundation.sandbox.wasm_sandbox import WasmtimeSandbox
    sb = SandboxFactory.for_strategy_path(Path("strategies/team_a/current.rs"))
    assert isinstance(sb, WasmtimeSandbox)
    assert sb.language == "rust"