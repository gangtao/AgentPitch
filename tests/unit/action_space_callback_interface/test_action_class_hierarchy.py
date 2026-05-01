"""Tests for Action class hierarchy.

Tests all 12 acceptance criteria from Story 001:
AC-1: Action base class is a marker
AC-2: All 5 subclasses are Action subclasses
AC-3: Frozen dataclass enforcement — Move
AC-4: Frozen dataclass enforcement — all subclasses
AC-5: Move signature
AC-6: Pass signature
AC-7: Shoot signature
AC-8: Tackle signature — TR-ASCI-005, ADR-0004
AC-9: Hold signature
AC-10: Dispatch by isinstance
AC-11: Invalid-return detection — AC-ASCI-04 partial
AC-12: Equality and hashing
"""

import dataclasses
import pytest
from src.foundation.action import Action, Move, Pass, Shoot, Tackle, Hold


class TestAC1ActionBaseClassIsAMarker:
    """AC-1: Action base class is a marker."""

    def test_action_exists_and_is_importable(self):
        """Action exists as an importable class."""
        from src.foundation.action import Action
        assert isinstance(Action, type)

    def test_action_is_a_class(self):
        """Action is a class."""
        assert isinstance(Action, type)

    def test_action_can_be_instantiated(self):
        """Action can be instantiated (marker class)."""
        # This should not raise an exception
        action = Action()
        assert isinstance(action, Action)


class TestAC2All5SubclassesAreActionSubclasses:
    """AC-2: All 5 subclasses are Action subclasses."""

    def test_all_subclasses_isinstance_action(self):
        """Each subclass instance is an instance of Action."""
        move = Move(dx=1.0, dy=0.0, speed=0.5)
        pass_action = Pass(target_pos=(50.0, 25.0), power=10)
        shoot = Shoot(angle=12.0, power=18)
        tackle = Tackle(target_player_id="team_b_3")
        hold = Hold()

        assert isinstance(move, Action)
        assert isinstance(pass_action, Action)
        assert isinstance(shoot, Action)
        assert isinstance(tackle, Action)
        assert isinstance(hold, Action)

    def test_all_subclasses_issubclass_action(self):
        """Each subclass type is a subclass of Action."""
        assert issubclass(Move, Action)
        assert issubclass(Pass, Action)
        assert issubclass(Shoot, Action)
        assert issubclass(Tackle, Action)
        assert issubclass(Hold, Action)


class TestAC3FrozenDataclassEnforcementMove:
    """AC-3: Frozen dataclass enforcement — Move."""

    def test_move_speed_mutation_raises_frozen_error(self):
        """Move field cannot be mutated — speed."""
        move = Move(dx=1.0, dy=0.0, speed=0.5)
        with pytest.raises(dataclasses.FrozenInstanceError):
            move.speed = 0.9  # type: ignore

    def test_move_dx_mutation_raises_frozen_error(self):
        """Move field cannot be mutated — dx."""
        move = Move(dx=1.0, dy=0.0, speed=0.5)
        with pytest.raises(dataclasses.FrozenInstanceError):
            move.dx = 2.0  # type: ignore

    def test_move_dy_mutation_raises_frozen_error(self):
        """Move field cannot be mutated — dy."""
        move = Move(dx=1.0, dy=0.0, speed=0.5)
        with pytest.raises(dataclasses.FrozenInstanceError):
            move.dy = 3.0  # type: ignore


class TestAC4FrozenDataclassEnforcementAllSubclasses:
    """AC-4: Frozen dataclass enforcement — all subclasses."""

    def test_pass_mutation_raises_frozen_error(self):
        """Pass field cannot be mutated."""
        pass_action = Pass(target_pos=(50.0, 25.0), power=10)
        with pytest.raises(dataclasses.FrozenInstanceError):
            pass_action.power = 15  # type: ignore

    def test_shoot_mutation_raises_frozen_error(self):
        """Shoot field cannot be mutated."""
        shoot = Shoot(angle=12.0, power=18)
        with pytest.raises(dataclasses.FrozenInstanceError):
            shoot.angle = 20.0  # type: ignore

    def test_tackle_mutation_raises_frozen_error(self):
        """Tackle field cannot be mutated."""
        tackle = Tackle(target_player_id="team_b_3")
        with pytest.raises(dataclasses.FrozenInstanceError):
            tackle.target_player_id = "team_b_4"  # type: ignore

    def test_hold_new_attribute_raises_frozen_error(self):
        """Hold cannot have new attributes added (frozen + no fields)."""
        hold = Hold()
        with pytest.raises(dataclasses.FrozenInstanceError):
            hold.foo = 1  # type: ignore


