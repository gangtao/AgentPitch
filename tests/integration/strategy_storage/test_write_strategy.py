"""Integration tests for Strategy Storage Story 002: write_strategy."""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.foundation import strategy_storage as ss
from src.foundation.strategy_storage import (
    StrategyMetadata,
    WriteFailedError,
    _build_header,
    list_versions,
    strategy_dir,
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


CODE_A = "def decide(game_state, player_state, history):\n    return Hold()\n"
CODE_B = "def decide(game_state, player_state, history):\n    return Move(1.0, 0.0, 1.0)\n"


# ---------------------------------------------------------------------------
# AC-1: First write — happy path (AC-SS-01 + AC-SS-17 + AC-SS-02)
# ---------------------------------------------------------------------------


class TestAC1FirstWriteHappyPath:
    def test_first_write_returns_version_1(self, tmp_path):
        version = write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        assert version == 1

    def test_first_write_creates_versioned_file(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        assert (tmp_path / "strategies" / "team_a" / "strategy_v1.py").exists()

    def test_first_write_creates_current_py(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        assert (tmp_path / "strategies" / "team_a" / "current.py").exists()

    def test_versioned_and_current_are_byte_identical(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        d = tmp_path / "strategies" / "team_a"
        assert (d / "strategy_v1.py").read_bytes() == (d / "current.py").read_bytes()

    def test_file_starts_with_correct_header(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        content = (tmp_path / "strategies" / "team_a" / "strategy_v1.py").read_text()
        assert content.startswith("# strategy_v1.py\n# team_id:      team_a\n")

    def test_code_appears_after_blank_separator(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        content = (tmp_path / "strategies" / "team_a" / "strategy_v1.py").read_text()
        assert CODE_A in content
        # generated_by is the final header field; blank line separator precedes code.
        assert "# generated_by: code-generation-pipeline\n\n" + CODE_A in content

    def test_team_b_creates_team_b_dir(self, tmp_path):
        write_strategy(str(tmp_path), "team_b", CODE_A, _meta(team_id="team_b"))
        assert (tmp_path / "strategies" / "team_b" / "strategy_v1.py").exists()

    def test_empty_code_still_writes_header(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", "", _meta())
        content = (tmp_path / "strategies" / "team_a" / "strategy_v1.py").read_text()
        assert content.startswith("# strategy_v1.py\n")


# ---------------------------------------------------------------------------
# AC-2: Second write — version increment + v1 immutable (AC-SS-03)
# ---------------------------------------------------------------------------


class TestAC2SecondWriteIncrementsAndPreservesV1:
    def test_second_write_returns_2(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        version = write_strategy(str(tmp_path), "team_a", CODE_B, _meta(match_number=1))
        assert version == 2

    def test_v1_unchanged_after_second_write(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        v1_bytes_before = (tmp_path / "strategies" / "team_a" / "strategy_v1.py").read_bytes()
        write_strategy(str(tmp_path), "team_a", CODE_B, _meta(match_number=1))
        v1_bytes_after = (tmp_path / "strategies" / "team_a" / "strategy_v1.py").read_bytes()
        assert v1_bytes_before == v1_bytes_after

    def test_current_py_matches_v2_after_second_write(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        write_strategy(str(tmp_path), "team_a", CODE_B, _meta(match_number=1))
        d = tmp_path / "strategies" / "team_a"
        assert (d / "strategy_v2.py").read_bytes() == (d / "current.py").read_bytes()

    def test_third_write_returns_3(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        write_strategy(str(tmp_path), "team_a", CODE_B, _meta(match_number=1))
        version = write_strategy(str(tmp_path), "team_a", CODE_A, _meta(match_number=2))
        assert version == 3


# ---------------------------------------------------------------------------
# AC-3: Version-gap preservation (GDD §8 Formula 1, AC-SS-15 application)
# ---------------------------------------------------------------------------


class TestAC3VersionGapPreservation:
    def test_v1_v2_v4_present_next_write_is_v5(self, tmp_path):
        d = tmp_path / "strategies" / "team_a"
        d.mkdir(parents=True)
        for v in (1, 2, 4):
            (d / f"strategy_v{v}.py").touch()
        version = write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        assert version == 5
        assert (d / "strategy_v5.py").exists()

    def test_v100_alone_next_write_is_101(self, tmp_path):
        d = tmp_path / "strategies" / "team_a"
        d.mkdir(parents=True)
        (d / "strategy_v100.py").touch()
        version = write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        assert version == 101


# ---------------------------------------------------------------------------
# AC-4: Non-integer suffixes ignored — write path (AC-SS-15)
# ---------------------------------------------------------------------------


class TestAC4NonIntegerSuffixesIgnoredOnWrite:
    def test_malformed_files_not_counted_for_next_version(self, tmp_path):
        d = tmp_path / "strategies" / "team_a"
        d.mkdir(parents=True)
        (d / "strategy_v1.py").touch()
        (d / "strategy_vabc.py").write_text("garbage")
        (d / "strategy_v2.py.bak").write_text("more garbage")

        version = write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        assert version == 2
        assert (d / "strategy_v2.py").exists()

        # Malformed files untouched
        assert (d / "strategy_vabc.py").read_text() == "garbage"
        assert (d / "strategy_v2.py.bak").read_text() == "more garbage"


# ---------------------------------------------------------------------------
# AC-5: Atomic — os.replace failure leaves no partial state (AC-SS-13)
# ---------------------------------------------------------------------------


class TestAC5AtomicReplaceFailure:
    def test_os_replace_failure_raises_write_failed_error(self, tmp_path, monkeypatch):
        # First successful write
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        v1_bytes = (tmp_path / "strategies" / "team_a" / "strategy_v1.py").read_bytes()
        current_bytes_before = (tmp_path / "strategies" / "team_a" / "current.py").read_bytes()

        # Patch os.replace inside strategy_storage to raise
        def fake_replace(src, dst):
            raise OSError(28, "ENOSPC")

        monkeypatch.setattr(ss.os, "replace", fake_replace)

        with pytest.raises(WriteFailedError) as exc_info:
            write_strategy(str(tmp_path), "team_a", CODE_B, _meta(match_number=1))

        # __cause__ chain preserved
        assert isinstance(exc_info.value.__cause__, OSError)
        assert exc_info.value.__cause__.errno == 28

        # strategy_v2.py NOT created
        assert not (tmp_path / "strategies" / "team_a" / "strategy_v2.py").exists()

        # current.py unchanged (still v1)
        current_bytes_after = (tmp_path / "strategies" / "team_a" / "current.py").read_bytes()
        assert current_bytes_after == current_bytes_before

        # v1 unchanged
        assert (tmp_path / "strategies" / "team_a" / "strategy_v1.py").read_bytes() == v1_bytes


# ---------------------------------------------------------------------------
# AC-6: Disk-full → WriteFailedError (AC-SS-14)
# ---------------------------------------------------------------------------


class TestAC6DiskFullWrappedAsWriteFailedError:
    def test_mkdir_disk_full_raises_write_failed_error(self, tmp_path, monkeypatch):
        # Patch Path.mkdir on the strategy_storage module's Path reference
        original_mkdir = Path.mkdir

        def fake_mkdir(self, *args, **kwargs):
            raise OSError(28, "No space left on device")

        monkeypatch.setattr(ss.Path, "mkdir", fake_mkdir)

        with pytest.raises(WriteFailedError) as exc_info:
            write_strategy(str(tmp_path), "team_a", CODE_A, _meta())

        assert isinstance(exc_info.value.__cause__, OSError)
        assert exc_info.value.__cause__.errno == 28

        # No directory created
        assert not (tmp_path / "strategies").exists()

    def test_permission_denied_on_mkdir_wrapped_too(self, tmp_path, monkeypatch):
        def fake_mkdir(self, *args, **kwargs):
            raise OSError(13, "Permission denied")

        monkeypatch.setattr(ss.Path, "mkdir", fake_mkdir)

        with pytest.raises(WriteFailedError) as exc_info:
            write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        assert exc_info.value.__cause__.errno == 13


# ---------------------------------------------------------------------------
# AC-7: team_id mismatch guard
# ---------------------------------------------------------------------------


class TestAC7TeamIdMismatchGuard:
    def test_mismatched_team_id_raises_value_error(self, tmp_path):
        with pytest.raises(ValueError, match="team_id mismatch"):
            write_strategy(str(tmp_path), "team_b", CODE_A, _meta(team_id="team_a"))

    def test_no_filesystem_mutation_on_mismatch(self, tmp_path):
        with pytest.raises(ValueError):
            write_strategy(str(tmp_path), "team_b", CODE_A, _meta(team_id="team_a"))
        assert not (tmp_path / "strategies").exists()

    def test_matching_ids_succeed(self, tmp_path):
        version = write_strategy(str(tmp_path), "team_a", CODE_A, _meta(team_id="team_a"))
        assert version == 1


# ---------------------------------------------------------------------------
# AC-8: Header content matches _build_header output (cross-story integration)
# ---------------------------------------------------------------------------


class TestAC8HeaderMatchesBuildHeader:
    def test_first_10_lines_equal_build_header_output(self, tmp_path):
        m = _meta()
        write_strategy(str(tmp_path), "team_a", CODE_A, m)
        content = (tmp_path / "strategies" / "team_a" / "strategy_v1.py").read_text()
        # The first 10 lines (filename + 8 fields + blank separator) form the header.
        # Timestamp will differ slightly between calls; verify structurally.
        actual_lines = content.split("\n")[:10]
        assert actual_lines[0] == "# strategy_v1.py"
        assert actual_lines[1] == "# team_id:      team_a"
        assert actual_lines[2] == "# version:      1"
        assert actual_lines[3] == "# match_number: 0"
        assert actual_lines[4] == "# language:     python"
        assert actual_lines[5].startswith("# timestamp:    ")
        assert actual_lines[6] == "# llm_provider: openai"
        assert actual_lines[7] == "# llm_model:    gpt-4o"
        assert actual_lines[8] == "# generated_by: code-generation-pipeline"
        assert actual_lines[9] == ""

    def test_timestamp_within_5_seconds_of_now(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", CODE_A, _meta())
        content = (tmp_path / "strategies" / "team_a" / "strategy_v1.py").read_text()
        m = re.search(r"# timestamp:\s+(\S+)", content)
        assert m is not None
        ts = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        delta = abs((datetime.now(timezone.utc) - ts).total_seconds())
        assert delta < 5.0
