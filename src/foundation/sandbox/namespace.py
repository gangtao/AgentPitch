"""Restricted namespace builder for the Code Sandbox.

`make_restricted_globals()` returns a fresh dict suitable for executing
RestrictedPython-compiled code. Per ADR-0001 + 2026-04-20 prototype:

  - 6 Action classes (Action + Move/Pass/Shoot/Tackle/Hold) — no import needed
  - 28 safe builtins (numeric / sequence / type constructors / introspection / hash)
  - 5 mandatory RestrictedPython guards (_getitem_, _getattr_, _getiter_,
    _write_ = full_write_guard, _inplacevar_) — without these, ALL dict
    access in the callback raises NameError
  - Plus 2 helper guards for sequence unpacking

Forbidden: __import__, exec, eval, compile, open, getattr, setattr, delattr,
print, input, breakpoint, exit, quit, globals, locals, vars.

The namespace IS the security boundary — see Story 002 spec for the full audit
list. HIGH-priority security-engineer review applies before this epic ships.
"""

from __future__ import annotations

from RestrictedPython import safe_globals
from RestrictedPython.Guards import (
    full_write_guard,
    guarded_iter_unpack_sequence,
    guarded_unpack_sequence,
    safer_getattr,
)

from src.foundation.action import Action, Hold, Move, Pass, Shoot, Tackle


# 28 safe builtins (per GDD Core Rule 3).
_ALLOWED_BUILTINS = {
    # Numeric (7)
    "abs": abs, "divmod": divmod, "max": max, "min": min,
    "pow": pow, "round": round, "sum": sum,
    # Sequence (10)
    "all": all, "any": any, "enumerate": enumerate, "filter": filter,
    "len": len, "map": map, "range": range, "reversed": reversed,
    "sorted": sorted, "zip": zip,
    # Type constructors (9)
    "bool": bool, "dict": dict, "float": float, "frozenset": frozenset,
    "int": int, "list": list, "set": set, "str": str, "tuple": tuple,
    # Introspection (1) — "type" excluded: 3-arg type() creates new classes (escape vector)
    "isinstance": isinstance,
    # Hash (1)
    "hash": hash,
}


def _safe_getitem(obj, key):
    """Permit dict/list/tuple subscript access. Required guard hook.

    Blocks dunder key access to prevent inspection of internal Python objects.
    """
    if isinstance(key, str) and key.startswith("__") and key.endswith("__"):
        raise AttributeError(f"Access to dunder key {key!r} is not allowed in sandbox")
    return obj[key]


_AUGMENTED_OPS = {
    "+=": lambda x, y: x + y,
    "-=": lambda x, y: x - y,
    "*=": lambda x, y: x * y,
    "/=": lambda x, y: x / y,
}


def _safe_inplacevar(op, x, y):
    """Permit augmented assignment for cross-tick counters (per GDD Core Rule 5).

    Only the four arithmetic operators are allowed. Bitwise / shift / power
    augmented forms are deliberately forbidden — keeps the sandbox surface small.
    """
    fn = _AUGMENTED_OPS.get(op)
    if fn is None:
        raise SyntaxError(f"Augmented operator {op!r} not allowed in sandbox")
    return fn(x, y)


def make_restricted_globals() -> dict:
    """Build a fresh restricted globals dict for one PlayerSandboxContext.

    Each call returns a new dict so cross-player state cannot leak (per GDD
    Core Rule 5 + EC-SANDBOX-08).
    """
    g = dict(safe_globals)  # RestrictedPython baseline
    g["__builtins__"] = dict(_ALLOWED_BUILTINS)

    # Action classes — available without import (per GDD Rule 4)
    g["Action"] = Action
    g["Move"] = Move
    g["Pass"] = Pass
    g["Shoot"] = Shoot
    g["Tackle"] = Tackle
    g["Hold"] = Hold

    # 5 mandatory RestrictedPython guards (per 2026-04-20 prototype)
    g["_getitem_"] = _safe_getitem
    g["_getattr_"] = safer_getattr
    g["_getiter_"] = iter
    g["_write_"] = full_write_guard
    g["_inplacevar_"] = _safe_inplacevar

    # Optional but defensive — sequence unpacking guards
    g["_iter_unpack_sequence_"] = guarded_iter_unpack_sequence
    g["_unpack_sequence_"] = guarded_unpack_sequence

    return g
