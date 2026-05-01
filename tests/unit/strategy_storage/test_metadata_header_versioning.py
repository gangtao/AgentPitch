"""Tests for Strategy Storage Story 001: metadata, header, version scanning."""

from __future__ import annotations

import ast
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.foundation.strategy_storage import (
    StrategyMetadata,
    StrategyNotFoundError,
    StrategyStorageError,
    VersionNotFoundError,
    WriteFailedError,
    _build_header,
    list_versions,
    strategy_dir,
)


def _meta(**overrides) -> StrategyMetadata:
    base = {
        "team_id": "team_a",
        "match_number": 2,
        "llm_provider": "openai",
        "llm_model": "gpt-4o",
        "generated_by": "post-match-evolution",
    }
    base.update(overrides)
    return StrategyMetadata(**base)


# ---------------------------------------------------------------------------
# AC-1: strategy_dir path arithmetic (pure, no filesystem)
# ---------------------------------------------------------------------------


class TestAC1StrategyDirPath:
    def test_basic_path_composition(self):
        assert strategy_dir("/tmp/run_x", "team_a") == Path("/tmp/run_x/strategies/team_a")

    def test_team_b(self):
        assert strategy_dir("/tmp/run_x", "team_b") == Path("/tmp/run_x/strategies/team_b")

    def test_trailing_slash_normalised(self):
        # Path normalises trailing slashes
        assert strategy_dir("/tmp/run_x/", "team_a") == Path("/tmp/run_x/strategies/team_a")

    def test_relative_path(self):
        assert strategy_dir("logs", "team_a") == Path("logs/strategies/team_a")

    def test_no_filesystem_access_for_nonexistent_path(self):
        # Pure arithmetic — does not touch the filesystem
        result = strategy_dir("/this/path/does/not/exist", "team_a")
        assert isinstance(result, Path)


# ---------------------------------------------------------------------------
# AC-2: list_versions empty on missing dir (AC-SS-08)
# ---------------------------------------------------------------------------


class TestAC2ListVersionsEmpty:
    def test_missing_team_dir_returns_empty(self, tmp_path):
        assert list_versions(str(tmp_path), "team_a") == []

    def test_strategies_parent_exists_but_team_does_not(self, tmp_path):
        (tmp_path / "strategies").mkdir()
        assert list_versions(str(tmp_path), "team_a") == []


# ---------------------------------------------------------------------------
# AC-3: list_versions sorted (AC-SS-07)
# ---------------------------------------------------------------------------


class TestAC3ListVersionsSorted:
    def test_three_files_sorted_ascending(self, tmp_path):
        d = tmp_path / "strategies" / "team_a"
        d.mkdir(parents=True)
        for v in (3, 1, 2):
            (d / f"strategy_v{v}.py").touch()
        assert list_versions(str(tmp_path), "team_a") == [1, 2, 3]

    def test_single_file(self, tmp_path):
        d = tmp_path / "strategies" / "team_a"
        d.mkdir(parents=True)
        (d / "strategy_v1.py").touch()
        assert list_versions(str(tmp_path), "team_a") == [1]

    def test_gap_preserved(self, tmp_path):
        d = tmp_path / "strategies" / "team_a"
        d.mkdir(parents=True)
        for v in (1, 2, 4):
            (d / f"strategy_v{v}.py").touch()
        assert list_versions(str(tmp_path), "team_a") == [1, 2, 4]

    def test_two_digit_version(self, tmp_path):
        d = tmp_path / "strategies" / "team_a"
        d.mkdir(parents=True)
        (d / "strategy_v12.py").touch()
        (d / "strategy_v3.py").touch()
        assert list_versions(str(tmp_path), "team_a") == [3, 12]

    def test_returns_int_not_str(self, tmp_path):
        d = tmp_path / "strategies" / "team_a"
        d.mkdir(parents=True)
        (d / "strategy_v1.py").touch()
        result = list_versions(str(tmp_path), "team_a")
        assert all(isinstance(v, int) for v in result)


# ---------------------------------------------------------------------------
# AC-4: list_versions ignores non-integer suffixes (AC-SS-15)
# ---------------------------------------------------------------------------


class TestAC4ListVersionsIgnoresMalformed:
    def test_mixed_directory_returns_only_valid_versions(self, tmp_path):
        d = tmp_path / "strategies" / "team_a"
        d.mkdir(parents=True)
        for name in (
            "strategy_v1.py",
            "strategy_vabc.py",      # ignored
            "strategy_v2.py.bak",    # ignored (extension wrong)
            "current.py",            # ignored
            "notes.md",              # ignored
            ".DS_Store",             # ignored
        ):
            (d / name).touch()
        assert list_versions(str(tmp_path), "team_a") == [1]

    def test_no_digits_ignored(self, tmp_path):
        d = tmp_path / "strategies" / "team_a"
        d.mkdir(parents=True)
        (d / "strategy_v.py").touch()
        assert list_versions(str(tmp_path), "team_a") == []

    def test_leading_zero_accepted_as_int(self, tmp_path):
        d = tmp_path / "strategies" / "team_a"
        d.mkdir(parents=True)
        (d / "strategy_v01.py").touch()
        assert list_versions(str(tmp_path), "team_a") == [1]


# ---------------------------------------------------------------------------
# AC-5: Header field set (AC-SS-11)
# ---------------------------------------------------------------------------


