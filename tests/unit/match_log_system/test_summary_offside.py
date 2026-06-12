"""Issue #31 — offsides surfaced in the PMEP match summary.

The evolution LLM only sees generate_summary() output, so the offside
signal must be aggregated per team (stats block) and attributed in the
KEY EVENTS lines — otherwise strategies can't learn to stop goal-hanging.
"""

from __future__ import annotations

from src.core.match_log_system import ActionRecord, TickRecord, MatchLog


def _offside_tick(tick: int, offender_pid: str = "team_a_8",
                  offender_team: str = "team_a",
                  restart_team: str = "team_b") -> TickRecord:
    actions = [
        ActionRecord(
            player_id="system", team="system", action="hold", result="ok",
            details={
                "offside": True,
                "offender_id": offender_pid,
                "restart_type": "free_kick_offside",
                "restart_team": restart_team,
                "kicker_id": f"{restart_team}_1",
            },
        ),
        ActionRecord(
            player_id=offender_pid, team=offender_team, action="hold",
            result="ok", details={"offside_offence": True},
        ),
    ]
    return TickRecord(
        tick=tick,
        ball_position=(50.0, 30.0),
        ball_possession=None,
        score={"team_a": 0, "team_b": 0},
        player_positions={},
        actions=actions,
        is_key_event=True,
        event_type="offside",
    )


def _finalized_log(*ticks: TickRecord) -> MatchLog:
    ml = MatchLog("test-match")
    for tr in ticks:
        ml.record_tick(tr)
    ml.finalize({"final_score": {"team_a": 0, "team_b": 0}})
    return ml


def test_team_section_counts_offsides_for_offending_team():
    ml = _finalized_log(
        _offside_tick(100),
        _offside_tick(200, offender_pid="team_a_9"),
        _offside_tick(300, offender_pid="team_b_9", offender_team="team_b",
                      restart_team="team_a"),
    )
    summary = ml.generate_summary()
    team_a_section = summary.split("TEAM A:")[1].split("TEAM B:")[0]
    team_b_section = summary.split("TEAM B:")[1].split("KEY EVENTS")[0]
    assert "Offsides: 2" in team_a_section
    assert "Offsides: 1" in team_b_section


def test_team_section_shows_zero_offsides_when_none():
    ml = _finalized_log()
    summary = ml.generate_summary()
    assert "Offsides: 0" in summary


def test_key_event_line_attributes_offside_to_offender():
    ml = _finalized_log(_offside_tick(101))
    summary = ml.generate_summary()
    assert "[101] offside: team_a_8 flagged — free kick to team_b" in summary
