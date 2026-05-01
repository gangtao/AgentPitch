"""Tests for Code Sandbox Story 002: restricted namespace + guards."""

from __future__ import annotations

import pytest
from RestrictedPython import compile_restricted

from src.foundation.action import Action, Hold, Move, Pass, Shoot, Tackle
from src.foundation.sandbox.namespace import make_restricted_globals


# Canonical allowlist — used by AC-2 parametrize
_ALLOWED_BUILTIN_NAMES = {
    # Numeric
    "abs", "divmod", "max", "min", "pow", "round", "sum",
    # Sequence
    "all", "any", "enumerate", "filter", "len", "map", "range", "reversed", "sorted", "zip",
    # Type constructors
    "bool", "dict", "float", "frozenset", "int", "list", "set", "str", "tuple",
    # Introspection
    "isinstance",
    # Hash
    "hash",
}

_FORBIDDEN_BUILTIN_NAMES = [
    "__import__", "exec", "eval", "compile", "open",
    "globals", "locals", "vars",
    "getattr", "setattr", "delattr",
    "print", "input", "breakpoint", "exit", "quit",
]


# ---------------------------------------------------------------------------
# AC-1: 6 Action classes present
# ---------------------------------------------------------------------------


class TestAC1ActionClassesPresent:
    def test_action_keys_present(self):
        g = make_restricted_globals()
        for name in ("Action", "Move", "Pass", "Shoot", "Tackle", "Hold"):
            assert name in g

    def test_action_keys_are_actual_classes(self):
        g = make_restricted_globals()
        assert g["Action"] is Action
        assert g["Move"] is Move
        assert g["Pass"] is Pass
        assert g["Shoot"] is Shoot
        assert g["Tackle"] is Tackle
        assert g["Hold"] is Hold

    def test_constructed_subclass_isinstance_action(self):
        g = make_restricted_globals()
        assert isinstance(g["Hold"](), g["Action"])
        assert isinstance(g["Move"](1.0, 0.0, 1.0), g["Action"])


# ---------------------------------------------------------------------------
# AC-2: 29 builtins exact membership
# ---------------------------------------------------------------------------


class TestAC2BuiltinsExactMembership:
    def test_builtins_dict_present(self):
        g = make_restricted_globals()
        assert "__builtins__" in g
        assert isinstance(g["__builtins__"], dict)

    def test_builtins_count_28(self):
        g = make_restricted_globals()
        assert len(g["__builtins__"]) == 28

    def test_builtins_set_matches_allowlist(self):
        g = make_restricted_globals()
        assert set(g["__builtins__"].keys()) == _ALLOWED_BUILTIN_NAMES

    @pytest.mark.parametrize("name", sorted(_ALLOWED_BUILTIN_NAMES))
    def test_each_allowed_builtin_callable(self, name):
        g = make_restricted_globals()
        assert callable(g["__builtins__"][name])


# ---------------------------------------------------------------------------
# AC-3: forbidden builtins absent
# ---------------------------------------------------------------------------


class TestAC3ForbiddenBuiltinsAbsent:
    @pytest.mark.parametrize("name", _FORBIDDEN_BUILTIN_NAMES)
    def test_forbidden_name_raises_keyerror(self, name):
        g = make_restricted_globals()
        with pytest.raises(KeyError):
            _ = g["__builtins__"][name]


# ---------------------------------------------------------------------------
# AC-4: 5 mandatory guards present
# ---------------------------------------------------------------------------


class TestAC4MandatoryGuardsPresent:
    @pytest.mark.parametrize("guard", [
        "_getitem_", "_getattr_", "_getiter_", "_write_", "_inplacevar_",
    ])
    def test_guard_present_and_callable(self, guard):
        g = make_restricted_globals()
        assert guard in g
        assert callable(g[guard])

    def test_inplacevar_arithmetic_ops_work(self):
        g = make_restricted_globals()
        f = g["_inplacevar_"]
        assert f("+=", 5, 3) == 8
        assert f("-=", 5, 3) == 2
        assert f("*=", 5, 3) == 15
        assert f("/=", 6, 2) == 3.0

    def test_inplacevar_disallowed_op_raises_syntaxerror(self):
        g = make_restricted_globals()
        f = g["_inplacevar_"]
        with pytest.raises(SyntaxError, match="not allowed"):
            f("**=", 2, 3)
        with pytest.raises(SyntaxError):
            f("&=", 2, 3)

    def test_getitem_permits_dict_access(self):
        g = make_restricted_globals()
        f = g["_getitem_"]
        assert f({"k": 42}, "k") == 42
        assert f([10, 20, 30], 1) == 20


