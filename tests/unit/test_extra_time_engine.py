"""Extra-time state machine (issue #83). Uses real config + a tiny tick budget."""
import pytest
from src.orchestration.tick_engine.engine import TickEngine


def test_scores_level_helper():
    eng = TickEngine()

    class _GSM:
        class state:
            score = {"team_a": 1, "team_b": 1}
    assert eng._scores_level(_GSM()) is True
    _GSM.state.score = {"team_a": 2, "team_b": 1}
    assert eng._scores_level(_GSM()) is False


def test_extra_time_tick_math():
    eng = TickEngine()
    # 3000-tick regulation, ratio 1/3 → 1000 ET ticks, 500 per half.
    et_total, et_half = eng._extra_time_ticks(regulation_total=3000, ratio=1 / 3)
    assert et_total == 1000
    assert et_half == 500


def test_extra_time_ticks_minimum_two():
    eng = TickEngine()
    # Degenerate ratio rounds to <2 → clamp so two halves exist.
    et_total, et_half = eng._extra_time_ticks(regulation_total=2, ratio=0.0)
    assert et_total >= 2 and et_half >= 1
