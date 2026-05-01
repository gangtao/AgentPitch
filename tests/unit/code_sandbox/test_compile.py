"""Tests for Code Sandbox Story 003: Sandbox.compile() entry point."""

from __future__ import annotations

import inspect
import re

import pytest

from src.foundation.sandbox.result import SandboxResult
from src.foundation.sandbox.sandbox import Sandbox
from src.foundation.sandbox.status import ExecutionStatus


_VALID_DECIDE = "def decide(g, p, h):\n    return Hold()\n"


# ---------------------------------------------------------------------------
# AC-1: public API signature
# ---------------------------------------------------------------------------


class TestAC1Signature:
    def test_compile_method_exists(self):
        sb = Sandbox()
        assert callable(sb.compile)

    def test_compile_signature(self):
        sb = Sandbox()
        sig = inspect.signature(sb.compile)
        params = list(sig.parameters.keys())
        assert params == ["player_id", "code_str"]

    def test_compile_returns_sandbox_result(self):
        sb = Sandbox()
        result = sb.compile("team_a_0", _VALID_DECIDE)
        assert isinstance(result, SandboxResult)


# ---------------------------------------------------------------------------
# AC-2: success path stores compiled_fn
# ---------------------------------------------------------------------------


class TestAC2SuccessStoresCompiledFn:
    def test_status_success(self):
        sb = Sandbox()
        result = sb.compile("team_a_0", _VALID_DECIDE)
        assert result.status is ExecutionStatus.SUCCESS

    def test_compiled_fn_is_callable(self):
        sb = Sandbox()
        sb.compile("team_a_0", _VALID_DECIDE)
        assert callable(sb._contexts["team_a_0"].compiled_fn)

    def test_module_globals_contains_decide(self):
        sb = Sandbox()
        sb.compile("team_a_0", _VALID_DECIDE)
        assert "decide" in sb._contexts["team_a_0"].module_globals


# ---------------------------------------------------------------------------
# AC-3: SyntaxError → COMPILE_ERROR
# ---------------------------------------------------------------------------


class TestAC3SyntaxError:
    def test_malformed_def_returns_compile_error(self):
        sb = Sandbox()
        result = sb.compile("team_a_0", "def decide(:\n")
        assert result.status is ExecutionStatus.COMPILE_ERROR
        assert result.error_type == "SyntaxError"

    def test_no_exception_raised(self):
        sb = Sandbox()
        # Should not raise — error must be returned in SandboxResult
        sb.compile("team_a_0", "this is not valid python at all $$$")


# ---------------------------------------------------------------------------
# AC-4: missing decide → COMPILE_ERROR
# ---------------------------------------------------------------------------


class TestAC4MissingDecide:
    def test_no_decide_function(self):
        sb = Sandbox()
        result = sb.compile("team_a_0", "x = 1\n")
        assert result.status is ExecutionStatus.COMPILE_ERROR
        assert result.error_type == "MissingDecideFunction"


# ---------------------------------------------------------------------------
# AC-5: non-callable decide → COMPILE_ERROR
# ---------------------------------------------------------------------------


class TestAC5NonCallableDecide:
    def test_decide_assigned_int_returns_compile_error(self):
        sb = Sandbox()
        result = sb.compile("team_a_0", "decide = 42\n")
        assert result.status is ExecutionStatus.COMPILE_ERROR
        assert result.error_type == "MissingDecideFunction"


# ---------------------------------------------------------------------------
# AC-6: forbidden import at compile time → COMPILE_ERROR
# ---------------------------------------------------------------------------


class TestAC6ImportRejected:
    def test_import_os_returns_compile_error(self):
        sb = Sandbox()
        code = "import os\ndef decide(g, p, h):\n    return Hold()\n"
        result = sb.compile("team_a_0", code)
        assert result.status is ExecutionStatus.COMPILE_ERROR
        assert result.error_type  # non-empty


# ---------------------------------------------------------------------------
# AC-7: recompile replaces context
# ---------------------------------------------------------------------------


class TestAC7RecompileReplacesContext:
    def test_second_compile_overwrites(self):
        sb = Sandbox()
        code_a = "x_marker_a = True\ndef decide(g, p, h):\n    return Hold()\n"
        code_b = "x_marker_b = True\ndef decide(g, p, h):\n    return Move(0.0, 0.0, 0.0)\n"

        sb.compile("team_a_0", code_a)
        first_globals = sb._contexts["team_a_0"].module_globals
        assert "x_marker_a" in first_globals

        sb.compile("team_a_0", code_b)
        second_globals = sb._contexts["team_a_0"].module_globals
        # Fresh dict — code_a's marker not present
        assert "x_marker_a" not in second_globals
        assert "x_marker_b" in second_globals
        # Different dict object
        assert first_globals is not second_globals

    def test_failed_recompile_still_replaces_context(self):
        sb = Sandbox()
        sb.compile("team_a_0", _VALID_DECIDE)
        original_ctx = sb._contexts["team_a_0"]
        # Failed recompile
        sb.compile("team_a_0", "def decide(:\n")
        # Context replaced (per AC-7 — fresh state per compile)
        assert sb._contexts["team_a_0"] is not original_ctx
        # And compiled_fn is None on the new context (compile failed)
        assert sb._contexts["team_a_0"].compiled_fn is None


# ---------------------------------------------------------------------------
# AC-8: per-player isolation
# ---------------------------------------------------------------------------


class TestAC8PerPlayerIsolation:
    def test_two_players_have_distinct_contexts(self):
        sb = Sandbox()
        sb.compile("team_a_0", _VALID_DECIDE)
        sb.compile("team_b_0", _VALID_DECIDE)
        assert sb._contexts["team_a_0"] is not sb._contexts["team_b_0"]
        assert (
            sb._contexts["team_a_0"].module_globals
            is not sb._contexts["team_b_0"].module_globals
        )

    def test_mutation_isolated(self):
        sb = Sandbox()
        sb.compile("team_a_0", _VALID_DECIDE)
        sb.compile("team_b_0", _VALID_DECIDE)
        sb._contexts["team_a_0"].module_globals["MUTATED"] = "yes"
        assert "MUTATED" not in sb._contexts["team_b_0"].module_globals


# ---------------------------------------------------------------------------
# AC-SANDBOX-16: error_type sanitization
# ---------------------------------------------------------------------------


_TOKEN_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


class TestACSandbox16ErrorTypeSanitization:
    @pytest.mark.parametrize("source", [
        "def decide(:\n",                                            # syntax err
        "x = 1\n",                                                   # missing decide
        "decide = 42\n",                                             # not callable
        "import os\ndef decide(g, p, h):\n    return Hold()\n",      # import rejected
    ])
    def test_error_type_is_single_token(self, source):
        sb = Sandbox()
        result = sb.compile("team_a_0", source)
        assert result.status is ExecutionStatus.COMPILE_ERROR
        assert result.error_type is not None
        assert "\n" not in result.error_type
        assert "Traceback" not in result.error_type
        assert "/" not in result.error_type
        assert _TOKEN_PATTERN.match(result.error_type), (
            f"error_type {result.error_type!r} not single-token"
        )
