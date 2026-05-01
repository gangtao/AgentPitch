"""
Integration tests for MatchLog serialization (Story 007).

Tests all 12 acceptance criteria from
production/epics/match-log-system/story-007-serialization.md.

This is an integration-type story — tests filesystem isolation via tmp_path.
"""

from __future__ import annotations
import json
import os
import pytest
from pathlib import Path

from src.core.match_log_system import (
    ActionRecord,
    TickRecord,
    MatchLog,
    MatchNotFinalizedError,
)


def _create_test_action_record(action: str = "move", details: dict = None) -> ActionRecord:
    """Helper to construct a minimal ActionRecord for tests."""
    return ActionRecord(
        player_id="team_a_0",
        team="team_a",
        action=action,
        result="success",
        details=details if details is not None else {},
    )


def _create_test_tick_record(tick: int = 0, **overrides) -> TickRecord:
    """Helper to construct a minimal TickRecord for tests with sensible defaults."""
    defaults = {
        "tick": tick,
        "ball_position": (50.0, 30.0),
        "ball_possession": None,
        "score": {"team_a": 0, "team_b": 0},
        "player_positions": {f"team_{t}_{i}": [0.0, 0.0] for t in ("a", "b") for i in range(5)},
        "actions": [],
        "is_key_event": False,
        "event_type": None,
    }
    defaults.update(overrides)
    return TickRecord(**defaults)


class TestAC1FilesExistAndLineCounts:
    """AC-1 (files exist + line counts — AC-MLS-18): 5 ticks, finalize, serialize. events.jsonl exists with 5 lines; meta.json exists and is valid JSON."""

    def test_serialize_creates_both_files_with_correct_line_count(self, tmp_path):
        """After serialize(), both events.jsonl and meta.json exist with expected content."""
        ml = MatchLog("test-match-01")

        # Record 5 ticks
        for i in range(5):
            tr = _create_test_tick_record(tick=i)
            ml.record_tick(tr)

        ml.finalize({"final_score": {"team_a": 1, "team_b": 2}})
        result_dir = ml.serialize(str(tmp_path))

        events_path = result_dir / "events.jsonl"
        meta_path = result_dir / "meta.json"

        # Both files must exist
        assert events_path.exists()
        assert meta_path.exists()

        # events.jsonl must have exactly 5 lines
        with events_path.open() as f:
            lines = f.readlines()
        assert len(lines) == 5

        # meta.json must be valid JSON
        with meta_path.open() as f:
            meta_data = json.load(f)
        assert isinstance(meta_data, dict)


class TestAC2JSONLNotArray:
    """AC-2 (JSONL not array): each line is valid json.loads. File does NOT start with [."""

    def test_each_line_is_valid_json_object_not_array(self, tmp_path):
        """events.jsonl lines are individual JSON objects, not an array."""
        ml = MatchLog("test-match-01")

        # Record 3 ticks
        for i in range(3):
            tr = _create_test_tick_record(tick=i)
            ml.record_tick(tr)

        ml.finalize({})
        result_dir = ml.serialize(str(tmp_path))

        events_path = result_dir / "events.jsonl"
        with events_path.open() as f:
            content = f.read()

        # Should NOT start with [ (array)
        assert not content.startswith('[')

        # Each line should be valid JSON
        lines = content.strip().split('\n')
        for line in lines:
            if line.strip():  # Skip empty lines
                obj = json.loads(line)
                assert isinstance(obj, dict)


class TestAC3MetaJSONSchema:
    """AC-3 (meta.json schema): contains match_id, final_score, final_tick, key_event_indices."""

    def test_meta_json_contains_required_fields(self, tmp_path):
        """meta.json contains all required schema fields."""
        ml = MatchLog("test-match-01")

        tr = _create_test_tick_record(tick=0)
        ml.record_tick(tr)
        ml.finalize({"final_score": {"team_a": 1, "team_b": 2}})

        result_dir = ml.serialize(str(tmp_path))
        meta_path = result_dir / "meta.json"

        with meta_path.open() as f:
            meta = json.load(f)

        assert meta["match_id"] == "test-match-01"
        assert "final_score" in meta
        assert "final_tick" in meta
        assert "key_event_indices" in meta


