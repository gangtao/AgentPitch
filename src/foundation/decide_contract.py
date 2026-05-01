"""decide() callback contract: signature verification + reference invocation harness.

Defines the function signature contract LLM-generated `decide()` callbacks must
satisfy and a thin reference harness that invokes them with deep-copied args.

This module is the contract surface ONLY — the production sandboxed execution
path (RestrictedPython + signal.setitimer + BaseException catch) lives in the
Code Sandbox epic per ADR-0001. The Fallback Handler epic per ADR-0012 owns
the translation of propagated exceptions / InvalidReturnTypeError into
Hold() substitutions.
"""

from __future__ import annotations

import copy
import inspect
from typing import Any, Callable

from src.foundation.action import Action


class CallbackContractError(Exception):
    """Base class for all decide() contract violations."""


class InvalidCallbackSignatureError(CallbackContractError):
    """The callable does not match decide(game_state, player_state, history)."""


class InvalidReturnTypeError(CallbackContractError):
    """The callable returned a non-Action value."""


# The exact required parameter names, in order (TR-ASCI-007).
_REQUIRED_PARAMS: tuple[str, str, str] = ("game_state", "player_state", "history")


def verify_decide_signature(callback: Any) -> None:
    """Confirm the callback matches decide(game_state, player_state, history).

    Raises InvalidCallbackSignatureError on any deviation:
      - non-callable
      - introspection failure
      - wrong arity (not exactly 3 positional params)
      - wrong parameter names
      - wrong order
      - keyword-only or var-positional params (must be plain positional)

    Called once per compile in production by the Code Sandbox, NOT per tick.
    """
    if not callable(callback):
        raise InvalidCallbackSignatureError(
            f"decide must be callable; got {type(callback).__name__}"
        )

    try:
        sig = inspect.signature(callback)
    except (TypeError, ValueError) as exc:
        raise InvalidCallbackSignatureError(
            f"decide: cannot introspect signature: {exc}"
        ) from exc

    params = list(sig.parameters.values())
    if len(params) != 3:
        raise InvalidCallbackSignatureError(
            f"decide must accept exactly 3 parameters; got {len(params)}: "
            f"{[p.name for p in params]}"
        )

    actual_names = tuple(p.name for p in params)
    if actual_names != _REQUIRED_PARAMS:
        raise InvalidCallbackSignatureError(
            f"decide parameter name/order mismatch: expected {_REQUIRED_PARAMS!r}, "
            f"got {actual_names!r}"
        )

    for got in params:
        if got.kind not in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.POSITIONAL_ONLY,
        ):
            raise InvalidCallbackSignatureError(
                f"decide.{got.name} must be a positional parameter; got {got.kind!r}"
            )


def invoke_decide(
    callback: Callable,
    game_state: dict,
    player_state: dict,
    history: list,
) -> Action:
    """Reference harness — invoke decide() once with the contract semantics.

    Deep-copies all three args so the callback cannot mutate caller state.
    Calls the callback exactly once. Asserts the return is an Action subclass.

    Does NOT catch exceptions, does NOT enforce timeouts, does NOT substitute
    Hold() on failure — those are Code Sandbox / Fallback Handler concerns
    per ADR-0001 / ADR-0012.

    Raises:
        InvalidReturnTypeError: callback returned a non-Action value.
        Exception: any exception raised by the callback propagates unchanged.
    """
    gs_copy = copy.deepcopy(game_state)
    ps_copy = copy.deepcopy(player_state)
    hist_copy = copy.deepcopy(history)

    result = callback(gs_copy, ps_copy, hist_copy)

    if not isinstance(result, Action):
        raise InvalidReturnTypeError(
            f"decide must return an Action subclass instance; got "
            f"{type(result).__name__} (value: {result!r})"
        )
    return result