class TestAC5MoveSignature:
    """AC-5: Move signature."""

    def test_move_required_fields_construction_succeeds(self):
        """Move with all required fields succeeds."""
        move = Move(dx=1.0, dy=0.0, speed=1.0)
        assert move.dx == 1.0
        assert move.dy == 0.0
        assert move.speed == 1.0

    def test_move_no_args_raises_type_error(self):
        """Move() with no args raises TypeError."""
        with pytest.raises(TypeError, match="missing.*required.*argument"):
            Move()  # type: ignore

    def test_move_missing_dx_raises_type_error(self):
        """Move missing dx raises TypeError."""
        with pytest.raises(TypeError, match="missing.*required.*argument"):
            Move(dy=0.0, speed=1.0)  # type: ignore

    def test_move_positional_construction_works(self):
        """Move accepts positional arguments."""
        move = Move(1.0, 0.0, 1.0)
        assert move.dx == 1.0
        assert move.dy == 0.0
        assert move.speed == 1.0

    def test_move_extra_args_raises_type_error(self):
        """Move with extra args raises TypeError."""
        with pytest.raises(TypeError):
            Move(dx=1.0, dy=0.0, speed=1.0, extra=42)  # type: ignore


class TestAC6PassSignature:
    """AC-6: Pass signature."""

    def test_pass_required_fields_construction_succeeds(self):
        """Pass with all required fields succeeds."""
        pass_action = Pass(target_pos=(50.0, 25.0), power=10)
        assert pass_action.target_pos == (50.0, 25.0)
        assert pass_action.power == 10

    def test_pass_missing_power_raises_type_error(self):
        """Pass missing power raises TypeError."""
        with pytest.raises(TypeError, match="missing.*required.*argument"):
            Pass(target_pos=(50.0, 25.0))  # type: ignore

    def test_pass_missing_target_pos_raises_type_error(self):
        """Pass missing target_pos raises TypeError."""
        with pytest.raises(TypeError, match="missing.*required.*argument"):
            Pass(power=10)  # type: ignore


class TestAC7ShootSignature:
    """AC-7: Shoot signature."""

    def test_shoot_required_fields_construction_succeeds(self):
        """Shoot with all required fields succeeds."""
        shoot = Shoot(angle=12.0, power=18)
        assert shoot.angle == 12.0
        assert shoot.power == 18

    def test_shoot_missing_angle_raises_type_error(self):
        """Shoot missing angle raises TypeError."""
        with pytest.raises(TypeError, match="missing.*required.*argument"):
            Shoot(power=18)  # type: ignore

    def test_shoot_missing_power_raises_type_error(self):
        """Shoot missing power raises TypeError."""
        with pytest.raises(TypeError, match="missing.*required.*argument"):
            Shoot(angle=12.0)  # type: ignore


class TestAC8TackleSignatureTRASCI005ADR0004:
    """AC-8: Tackle signature — TR-ASCI-005, ADR-0004."""

    def test_tackle_target_player_id_annotation_is_str(self):
        """Tackle.target_player_id is annotated as str."""
        fields = dataclasses.fields(Tackle)
        assert len(fields) == 1
        target_field = fields[0]
        assert target_field.name == "target_player_id"
        # With `from __future__ import annotations`, type is stored as string
        assert target_field.type == "str"

    def test_tackle_construction_with_str_succeeds(self):
        """Tackle with string player_id succeeds."""
        tackle = Tackle(target_player_id="team_b_3")
        assert tackle.target_player_id == "team_b_3"

    def test_tackle_stores_string_verbatim(self):
        """Tackle stores the string verbatim."""
        tackle = Tackle(target_player_id="team_b_3")
        assert tackle.target_player_id == "team_b_3"
        assert isinstance(tackle.target_player_id, str)

    def test_tackle_accepts_int_but_annotation_documents_str(self):
        """Tackle accepts int (Python doesn't enforce annotations) but annotation is str."""
        # Python doesn't enforce type annotations at runtime
        tackle = Tackle(target_player_id=3)  # type: ignore
        assert tackle.target_player_id == 3

        # But the annotation still documents the contract as str
        fields = dataclasses.fields(Tackle)
        assert fields[0].type == "str"


class TestAC9HoldSignature:
    """AC-9: Hold signature."""

    def test_hold_zero_args_succeeds(self):
        """Hold() with no args succeeds."""
        hold = Hold()
        assert isinstance(hold, Hold)
        assert isinstance(hold, Action)

    def test_hold_unexpected_keyword_raises_type_error(self):
        """Hold(foo=1) raises TypeError."""
        with pytest.raises(TypeError, match="unexpected keyword argument"):
            Hold(foo=1)  # type: ignore


