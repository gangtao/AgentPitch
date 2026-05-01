"""
Tests for ROLE_DEFAULTS module constant in player_attribute.py.

Tests all 9 acceptance criteria from Story 002:
AC-1: All 4 roles present {"GK", "DEF", "MID", "FWD"}
AC-2-5: Per-role exact value match against PAM GDD Role Defaults table
AC-6: All values are int; non-save in [1,20]; save in [0,20]
AC-7: save == 0 for DEF/MID/FWD; save == 16 for GK
AC-8: Each role has exactly 6 keys: speed, skill, strength, save, discipline, dribbling
AC-9: Cross-doc consistency — values match ADR-0003 documented values
"""

import pytest
from pydantic import ValidationError

from src.foundation.player_attribute import ROLE_DEFAULTS, PlayerAttribute


class TestAC1AllRolesPresent:
    """Test AC-1: ROLE_DEFAULTS has exactly 4 entries."""

    def test_role_defaults_has_all_four_roles(self):
        """ROLE_DEFAULTS should contain exactly the 4 expected role keys."""
        actual_roles = set(ROLE_DEFAULTS.keys())
        expected_roles = {"GK", "DEF", "MID", "FWD"}
        assert actual_roles == expected_roles


# PAM GDD Role Defaults table embedded for cross-doc consistency testing (AC-9)
# This is the authoritative source — if these values diverge from ROLE_DEFAULTS,
# it indicates regression/drift from the GDD requirements.
_PAM_GDD_ROLE_DEFAULTS = {
    "GK":  {"speed": 8,  "skill": 10, "strength": 8,  "save": 16, "discipline": 14, "dribbling": 4},
    "DEF": {"speed": 12, "skill": 8,  "strength": 16, "save": 0,  "discipline": 16, "dribbling": 6},
    "MID": {"speed": 14, "skill": 16, "strength": 10, "save": 0,  "discipline": 14, "dribbling": 12},
    "FWD": {"speed": 16, "skill": 14, "strength": 14, "save": 0,  "discipline": 10, "dribbling": 16},
}


class TestAC2Through5PerRoleValues:
    """Test AC-2 through AC-5: Per-role exact value match against PAM GDD."""

    @pytest.mark.parametrize("role", ["GK", "DEF", "MID", "FWD"])
    def test_role_defaults_exact_values_match_gdd(self, role):
        """Each role's default values should match PAM GDD Role Defaults table exactly."""
        actual = ROLE_DEFAULTS[role]
        expected = _PAM_GDD_ROLE_DEFAULTS[role]
        assert actual == expected, f"Role {role} defaults mismatch: got {actual}, expected {expected}"

    def test_role_defaults_gk_values_specific(self):
        """GK defaults should match specification exactly (AC-2)."""
        expected = {"speed": 8, "skill": 10, "strength": 8, "save": 16, "discipline": 14, "dribbling": 4}
        assert ROLE_DEFAULTS["GK"] == expected

    def test_role_defaults_def_values_specific(self):
        """DEF defaults should match specification exactly (AC-3)."""
        expected = {"speed": 12, "skill": 8, "strength": 16, "save": 0, "discipline": 16, "dribbling": 6}
        assert ROLE_DEFAULTS["DEF"] == expected

    def test_role_defaults_mid_values_specific(self):
        """MID defaults should match specification exactly (AC-4)."""
        expected = {"speed": 14, "skill": 16, "strength": 10, "save": 0, "discipline": 14, "dribbling": 12}
        assert ROLE_DEFAULTS["MID"] == expected

    def test_role_defaults_fwd_values_specific(self):
        """FWD defaults should match specification exactly (AC-5)."""
        expected = {"speed": 16, "skill": 14, "strength": 14, "save": 0, "discipline": 10, "dribbling": 16}
        assert ROLE_DEFAULTS["FWD"] == expected


class TestAC6ValueRangeValidation:
    """Test AC-6: All values are int; non-save in [1,20]; save in [0,20]."""

    @pytest.mark.parametrize("role", ["GK", "DEF", "MID", "FWD"])
    def test_role_defaults_all_values_are_int(self, role):
        """Every default value should be an integer."""
        for attr_name, value in ROLE_DEFAULTS[role].items():
            assert isinstance(value, int), f"{role}.{attr_name} is {type(value)}, not int"

    @pytest.mark.parametrize("role", ["GK", "DEF", "MID", "FWD"])
    def test_role_defaults_non_save_in_range(self, role):
        """Non-save attributes should be in range [1,20]."""
        for attr_name, value in ROLE_DEFAULTS[role].items():
            if attr_name != "save":
                assert 1 <= value <= 20, f"{role}.{attr_name} = {value} not in [1,20]"

    @pytest.mark.parametrize("role", ["GK", "DEF", "MID", "FWD"])
    def test_role_defaults_save_in_range(self, role):
        """save should be in range [0,20]."""
        save = ROLE_DEFAULTS[role]["save"]
        assert 0 <= save <= 20, f"{role}.save = {save} not in [0,20]"

    @pytest.mark.parametrize("role", ["GK", "DEF", "MID", "FWD"])
    def test_role_defaults_schema_compatible(self, role):
        """Each role's defaults should create a valid PlayerAttribute when applied."""
        # This is a STRONG test — it validates defaults against the actual schema
        try:
            player = PlayerAttribute(
                player_id=f"test_{role.lower()}",
                team="test_team",
                role=role,
                **ROLE_DEFAULTS[role]
            )
            # If we get here, defaults are schema-compliant
            assert player.role == role
        except ValidationError as e:
            pytest.fail(f"ROLE_DEFAULTS[{role}] creates invalid PlayerAttribute: {e}")