class TestAC4FailedWrite:
    """AC-4 (failed write — AC-MLS-19 / EC-MLS-16): monkeypatch f.write to raise IOError after 100 lines. 200 ticks, finalize, attempt serialize → raises IOError. events.jsonl exists with ~100 lines; meta.json does NOT exist; meta.json.tmp does NOT exist."""

    def test_failed_events_write_leaves_no_meta_json(self, tmp_path, monkeypatch):
        """When events.jsonl write fails, meta.json is never created and temp files are cleaned."""
        ml = MatchLog("test-match-01")

        # Record 200 ticks
        for i in range(200):
            tr = _create_test_tick_record(tick=i)
            ml.record_tick(tr)

        ml.finalize({})

        # Simpler approach: patch json.dumps to fail after 100 calls
        import json
        original_dumps = json.dumps
        dumps_count = 0

        def failing_dumps(*args, **kwargs):
            nonlocal dumps_count
            dumps_count += 1
            if dumps_count > 100:
                raise IOError("Simulated disk failure")
            return original_dumps(*args, **kwargs)

        monkeypatch.setattr(json, "dumps", failing_dumps)

        # Serialize should raise IOError
        with pytest.raises(IOError, match="Simulated disk failure"):
            ml.serialize(str(tmp_path))

        # Check filesystem state
        result_dir = tmp_path / "match_test-match-01"
        events_path = result_dir / "events.jsonl"
        meta_path = result_dir / "meta.json"
        meta_tmp_path = result_dir / "meta.json.tmp"

        # events.jsonl should exist with ~100 lines
        assert events_path.exists()
        with events_path.open() as f:
            lines = f.readlines()
        assert 90 <= len(lines) <= 110  # Around 100 lines

        # meta.json should NOT exist
        assert not meta_path.exists()

        # meta.json.tmp should NOT exist (cleanup)
        assert not meta_tmp_path.exists()


class TestAC5OverwriteWarning:
    """AC-5 (overwrite warning — EC-MLS-15): pre-create files, serialize. caplog WARNING logged for both files mentioning "already exists"."""

    def test_overwrite_warning_logged_for_existing_files(self, tmp_path, caplog):
        """When files already exist, warnings are logged mentioning 'already exists'."""
        ml = MatchLog("test-match-01")

        tr = _create_test_tick_record(tick=0)
        ml.record_tick(tr)
        ml.finalize({})

        # Pre-create files
        result_dir = tmp_path / "match_test-match-01"
        result_dir.mkdir()
        events_path = result_dir / "events.jsonl"
        meta_path = result_dir / "meta.json"

        events_path.write_text("existing content")
        meta_path.write_text('{"existing": "meta"}')

        # Clear previous logs and serialize
        caplog.clear()
        ml.serialize(str(tmp_path))

        # Check warnings were logged
        warning_messages = [record.message for record in caplog.records if record.levelname == "WARNING"]

        # Should have warnings for both files
        events_warning = any("already exists" in msg and "events.jsonl" in msg for msg in warning_messages)
        meta_warning = any("already exists" in msg and "meta.json" in msg for msg in warning_messages)

        assert events_warning, f"No events.jsonl overwrite warning found in: {warning_messages}"
        assert meta_warning, f"No meta.json overwrite warning found in: {warning_messages}"


class TestAC6NonSerializableDetails:
    """AC-6 (non-serializable details — EC-MLS-17): ActionRecord with details={"good": 1, "bad": object()}. Serialize. events.jsonl line has "details": "__SERIALIZATION_ERROR__" for affected action; other ticks normal. ERROR logged."""

    def test_non_serializable_details_replaced_with_error_marker(self, tmp_path, caplog):
        """Non-serializable details are replaced with __SERIALIZATION_ERROR__ marker."""
        ml = MatchLog("test-match-01")

        # Create action with non-serializable details
        bad_action = ActionRecord(
            player_id="team_a_0",
            team="team_a",
            action="pass",
            result="success",
            details={"good_field": 1, "bad_field": object()}  # object() is not JSON serializable
        )

        good_action = _create_test_action_record(action="move", details={"normal": "data"})

        # Record ticks: one with bad action, one normal
        tr_bad = _create_test_tick_record(tick=0, actions=[bad_action])
        tr_good = _create_test_tick_record(tick=1, actions=[good_action])

        ml.record_tick(tr_bad)
        ml.record_tick(tr_good)
        ml.finalize({})

        caplog.clear()
        result_dir = ml.serialize(str(tmp_path))

        # Read events.jsonl
        events_path = result_dir / "events.jsonl"
        with events_path.open() as f:
            lines = f.readlines()

        # Parse first line (should have error marker)
        tick_0_data = json.loads(lines[0])
        assert tick_0_data["actions"][0]["details"] == "__SERIALIZATION_ERROR__"

        # Parse second line (should be normal)
        tick_1_data = json.loads(lines[1])
        assert tick_1_data["actions"][0]["details"] == {"normal": "data"}

        # Check ERROR was logged
        error_messages = [record.message for record in caplog.records if record.levelname == "ERROR"]
        assert any("non-serializable" in msg for msg in error_messages)


