"""Tests for multi-language strategy library support."""
from __future__ import annotations

import pytest

from src.strategy_library import (
    StrategyLibraryMeta,
    StrategyLibraryNotFoundError,
    UNKNOWN_META,
    source_path,
    write_strategy,
    read_strategy,
    delete_strategy,
    list_strategies,
    _LANG_TO_EXT,
    _EXT_TO_LANG,
)
from dataclasses import replace


def test_lang_to_ext_mapping():
    assert _LANG_TO_EXT["python"] == ".py"
    assert _LANG_TO_EXT["javascript"] == ".js"


def test_ext_to_lang_mapping():
    assert _EXT_TO_LANG[".py"] == "python"
    assert _EXT_TO_LANG[".js"] == "javascript"


def test_source_path_default_python(tmp_path):
    p = source_path(tmp_path, "foo")
    assert p.suffix == ".py"
    assert p.name == "foo.py"


def test_source_path_javascript(tmp_path):
    p = source_path(tmp_path, "foo", language="javascript")
    assert p.suffix == ".js"
    assert p.name == "foo.js"


def test_unknown_meta_defaults_to_python():
    assert UNKNOWN_META.language == "python"


def test_meta_language_field():
    meta = StrategyLibraryMeta(
        provider="manual", model="hand-written",
        created_by="manual", created_at="", last_modified_at="",
        language="javascript",
    )
    assert meta.language == "javascript"


def test_meta_language_default():
    meta = StrategyLibraryMeta(
        provider="manual", model="hand-written",
        created_by="manual", created_at="", last_modified_at="",
    )
    assert meta.language == "python"


def test_write_and_read_js_strategy(tmp_path):
    meta = StrategyLibraryMeta(
        provider="manual", model="hand-written",
        created_by="manual", created_at="2026-01-01T00:00:00Z",
        last_modified_at="2026-01-01T00:00:00Z",
        language="javascript",
    )
    write_strategy(tmp_path, "my-bot", "function decide(gs,ps,h){return {type:'Hold'};}", meta)
    assert (tmp_path / "strategies" / "my-bot.js").exists()
    assert not (tmp_path / "strategies" / "my-bot.py").exists()

    source, read_meta_result = read_strategy(tmp_path, "my-bot")
    assert "function decide" in source
    assert read_meta_result.language == "javascript"


def test_write_and_read_py_strategy(tmp_path):
    meta = StrategyLibraryMeta(
        provider="manual", model="hand-written",
        created_by="manual", created_at="2026-01-01T00:00:00Z",
        last_modified_at="2026-01-01T00:00:00Z",
        language="python",
    )
    write_strategy(tmp_path, "py-bot", "def decide(gs,ps,h): return Hold()", meta)
    assert (tmp_path / "strategies" / "py-bot.py").exists()

    source, read_meta_result = read_strategy(tmp_path, "py-bot")
    assert "def decide" in source
    assert read_meta_result.language == "python"


def test_delete_js_strategy(tmp_path):
    meta = StrategyLibraryMeta(
        provider="manual", model="hand-written",
        created_by="manual", created_at="2026-01-01T00:00:00Z",
        last_modified_at="2026-01-01T00:00:00Z",
        language="javascript",
    )
    write_strategy(tmp_path, "del-me", "function decide(){}", meta)
    assert (tmp_path / "strategies" / "del-me.js").exists()

    delete_strategy(tmp_path, "del-me")
    assert not (tmp_path / "strategies" / "del-me.js").exists()
    assert not (tmp_path / "strategies" / "del-me.meta.json").exists()


def test_list_strategies_includes_both_languages(tmp_path):
    py_meta = StrategyLibraryMeta(
        provider="manual", model="hand-written",
        created_by="manual", created_at="", last_modified_at="",
        language="python",
    )
    js_meta = StrategyLibraryMeta(
        provider="manual", model="hand-written",
        created_by="manual", created_at="", last_modified_at="",
        language="javascript",
    )
    write_strategy(tmp_path, "py-bot", "def decide(gs,ps,h): return Hold()", py_meta)
    write_strategy(tmp_path, "js-bot", "function decide(gs,ps,h){return {type:'Hold'};}", js_meta)

    entries = list_strategies(tmp_path)
    names = {name for name, _ in entries}
    assert names == {"py-bot", "js-bot"}
    langs = {name: m.language for name, m in entries}
    assert langs["py-bot"] == "python"
    assert langs["js-bot"] == "javascript"