class TestAC7SaveReachGKOnly:
    """Test AC-7: save == 0 for DEF/MID/FWD; save == 16 for GK."""

    @pytest.mark.parametrize("role", ["DEF", "MID", "FWD"])
    def test_role_defaults_non_gk_save_zero(self, role):
        """Non-GK roles should have save == 0."""
        assert ROLE_DEFAULTS[role]["save"] == 0, f"{role} save should be 0"

    def test_role_defaults_gk_save_sixteen(self):
        """GK role should have save == 16."""
        assert ROLE_DEFAULTS["GK"]["save"] == 16, "GK save should be 16"


class TestAC8RoleFieldCompleteness:
    """Test AC-8: Each role has exactly 6 keys: speed, skill, strength, save, discipline, dribbling."""

    @pytest.mark.parametrize("role", ["GK", "DEF", "MID", "FWD"])
    def test_role_defaults_has_all_six_attributes(self, role):
        """Each role should have exactly the 6 expected attribute keys."""
        actual_keys = set(ROLE_DEFAULTS[role].keys())
        expected_keys = {"speed", "skill", "strength", "save", "discipline", "dribbling"}
        assert actual_keys == expected_keys, f"Role {role} has wrong keys: got {actual_keys}, expected {expected_keys}"

    @pytest.mark.parametrize("role", ["GK", "DEF", "MID", "FWD"])
    def test_role_defaults_exactly_six_attributes(self, role):
        """Each role should have exactly 6 attributes."""
        assert len(ROLE_DEFAULTS[role]) == 6, f"Role {role} has {len(ROLE_DEFAULTS[role])} attributes, expected 6"


class TestAC9CrossDocConsistency:
    """Test AC-9: Cross-doc consistency — ROLE_DEFAULTS values match ADR-0003."""

    def test_role_defaults_matches_adr_values(self):
        """ROLE_DEFAULTS should match the values documented in ADR-0003."""
        # This test uses _PAM_GDD_ROLE_DEFAULTS which represents the ADR-0003 documented values
        # It's a regression guard against the 2026-04-20 drift fix mentioned in the story
        assert ROLE_DEFAULTS == _PAM_GDD_ROLE_DEFAULTS, (
            "ROLE_DEFAULTS has drifted from ADR-0003 documented values. "
            "This indicates code/docs are out of sync."
        )

    def test_role_defaults_adr_gdd_consistency_spot_check(self):
        """Spot check a few values to ensure cross-document consistency."""
        # High-impact values that would indicate systematic drift
        assert ROLE_DEFAULTS["GK"]["save"] == 16, "GK save drift from GDD"
        assert ROLE_DEFAULTS["FWD"]["speed"] == 16, "FWD speed drift from GDD"
        assert ROLE_DEFAULTS["DEF"]["strength"] == 16, "DEF strength drift from GDD"
        assert ROLE_DEFAULTS["MID"]["skill"] == 16, "MID skill drift from GDD"


class TestBonusImportability:
    """Bonus tests for importability and module-level constant behavior."""

    def test_role_defaults_importable_as_module_constant(self):
        """ROLE_DEFAULTS should be importable as a module-level constant."""
        # This test verifies the import works (already proven by the fact that this file runs)
        # but also checks that it's a proper constant (dict type, not callable, etc.)
        assert isinstance(ROLE_DEFAULTS, dict)
        assert len(ROLE_DEFAULTS) > 0

    def test_role_defaults_mutability_warning(self):
        """ROLE_DEFAULTS is mutable by convention — this test documents the risk."""
        # This isn't a requirement, but it documents the fact that ROLE_DEFAULTS
        # can be mutated (dict is mutable) — it's protected by convention, not enforcement
        original_gk_speed = ROLE_DEFAULTS["GK"]["speed"]

        # Temporarily mutate to show it's possible
        ROLE_DEFAULTS["GK"]["speed"] = 999
        assert ROLE_DEFAULTS["GK"]["speed"] == 999

        # Restore original value so other tests aren't affected
        ROLE_DEFAULTS["GK"]["speed"] = original_gk_speed
        assert ROLE_DEFAULTS["GK"]["speed"] == original_gk_speed