class TestAC5HeaderFields:
    def test_header_has_all_9_lines_plus_blank(self):
        header = _build_header(3, _meta())
        lines = header.split("\n")
        # Lines 0-8 are content (filename + 8 fields), line 9 blank, line 10 empty (final \n)
        assert lines[0] == "# strategy_v3.py"
        assert lines[1].startswith("# team_id:")
        assert "team_a" in lines[1]
        assert lines[2].startswith("# version:")
        assert lines[3].startswith("# match_number:")
        assert lines[4].startswith("# language:")
        assert "python" in lines[4]
        assert lines[5].startswith("# timestamp:")
        assert lines[6].startswith("# llm_provider:")
        assert lines[7].startswith("# llm_model:")
        assert lines[8].startswith("# generated_by:")
        assert lines[9] == ""  # blank separator

    def test_header_field_order_exact(self):
        header = _build_header(1, _meta())
        # Verify the metadata field labels appear in the required order.
        ordered = [
            "team_id", "version", "match_number", "language",
            "timestamp", "llm_provider", "llm_model", "generated_by",
        ]
        positions = [header.index(f"# {label}:") for label in ordered]
        assert positions == sorted(positions)

    def test_match_number_zero_renders(self):
        header = _build_header(1, _meta(match_number=0))
        assert "# match_number: 0" in header

    def test_long_model_name_does_not_break_format(self):
        header = _build_header(1, _meta(llm_model="claude-3-5-sonnet-20240620"))
        assert "claude-3-5-sonnet-20240620" in header


# ---------------------------------------------------------------------------
# AC-6: Timestamp owned by header builder (AC-SS-12)
# ---------------------------------------------------------------------------


class TestAC6TimestampOwnedByBuilder:
    def test_timestamp_format_parses(self):
        header = _build_header(1, _meta())
        m = re.search(r"# timestamp:\s+(\S+)", header)
        assert m is not None
        ts_str = m.group(1)
        parsed = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        # Within 5 seconds of now
        delta = abs((datetime.now(timezone.utc) - parsed).total_seconds())
        assert delta < 5.0

    def test_two_calls_have_monotonic_timestamps(self):
        h1 = _build_header(1, _meta())
        time.sleep(1.1)  # ensure UTC seconds tick over
        h2 = _build_header(2, _meta())
        ts1 = re.search(r"# timestamp:\s+(\S+)", h1).group(1)
        ts2 = re.search(r"# timestamp:\s+(\S+)", h2).group(1)
        assert ts2 >= ts1  # ISO 8601 strings sort lexicographically when same length

    def test_metadata_rejects_timestamp_kwarg(self):
        with pytest.raises(TypeError):
            StrategyMetadata(  # type: ignore[call-arg]
                team_id="team_a",
                match_number=0,
                llm_provider="openai",
                llm_model="gpt-4o",
                generated_by="cgp",
                timestamp="2026-04-21T00:00:00Z",
            )


# ---------------------------------------------------------------------------
# AC-7: Exception hierarchy
# ---------------------------------------------------------------------------


class TestAC7ExceptionHierarchy:
    @pytest.mark.parametrize("cls", [StrategyNotFoundError, VersionNotFoundError, WriteFailedError])
    def test_all_subclass_storage_error(self, cls):
        assert issubclass(cls, StrategyStorageError)

    def test_storage_error_subclasses_exception(self):
        assert issubclass(StrategyStorageError, Exception)

    def test_write_failed_preserves_cause_chain(self):
        try:
            try:
                raise OSError(28, "No space left on device")
            except OSError as e:
                raise WriteFailedError("disk full") from e
        except WriteFailedError as caught:
            assert isinstance(caught.__cause__, OSError)
            assert caught.__cause__.errno == 28


# ---------------------------------------------------------------------------
# AC-8: No compile/exec in module (TR-SS-004)
# ---------------------------------------------------------------------------


class TestAC8NoCompileExec:
    def test_module_source_has_no_dynamic_code_calls(self):
        from src.foundation import strategy_storage
        source = Path(strategy_storage.__file__).read_text()
        tree = ast.parse(source)
        # Forbidden: the BUILTINS compile/exec/eval (Python-source execution).
        # Allowed: re.compile (regex pattern compilation — not source execution).
        forbidden_builtin_names = {"compile", "exec", "eval"}
        # Also forbidden: importlib.import_module (dynamic import)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                # Bare-name builtins: compile(...), exec(...), eval(...)
                if isinstance(func, ast.Name) and func.id in forbidden_builtin_names:
                    pytest.fail(f"Found forbidden builtin call: {func.id}()")
                # Attribute call: importlib.import_module(...)
                if isinstance(func, ast.Attribute) and func.attr == "import_module":
                    pytest.fail("Found forbidden importlib.import_module() call")

    def test_module_does_not_import_importlib(self):
        from src.foundation import strategy_storage
        source = Path(strategy_storage.__file__).read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "importlib"
            if isinstance(node, ast.ImportFrom):
                assert node.module != "importlib"


# ---------------------------------------------------------------------------
# AC-9: StrategyMetadata immutability
# ---------------------------------------------------------------------------


class TestAC9StrategyMetadataImmutable:
    def test_mutation_raises_frozen_instance_error(self):
        from dataclasses import FrozenInstanceError

        m = _meta()
        with pytest.raises(FrozenInstanceError):
            m.team_id = "team_b"  # type: ignore[misc]