def test_list_strategies_legacy_py_without_language_field(tmp_path):
    """Legacy .py files without a language field in sidecar default to python."""
    d = tmp_path / "strategies"
    d.mkdir(parents=True)
    (d / "old-strat.py").write_text("def decide(gs,ps,h): return Hold()")

    entries = list_strategies(tmp_path)
    assert len(entries) == 1
    name, meta = entries[0]
    assert name == "old-strat"
    assert meta.language == "python"


def test_list_strategies_legacy_js_without_sidecar(tmp_path):
    """A .js file without a sidecar infers language=javascript from extension."""
    d = tmp_path / "strategies"
    d.mkdir(parents=True)
    (d / "raw-js.js").write_text("function decide(){return {type:'Hold'};}")

    entries = list_strategies(tmp_path)
    assert len(entries) == 1
    name, meta = entries[0]
    assert name == "raw-js"
    assert meta.language == "javascript"


# ── Rust language coverage (ADR-0026) ─────────────────────────────────────


def test_lang_to_ext_includes_rust():
    assert _LANG_TO_EXT["rust"] == ".rs"


def test_ext_to_lang_includes_rs():
    assert _EXT_TO_LANG[".rs"] == "rust"


def test_source_path_rust(tmp_path):
    p = source_path(tmp_path, "foo", language="rust")
    assert p.suffix == ".rs"
    assert p.name == "foo.rs"


def test_write_and_read_rs_strategy(tmp_path):
    meta = StrategyLibraryMeta(
        provider="manual", model="hand-written",
        created_by="manual", created_at="2026-01-01T00:00:00Z",
        last_modified_at="2026-01-01T00:00:00Z",
        language="rust",
    )
    write_strategy(tmp_path, "rs-bot", "fn decide_logic() {}", meta)
    assert (tmp_path / "strategies" / "rs-bot.rs").exists()
    assert not (tmp_path / "strategies" / "rs-bot.py").exists()
    assert not (tmp_path / "strategies" / "rs-bot.js").exists()

    source, read_meta_result = read_strategy(tmp_path, "rs-bot")
    assert "fn decide_logic" in source
    assert read_meta_result.language == "rust"


def test_delete_rs_strategy(tmp_path):
    meta = StrategyLibraryMeta(
        provider="manual", model="hand-written",
        created_by="manual", created_at="2026-01-01T00:00:00Z",
        last_modified_at="2026-01-01T00:00:00Z",
        language="rust",
    )
    write_strategy(tmp_path, "del-rs", "fn decide_logic() {}", meta)
    assert (tmp_path / "strategies" / "del-rs.rs").exists()

    delete_strategy(tmp_path, "del-rs")
    assert not (tmp_path / "strategies" / "del-rs.rs").exists()
    assert not (tmp_path / "strategies" / "del-rs.meta.json").exists()


def test_list_strategies_legacy_rs_without_sidecar(tmp_path):
    """A .rs file without a sidecar infers language=rust from extension."""
    d = tmp_path / "strategies"
    d.mkdir(parents=True)
    (d / "raw-rs.rs").write_text("fn decide_logic() {}")

    entries = list_strategies(tmp_path)
    assert len(entries) == 1
    name, meta = entries[0]
    assert name == "raw-rs"
    assert meta.language == "rust"


def test_list_strategies_includes_all_three_languages(tmp_path):
    py_meta = StrategyLibraryMeta(
        provider="manual", model="hand-written",
        created_by="manual", created_at="", last_modified_at="",
        language="python",
    )
    js_meta = replace(py_meta, language="javascript")
    rs_meta = replace(py_meta, language="rust")
    write_strategy(tmp_path, "py-bot", "def decide(gs,ps,h): return Hold()", py_meta)
    write_strategy(tmp_path, "js-bot", "function decide(gs,ps,h){return {type:'Hold'};}", js_meta)
    write_strategy(tmp_path, "rs-bot", "fn decide_logic() {}", rs_meta)

    entries = list_strategies(tmp_path)
    langs = {name: m.language for name, m in entries}
    assert langs == {"py-bot": "python", "js-bot": "javascript", "rs-bot": "rust"}