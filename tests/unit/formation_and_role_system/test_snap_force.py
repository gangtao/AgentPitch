"""Tests for Formation & Role System snap force computation.

Per ADR-0013 (2026-04-22): formula is discipline/100 capped at 0.20.
Position_sense=20 hits cap exactly; discipline=1 → 0.01.

Tests all 8 acceptance criteria from Story 002:
AC-1: discipline=20 hits cap (AC-FORM-05/AC-FORM-08)
AC-2: discipline=1 minimum (AC-FORM-06)
AC-3: Mid-range discipline=16 (AC-FORM-07)
AC-4: Cap holds across all valid inputs (AC-FORM-08)
AC-5: Determinism
AC-6: Linear blend invariants (formula sanity)
AC-7: Hold() context (AC-FORM-07) - action-agnostic
AC-8: Public API surface
"""

import inspect
import pytest
from src.foundation.formation_and_role_system import compute_snap_force, SNAP_FORCE_CAP


class TestAC1PositionSense20HitsCap:
    """AC-1: discipline=20 hits cap (AC-FORM-05/AC-FORM-08)."""

    def test_discipline_20_returns_exact_cap(self):
        """Test discipline=20 returns exactly 0.20 (cap, per ADR-0013)."""
        result = compute_snap_force(20)
        assert result == 0.20
        assert result != 1.0

    def test_discipline_20_equals_snap_force_cap(self):
        """Test symbolic check: discipline=20 equals SNAP_FORCE_CAP."""
        result = compute_snap_force(20)
        assert result == SNAP_FORCE_CAP

    def test_discipline_20_returns_float_type(self):
        """Test result type is float."""
        result = compute_snap_force(20)
        assert isinstance(result, float)


class TestAC2PositionSense1Minimum:
    """AC-2: discipline=1 minimum (AC-FORM-06)."""

    def test_discipline_1_returns_0_01(self):
        """Test discipline=1 returns 0.01 (per ADR-0013 formula p/100)."""
        result = compute_snap_force(1)
        assert result == 0.01

    def test_discipline_1_under_cap(self):
        """Test 0.01 < SNAP_FORCE_CAP (no cap interaction at lower bound)."""
        result = compute_snap_force(1)
        assert result < SNAP_FORCE_CAP


class TestAC3MidRange:
    """AC-3: Mid-range discipline=16 (AC-FORM-07)."""

    def test_discipline_16_returns_0_16(self):
        """Test discipline=16 returns 0.16 (per ADR-0013 formula p/100)."""
        result = compute_snap_force(16)
        assert result == 0.16

    def test_discipline_16_follows_linear_rule(self):
        """Test intermediate values follow linear p/100 rule below cap."""
        result = compute_snap_force(16)
        expected = 16 / 100.0
        assert result == expected
        assert result < SNAP_FORCE_CAP


class TestAC4CapHoldsAcrossAllValidInputs:
    """AC-4: Cap holds across all valid inputs (AC-FORM-08)."""

    @pytest.mark.parametrize("p", range(1, 21))
    def test_cap_holds_for_all_discipline_values(self, p):
        """Test all discipline values in [1, 20] respect bounds."""
        result = compute_snap_force(p)
        assert result <= 0.20
        assert result < 1.0
        assert result >= 0.01

    @pytest.mark.parametrize("p", range(1, 20))
    def test_monotonic_non_decreasing(self, p):
        """Test strictly-monotonic-non-decreasing property."""
        current_result = compute_snap_force(p)
        next_result = compute_snap_force(p + 1)
        assert current_result <= next_result


class TestAC5Determinism:
    """AC-5: Determinism."""

    def test_repeated_calls_identical(self):
        """Test 1000 repeated calls produce identical output."""
        discipline = 7
        expected = 0.07  # 7/100 per ADR-0013

        results = [compute_snap_force(discipline) for _ in range(1000)]
        assert all(result == expected for result in results)

    def test_order_independence(self):
        """Test calling in different orders produces same values."""
        # Forward order
        forward_results = [compute_snap_force(p) for p in [1, 20, 10]]

        # Reverse order
        reverse_results = [compute_snap_force(p) for p in [10, 20, 1]]

        # Results should match when indexed properly
        assert forward_results[0] == reverse_results[2]  # discipline=1
        assert forward_results[1] == reverse_results[1]  # discipline=20
        assert forward_results[2] == reverse_results[0]  # discipline=10


class TestAC6LinearBlendInvariants:
    """AC-6: Linear blend invariants (formula sanity)."""

    @pytest.mark.parametrize("p", range(1, 21))
    def test_convex_combination_invariant(self, p):
        """Test (1 - snap_force) + snap_force == 1.0 for all valid inputs."""
        s = compute_snap_force(p)
        result = (1.0 - s) + s
        assert result == 1.0

    def test_cap_preserves_llm_contribution(self):
        """At cap, LLM intent contributes 80% (1.0 - 0.20). Per ADR-0013 the
        snap is a soft preference — even max discipline leaves the
        majority of motion under strategy control."""
        s = compute_snap_force(20)
        assert s == 0.20  # exact — cap reached at discipline=20
        llm_contribution = 1.0 - s
        # Use pytest.approx for the subtraction result due to floating point
        assert llm_contribution == pytest.approx(0.80)


class TestAC7HoldContextActionAgnostic:
    """AC-7: Hold() context (AC-FORM-07) - action-agnostic."""

    def test_discipline_16_action_agnostic(self):
        """Test discipline=16 returns 0.16 regardless of action source."""
        # This documents the contract - snap_force is independent of action type
        # (Hold() vs Move() is handled by PMS, not FRS)
        result = compute_snap_force(16)
        assert result == 0.16

        # Call multiple times to verify consistency
        hold_context_result = compute_snap_force(16)
        move_context_result = compute_snap_force(16)
        assert hold_context_result == move_context_result == 0.16


class TestAC8PublicAPISurface:
    """AC-8: Public API surface."""

    def test_function_importable_from_frs_module(self):
        """Test function can be imported from formation_and_role_system."""
        # Import was successful (tested by the import at top of file)
        assert callable(compute_snap_force)

    def test_function_signature_accepts_int_returns_float(self):
        """Test function signature accepts single int, returns float."""
        result = compute_snap_force(10)
        assert isinstance(result, float)

        # Test with int input
        int_input = 15
        result = compute_snap_force(int_input)
        assert isinstance(result, float)

    def test_function_parameter_named_discipline(self):
        """Test parameter is named 'discipline' per FRS GDD."""
        sig = inspect.signature(compute_snap_force)
        param_names = list(sig.parameters.keys())
        assert len(param_names) == 1
        assert param_names[0] == "discipline"

    def test_snap_force_cap_constant_importable(self):
        """Test SNAP_FORCE_CAP constant is importable. Per ADR-0013: 0.20."""
        # Import was successful (tested by the import at top of file)
        assert SNAP_FORCE_CAP == 0.20
        assert isinstance(SNAP_FORCE_CAP, float)