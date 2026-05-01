"""
Tests for hash_01() deterministic RNG utility function.

Tests all 10 acceptance criteria from Story 003:
AC-1: Output range validation (0.0 <= result < 1.0)
AC-2: Output type validation (isinstance(result, float))
AC-3: Determinism - same args produce same result
AC-4: Known-value pinning (regression guard against algorithm drift)
AC-5: Variadic args - strings work
AC-6: Variadic args - integers work, with str() coercion
AC-7: Different args produce different values
AC-8: Tick increment changes output
AC-9: Pure function - no side effects
AC-10: Distribution uniformity smoke test
"""

import gc
import sys

import pytest

from src.foundation.simulation_utils import hash_01


class TestAC1OutputRange:
    """Test AC-1: Output range validation (0.0 <= result < 1.0)."""

    def test_hash_01_output_within_bounds_many_combinations(self):
        """Result is in [0.0, 1.0) for 1000 deterministic combinations."""
        for seed in range(1000):
            tick = seed % 100  # Vary tick too
            args = [f"player_{seed % 5}", f"action_{seed % 3}"]

            result = hash_01(seed, tick, *args)

            assert 0.0 <= result < 1.0, f"Result {result} out of bounds for seed={seed}, tick={tick}, args={args}"

    def test_hash_01_upper_bound_strict(self):
        """Result is strictly less than 1.0, never exactly 1.0."""
        # Test many combinations to increase confidence
        for seed in range(100):
            for tick in range(10):
                result = hash_01(seed, tick, "test")
                assert result < 1.0, f"Result {result} should be < 1.0"

    def test_hash_01_lower_bound_inclusive(self):
        """Result can be exactly 0.0 (inclusive lower bound)."""
        # This is probabilistic but we test enough combinations that
        # we should see at least one zero or very close to zero
        results = [hash_01(seed, 0, "zero_test") for seed in range(10000)]
        min_result = min(results)
        assert min_result >= 0.0, f"Minimum result {min_result} should be >= 0.0"


class TestAC2OutputType:
    """Test AC-2: Output type validation (isinstance(result, float))."""

    def test_hash_01_returns_float(self):
        """Result should be a Python float, not int or other type."""
        result = hash_01(42, 0)
        assert isinstance(result, float), f"Result {result} should be float, got {type(result)}"

    def test_hash_01_returns_float_with_args(self):
        """Result should be a Python float with variadic args."""
        result = hash_01(42, 5, "team_a_0", "pass")
        assert isinstance(result, float), f"Result {result} should be float, got {type(result)}"


class TestAC3DeterminismSameArgs:
    """Test AC-3: Determinism - same args produce same result."""

    def test_hash_01_same_args_same_result_exact_equality(self):
        """Same inputs always return identical floats (exact equality)."""
        result_a = hash_01(42, 5, "team_a_0", "pass")
        result_b = hash_01(42, 5, "team_a_0", "pass")

        assert result_a == result_b, f"Results should be identical: {result_a} != {result_b}"

    def test_hash_01_determinism_100_calls(self):
        """100 calls with same args should all return identical results."""
        expected = hash_01(123, 10, "player_test", "action")

        for i in range(100):
            result = hash_01(123, 10, "player_test", "action")
            assert result == expected, f"Call {i}: expected {expected}, got {result}"


class TestAC4KnownValuePinning:
    """Test AC-4: Known-value pinning (regression guard)."""

    def test_hash_01_known_reference_value(self):
        """Specific inputs produce specific output (regression test)."""
        # This value was computed once during implementation and is now pinned
        # as a regression guard against accidental algorithm changes
        result = hash_01(42, 5, "team_a_0", "pass")
        expected = 0.546607501571998  # Computed from the exact implementation

        assert result == expected, f"Known-value mismatch: expected {expected}, got {result}"


class TestAC5VariadicStrings:
    """Test AC-5: Variadic args - strings work."""

    def test_hash_01_multiple_string_args(self):
        """Function should accept multiple string arguments."""
        # Should not raise any exceptions
        result = hash_01(42, 5, "team_a_0", "pass", "extra_context")
        assert isinstance(result, float)
        assert 0.0 <= result < 1.0

    def test_hash_01_many_string_args(self):
        """Function should accept many string arguments."""
        args = [f"arg_{i}" for i in range(10)]
        result = hash_01(42, 5, *args)
        assert isinstance(result, float)
        assert 0.0 <= result < 1.0

    def test_hash_01_empty_string_args(self):
        """Function should handle empty string arguments."""
        result = hash_01(42, 5, "", "non_empty", "")
        assert isinstance(result, float)
        assert 0.0 <= result < 1.0


