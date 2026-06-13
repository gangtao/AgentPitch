"""Tests for player_state and history schemas (ASCI Story 003)."""

from __future__ import annotations

import copy
import warnings

import pytest

from src.foundation.player_state_schema import (
    HISTORY_MAX_TICKS,
    HistoryActionDict,
    HistoryEntryDict,
    PlayerStateDict,
    ScoreDict,
    _PAM_ATTRIBUTE_KEYS,
    validate_history,
    validate_player_state,
)


def _valid_player_state(**overrides) -> dict:
    base = {
        "player_id": "team_a_0",
        "team": "team_a",
        "number": 1,
        "role": "GK",
        "position": (8.0, 30.0),
        "has_ball": False,
        "formation_position": (8.0, 30.0),
        "formation_zone": {"x": 8.0, "y": 30.0},
        "formation_zone_phase": "defend",
        "speed": 8,
        "skill": 10,
        "strength": 8,
        "save": 16,
        "discipline": 14,
        "dribbling": 4,
        "passing": 8,
        "shooting": 6,
        "stamina": 10,
        # Issue #38 (IFAB Law 12/14): aggression / penalty ratings + cautions.
        "offensive": 10,
        "penalty": 10,
        "yellow_cards": 0,
        "current_health": 100.0,
        # Cooldown feedback (per ADR-0015 amendment / 2026-04-22). Single
        # unified timer; 0 = Pass/Shoot/Tackle/Pickup currently allowed.
        "cooldown_remaining": 0,
    }
    base.update(overrides)
    return base


def _valid_history_action(**overrides) -> dict:
    base = {
        "player_id": "team_a_0",
        "team": "team_a",
        "action": "move",
        "result": "success",
        "details": {},
    }
    base.update(overrides)
    return base


def _valid_history_entry(tick: int = 1, n_actions: int = 10) -> dict:
    return {
        "tick": tick,
        "ball_position": (50.0, 30.0),
        "score": {"team_a": 0, "team_b": 0},
        "actions": [_valid_history_action(player_id=f"team_a_{i % 5}") for i in range(n_actions)],
    }


# ---------------------------------------------------------------------------
# player_state validation
# ---------------------------------------------------------------------------


class TestAC1PlayerStateHappyPath:
    def test_full_state_validates(self):
        state = _valid_player_state()
        assert validate_player_state(state) is None

    def test_def_with_save_zero_accepts(self):
        state = _valid_player_state(role="DEF", save=0)
        assert validate_player_state(state) is None


class TestAC2PlayerStateMissingKey:
    @pytest.mark.parametrize("key", [
        "player_id", "team", "role", "position", "has_ball", "formation_position",
        "formation_zone", "formation_zone_phase",
        "speed", "skill", "strength", "save", "discipline", "dribbling",
        "passing", "shooting", "stamina", "offensive", "penalty",
        "yellow_cards", "current_health",
    ])
    def test_missing_required_key_rejected(self, key):
        state = _valid_player_state()
        del state[key]
        with pytest.raises(ValueError, match="missing"):
            validate_player_state(state)


class TestAC3PlayerStateExtraKey:
    def test_extra_key_rejected(self):
        state = _valid_player_state()
        state["mood"] = "happy"
        with pytest.raises(ValueError, match="unexpected"):
            validate_player_state(state)


class TestAC4PlayerIdIsStr:
    def test_int_player_id_rejected(self):
        state = _valid_player_state(player_id=2)
        with pytest.raises(ValueError, match="ADR-0004"):
            validate_player_state(state)

    def test_str_player_id_accepts(self):
        state = _valid_player_state(player_id="team_a_2")
        assert validate_player_state(state) is None


class TestAC5RoleEnum:
    def test_invalid_role_rejected(self):
        state = _valid_player_state(role="STRIKER")
        with pytest.raises(ValueError, match="role"):
            validate_player_state(state)

    def test_lowercase_role_rejected(self):
        state = _valid_player_state(role="gk")
        with pytest.raises(ValueError, match="role"):
            validate_player_state(state)

    @pytest.mark.parametrize("role", ["GK", "DEF", "MID", "FWD"])
    def test_canonical_roles_accept(self, role):
        # Use save=0 for non-GK to avoid validator confusion at structural level
        state = _valid_player_state(role=role, save=16 if role == "GK" else 0)
        assert validate_player_state(state) is None


class TestAC6NumericAttributesIntOnly:
    @pytest.mark.parametrize("attr", ["speed", "skill", "strength", "save", "discipline", "dribbling"])
    def test_float_rejected(self, attr):
        state = _valid_player_state(**{attr: 8.0})
        with pytest.raises(ValueError, match=attr):
            validate_player_state(state)

    @pytest.mark.parametrize("attr", ["speed", "skill", "strength", "save", "discipline", "dribbling"])
    def test_bool_rejected(self, attr):
        state = _valid_player_state(**{attr: True})
        with pytest.raises(ValueError, match=attr):
            validate_player_state(state)

    @pytest.mark.parametrize("attr", ["speed", "skill", "strength", "save", "discipline", "dribbling"])
    def test_int_accepts(self, attr):
        state = _valid_player_state(**{attr: 12})
        assert validate_player_state(state) is None


class TestAC7PamMirror:
    def test_pam_attribute_keys_match_pam_exactly(self):
        # Mirrors PAM Story 001 PlayerAttribute schema's 6 numeric fields
        from src.foundation.player_attribute import PlayerAttribute

        pam_field_names = set(PlayerAttribute.model_fields.keys())
        # Subtract the non-numeric PAM identity fields (player_id, team, role)
        expected_numeric = pam_field_names - {"player_id", "team", "role"}
        assert _PAM_ATTRIBUTE_KEYS == expected_numeric

    def test_pam_attribute_keys_count_is_6(self):
        assert len(_PAM_ATTRIBUTE_KEYS) == 6

    def test_pam_attribute_keys_exact_set(self):
        assert _PAM_ATTRIBUTE_KEYS == frozenset({
            "speed", "skill", "strength", "save", "discipline", "dribbling"
        })


