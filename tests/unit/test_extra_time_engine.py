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


def test_handle_pause_tick_emits_et_second_half_label(monkeypatch):
    """_handle_pause_tick must emit 'et_second_half' (not 'kick_off') during extra_time."""
    eng = TickEngine()
    eng._period = "extra_time"
    eng._halftime_pause_remaining = 1
    eng._second_half_kickoff_team = "team_a"

    class _FakeGSM:
        tick = 5
        total_ticks = 100

        def get_phase(self):
            return "half_time"

        def swap_attack_direction(self):
            pass

        def restore_all_health(self):
            pass

        def set_phase(self, phase):
            pass

    class _FakeLog:
        def __init__(self):
            self.transitions = []

        def record_phase_transition(self, tick, old, new):
            self.transitions.append((tick, old, new))

    gsm = _FakeGSM()
    fake_log = _FakeLog()

    monkeypatch.setattr(eng, "_setup_kickoff", lambda g, l, t: None)

    eng._handle_pause_tick(gsm, fake_log, config=None)

    resume_labels = [new for (_, old, new) in fake_log.transitions if old == "half_time"]
    assert "et_second_half" in resume_labels, f"Expected 'et_second_half', got {resume_labels}"


def test_handle_pause_tick_emits_kick_off_label_in_regulation(monkeypatch):
    """_handle_pause_tick must emit 'kick_off' (not 'et_second_half') in regulation."""
    eng = TickEngine()
    eng._period = "regulation"
    eng._halftime_pause_remaining = 1
    eng._second_half_kickoff_team = "team_a"

    class _FakeGSM:
        tick = 5
        total_ticks = 100

        def get_phase(self):
            return "half_time"

        def swap_attack_direction(self):
            pass

        def restore_all_health(self):
            pass

        def set_phase(self, phase):
            pass

    class _FakeLog:
        def __init__(self):
            self.transitions = []

        def record_phase_transition(self, tick, old, new):
            self.transitions.append((tick, old, new))

    gsm = _FakeGSM()
    fake_log = _FakeLog()

    monkeypatch.setattr(eng, "_setup_kickoff", lambda g, l, t: None)

    eng._handle_pause_tick(gsm, fake_log, config=None)

    resume_labels = [new for (_, old, new) in fake_log.transitions if old == "half_time"]
    assert "kick_off" in resume_labels, f"Expected 'kick_off', got {resume_labels}"
    assert "et_second_half" not in resume_labels, f"Got unexpected 'et_second_half' in regulation: {resume_labels}"


def test_build_shootout_knobs_reads_config():
    from src.orchestration.tick_engine.engine import TickEngine
    eng = TickEngine()

    class _Sim:
        penalty_goal_base = 0.6
        penalty_goal_per_point = 0.015
        penalty_save_per_point = 0.01

    knobs = eng._shootout_knobs(_Sim())
    assert knobs.base == 0.6
    assert knobs.per_point == 0.015
    assert knobs.save_per_point == 0.01
