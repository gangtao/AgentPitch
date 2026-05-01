"""Unit tests for src/foundation/strategy_library.py (ADR-0023).

Covers paired write/read/update/delete/list, atomic semantics, legacy
(missing-sidecar) tolerance, and validation rules.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.strategy_library import (
    InvalidStrategyNameError,
    StrategyLibraryError,
    StrategyLibraryMeta,
    StrategyLibraryNotFoundError,
    UNKNOWN_META,
    delete_strategy,
    library_dir,
    list_strategies,
    meta_path,
    read_meta,
    read_strategy,
    source_path,
    update_meta,
    write_strategy,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def data_home(tmp_path: Path) -> Path:
    """Empty data home; library_dir() creates `<data_home>/strategies/` lazily."""
    return tmp_path


def _llm_meta(**overrides) -> StrategyLibraryMeta:
    base = dict(
        provider="anthropic",
        model="claude-sonnet-4-6",
        created_by="llm",
        created_at="2026-04-25T21:30:00Z",
        last_modified_at="2026-04-25T21:30:00Z",
        prompt="Aggressive midfield press.",
        template_version="2.5",
    )
    base.update(overrides)
    return StrategyLibraryMeta(**base)


def _manual_meta(**overrides) -> StrategyLibraryMeta:
    base = dict(
        provider="manual",
        model="hand-written",
        created_by="manual",
        created_at="2026-04-25T22:00:00Z",
        last_modified_at="2026-04-25T22:00:00Z",
    )
    base.update(overrides)
    return StrategyLibraryMeta(**base)


SAMPLE_SOURCE = '''"""Strategy: sample"""

def decide(game_state, player_state, history):
    return Hold()
'''


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


class TestPathHelpers:
    def test_library_dir_composition(self, data_home):
        assert library_dir(data_home) == data_home / "strategies"

    def test_source_path_includes_py_suffix(self, data_home):
        assert source_path(data_home, "foo") == data_home / "strategies" / "foo.py"

    def test_meta_path_uses_meta_json_suffix(self, data_home):
        assert meta_path(data_home, "foo") == data_home / "strategies" / "foo.meta.json"

    def test_invalid_name_rejected(self, data_home):
        with pytest.raises(InvalidStrategyNameError):
            source_path(data_home, "has spaces")
        with pytest.raises(InvalidStrategyNameError):
            source_path(data_home, "")
        with pytest.raises(InvalidStrategyNameError):
            source_path(data_home, "a" * 65)
        with pytest.raises(InvalidStrategyNameError):
            source_path(data_home, "../escape")

    def test_valid_name_shapes(self, data_home):
        for name in ["foo", "FOO", "f_oo", "f-oo-1", "anthropic-claude-sonnet-4-6-1"]:
            source_path(data_home, name)  # should not raise


# ---------------------------------------------------------------------------
# Round-trip
# ---------------------------------------------------------------------------


class TestRoundTrip:
    def test_write_then_read_returns_same_source_and_meta(self, data_home):
        meta = _llm_meta()
        write_strategy(data_home, "foo", SAMPLE_SOURCE, meta)
        source, read_back = read_strategy(data_home, "foo")
        assert source == SAMPLE_SOURCE
        assert read_back == meta

    def test_write_creates_both_files(self, data_home):
        write_strategy(data_home, "foo", SAMPLE_SOURCE, _llm_meta())
        assert source_path(data_home, "foo").exists()
        assert meta_path(data_home, "foo").exists()

    def test_sidecar_is_indented_json(self, data_home):
        write_strategy(data_home, "foo", SAMPLE_SOURCE, _llm_meta())
        text = meta_path(data_home, "foo").read_text(encoding="utf-8")
        # Indented JSON has at least one newline + leading space per field.
        assert "\n  " in text
        # Round-trips through JSON.
        parsed = json.loads(text)
        assert parsed["provider"] == "anthropic"
        assert parsed["template_version"] == "2.5"

    def test_manual_meta_omits_optional_fields(self, data_home):
        write_strategy(data_home, "foo", SAMPLE_SOURCE, _manual_meta())
        text = meta_path(data_home, "foo").read_text(encoding="utf-8")
        parsed = json.loads(text)
        assert "prompt" not in parsed
        assert "template_version" not in parsed

    def test_overwrite_replaces_both_files(self, data_home):
        write_strategy(data_home, "foo", SAMPLE_SOURCE, _llm_meta())
        new_source = "# replaced\ndef decide(g, p, h): return Hold()\n"
        new_meta = _manual_meta(last_modified_at="2026-04-25T23:00:00Z")
        write_strategy(data_home, "foo", new_source, new_meta)
        source, meta = read_strategy(data_home, "foo")
        assert source == new_source
        assert meta == new_meta


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class TestMetaValidation:
    def test_custom_provider_accepted(self, data_home):
        # Custom providers (ollama, vllm, etc.) are allowed
        custom = _llm_meta(provider="ollama")
        written = write_strategy(data_home, "foo", SAMPLE_SOURCE, custom)
        assert written.provider == "ollama"

    def test_unknown_created_by_rejected(self, data_home):
        bad = _manual_meta(created_by="auto")  # type: ignore[arg-type]
        with pytest.raises(StrategyLibraryError, match="Invalid created_by"):
            write_strategy(data_home, "foo", SAMPLE_SOURCE, bad)

    def test_llm_with_empty_prompt_allowed(self, data_home):
        # Per ADR-0023 amendment 2026-04-26: empty/missing prompt is valid for
        # LLM strategies, mirroring /api/strategies/generate which accepts an
        # empty prompt (USER INTENT fallback in the SPB template).
        for prompt_value in (None, ""):
            ok = _llm_meta(prompt=prompt_value)
            written = write_strategy(data_home, "foo", SAMPLE_SOURCE, ok)
            assert written.created_by == "llm"
            # Clean up between iterations so the second write isn't an overwrite check.
            from src.strategy_library import delete_strategy as _del
            _del(data_home, "foo")

    def test_llm_without_template_version_rejected(self, data_home):
        bad = _llm_meta(template_version=None)
        with pytest.raises(StrategyLibraryError, match="must include `template_version`"):
            write_strategy(data_home, "foo", SAMPLE_SOURCE, bad)

    def test_empty_model_rejected(self, data_home):
        bad = _manual_meta(model="")
        with pytest.raises(StrategyLibraryError, match="model must be a non-empty string"):
            write_strategy(data_home, "foo", SAMPLE_SOURCE, bad)

    def test_empty_provider_rejected(self, data_home):
        bad = _llm_meta(provider="")
        with pytest.raises(StrategyLibraryError, match="Invalid provider"):
            write_strategy(data_home, "foo", SAMPLE_SOURCE, bad)

    def test_provider_exceeding_length_rejected(self, data_home):
        bad = _llm_meta(provider="x" * 65)  # 65 chars, max is 64
        with pytest.raises(StrategyLibraryError, match="Invalid provider"):
            write_strategy(data_home, "foo", SAMPLE_SOURCE, bad)


# ---------------------------------------------------------------------------
# Read paths — legacy / missing
# ---------------------------------------------------------------------------


class TestReadLegacy:
    def test_read_strategy_missing_source_raises(self, data_home):
        with pytest.raises(StrategyLibraryNotFoundError):
            read_strategy(data_home, "ghost")

    def test_read_strategy_missing_sidecar_returns_unknown(self, data_home):
        # Simulate legacy: only the .py exists.
        d = library_dir(data_home)
        d.mkdir(parents=True)
        (d / "legacy.py").write_text(SAMPLE_SOURCE, encoding="utf-8")
        source, meta = read_strategy(data_home, "legacy")
        assert source == SAMPLE_SOURCE
        assert meta == UNKNOWN_META

    def test_read_meta_missing_returns_unknown(self, data_home):
        d = library_dir(data_home)
        d.mkdir(parents=True)
        (d / "legacy.py").write_text(SAMPLE_SOURCE, encoding="utf-8")
        assert read_meta(data_home, "legacy") == UNKNOWN_META

    def test_read_meta_malformed_json_raises(self, data_home):
        d = library_dir(data_home)
        d.mkdir(parents=True)
        (d / "broken.py").write_text(SAMPLE_SOURCE, encoding="utf-8")
        (d / "broken.meta.json").write_text("not valid json {", encoding="utf-8")
        with pytest.raises(StrategyLibraryError, match="sidecar unreadable"):
            read_meta(data_home, "broken")

    def test_read_meta_missing_required_field_raises(self, data_home):
        d = library_dir(data_home)
        d.mkdir(parents=True)
        (d / "partial.py").write_text(SAMPLE_SOURCE, encoding="utf-8")
        (d / "partial.meta.json").write_text(
            json.dumps({"provider": "anthropic"}), encoding="utf-8"
        )
        with pytest.raises(StrategyLibraryError, match="missing required fields"):
            read_meta(data_home, "partial")


# ---------------------------------------------------------------------------
# update_meta
# ---------------------------------------------------------------------------


class TestUpdateMeta:
    def test_preserves_unchanged_fields(self, data_home):
        original = _llm_meta()
        write_strategy(data_home, "foo", SAMPLE_SOURCE, original)
        updated = update_meta(
            data_home, "foo", last_modified_at="2026-04-26T08:00:00Z"
        )
        assert updated.provider == original.provider
        assert updated.model == original.model
        assert updated.created_by == original.created_by
        assert updated.created_at == original.created_at
        assert updated.prompt == original.prompt
        assert updated.template_version == original.template_version
        assert updated.last_modified_at == "2026-04-26T08:00:00Z"

    def test_legacy_file_synthesizes_sidecar(self, data_home):
        d = library_dir(data_home)
        d.mkdir(parents=True)
        (d / "legacy.py").write_text(SAMPLE_SOURCE, encoding="utf-8")
        # No sidecar present.
        updated = update_meta(
            data_home, "legacy", last_modified_at="2026-04-25T22:00:00Z"
        )
        assert updated.provider == "unknown"
        assert updated.created_by == "manual"
        assert updated.last_modified_at == "2026-04-25T22:00:00Z"
        # Sidecar now exists on disk.
        assert meta_path(data_home, "legacy").exists()

    def test_no_source_raises(self, data_home):
        with pytest.raises(StrategyLibraryNotFoundError):
            update_meta(data_home, "ghost", last_modified_at="2026-04-25T22:00:00Z")

    def test_custom_provider_override_accepted(self, data_home):
        # Custom provider names should be accepted in update_meta
        write_strategy(data_home, "foo", SAMPLE_SOURCE, _llm_meta())
        updated = update_meta(data_home, "foo", provider="ollama")
        assert updated.provider == "ollama"


# ---------------------------------------------------------------------------
# delete_strategy
# ---------------------------------------------------------------------------


class TestDelete:
    def test_removes_both_files(self, data_home):
        write_strategy(data_home, "foo", SAMPLE_SOURCE, _llm_meta())
        delete_strategy(data_home, "foo")
        assert not source_path(data_home, "foo").exists()
        assert not meta_path(data_home, "foo").exists()

    def test_missing_sidecar_tolerated(self, data_home):
        d = library_dir(data_home)
        d.mkdir(parents=True)
        (d / "legacy.py").write_text(SAMPLE_SOURCE, encoding="utf-8")
        delete_strategy(data_home, "legacy")
        assert not (d / "legacy.py").exists()

    def test_missing_source_raises(self, data_home):
        with pytest.raises(StrategyLibraryNotFoundError):
            delete_strategy(data_home, "ghost")


# ---------------------------------------------------------------------------
# list_strategies
# ---------------------------------------------------------------------------


class TestList:
    def test_empty_dir_returns_empty(self, data_home):
        assert list_strategies(data_home) == []

    def test_lists_only_py_files(self, data_home):
        write_strategy(data_home, "foo", SAMPLE_SOURCE, _llm_meta())
        write_strategy(data_home, "bar", SAMPLE_SOURCE, _manual_meta())
        # Drop in a non-strategy file; must be ignored.
        (library_dir(data_home) / "README.txt").write_text("hi")
        names = sorted(name for name, _ in list_strategies(data_home))
        assert names == ["bar", "foo"]

    def test_pairs_meta_with_each_entry(self, data_home):
        write_strategy(data_home, "llm-one", SAMPLE_SOURCE, _llm_meta())
        write_strategy(data_home, "manual-one", SAMPLE_SOURCE, _manual_meta())
        results = dict(list_strategies(data_home))
        assert results["llm-one"].created_by == "llm"
        assert results["manual-one"].created_by == "manual"

    def test_legacy_entries_get_unknown_meta(self, data_home):
        d = library_dir(data_home)
        d.mkdir(parents=True)
        (d / "legacy.py").write_text(SAMPLE_SOURCE, encoding="utf-8")
        results = dict(list_strategies(data_home))
        assert results["legacy"] == UNKNOWN_META

    def test_invalid_filename_skipped(self, data_home):
        d = library_dir(data_home)
        d.mkdir(parents=True)
        # Filename has a space — not a valid strategy name.
        (d / "has space.py").write_text(SAMPLE_SOURCE, encoding="utf-8")
        # Valid one for contrast.
        write_strategy(data_home, "good", SAMPLE_SOURCE, _manual_meta())
        names = [name for name, _ in list_strategies(data_home)]
        assert names == ["good"]

    def test_malformed_sidecar_degrades_to_unknown(self, data_home):
        d = library_dir(data_home)
        d.mkdir(parents=True)
        (d / "broken.py").write_text(SAMPLE_SOURCE, encoding="utf-8")
        (d / "broken.meta.json").write_text("garbage", encoding="utf-8")
        results = dict(list_strategies(data_home))
        # Listing must not crash on malformed sidecars.
        assert results["broken"] == UNKNOWN_META


# ---------------------------------------------------------------------------
# Atomicity
# ---------------------------------------------------------------------------


class TestAtomicity:
    def test_write_leaves_no_tmp_files(self, data_home):
        write_strategy(data_home, "foo", SAMPLE_SOURCE, _llm_meta())
        d = library_dir(data_home)
        leftovers = [p.name for p in d.iterdir() if p.suffix == ".tmp"]
        assert leftovers == []

    def test_source_written_before_sidecar(self, data_home, monkeypatch):
        """If the sidecar write fails, the source still exists on disk —
        matches the legacy state, which readers tolerate. The reverse must
        never happen."""
        from src import strategy_library as lib

        original = lib._atomic_write_bytes

        call_count = {"n": 0}

        def flaky(target: Path, payload: bytes) -> None:
            call_count["n"] += 1
            # First call is the source write; second is the sidecar — fail it.
            if call_count["n"] == 2:
                raise lib.StrategyLibraryWriteError("simulated sidecar failure")
            original(target, payload)

        monkeypatch.setattr(lib, "_atomic_write_bytes", flaky)

        with pytest.raises(lib.StrategyLibraryWriteError):
            write_strategy(data_home, "foo", SAMPLE_SOURCE, _llm_meta())

        # Source landed; sidecar did not — tolerated legacy state.
        assert source_path(data_home, "foo").exists()
        assert not meta_path(data_home, "foo").exists()
        # And reading back gives UNKNOWN_META instead of crashing.
        source, meta = read_strategy(data_home, "foo")
        assert source == SAMPLE_SOURCE
        assert meta == UNKNOWN_META