# ---------------------------------------------------------------------------
# AC-SANDBOX-02: Namespace blocks `import os`
# ---------------------------------------------------------------------------


def _compile_or_raises(source: str) -> object:
    """Compile RestrictedPython source. Returns the code object if compile
    succeeded; returns None if RestrictedPython rejected it at compile time
    (any of: SyntaxError raised, None returned, or empty errors list)."""
    try:
        compiled = compile_restricted(source, "<test>", "exec")
    except SyntaxError:
        return None
    return compiled


class TestACSandbox02ImportBlocked:
    def test_import_statement_rejected(self):
        compiled = _compile_or_raises("import os\nx = os.getcwd()")
        if compiled is None:
            return  # rejected at compile time — ✓
        g = make_restricted_globals()
        with pytest.raises((ImportError, NameError, AttributeError, SyntaxError)):
            exec(compiled, g)

    def test_dunder_import_call_rejected(self):
        # RestrictedPython rejects names starting with `_` at compile time.
        compiled = _compile_or_raises("__import__('os')")
        if compiled is None:
            return  # ✓ — compile-time rejection (security boundary held)
        g = make_restricted_globals()
        with pytest.raises((NameError, AttributeError, ImportError, SyntaxError)):
            exec(compiled, g)


# ---------------------------------------------------------------------------
# AC-SANDBOX-03: Namespace blocks exec/eval/compile
# ---------------------------------------------------------------------------


class TestACSandbox03ExecEvalBlocked:
    @pytest.mark.parametrize("source", [
        "exec('x=1')",
        "eval('1+1')",
        "compile('x', 'y', 'exec')",
    ])
    def test_dynamic_code_rejected(self, source):
        compiled = _compile_or_raises(source)
        if compiled is None:
            return  # compile-time rejection ✓
        g = make_restricted_globals()
        with pytest.raises((NameError, AttributeError, SyntaxError)):
            exec(compiled, g)


# ---------------------------------------------------------------------------
# AC-SANDBOX-01: Namespace blocks open()
# ---------------------------------------------------------------------------


class TestACSandbox01OpenBlocked:
    def test_open_call_raises_nameerror(self):
        compiled = _compile_or_raises("f = open('/etc/passwd')")
        if compiled is None:
            return
        g = make_restricted_globals()
        with pytest.raises((NameError, AttributeError, SyntaxError)):
            exec(compiled, g)


# ---------------------------------------------------------------------------
# AC-extra: dict access works (validates 2026-04-20 prototype finding)
# ---------------------------------------------------------------------------


class TestExtraDictAccessWorks:
    def test_subscript_in_compiled_code_works(self):
        # Without _getitem_ guard, this would raise NameError
        source = "d = {'k': 1}\nresult = d['k']"
        compiled = compile_restricted(source, "<test>", "exec")
        assert compiled is not None
        g = make_restricted_globals()
        l = {}
        exec(compiled, g, l)
        assert l["result"] == 1


# ---------------------------------------------------------------------------
# AC-extra: dunder access blocked via safer_getattr
# ---------------------------------------------------------------------------


class TestExtraDunderAccessBlocked:
    def test_class_attribute_access_rejected(self):
        # `.__class__` starts with `_` — RestrictedPython rejects at compile time
        compiled = _compile_or_raises("x = ().__class__")
        if compiled is None:
            return  # ✓ — compile-time rejection
        g = make_restricted_globals()
        with pytest.raises(Exception):
            exec(compiled, g)


# ---------------------------------------------------------------------------
# Bonus: each call returns a fresh dict (no shared state across players)
# ---------------------------------------------------------------------------


class TestFreshDictPerCall:
    def test_two_calls_produce_distinct_dicts(self):
        g1 = make_restricted_globals()
        g2 = make_restricted_globals()
        assert g1 is not g2
        assert g1["__builtins__"] is not g2["__builtins__"]
        # Mutation in one does not leak
        g1["x"] = 99
        assert "x" not in g2