# ---------------------------------------------------------------------------
# history validation
# ---------------------------------------------------------------------------


class TestAC8HistoryHappyPath:
    def test_3_tick_history_validates(self):
        history = [_valid_history_entry(tick=t) for t in (1, 2, 3)]
        assert validate_history(history) is None

    def test_empty_history_accepts(self):
        assert validate_history([]) is None

    def test_single_entry_accepts(self):
        assert validate_history([_valid_history_entry(tick=0)]) is None


class TestAC9HistoryEntryMissingKey:
    @pytest.mark.parametrize("key", ["tick", "ball_position", "score", "actions"])
    def test_missing_entry_key_rejected(self, key):
        entry = _valid_history_entry(tick=1)
        del entry[key]
        with pytest.raises(ValueError, match="missing"):
            validate_history([entry])


class TestAC10HistoryActionStructure:
    @pytest.mark.parametrize("key", ["player_id", "team", "action", "result", "details"])
    def test_missing_action_key_rejected(self, key):
        entry = _valid_history_entry(tick=1, n_actions=1)
        del entry["actions"][0][key]
        with pytest.raises(ValueError, match="missing"):
            validate_history([entry])


class TestAC11HistoryActionPlayerIdIsStr:
    def test_int_player_id_in_action_rejected(self):
        entry = _valid_history_entry(tick=1, n_actions=1)
        entry["actions"][0]["player_id"] = 3
        with pytest.raises(ValueError, match="ADR-0004"):
            validate_history([entry])

    def test_str_player_id_in_action_accepts(self):
        entry = _valid_history_entry(tick=1, n_actions=1)
        entry["actions"][0]["player_id"] = "team_a_3"
        assert validate_history([entry]) is None


class TestAC12ActionEnum:
    @pytest.mark.parametrize("invalid", ["dribble", "DRIBBLE", "Move", "skip", ""])
    def test_invalid_action_rejected(self, invalid):
        entry = _valid_history_entry(tick=1, n_actions=1)
        entry["actions"][0]["action"] = invalid
        with pytest.raises(ValueError, match="action"):
            validate_history([entry])

    @pytest.mark.parametrize("valid", ["move", "pass", "shoot", "tackle", "hold"])
    def test_canonical_actions_accept(self, valid):
        entry = _valid_history_entry(tick=1, n_actions=1)
        entry["actions"][0]["action"] = valid
        assert validate_history([entry]) is None


class TestAC13ResultEnum:
    @pytest.mark.parametrize("invalid", ["touchback", "TIE", "incomplete", ""])
    def test_invalid_result_rejected(self, invalid):
        entry = _valid_history_entry(tick=1, n_actions=1)
        entry["actions"][0]["result"] = invalid
        with pytest.raises(ValueError, match="result"):
            validate_history([entry])

    @pytest.mark.parametrize("valid", ["success", "fail", "goal", "save", "out_of_bounds"])
    def test_canonical_results_accept(self, valid):
        entry = _valid_history_entry(tick=1, n_actions=1)
        entry["actions"][0]["result"] = valid
        assert validate_history([entry]) is None


class TestAC14HistoryOrdering:
    def test_descending_ticks_rejected(self):
        history = [_valid_history_entry(tick=5), _valid_history_entry(tick=3)]
        with pytest.raises(ValueError, match="oldest-first"):
            validate_history(history)

    def test_equal_ticks_rejected(self):
        history = [_valid_history_entry(tick=2), _valid_history_entry(tick=2)]
        with pytest.raises(ValueError, match="oldest-first"):
            validate_history(history)

    def test_strict_increasing_accepts(self):
        history = [_valid_history_entry(tick=t) for t in (0, 1, 2, 3)]
        assert validate_history(history) is None


class TestAC15HistoryMaxTicksWarning:
    def test_overflow_emits_warning_not_error(self):
        history = [_valid_history_entry(tick=t) for t in range(15)]
        with pytest.warns(UserWarning, match="HISTORY_MAX_TICKS"):
            result = validate_history(history)
        assert result is None  # Validation succeeds despite warning

    def test_at_limit_no_warning(self):
        history = [_valid_history_entry(tick=t) for t in range(HISTORY_MAX_TICKS)]
        with warnings.catch_warnings():
            warnings.simplefilter("error")  # Convert any warning to error
            assert validate_history(history) is None

    def test_one_over_limit_warns(self):
        history = [_valid_history_entry(tick=t) for t in range(HISTORY_MAX_TICKS + 1)]
        with pytest.warns(UserWarning):
            validate_history(history)


class TestAC16DeepCopy:
    def test_player_state_round_trips(self):
        state = _valid_player_state()
        deep = copy.deepcopy(state)
        assert validate_player_state(deep) is None
        assert deep is not state
        assert deep == state

    def test_history_round_trips(self):
        history = [_valid_history_entry(tick=t) for t in (1, 2, 3)]
        deep = copy.deepcopy(history)
        assert validate_history(deep) is None
        assert deep is not history
        # Mutation isolation
        deep[0]["actions"][0]["details"]["foo"] = "bar"
        assert "foo" not in history[0]["actions"][0]["details"]


class TestAC17HistoryMaxTicksConstant:
    def test_default_value_matches_gdd(self):
        assert HISTORY_MAX_TICKS == 10

    def test_constant_is_int(self):
        assert isinstance(HISTORY_MAX_TICKS, int)
