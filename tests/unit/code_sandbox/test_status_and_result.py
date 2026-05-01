"""Tests for Code Sandbox Story 001: ExecutionStatus + SandboxResult + PlayerSandboxContext."""

from __future__ import annotations

import dataclasses

import pytest

from src.foundation.action import Hold, Move
from src.foundation.sandbox.result import PlayerSandboxContext, SandboxResult
from src.foundation.sandbox.status import ExecutionStatus


# ---------------------------------------------------------------------------
# AC-1: ExecutionStatus exact membership (6 values per ADR-0012)
# ---------------------------------------------------------------------------


class TestAC1EnumExactMembership:
    def test_exactly_six_members(self):
        assert len(ExecutionStatus) == 6

    def test_member_names_match_adr_0012(self):
        names = set(ExecutionStatus.__members__.keys())
        assert names == {
            "SUCCESS", "EXCEPTION", "TIMEOUT",
            "INVALID_RETURN", "DISABLED", "COMPILE_ERROR",
        }

    def test_no_runtime_error_member(self):
        # GDD wording listed RUNTIME_ERROR; ADR-0012 supersedes with EXCEPTION.
        assert "RUNTIME_ERROR" not in ExecutionStatus.__members__


# ---------------------------------------------------------------------------
# AC-2: enum string values are lowercase snake_case
# ---------------------------------------------------------------------------


class TestAC2EnumStringValues:
    @pytest.mark.parametrize("member", list(ExecutionStatus))
    def test_value_is_lowercase_name(self, member):
        assert member.value == member.name.lower()

    def test_invalid_return_value_exact(self):
        assert ExecutionStatus.INVALID_RETURN.value == "invalid_return"

    def test_compile_error_value_exact(self):
        assert ExecutionStatus.COMPILE_ERROR.value == "compile_error"


# ---------------------------------------------------------------------------
# AC-3: SandboxResult schema (4 fields, status required, sensible defaults)
# ---------------------------------------------------------------------------


class TestAC3SandboxResultSchema:
    def test_minimal_construction(self):
        r = SandboxResult(status=ExecutionStatus.SUCCESS)
        assert r.status is ExecutionStatus.SUCCESS
        assert r.action is None
        assert r.execution_time_ms == 0.0
        assert r.error_type is None

    def test_status_required(self):
        with pytest.raises(TypeError):
            SandboxResult()  # type: ignore[call-arg]

    def test_full_construction_round_trip(self):
        r = SandboxResult(
            status=ExecutionStatus.EXCEPTION,
            action=None,
            execution_time_ms=2.3,
            error_type="ValueError",
        )
        assert r.status is ExecutionStatus.EXCEPTION
        assert r.action is None
        assert r.execution_time_ms == 2.3
        assert r.error_type == "ValueError"

    def test_action_field_accepts_action_subclass(self):
        m = Move(1.0, 0.0, 1.0)
        r = SandboxResult(status=ExecutionStatus.SUCCESS, action=m)
        assert r.action is m

    def test_field_names(self):
        names = {f.name for f in dataclasses.fields(SandboxResult)}
        assert names == {"status", "action", "serialization_ms", "execution_time_ms", "error_type", "error_message"}


# ---------------------------------------------------------------------------
# AC-4: PlayerSandboxContext schema (4 fields, default_factory dict, mutable)
# ---------------------------------------------------------------------------


class TestAC4PlayerSandboxContextSchema:
    def test_defaults(self):
        ctx = PlayerSandboxContext()
        assert ctx.compiled_fn is None
        assert ctx.module_globals == {}
        assert ctx.consecutive_timeout_count == 0
        assert ctx.disabled is False

    def test_module_globals_default_factory_isolated(self):
        ctx_a = PlayerSandboxContext()
        ctx_b = PlayerSandboxContext()
        # Each call produces a distinct dict — no shared mutable default
        assert ctx_a.module_globals is not ctx_b.module_globals
        ctx_a.module_globals["x"] = 1
        assert "x" not in ctx_b.module_globals

    def test_fields_are_mutable(self):
        ctx = PlayerSandboxContext()
        ctx.disabled = True
        ctx.consecutive_timeout_count = 5
        ctx.module_globals["k"] = "v"
        assert ctx.disabled is True
        assert ctx.consecutive_timeout_count == 5
        assert ctx.module_globals["k"] == "v"

    def test_field_names_exactly_four(self):
        names = {f.name for f in dataclasses.fields(PlayerSandboxContext)}
        assert names == {"compiled_fn", "module_globals", "consecutive_timeout_count", "disabled"}

    def test_compiled_fn_accepts_callable(self):
        def fake_fn(*args):
            return Hold()

        ctx = PlayerSandboxContext(compiled_fn=fake_fn)
        assert ctx.compiled_fn is fake_fn


# ---------------------------------------------------------------------------
# AC-SANDBOX-16: error_type schema is str | None only — no traceback helpers
# ---------------------------------------------------------------------------


class TestACSandbox16ErrorTypeSchema:
    def test_error_type_is_single_token_string(self):
        r = SandboxResult(status=ExecutionStatus.EXCEPTION, error_type="ValueError")
        assert r.error_type == "ValueError"
        assert "\n" not in r.error_type

    def test_no_traceback_helper_on_dataclass(self):
        r = SandboxResult(status=ExecutionStatus.EXCEPTION, error_type="ValueError")
        # Defensive: confirm no method exists that could leak a traceback
        for forbidden in ("format_traceback", "traceback", "format_exc", "tb"):
            assert not hasattr(r, forbidden), f"SandboxResult must not expose {forbidden!r}"
