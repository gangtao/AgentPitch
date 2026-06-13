"""Issue #38 — GSM card bookkeeping, send-off removal, and snapshot exclusion."""

import pytest

from src.core.game_state_manager import GameStateManager
from src.foundation.config_models import (
    MatchConfig, MatchParams, OutputConfig, PlayerConfig, TeamConfig,
)


def _team(team_id: str) -> TeamConfig:
    players = [PlayerConfig(
        player_id=f"{team_id}_{i}",
        role="GK" if i == 0 else "DEF" if i == 1 else "MID" if i in (2, 3) else "FWD",
        speed=10, skill=10, strength=10, save=10 if i == 0 else 0,
        discipline=10, dribbling=10,
        offensive=18 if i == 1 else 10,
        penalty=19 if i == 4 else None,
        shooting=14 if i == 4 else None,
    ) for i in range(5)]
    return TeamConfig(team_id=team_id.replace("_", "-"), name=team_id, players=players)


@pytest.fixture
def gsm() -> GameStateManager:
    config = MatchConfig(
        match=MatchParams(seed=42, tick_rate=10, duration_minutes=5,
                          field_width=100.0, field_height=60.0),
        output=OutputConfig(log_dir="./logs"),
        team_a=_team("team_a"),
        team_b=_team("team_b"),
    )
    anchors = {f"team_a_{i}": (10.0 + i, 30.0) for i in range(5)}
    anchors.update({f"team_b_{i}": (90.0 - i, 30.0) for i in range(5)})
    return GameStateManager(config, anchors)


class TestNewAttributesStored:
    def test_offensive_in_player_state(self, gsm):
        assert gsm.build_player_state("team_a_1")["offensive"] == 18
        assert gsm.build_player_state("team_a_0")["offensive"] == 10

    def test_penalty_falls_back_to_shooting(self, gsm):
        assert gsm.build_player_state("team_a_4")["penalty"] == 19
        # No penalty, no shooting → falls back to skill (10)
        assert gsm.build_player_state("team_a_2")["penalty"] == 10

    def test_yellow_cards_starts_zero(self, gsm):
        assert gsm.build_player_state("team_a_1")["yellow_cards"] == 0


class TestCards:
    def test_first_yellow_not_sent_off(self, gsm):
        assert gsm.record_card("team_a_1", "yellow") is False
        assert gsm.build_player_state("team_a_1")["yellow_cards"] == 1

    def test_second_yellow_sends_off(self, gsm):
        gsm.record_card("team_a_1", "yellow")
        assert gsm.record_card("team_a_1", "yellow") is True
        assert gsm.state.players["team_a_1"]["sent_off"] is True

    def test_straight_red_sends_off(self, gsm):
        assert gsm.record_card("team_a_1", "red") is True
        assert gsm.state.players["team_a_1"]["sent_off"] is True


class TestSendOffRemoval:
    def test_sent_off_excluded_from_snapshot(self, gsm):
        gsm.record_card("team_a_1", "red")
        snap = gsm.build_tick_snapshot()
        assert "team_a_1" not in snap["players"]
        assert len(snap["players"]) == 9

    def test_sent_off_carrier_drops_ball(self, gsm):
        gsm.transfer_possession(None, "team_a_1")
        gsm.record_card("team_a_1", "red")
        assert gsm.state.ball["carrier_id"] is None

    def test_kickoff_reset_skips_sent_off(self, gsm):
        gsm.record_card("team_a_1", "red")
        gsm.state.players["team_a_1"]["position"] = (1.0, 1.0)
        gsm.start_match()
        assert gsm.state.players["team_a_1"]["position"] == (1.0, 1.0)

    def test_nearest_player_skips_sent_off(self, gsm):
        gsm.record_card("team_a_1", "red")
        # team_a_1 anchor (11, 30) is nearest to (11, 30) but is sent off
        nearest = gsm._nearest_player_of_team("team_a", (11.0, 30.0))
        assert nearest != "team_a_1"
