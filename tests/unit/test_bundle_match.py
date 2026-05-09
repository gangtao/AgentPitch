import json
import sys
import tempfile
from pathlib import Path

# Ensure tools/ is importable
sys.path.insert(0, str(Path(__file__).parents[2]))

from tools.bundle_match import bundle_match, parse_match_dir


def _make_match_dir(tmp_path: Path, include_strategies: bool = False) -> Path:
    match_dir = tmp_path / "match_test123"
    match_dir.mkdir()
    meta = {
        "match_id": "test123",
        "final_score": {"team_a": 2, "team_b": 1},
        "tick_rate": 10,
        "total_ticks": 100,
        "teams": {"team_a": [], "team_b": []},
    }
    (match_dir / "meta.json").write_text(json.dumps(meta))
    events = "\n".join([
        json.dumps({"tick": i, "ball_possession": "team_a", "player_positions": {}, "actions": []})
        for i in range(3)
    ])
    (match_dir / "events.jsonl").write_text(events)
    if include_strategies:
        (match_dir / "strategy_team_a.py").write_text("def decide(): pass")
        (match_dir / "strategy_team_b.js").write_text("function decide() {}")
    return match_dir


def test_parse_match_dir_required_files(tmp_path):
    match_dir = _make_match_dir(tmp_path)
    result = parse_match_dir(match_dir)
    assert result["meta"]["match_id"] == "test123"
    assert len(result["ticks"]) == 3
    assert result["ticks"][0]["tick"] == 0
    assert result["strategies"] is None


def test_parse_match_dir_with_strategies(tmp_path):
    match_dir = _make_match_dir(tmp_path, include_strategies=True)
    result = parse_match_dir(match_dir)
    assert result["strategies"]["team_a"] == "def decide(): pass"
    assert result["strategies"]["team_b"] == "function decide() {}"


def test_bundle_match_injects_script(tmp_path):
    match_dir = _make_match_dir(tmp_path)
    viewer_html = "<html><body><p>viewer</p></body></html>"
    output = bundle_match(viewer_html, parse_match_dir(match_dir))
    assert "window.BUNDLED_MATCH" in output
    assert '"match_id": "test123"' in output or '"match_id":"test123"' in output
    # Script must be injected after <body>
    body_pos = output.index("<body>")
    script_pos = output.index("window.BUNDLED_MATCH")
    assert script_pos > body_pos


def test_bundle_match_output_is_valid_html(tmp_path):
    match_dir = _make_match_dir(tmp_path)
    viewer_html = "<html><body></body></html>"
    output = bundle_match(viewer_html, parse_match_dir(match_dir))
    assert output.startswith("<html>")
    assert output.endswith("</html>")


def test_parse_match_dir_missing_meta_raises(tmp_path):
    match_dir = tmp_path / "match_bad"
    match_dir.mkdir()
    (match_dir / "events.jsonl").write_text('{"tick":0}\n')
    try:
        parse_match_dir(match_dir)
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        pass


def test_parse_match_dir_missing_events_raises(tmp_path):
    match_dir = tmp_path / "match_bad"
    match_dir.mkdir()
    (match_dir / "meta.json").write_text('{"match_id":"x"}')
    try:
        parse_match_dir(match_dir)
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        pass
