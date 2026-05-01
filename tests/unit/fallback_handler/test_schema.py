"""Tests for Fallback Handler Story 001: schema dataclasses + ExecutionStatus re-export."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields

import pytest

from src.foundation.action import Hold
from src.foundation.fallback import ExecutionStatus, FallbackEvent, FallbackResult


def _make_event(**overrides) -> FallbackEvent:
    base = {
        "event_type": "fallback",
        "tick": 5,
        "player_id": "team_a_2",
        "team": "team_a",
        "llm_provider": "openai/gpt-4o",
        "failure_status": "exception",
        "error_type": "ValueError",
        "execution_time_ms": 2.5,
        "substituted_action": "Hold",
        "fallback_substituted": True,
    }
    base.update(overrides)
    return FallbackEvent(**base)


# ---------------------------------------------------------------------------
# AC-1: FallbackEvent has exactly 10 fields in spec order
# ---------------------------------------------------------------------------


class TestAC1FallbackEventFields:
    def test_field_count_is_10(self):
        assert len(fields(FallbackEvent)) == 10

    def test_field_names_in_order(self):
        expected = [
            "event_type", "tick", "player_id", "team", "llm_provider",
            "failure_status", "error_type", "execution_time_ms",
            "substituted_action", "fallback_substituted",
        ]
        assert [f.name for f in fields(FallbackEvent)] == expected


# ---------------------------------------------------------------------------
# AC-2: FallbackResult has exactly 2 fields
# ---------------------------------------------------------------------------


class TestAC2FallbackResultFields:
    def test_field_count_is_2(self):
        assert len(fields(FallbackResult)) == 2

    def test_field_names(self):
        assert [f.name for f in fields(FallbackResult)] == ["action", "log_event"]


# ---------------------------------------------------------------------------
# AC-3: event_type is "fallback"
# ---------------------------------------------------------------------------


class TestAC3EventTypeLiteral:
    def test_event_type_constructed_value(self):
        e = _make_event(event_type="fallback")
        assert e.event_type == "fallback"


# ---------------------------------------------------------------------------
# AC-4: substituted_action is "Hold"
# ---------------------------------------------------------------------------


class TestAC4SubstitutedActionLiteral:
    def test_substituted_action_value(self):
        e = _make_event(substituted_action="Hold")
        assert e.substituted_action == "Hold"


# ---------------------------------------------------------------------------
# AC-5: fallback_substituted is True
# ---------------------------------------------------------------------------


class TestAC5FallbackSubstitutedTrue:
    def test_fallback_substituted_is_true(self):
        e = _make_event(fallback_substituted=True)
        assert e.fallback_substituted is True


# ---------------------------------------------------------------------------
# AC-6: player_id annotation is str
# ---------------------------------------------------------------------------


class TestAC6PlayerIdIsStr:
    def test_annotation_is_str(self):
        # `from __future__ import annotations` means annotations are strings;
        # check the name
        ann = FallbackEvent.__annotations__["player_id"]
        # When PEP 563 is in effect, this is the string "str"; otherwise the type
        assert ann == "str" or ann is str

    def test_str_player_id_constructs(self):
        e = _make_event(player_id="team_a_2")
        assert e.player_id == "team_a_2"


# ---------------------------------------------------------------------------
# AC-7: error_type accepts None and str
# ---------------------------------------------------------------------------


class TestAC7ErrorTypeOptional:
    def test_none_accepted(self):
        e = _make_event(error_type=None)
        assert e.error_type is None

    def test_str_accepted(self):
        e = _make_event(error_type="ValueError")
        assert e.error_type == "ValueError"


# ---------------------------------------------------------------------------
# AC-8: ExecutionStatus has exactly 6 members per ADR-0012
# ---------------------------------------------------------------------------


class TestAC8ExecutionStatusMembership:
    def test_six_members(self):
        assert len(list(ExecutionStatus)) == 6

    def test_member_names_match_adr_0012(self):
        names = {m.name for m in ExecutionStatus}
        assert names == {
            "SUCCESS", "EXCEPTION", "TIMEOUT",
            "INVALID_RETURN", "DISABLED", "COMPILE_ERROR",
        }


# ---------------------------------------------------------------------------
# AC-9: ExecutionStatus values are lowercase strings
# ---------------------------------------------------------------------------


class TestAC9ExecutionStatusValues:
    @pytest.mark.parametrize("name,value", [
        ("SUCCESS", "success"),
        ("EXCEPTION", "exception"),
        ("TIMEOUT", "timeout"),
        ("INVALID_RETURN", "invalid_return"),
        ("DISABLED", "disabled"),
        ("COMPILE_ERROR", "compile_error"),
    ])
    def test_member_value_is_lowercase_name(self, name, value):
        assert ExecutionStatus[name].value == value


# ---------------------------------------------------------------------------
# AC-10: FallbackEvent immutability
# ---------------------------------------------------------------------------


class TestAC10FallbackEventImmutable:
    @pytest.mark.parametrize("field_name,new_value", [
        ("tick", 999),
        ("player_id", "modified"),
        ("error_type", "RuntimeError"),
        ("fallback_substituted", False),
    ])
    def test_each_field_rejects_mutation(self, field_name, new_value):
        e = _make_event()
        with pytest.raises(FrozenInstanceError):
            setattr(e, field_name, new_value)


# ---------------------------------------------------------------------------
# AC-11: FallbackResult immutability
# ---------------------------------------------------------------------------


class TestAC11FallbackResultImmutable:
    def test_log_event_mutation_rejected(self):
        result = FallbackResult(action=Hold(), log_event=_make_event())
        with pytest.raises(FrozenInstanceError):
            result.log_event = None  # type: ignore[misc]

    def test_action_mutation_rejected(self):
        result = FallbackResult(action=Hold(), log_event=None)
        with pytest.raises(FrozenInstanceError):
            result.action = Hold()  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Bonus: ExecutionStatus is the same enum object as the Code Sandbox version
# ---------------------------------------------------------------------------


class TestBonusExecutionStatusIsCodeSandboxEnum:
    def test_same_enum_class(self):
        from src.foundation.sandbox.status import ExecutionStatus as CSStatus
        assert ExecutionStatus is CSStatus
