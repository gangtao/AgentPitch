"""Tests for decide() callback contract (ASCI Story 004)."""

from __future__ import annotations

import pytest

from src.foundation.action import Action, Hold, Move, Pass, Shoot, Tackle
from src.foundation.decide_contract import (
    CallbackContractError,
    InvalidCallbackSignatureError,
    InvalidReturnTypeError,
    invoke_decide,
    verify_decide_signature,
)


# ---------------------------------------------------------------------------
# Signature verification
# ---------------------------------------------------------------------------


class TestAC1CanonicalSignatureAccepts:
    def test_canonical_function_accepts(self):
        def decide(game_state, player_state, history):
            return Hold()

        assert verify_decide_signature(decide) is None

    def test_lambda_accepts(self):
        decide = lambda game_state, player_state, history: Hold()  # noqa: E731
        assert verify_decide_signature(decide) is None

    def test_type_annotated_accepts(self):
        def decide(game_state: dict, player_state: dict, history: list) -> Action:
            return Hold()

        assert verify_decide_signature(decide) is None


class TestAC2WrongArityRejected:
    def test_two_arg_rejected(self):
        def decide(gs, ps):
            return Hold()

        with pytest.raises(InvalidCallbackSignatureError, match="3"):
            verify_decide_signature(decide)

    def test_four_arg_rejected(self):
        def decide(a, b, c, d):
            return Hold()

        with pytest.raises(InvalidCallbackSignatureError, match="3"):
            verify_decide_signature(decide)

    def test_zero_arg_rejected(self):
        def decide():
            return Hold()

        with pytest.raises(InvalidCallbackSignatureError, match="3"):
            verify_decide_signature(decide)


class TestAC3WrongParamNamesRejected:
    def test_renamed_params_rejected(self):
        def decide(state, player, hist):
            return Hold()

        with pytest.raises(InvalidCallbackSignatureError, match="name"):
            verify_decide_signature(decide)

    def test_single_name_swap_rejected(self):
        def decide(gs, player_state, history):
            return Hold()

        with pytest.raises(InvalidCallbackSignatureError):
            verify_decide_signature(decide)


class TestAC4WrongOrderRejected:
    def test_reordered_params_rejected(self):
        def decide(history, game_state, player_state):
            return Hold()

        with pytest.raises(InvalidCallbackSignatureError):
            verify_decide_signature(decide)


class TestAC5VarArgsRejected:
    def test_var_args_rejected(self):
        def decide(*args, **kwargs):
            return Hold()

        with pytest.raises(InvalidCallbackSignatureError):
            verify_decide_signature(decide)

    def test_only_var_positional_rejected(self):
        def decide(*args):
            return Hold()

        with pytest.raises(InvalidCallbackSignatureError):
            verify_decide_signature(decide)


class TestAC6KeywordOnlyRejected:
    def test_keyword_only_rejected(self):
        def decide(game_state, *, player_state, history):
            return Hold()

        with pytest.raises(InvalidCallbackSignatureError, match="positional"):
            verify_decide_signature(decide)


class TestAC7NonCallableRejected:
    @pytest.mark.parametrize("non_callable", [42, "decide", None, 3.14, [1, 2, 3]])
    def test_non_callable_rejected(self, non_callable):
        with pytest.raises(InvalidCallbackSignatureError, match="callable"):
            verify_decide_signature(non_callable)

    def test_class_with_call_method_accepts(self):
        class CallableObj:
            def __call__(self, game_state, player_state, history):
                return Hold()

        assert verify_decide_signature(CallableObj()) is None


# ---------------------------------------------------------------------------
# Invocation harness
# ---------------------------------------------------------------------------


class TestAC8SingleCall:
    def test_harness_calls_callback_exactly_once(self):
        counter = {"n": 0}

        def callback(gs, ps, h):
            counter["n"] += 1
            return Hold()

        result = invoke_decide(callback, {}, {}, [])
        assert counter["n"] == 1
        assert isinstance(result, Hold)

    def test_invoking_10_times_produces_count_10(self):
        counter = {"n": 0}

        def callback(gs, ps, h):
            counter["n"] += 1
            return Hold()

        for _ in range(10):
            invoke_decide(callback, {}, {}, [])
        assert counter["n"] == 10


class TestAC9ValidActionPassesThrough:
    def test_move_returned_unchanged(self):
        m = Move(dx=1.0, dy=0.0, speed=1.0)

        def callback(gs, ps, h):
            return m

        result = invoke_decide(callback, {}, {}, [])
        assert result is m
        assert isinstance(result, Action) and isinstance(result, Move)

    @pytest.mark.parametrize("action", [
        Move(0.0, 0.0, 0.0),
        Pass((50.0, 25.0), 10),
        Shoot(0.0, 15),
        Tackle("team_b_3"),
        Hold(),
    ])
    def test_each_subclass_passes_through(self, action):
        def callback(gs, ps, h):
            return action

        result = invoke_decide(callback, {}, {}, [])
        assert result is action
        assert isinstance(result, Action)


