"""Integration tests for Strategy Storage Story 003: read_current + read_version."""

from __future__ import annotations

import logging
import shutil

import pytest

from src.foundation import strategy_storage as ss
from src.foundation.strategy_storage import (
    StrategyMetadata,
    StrategyNotFoundError,
    VersionNotFoundError,
    read_current,
    read_version,
    write_strategy,
)


def _meta(**overrides) -> StrategyMetadata:
    base = {
        "team_id": "team_a",
        "match_number": 0,
        "llm_provider": "openai",
        "llm_model": "gpt-4o",
        "generated_by": "code-generation-pipeline",
    }
    base.update(overrides)
    return StrategyMetadata(**base)


CODE_A = "def decide(g, p, h):\n    return Hold()\n"
CODE_B = "def decide(g, p, h):\n    return Move(1.0, 0.0, 1.0)\n"


# ---------------------------------------------------------------------------
# AC-1: Round-trip happy path (AC-SS-04)
# ---------------------------------------------------------------------------


class TestAC1RoundTripHappyPath:
    def test_read_current_returns_full_file_content(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        result = read_current(str(tmp_path), "team_a")
        assert result.startswith("# strategy_v1.py\n# team_id:      team_a\n")
        assert CODE_A in result

    def test_read_current_length_matches_file(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        result = read_current(str(tmp_path), "team_a")
        on_disk = (tmp_path / "strategies" / "team_a" / "current.py").read_text()
        assert len(result) == len(on_disk)
        assert result == on_disk

    def test_empty_code_round_trip(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", "", _meta())
        result = read_current(str(tmp_path), "team_a")
        assert result.startswith("# strategy_v1.py\n")
        assert result.endswith("\n")  # at least header trailing blank


# ---------------------------------------------------------------------------
# AC-2: No directory → StrategyNotFoundError (AC-SS-05)
# ---------------------------------------------------------------------------


class TestAC2MissingStrategyRaises:
    def test_no_strategies_subtree_raises(self, tmp_path):
        with pytest.raises(StrategyNotFoundError, match="team_a"):
            read_current(str(tmp_path), "team_a")

    def test_strategies_exists_but_team_dir_missing(self, tmp_path):
        (tmp_path / "strategies").mkdir()
        with pytest.raises(StrategyNotFoundError, match="team_a"):
            read_current(str(tmp_path), "team_a")

    def test_team_dir_exists_but_empty(self, tmp_path):
        (tmp_path / "strategies" / "team_a").mkdir(parents=True)
        with pytest.raises(StrategyNotFoundError, match="team_a"):
            read_current(str(tmp_path), "team_a")


# ---------------------------------------------------------------------------
# AC-3: Self-heal — missing current.py (AC-SS-06)
# ---------------------------------------------------------------------------


class TestAC3SelfHealMissingCurrentPy:
    def test_repair_from_v1_when_current_deleted(self, tmp_path, caplog):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        (tmp_path / "strategies" / "team_a" / "current.py").unlink()

        with caplog.at_level(logging.WARNING):
            result = read_current(str(tmp_path), "team_a")

        # current.py recreated, byte-identical to v1
        v1_bytes = (tmp_path / "strategies" / "team_a" / "strategy_v1.py").read_bytes()
        cur_bytes = (tmp_path / "strategies" / "team_a" / "current.py").read_bytes()
        assert cur_bytes == v1_bytes

        # Returned string equals v1 content
        assert result == v1_bytes.decode("utf-8")

        # Exactly one warning, mentions team_a + version 1
        assert len(caplog.records) == 1
        msg = caplog.records[0].getMessage()
        assert "team_a" in msg and "1" in msg

    def test_repair_uses_highest_version_when_gaps(self, tmp_path, caplog):
        # Build a state with gaps: only strategy_v3.py present, current.py missing
        d = tmp_path / "strategies" / "team_a"
        d.mkdir(parents=True)
        (d / "strategy_v3.py").write_text("# strategy_v3.py\n# fake\n\nbody3\n")

        with caplog.at_level(logging.WARNING):
            result = read_current(str(tmp_path), "team_a")

        assert "body3" in result
        msg = caplog.records[0].getMessage()
        assert "3" in msg


# ---------------------------------------------------------------------------
# AC-4: Self-heal — stale current.py (new AC from this story)
# ---------------------------------------------------------------------------


class TestAC4SelfHealStaleCurrentPy:
    def test_stale_current_repaired_from_highest(self, tmp_path, caplog):
        # Write v1 with code_a, then v2 with code_b
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        v1_bytes = (tmp_path / "strategies" / "team_a" / "strategy_v1.py").read_bytes()
        write_strategy(str(tmp_path), "team_a", CODE_B, _meta(match_number=1))
        v2_bytes = (tmp_path / "strategies" / "team_a" / "strategy_v2.py").read_bytes()

        # Simulate crashed shutil.copy2 by overwriting current.py with v1 content
        (tmp_path / "strategies" / "team_a" / "current.py").write_bytes(v1_bytes)

        with caplog.at_level(logging.WARNING):
            result = read_current(str(tmp_path), "team_a")

        # current.py now matches v2
        cur_bytes = (tmp_path / "strategies" / "team_a" / "current.py").read_bytes()
        assert cur_bytes == v2_bytes

        # Returned string is v2 content
        assert result == v2_bytes.decode("utf-8")

        # Warning logged mentioning version 2
        msg = caplog.records[0].getMessage()
        assert "2" in msg
        assert "team_a" in msg

        # v1 and v2 unchanged
        assert (tmp_path / "strategies" / "team_a" / "strategy_v1.py").read_bytes() == v1_bytes
        assert (tmp_path / "strategies" / "team_a" / "strategy_v2.py").read_bytes() == v2_bytes


# ---------------------------------------------------------------------------
# AC-5: No mutation on healthy read (new AC from this story)
# ---------------------------------------------------------------------------


class TestAC5NoMutationOnHealthyRead:
    def test_healthy_read_does_not_call_copy2(self, tmp_path, monkeypatch, caplog):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())

        copy2_called = {"n": 0}

        def fake_copy2(src, dst):
            copy2_called["n"] += 1
            raise AssertionError("shutil.copy2 must not be called on a healthy read")

        monkeypatch.setattr(ss.shutil, "copy2", fake_copy2)

        with caplog.at_level(logging.WARNING):
            result = read_current(str(tmp_path), "team_a")

        assert copy2_called["n"] == 0
        assert len(caplog.records) == 0
        assert result.startswith("# strategy_v1.py")

    def test_two_consecutive_reads_remain_idempotent(self, tmp_path, monkeypatch, caplog):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())

        def fake_copy2(src, dst):
            raise AssertionError("shutil.copy2 must not be called")

        monkeypatch.setattr(ss.shutil, "copy2", fake_copy2)
        with caplog.at_level(logging.WARNING):
            r1 = read_current(str(tmp_path), "team_a")
            r2 = read_current(str(tmp_path), "team_a")
        assert r1 == r2
        assert len(caplog.records) == 0


# ---------------------------------------------------------------------------
# AC-6: read_version happy path (AC-SS-09)
# ---------------------------------------------------------------------------


class TestAC6ReadVersionHappyPath:
    def test_read_version_2_after_two_writes(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        write_strategy(str(tmp_path), "team_a", CODE_B, _meta(match_number=1))
        result = read_version(str(tmp_path), "team_a", 2)
        on_disk = (tmp_path / "strategies" / "team_a" / "strategy_v2.py").read_text()
        assert result == on_disk
        assert CODE_B in result
        assert CODE_A not in result

    def test_read_version_1_returns_first_write(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        write_strategy(str(tmp_path), "team_a", CODE_B, _meta(match_number=1))
        result = read_version(str(tmp_path), "team_a", 1)
        assert CODE_A in result
        assert CODE_B not in result

    def test_read_version_does_not_modify_current_py(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        write_strategy(str(tmp_path), "team_a", CODE_B, _meta(match_number=1))
        cur_bytes_before = (tmp_path / "strategies" / "team_a" / "current.py").read_bytes()
        read_version(str(tmp_path), "team_a", 1)
        cur_bytes_after = (tmp_path / "strategies" / "team_a" / "current.py").read_bytes()
        assert cur_bytes_before == cur_bytes_after


# ---------------------------------------------------------------------------
# AC-7: read_version missing → VersionNotFoundError (AC-SS-10)
# ---------------------------------------------------------------------------


class TestAC7ReadVersionMissingRaises:
    def test_missing_version_99_raises(self, tmp_path, caplog):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        with caplog.at_level(logging.WARNING):
            with pytest.raises(VersionNotFoundError) as exc_info:
                read_version(str(tmp_path), "team_a", 99)
        msg = str(exc_info.value)
        assert "99" in msg
        assert "team_a" in msg
        # No auto-repair → no warning
        assert len(caplog.records) == 0

    def test_current_py_unchanged_after_missing_version_lookup(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        cur_bytes_before = (tmp_path / "strategies" / "team_a" / "current.py").read_bytes()
        with pytest.raises(VersionNotFoundError):
            read_version(str(tmp_path), "team_a", 99)
        cur_bytes_after = (tmp_path / "strategies" / "team_a" / "current.py").read_bytes()
        assert cur_bytes_before == cur_bytes_after

    def test_version_0_raises(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        with pytest.raises(VersionNotFoundError):
            read_version(str(tmp_path), "team_a", 0)


# ---------------------------------------------------------------------------
# AC-8: read_version does not interfere with read_current
# ---------------------------------------------------------------------------


class TestAC8ReadVersionDoesNotInterfereWithReadCurrent:
    def test_read_version_then_read_current(self, tmp_path, caplog):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        write_strategy(str(tmp_path), "team_a", CODE_B, _meta(match_number=1))

        with caplog.at_level(logging.WARNING):
            v1 = read_version(str(tmp_path), "team_a", 1)
            cur = read_current(str(tmp_path), "team_a")

        # read_current returns v2 (the latest); read_version returned v1
        assert CODE_A in v1 and CODE_B not in v1
        assert CODE_B in cur and CODE_A not in cur
        # No warnings — both reads were healthy
        assert len(caplog.records) == 0