class TestAC6VariadicIntegers:
    """Test AC-6: Variadic args - integers work, with str() coercion."""

    def test_hash_01_integer_args(self):
        """Function should accept integer arguments."""
        result = hash_01(42, 5, 0, 1)
        assert isinstance(result, float)
        assert 0.0 <= result < 1.0

    def test_hash_01_integer_string_equivalence(self):
        """Integer 0 should produce same hash as string "0" (due to str() coercion)."""
        result_int = hash_01(42, 5, 0)
        result_str = hash_01(42, 5, "0")

        assert result_int == result_str, f"Integer 0 and string '0' should hash identically: {result_int} != {result_str}"

    def test_hash_01_mixed_types_work(self):
        """Function should handle mixed integer and string arguments."""
        result = hash_01(42, 5, "team_a", 0, "pass", 1)
        assert isinstance(result, float)
        assert 0.0 <= result < 1.0


class TestAC7DifferentArgsDifferentValues:
    """Test AC-7: Different args produce different values."""

    def test_hash_01_different_players_different_results(self):
        """Different player IDs should produce different hashes."""
        result_a = hash_01(42, 5, "team_a_0")
        result_b = hash_01(42, 5, "team_a_1")

        assert result_a != result_b, f"Different players should hash differently: {result_a} == {result_b}"

    def test_hash_01_different_contexts_different_results(self):
        """Different context strings should produce different hashes."""
        result_pass = hash_01(42, 5, "team_a_0", "pass")
        result_shot = hash_01(42, 5, "team_a_0", "shot")

        assert result_pass != result_shot, f"Different contexts should hash differently: {result_pass} == {result_shot}"

    def test_hash_01_different_seeds_different_results(self):
        """Different seeds should produce different hashes."""
        result_a = hash_01(42, 5, "test")
        result_b = hash_01(43, 5, "test")

        assert result_a != result_b, f"Different seeds should hash differently: {result_a} == {result_b}"


class TestAC8TickIncrementChangesOutput:
    """Test AC-8: Tick increment changes output."""

    def test_hash_01_tick_increment_changes_result(self):
        """Same player and context, different tick should produce different results."""
        result_tick5 = hash_01(42, 5, "team_a_0", "pass")
        result_tick6 = hash_01(42, 6, "team_a_0", "pass")

        assert result_tick5 != result_tick6, f"Different ticks should hash differently: {result_tick5} == {result_tick6}"

    def test_hash_01_many_tick_increments_unique(self):
        """Many consecutive ticks should produce unique results."""
        results = []
        for tick in range(100):
            result = hash_01(42, tick, "test")
            results.append(result)

        # All results should be unique
        unique_results = set(results)
        assert len(unique_results) == len(results), f"Expected 100 unique results, got {len(unique_results)}"


class TestAC9PureFunction:
    """Test AC-9: Pure function - no side effects."""

    def test_hash_01_no_module_globals_mutation(self):
        """Calling hash_01 should not mutate any module-level state."""
        # Capture module state before
        module = sys.modules['src.foundation.simulation_utils']
        globals_before = dict(module.__dict__)

        # Call the function
        hash_01(42, 0)

        # Check module state after
        globals_after = dict(module.__dict__)

        assert globals_before == globals_after, "Module globals were mutated by hash_01 call"

    def test_hash_01_no_gc_side_effects(self):
        """Calling hash_01 should not create unusual garbage collection patterns."""
        # Force garbage collection to stabilize
        gc.collect()
        gc_before = gc.get_count()

        # Call the function many times
        for i in range(100):
            hash_01(42, i, "test")

        # Garbage collection counts should be reasonable
        gc_after = gc.get_count()

        # This is a smoke test - we expect some allocation but not unbounded growth
        # The specific numbers aren't critical, we're just checking for obvious leaks
        total_objects_created = sum(a - b for a, b in zip(gc_after, gc_before))
        assert total_objects_created < 10000, f"Excessive object creation: {total_objects_created} new objects"

    def test_hash_01_repeated_calls_no_mutation_observable(self):
        """Multiple calls with same args should behave identically (no hidden state)."""
        # If there were hidden state mutations, behavior might change over time
        first_batch = [hash_01(42, i, "test") for i in range(10)]
        second_batch = [hash_01(42, i, "test") for i in range(10)]

        assert first_batch == second_batch, "Function behavior changed between call batches (hidden state mutation?)"


class TestAC10DistributionUniformity:
    """Test AC-10: Distribution uniformity smoke test."""

    def test_hash_01_mean_approximately_half(self):
        """1000 calls should produce roughly uniform [0,1) distribution (mean ≈ 0.5)."""
        results = [hash_01(42, t, "x") for t in range(1000)]
        mean = sum(results) / len(results)

        # Tolerance ± 0.05 as specified in the story
        assert 0.45 <= mean <= 0.55, f"Mean {mean} outside expected range [0.45, 0.55]"

    def test_hash_01_distribution_coverage(self):
        """1000 calls should cover a reasonable range of [0,1)."""
        results = [hash_01(42, t, "coverage") for t in range(1000)]
        min_val = min(results)
        max_val = max(results)

        # We should see results spread across a good portion of [0,1)
        # Not a strict requirement but indicates the hash is working
        assert min_val < 0.1, f"Minimum value {min_val} suggests poor low-end coverage"
        assert max_val > 0.9, f"Maximum value {max_val} suggests poor high-end coverage"