class TestAC7RoundTripIntegrity:
    """AC-7 (round-trip integrity): 10 TickRecords, serialize, read events.jsonl line-by-line, json.loads each, assert each dict has expected fields matching original (tuple→list)."""

    def test_serialized_data_matches_original_tick_records(self, tmp_path):
        """Serialized data can be read back and matches original records."""
        ml = MatchLog("test-match-01")

        original_records = []
        # Create 10 varied tick records
        for i in range(10):
            action = _create_test_action_record(
                action=["move", "pass", "shoot"][i % 3],
                details={"attempt": i, "player_x": float(i * 10)}
            )
            tr = _create_test_tick_record(
                tick=i,
                ball_position=(float(i), float(i + 5)),
                ball_possession=["team_a", "team_b", None][i % 3],
                score={"team_a": i // 5, "team_b": i // 7},
                actions=[action],
                is_key_event=(i % 3 == 0),
                event_type="goal" if i == 5 else None
            )
            original_records.append(tr)
            ml.record_tick(tr)

        ml.finalize({})
        result_dir = ml.serialize(str(tmp_path))

        # Read back events.jsonl
        events_path = result_dir / "events.jsonl"
        with events_path.open() as f:
            lines = f.readlines()

        assert len(lines) == 10

        # Verify each line matches the original record
        for i, line in enumerate(lines):
            serialized = json.loads(line.strip())
            original = original_records[i]

            # Key field comparisons (tuples become lists in JSON)
            assert serialized["tick"] == original.tick
            assert serialized["ball_position"] == list(original.ball_position)
            assert serialized["ball_possession"] == original.ball_possession
            assert serialized["score"] == original.score
            assert serialized["is_key_event"] == original.is_key_event
            assert serialized["event_type"] == original.event_type

            # Actions comparison
            assert len(serialized["actions"]) == len(original.actions)
            for j, action_data in enumerate(serialized["actions"]):
                orig_action = original.actions[j]
                assert action_data["player_id"] == orig_action.player_id
                assert action_data["team"] == orig_action.team
                assert action_data["action"] == orig_action.action
                assert action_data["result"] == orig_action.result
                assert action_data["details"] == orig_action.details


class TestAC8AtomicTempFileCleaned:
    """AC-8 (Atomic — temp file cleaned): after successful serialize, meta.json.tmp does NOT exist."""

    def test_temp_file_cleaned_after_successful_serialize(self, tmp_path):
        """meta.json.tmp is cleaned up after successful atomic write."""
        ml = MatchLog("test-match-01")

        tr = _create_test_tick_record(tick=0)
        ml.record_tick(tr)
        ml.finalize({})

        result_dir = ml.serialize(str(tmp_path))

        meta_tmp_path = result_dir / "meta.json.tmp"
        meta_path = result_dir / "meta.json"

        # meta.json should exist
        assert meta_path.exists()

        # meta.json.tmp should NOT exist (cleaned up)
        assert not meta_tmp_path.exists()


class TestAC9EmptyMatchSerialization:
    """AC-9 (Empty match T=0): finalize empty MatchLog, serialize. events.jsonl exists with 0 lines. meta.json valid with tick_count: 0, final_tick: 0."""

    def test_empty_match_serializes_correctly(self, tmp_path):
        """Empty MatchLog (no ticks) can be serialized successfully."""
        ml = MatchLog("test-empty-match")

        # Finalize without recording any ticks
        ml.finalize({"final_score": {"team_a": 0, "team_b": 0}})
        result_dir = ml.serialize(str(tmp_path))

        events_path = result_dir / "events.jsonl"
        meta_path = result_dir / "meta.json"

        # events.jsonl should exist but be empty
        assert events_path.exists()
        assert events_path.stat().st_size == 0

        # meta.json should exist with correct zero values
        with meta_path.open() as f:
            meta = json.load(f)

        assert meta["tick_count"] == 0
        assert meta["final_tick"] == 0
        assert meta["key_event_indices"] == []


class TestAC10LIVEStateRaises:
    """AC-10 (LIVE state raises): serialize without finalize → raises MatchNotFinalizedError."""

    def test_serialize_on_live_match_raises_error(self, tmp_path):
        """Calling serialize() on a LIVE match raises MatchNotFinalizedError."""
        ml = MatchLog("test-live-match")

        tr = _create_test_tick_record(tick=0)
        ml.record_tick(tr)

        # Don't call finalize() - state remains LIVE

        with pytest.raises(MatchNotFinalizedError, match="serialize called on LIVE match"):
            ml.serialize(str(tmp_path))


class TestAC11FilesystemOnlyDesignAssertion:
    """AC-11 (Filesystem-only — ADR-0006): serialize() returns a Path, not data. Document in test docstring as design assertion."""

    def test_serialize_returns_path_not_data(self, tmp_path):
        """
        Design assertion per ADR-0006: serialize() returns filesystem Path,
        not in-memory data, to enforce process isolation between simulation
        and HTTP server.
        """
        ml = MatchLog("test-match-01")

        tr = _create_test_tick_record(tick=0)
        ml.record_tick(tr)
        ml.finalize({})

        result = ml.serialize(str(tmp_path))

        # Result should be a Path object, not serialized data
        assert isinstance(result, Path)
        assert result.exists()
        assert result.is_dir()


class TestPerMatchStrategySnapshots:
    """serialize() drops <match_dir>/strategy_<team>.py for each team whose
    code was published via set_strategy_codes(). Lets the API viewer serve
    the exact code that ran in this match (vs. a global current.py that
    gets overwritten between runs)."""

    def test_serialize_writes_per_team_strategy_snapshot_when_codes_published(self, tmp_path):
        ml = MatchLog("test-match-01")
        code_a = "def decide(s, c, h):\n    return Hold()  # team_a"
        code_b = "def decide(s, c, h):\n    return Hold()  # team_b"
        ml.set_strategy_codes({"team_a": code_a, "team_b": code_b})

        ml.record_tick(_create_test_tick_record(tick=0))
        ml.finalize({})
        result_dir = ml.serialize(str(tmp_path))

        snap_a = result_dir / "strategy_team_a.py"
        snap_b = result_dir / "strategy_team_b.py"
        assert snap_a.exists() and snap_a.read_text() == code_a
        assert snap_b.exists() and snap_b.read_text() == code_b

    def test_serialize_omits_snapshots_when_codes_not_published(self, tmp_path):
        ml = MatchLog("test-match-02")
        ml.record_tick(_create_test_tick_record(tick=0))
        ml.finalize({})
        result_dir = ml.serialize(str(tmp_path))

        # Per-match snapshots are opt-in; without set_strategy_codes(), the
        # match dir contains only the standard events.jsonl + meta.json.
        assert not (result_dir / "strategy_team_a.py").exists()
        assert not (result_dir / "strategy_team_b.py").exists()


class TestAC12KeyEventIndicesInMeta:
    """AC-12 (key_event_indices in meta.json): 5 ticks, ticks 0,1,2 have is_key_event=True. meta["key_event_indices"] == [0, 1, 2]."""

    def test_key_event_indices_correctly_recorded_in_meta(self, tmp_path):
        """meta.json.key_event_indices contains correct indices of key events."""
        ml = MatchLog("test-match-01")

        # Record 5 ticks, with ticks 0, 1, 2 as key events
        key_event_flags = [True, True, True, False, False]
        for i, is_key in enumerate(key_event_flags):
            tr = _create_test_tick_record(tick=i, is_key_event=is_key)
            ml.record_tick(tr)

        ml.finalize({})
        result_dir = ml.serialize(str(tmp_path))

        meta_path = result_dir / "meta.json"
        with meta_path.open() as f:
            meta = json.load(f)

        assert meta["key_event_indices"] == [0, 1, 2]