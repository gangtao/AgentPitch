"""Tests for `language` field extraction in `_parse_strategy_header`.

Added 2026-04-26 so the live-viewer chyron can show JS vs PY for each team.
"""

from __future__ import annotations

from src.orchestration.tick_engine.engine import _parse_strategy_header


PY_HEADER_WITH_LANG = (
    "# strategy_v3.py\n"
    "# team_id:      team_a\n"
    "# version:      3\n"
    "# match_number: 0\n"
    "# language:     python\n"
    "# timestamp:    2026-04-26T17:35:11Z\n"
    "# llm_provider: openai\n"
    "# llm_model:    gpt-4o\n"
    "# generated_by: code-generation-pipeline/2.7\n"
    "\n"
    "def decide(g, p, h):\n"
    "    return Hold()\n"
)

JS_HEADER_WITH_LANG = (
    "// strategy_v1.js\n"
    "// team_id:      team_b\n"
    "// version:      1\n"
    "// match_number: 0\n"
    "// language:     javascript\n"
    "// timestamp:    2026-04-26T17:35:11Z\n"
    "// llm_provider: openai\n"
    "// llm_model:    gpt-4o\n"
    "// generated_by: code-generation-pipeline/js\n"
    "\n"
    "function decide(g, p, h) {\n"
    "  return Hold();\n"
    "}\n"
)

LEGACY_PY_HEADER_NO_LANG = (
    "# strategy_v1.py\n"
    "# team_id:      team_a\n"
    "# version:      1\n"
    "# match_number: 0\n"
    "# timestamp:    2026-04-21T00:00:00Z\n"
    "# llm_provider: anthropic\n"
    "# llm_model:    claude-sonnet-4-6\n"
    "# generated_by: code-generation-pipeline/2.5\n"
    "\n"
    "def decide(g, p, h):\n"
    "    return Hold()\n"
)


class TestParseStrategyHeaderLanguage:
    def test_python_header_with_language_field_extracted(self, tmp_path):
        p = tmp_path / "current.py"
        p.write_text(PY_HEADER_WITH_LANG)
        result = _parse_strategy_header(p)
        assert result["language"] == "python"

    def test_javascript_header_extracts_language_and_uses_double_slash(self, tmp_path):
        p = tmp_path / "current.js"
        p.write_text(JS_HEADER_WITH_LANG)
        result = _parse_strategy_header(p)
        assert result["language"] == "javascript"
        # Other fields parsed from the // header too
        assert result["provider"] == "openai"
        assert result["model"] == "gpt-4o"
        assert result["version"] == 1

    def test_legacy_python_header_without_language_defaults_to_python(self, tmp_path):
        p = tmp_path / "current.py"
        p.write_text(LEGACY_PY_HEADER_NO_LANG)
        result = _parse_strategy_header(p)
        assert result["language"] == "python"
        assert result["provider"] == "anthropic"

    def test_missing_file_returns_blank_with_python_default(self, tmp_path):
        result = _parse_strategy_header(tmp_path / "nope.py")
        assert result == {
            "provider": "unknown",
            "model": "unknown",
            "name": "unknown",
            "version": 0,
            "language": "python",
        }