class TestAC10NoneReturnRaises:
    def test_none_return_raises(self):
        def callback(gs, ps, h):
            return None

        with pytest.raises(InvalidReturnTypeError, match="NoneType"):
            invoke_decide(callback, {}, {}, [])

    def test_implicit_return_raises(self):
        def callback(gs, ps, h):
            pass  # implicit None

        with pytest.raises(InvalidReturnTypeError):
            invoke_decide(callback, {}, {}, [])

    @pytest.mark.parametrize("bad", [True, 42, "hold", {}, [1, 2, 3]])
    def test_non_action_returns_raise(self, bad):
        def callback(gs, ps, h):
            return bad

        with pytest.raises(InvalidReturnTypeError):
            invoke_decide(callback, {}, {}, [])


class TestAC11ExceptionPropagates:
    def test_value_error_propagates(self):
        def callback(gs, ps, h):
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            invoke_decide(callback, {}, {}, [])

    @pytest.mark.parametrize("exc_class", [RuntimeError, KeyError, ZeroDivisionError])
    def test_other_exceptions_propagate(self, exc_class):
        def callback(gs, ps, h):
            raise exc_class("test")

        with pytest.raises(exc_class):
            invoke_decide(callback, {}, {}, [])


class TestAC12ImportErrorPropagates:
    def test_import_error_not_specially_caught(self):
        def callback(gs, ps, h):
            raise ImportError("os is restricted")

        # Harness must NOT catch and translate — Fallback Handler's job.
        with pytest.raises(ImportError):
            invoke_decide(callback, {}, {}, [])


class TestAC13DeepCopyArgsIsolated:
    def test_callback_mutation_does_not_affect_caller_game_state(self):
        gs = {"tick": 0, "players": {"team_a_0": {"position": [0.0, 0.0]}}}

        def callback(game_state, player_state, history):
            game_state["players"]["team_a_0"]["position"][0] = 99.0
            return Hold()

        invoke_decide(callback, gs, {}, [])
        assert gs["players"]["team_a_0"]["position"][0] == 0.0

    def test_callback_mutation_does_not_affect_caller_history(self):
        hist = [{"tick": 1, "actions": []}]

        def callback(gs, ps, history):
            history.clear()
            history.append({"tampered": True})
            return Hold()

        invoke_decide(callback, {}, {}, hist)
        assert hist == [{"tick": 1, "actions": []}]

    def test_callback_mutation_does_not_affect_caller_player_state(self):
        ps = {"speed": 12, "nested": {"k": "v"}}

        def callback(gs, player_state, h):
            player_state["nested"]["k"] = "MUTATED"
            return Hold()

        invoke_decide(callback, {}, ps, [])
        assert ps["nested"]["k"] == "v"


class TestAC14NoHelpersInjected:
    def test_callback_receives_only_3_args(self):
        # The harness uses plain Python call semantics — no extra args injected.
        # Test by counting the function's arity vs what was actually passed.
        arity_seen = {"n": -1}

        def callback(gs, ps, h):
            # Use locals() at function entry to verify only 3 names exist
            arity_seen["n"] = len([k for k in locals() if k in ("gs", "ps", "h")])
            return Hold()

        invoke_decide(callback, {}, {}, [])
        assert arity_seen["n"] == 3


class TestAC15ActionSubclassDiscrimination:
    @pytest.mark.parametrize("action_class,args", [
        (Move, (1.0, 0.0, 1.0)),
        (Pass, ((50.0, 25.0), 10)),
        (Shoot, (0.0, 15)),
        (Tackle, ("team_b_3",)),
        (Hold, ()),
    ])
    def test_each_subclass_dispatches_correctly(self, action_class, args):
        instance = action_class(*args)

        def callback(gs, ps, h):
            return instance

        result = invoke_decide(callback, {}, {}, [])
        assert isinstance(result, Action)
        assert isinstance(result, action_class)


class TestAC16SentinelExceptionHierarchy:
    def test_invalid_signature_subclasses_callback_contract_error(self):
        assert issubclass(InvalidCallbackSignatureError, CallbackContractError)

    def test_invalid_return_type_subclasses_callback_contract_error(self):
        assert issubclass(InvalidReturnTypeError, CallbackContractError)

    def test_callback_contract_error_subclasses_exception(self):
        assert issubclass(CallbackContractError, Exception)

    def test_callers_can_catch_both_via_base(self):
        # Demonstrate a single except clause catches both error types
        for exc_cls in (InvalidCallbackSignatureError, InvalidReturnTypeError):
            try:
                raise exc_cls("test")
            except CallbackContractError:
                caught = True
            assert caught