class TestAC10DispatchByIsinstance:
    """AC-10: Dispatch by isinstance."""

    def test_each_subclass_isinstance_own_type_only(self):
        """Each subclass returns True for its own type, False for others."""
        move = Move(dx=1.0, dy=0.0, speed=0.5)
        pass_action = Pass(target_pos=(50.0, 25.0), power=10)
        shoot = Shoot(angle=12.0, power=18)
        tackle = Tackle(target_player_id="team_b_3")
        hold = Hold()

        # Move
        assert isinstance(move, Move)
        assert not isinstance(move, Pass)
        assert not isinstance(move, Shoot)
        assert not isinstance(move, Tackle)
        assert not isinstance(move, Hold)

        # Pass
        assert not isinstance(pass_action, Move)
        assert isinstance(pass_action, Pass)
        assert not isinstance(pass_action, Shoot)
        assert not isinstance(pass_action, Tackle)
        assert not isinstance(pass_action, Hold)

        # Shoot
        assert not isinstance(shoot, Move)
        assert not isinstance(shoot, Pass)
        assert isinstance(shoot, Shoot)
        assert not isinstance(shoot, Tackle)
        assert not isinstance(shoot, Hold)

        # Tackle
        assert not isinstance(tackle, Move)
        assert not isinstance(tackle, Pass)
        assert not isinstance(tackle, Shoot)
        assert isinstance(tackle, Tackle)
        assert not isinstance(tackle, Hold)

        # Hold
        assert not isinstance(hold, Move)
        assert not isinstance(hold, Pass)
        assert not isinstance(hold, Shoot)
        assert not isinstance(hold, Tackle)
        assert isinstance(hold, Hold)

    def test_isinstance_cross_checks_false(self):
        """Cross-type isinstance checks return False."""
        hold = Hold()
        move = Move(0, 0, 0)

        assert not isinstance(hold, Move)
        assert not isinstance(move, Hold)


class TestAC11InvalidReturnDetectionACASCI04Partial:
    """AC-11: Invalid-return detection — AC-ASCI-04 partial."""

    def test_none_is_not_action(self):
        """None fails isinstance Action check."""
        assert not isinstance(None, Action)

    def test_bool_is_not_action(self):
        """Boolean fails isinstance Action check."""
        assert not isinstance(True, Action)
        assert not isinstance(False, Action)

    def test_int_is_not_action(self):
        """Integer fails isinstance Action check."""
        assert not isinstance(42, Action)

    def test_str_is_not_action(self):
        """String fails isinstance Action check."""
        assert not isinstance("move", Action)

    def test_dict_is_not_action(self):
        """Dictionary fails isinstance Action check."""
        assert not isinstance({"action": "move"}, Action)

    def test_list_is_not_action(self):
        """List fails isinstance Action check."""
        assert not isinstance([1, 2, 3], Action)

    def test_provides_predicate_for_fallback_handler(self):
        """isinstance(result, Action) provides the predicate for Fallback Handler."""
        # Valid Action instances
        valid_actions = [
            Move(1.0, 0.0, 0.5),
            Pass((50.0, 25.0), 10),
            Shoot(12.0, 18),
            Tackle("team_b_3"),
            Hold()
        ]

        for action in valid_actions:
            assert isinstance(action, Action)

        # Invalid returns
        invalid_returns = [None, True, 42, "move", {"action": "move"}, [1, 2, 3]]

        for invalid in invalid_returns:
            assert not isinstance(invalid, Action)


class TestAC12EqualityAndHashing:
    """AC-12: Equality and hashing."""

    def test_two_identical_moves_compare_equal(self):
        """Two Move instances with same values compare equal."""
        move1 = Move(1.0, 0.0, 0.5)
        move2 = Move(1.0, 0.0, 0.5)
        assert move1 == move2

    def test_hold_instances_compare_equal(self):
        """Hold instances compare equal."""
        hold1 = Hold()
        hold2 = Hold()
        assert hold1 == hold2

    def test_frozen_actions_are_hashable(self):
        """Frozen dataclasses are hashable."""
        move = Move(1.0, 0.0, 0.5)
        pass_action = Pass((50.0, 25.0), 10)
        shoot = Shoot(12.0, 18)
        tackle = Tackle("team_b_3")
        hold = Hold()

        # These should not raise TypeError
        hash(move)
        hash(pass_action)
        hash(shoot)
        hash(tackle)
        hash(hold)

    def test_move_hash_works(self):
        """Move instances can be hashed."""
        move = Move(1.0, 0.0, 0.5)
        move_hash = hash(move)
        assert isinstance(move_hash, int)

    def test_identical_moves_have_same_hash(self):
        """Identical Move instances have same hash."""
        move1 = Move(1.0, 0.0, 0.5)
        move2 = Move(1.0, 0.0, 0.5)
        assert hash(move1) == hash(move2)

    def test_different_moves_have_different_values(self):
        """Different Move instances compare unequal."""
        move1 = Move(1.0, 0.0, 0.5)
        move2 = Move(1.0, 0.0, 0.8)
        assert move1 != move2