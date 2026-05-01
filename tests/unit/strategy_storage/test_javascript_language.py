"""Tests for `language` field on StrategyMetadata + JS-aware storage.

Covers the extension of StrategyMetadata + storage layer to support JavaScript
strategies alongside Python (added 2026-04-26 to follow the JS sandbox work).
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from src.foundation.strategy_storage import (
    StrategyMetadata,
    StrategyNotFoundError,
    VersionNotFoundError,
    _build_header,
    list_versions,
    read_current,
    read_version,
    write_strategy,
)


PY_CODE = "def decide(g, p, h):\n    return Hold()\n"
JS_CODE = "function decide(g, p, h) {\n  return Hold();\n}\n"


def _py_meta(**overrides) -> StrategyMetadata:
    base = {
        "team_id": "team_a",
        "match_number": 0,
        "llm_provider": "openai",
        "llm_model": "gpt-4o",
        "generated_by": "code-generation-pipeline",
    }
    base.update(overrides)
    return StrategyMetadata(**base)


def _js_meta(**overrides) -> StrategyMetadata:
    base = {
        "team_id": "team_a",
        "match_number": 0,
        "llm_provider": "openai",
        "llm_model": "gpt-4o",
        "generated_by": "code-generation-pipeline/js",
        "language": "javascript",
    }
    base.update(overrides)
    return StrategyMetadata(**base)


# ---------------------------------------------------------------------------
# Dataclass surface
# ---------------------------------------------------------------------------


class TestStrategyMetadataLanguageField:
    def test_default_language_is_python(self):
        meta = _py_meta()
        assert meta.language == "python"

    def test_javascript_language_assignable(self):
        meta = _js_meta()
        assert meta.language == "javascript"

    def test_language_is_immutable(self):
        meta = _js_meta()
        with pytest.raises(FrozenInstanceError):
            meta.language = "python"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Header builder — language affects comment prefix + filename + new field
# ---------------------------------------------------------------------------


class TestBuildHeaderLanguageAware:
    def test_python_header_uses_hash_prefix(self):
        header = _build_header(1, _py_meta())
        for line in header.splitlines():
            if not line:
                continue
            assert line.startswith("# "), f"non-blank line does not start with '# ': {line!r}"

    def test_javascript_header_uses_double_slash_prefix(self):
        header = _build_header(1, _js_meta())
        for line in header.splitlines():
            if not line:
                continue
            assert line.startswith("// "), f"non-blank line does not start with '// ': {line!r}"

    def test_javascript_header_filename_uses_js_extension(self):
        header = _build_header(7, _js_meta())
        assert header.startswith("// strategy_v7.js\n")

    def test_python_header_filename_uses_py_extension(self):
        header = _build_header(7, _py_meta())
        assert header.startswith("# strategy_v7.py\n")

    def test_javascript_header_records_language_field(self):
        header = _build_header(1, _js_meta())
        assert "// language:     javascript" in header

    def test_python_header_records_language_field(self):
        header = _build_header(1, _py_meta())
        assert "# language:     python" in header

    def test_unknown_language_raises_value_error(self):
        meta = _py_meta()
        # bypass frozen dataclass: build a fresh instance with a bogus value.
        # ("rust" was the bogus value pre-ADR-0026; now it's a real language,
        # so we use a genuinely-unknown one here.)
        bogus = StrategyMetadata(
            team_id=meta.team_id,
            match_number=meta.match_number,
            llm_provider=meta.llm_provider,
            llm_model=meta.llm_model,
            generated_by=meta.generated_by,
            language="cobol",
        )
        with pytest.raises(ValueError, match="Unknown language"):
            _build_header(1, bogus)


# ---------------------------------------------------------------------------
# write_strategy — JS file naming and current.js
# ---------------------------------------------------------------------------


class TestWriteJavascriptStrategy:
    def test_writes_strategy_v1_js(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", JS_CODE, _js_meta())
        assert (tmp_path / "strategies" / "team_a" / "strategy_v1.js").exists()
        assert not (tmp_path / "strategies" / "team_a" / "strategy_v1.py").exists()

    def test_writes_current_js_pointer(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", JS_CODE, _js_meta())
        assert (tmp_path / "strategies" / "team_a" / "current.js").exists()
        assert not (tmp_path / "strategies" / "team_a" / "current.py").exists()

    def test_versioned_and_current_byte_identical(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", JS_CODE, _js_meta())
        d = tmp_path / "strategies" / "team_a"
        assert (d / "strategy_v1.js").read_bytes() == (d / "current.js").read_bytes()

    def test_js_file_starts_with_double_slash_header(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", JS_CODE, _js_meta())
        content = (tmp_path / "strategies" / "team_a" / "strategy_v1.js").read_text()
        assert content.startswith("// strategy_v1.js\n// team_id:      team_a\n")
        assert JS_CODE in content

    def test_second_write_increments_to_v2_js(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", JS_CODE, _js_meta())
        v = write_strategy(str(tmp_path), "team_a", JS_CODE, _js_meta(match_number=1))
        assert v == 2
        assert (tmp_path / "strategies" / "team_a" / "strategy_v2.js").exists()


# ---------------------------------------------------------------------------
# Language-mismatch guard within a single team directory
# ---------------------------------------------------------------------------


class TestLanguageMismatchGuard:
    def test_writing_js_after_py_versions_raises(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", PY_CODE, _py_meta())
        with pytest.raises(ValueError, match="language mismatch"):
            write_strategy(str(tmp_path), "team_a", JS_CODE, _js_meta())

    def test_writing_py_after_js_versions_raises(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", JS_CODE, _js_meta())
        with pytest.raises(ValueError, match="language mismatch"):
            write_strategy(str(tmp_path), "team_a", PY_CODE, _py_meta())

    def test_no_filesystem_mutation_on_mismatch(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", PY_CODE, _py_meta())
        with pytest.raises(ValueError):
            write_strategy(str(tmp_path), "team_a", JS_CODE, _js_meta())
        d = tmp_path / "strategies" / "team_a"
        assert not (d / "strategy_v2.js").exists()
        assert not (d / "current.js").exists()


# ---------------------------------------------------------------------------
# Mixed-language teams (team_a Python, team_b JavaScript) coexist
# ---------------------------------------------------------------------------


class TestMixedLanguageTeams:
    def test_team_a_py_and_team_b_js_coexist(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", PY_CODE, _py_meta(team_id="team_a"))
        write_strategy(str(tmp_path), "team_b", JS_CODE,
                       _js_meta(team_id="team_b"))
        assert (tmp_path / "strategies" / "team_a" / "strategy_v1.py").exists()
        assert (tmp_path / "strategies" / "team_b" / "strategy_v1.js").exists()
        assert list_versions(str(tmp_path), "team_a") == [1]
        assert list_versions(str(tmp_path), "team_b") == [1]


# ---------------------------------------------------------------------------
# Read paths discover the on-disk extension
# ---------------------------------------------------------------------------


class TestReadPathsDiscoverExtension:
    def test_read_version_returns_js_content(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", JS_CODE, _js_meta())
        result = read_version(str(tmp_path), "team_a", 1)
        assert JS_CODE in result
        assert result.startswith("// strategy_v1.js\n")

    def test_read_current_returns_js_content(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", JS_CODE, _js_meta())
        result = read_current(str(tmp_path), "team_a")
        assert JS_CODE in result
        assert result.startswith("// strategy_v1.js\n")

    def test_read_version_missing_raises(self, tmp_path):
        write_strategy(str(tmp_path), "team_a", JS_CODE, _js_meta())
        with pytest.raises(VersionNotFoundError):
            read_version(str(tmp_path), "team_a", 99)

    def test_read_current_self_heals_from_js_version(self, tmp_path):
        # Hand-built archive with strategy_v1.js but no current.js — read_current
        # should repair by copying the highest version into current.js.
        d = tmp_path / "strategies" / "team_a"
        d.mkdir(parents=True)
        (d / "strategy_v1.js").write_text("// strategy_v1.js\n\n" + JS_CODE)
        result = read_current(str(tmp_path), "team_a")
        assert JS_CODE in result
        assert (d / "current.js").exists()

    def test_read_current_empty_dir_raises(self, tmp_path):
        with pytest.raises(StrategyNotFoundError):
            read_current(str(tmp_path), "team_a")


# ---------------------------------------------------------------------------
# list_versions ignores non-py-or-js suffixes (regression for new regex)
# ---------------------------------------------------------------------------


class TestListVersionsIgnoresOtherExtensions:
    def test_only_py_js_rs_counted(self, tmp_path):
        d = tmp_path / "strategies" / "team_a"
        d.mkdir(parents=True)
        (d / "strategy_v1.py").touch()
        (d / "strategy_v2.js").touch()
        (d / "strategy_v3.txt").touch()       # ignored
        (d / "strategy_v4.rs").touch()        # counted — Rust is a supported language
        # NOTE: Mixed languages in the same dir should never happen via write_strategy
        # (mismatch guard prevents it), but the scanner is tolerant to manual setup.
        assert list_versions(str(tmp_path), "team_a") == [1, 2, 4]
