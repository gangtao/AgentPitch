"""Tests for Arena series API endpoints.

Covers GET/POST/DELETE /api/arena and supporting helpers.
All filesystem I/O uses pytest tmp_path; subprocess spawning is mocked.
"""
from __future__ import annotations

import json
import time
import unittest.mock as mock
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.http_server.app import create_app
from src.api.http_server.series_metadata import (
    series_dir,
    read_series_json,
    write_series_json,
    list_series,
)


# ───────────────────────────────────────────────────────────────────
# Fixtures
# ───────────────────────────────────────────────────────────────────

@pytest.fixture
def data_home(tmp_path: Path) -> Path:
    """Minimal data-home directory with required subdirectories."""
    dh = tmp_path / "data"
    (dh / "configs").mkdir(parents=True)
    (dh / "strategies").mkdir(parents=True)
    (dh / "matches").mkdir(parents=True)
    (dh / "arena").mkdir(parents=True)
    return dh


@pytest.fixture
def app(data_home: Path):
    """FastAPI app wired to the temp data_home."""
    return create_app(str(data_home), seed_defaults=False)


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)


def _make_series_json(
    data_home: Path,
    series_id: str,
    started_iso: str = "2026-04-23T14:32:00Z",
    status: str = "complete",
    score: dict | None = None,
    matches: list | None = None,
    fmt: str = "3-match",
) -> dict:
    """Write a series directory + series.json and return the data dict."""
    arena_dir = data_home / "arena"
    s_dir = series_dir(arena_dir, series_id)
    s_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "series_id":     series_id,
        "format":        fmt,
        "status":        status,
        "config_name":   "5v5",
        "started_iso":   started_iso,
        "completed_iso": None,
        "matches":       matches or [],
        "score":         score or {"team_a": 0, "team_b": 0, "ties": 0},
    }
    write_series_json(s_dir, data)
    return data


# ───────────────────────────────────────────────────────────────────
# series_metadata helpers (unit)
# ───────────────────────────────────────────────────────────────────

class TestSeriesMetadataHelpers:
    def test_series_dir_returns_correct_path(self, tmp_path: Path):
        arena = tmp_path / "arena"
        result = series_dir(arena, "abc-123")
        assert result == arena / "series_abc-123"

    def test_read_series_json_success(self, tmp_path: Path):
        s_dir = tmp_path / "series_x"
        s_dir.mkdir()
        data = {"series_id": "x", "status": "running"}
        write_series_json(s_dir, data)
        assert read_series_json(s_dir) == data

    def test_read_series_json_missing_raises(self, tmp_path: Path):
        s_dir = tmp_path / "series_missing"
        s_dir.mkdir()
        with pytest.raises(FileNotFoundError):
            read_series_json(s_dir)

    def test_write_series_json_atomic(self, tmp_path: Path):
        """write_series_json must not leave a .tmp file behind."""
        s_dir = tmp_path / "series_atomic"
        s_dir.mkdir()
        data = {"series_id": "atomic", "status": "running"}
        write_series_json(s_dir, data)
        assert (s_dir / "series.json").exists()
        assert not (s_dir / "series.json.tmp").exists()

    def test_list_series_empty_when_no_arena_dir(self, tmp_path: Path):
        arena = tmp_path / "missing_arena"
        assert list_series(arena) == []

    def test_list_series_empty_when_no_series_dirs(self, tmp_path: Path):
        arena = tmp_path / "arena"
        arena.mkdir()
        assert list_series(arena) == []

    def test_list_series_sorted_by_started_iso_desc(self, tmp_path: Path):
        arena = tmp_path / "arena"
        arena.mkdir()
        for sid, iso in [("a", "2026-04-20T10:00:00Z"), ("b", "2026-04-22T10:00:00Z")]:
            s = arena / f"series_{sid}"
            s.mkdir()
            write_series_json(s, {"series_id": sid, "started_iso": iso, "format": "3-match",
                                   "status": "complete", "config_name": "5v5",
                                   "completed_iso": None, "matches": [],
                                   "score": {"team_a": 0, "team_b": 0, "ties": 0}})
        result = list_series(arena)
        assert len(result) == 2
        assert result[0]["series_id"] == "b"  # newer first
        assert result[1]["series_id"] == "a"

    def test_list_series_skips_malformed_series_json(self, tmp_path: Path):
        arena = tmp_path / "arena"
        arena.mkdir()
        # Good series
        s_good = arena / "series_good"
        s_good.mkdir()
        write_series_json(s_good, {"series_id": "good", "started_iso": "2026-04-23T00:00:00Z",
                                    "format": "3-match", "status": "complete", "config_name": "x",
                                    "completed_iso": None, "matches": [],
                                    "score": {"team_a": 0, "team_b": 0, "ties": 0}})
        # Bad series (malformed JSON)
        s_bad = arena / "series_bad"
        s_bad.mkdir()
        (s_bad / "series.json").write_text("NOT JSON", encoding="utf-8")

        result = list_series(arena)
        assert len(result) == 1
        assert result[0]["series_id"] == "good"

    def test_list_series_skips_non_series_dirs(self, tmp_path: Path):
        arena = tmp_path / "arena"
        arena.mkdir()
        # A dir without the prefix should be ignored
        (arena / "matches").mkdir()
        assert list_series(arena) == []


# ───────────────────────────────────────────────────────────────────
# GET /api/arena
# ───────────────────────────────────────────────────────────────────

class TestGetArena:
    def test_get_arena_empty_list_when_no_arena_dir(self, data_home: Path, client: TestClient):
        """Returns [] when arena dir doesn't exist yet."""
        import shutil
        shutil.rmtree(data_home / "arena")
        response = client.get("/api/arena")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_arena_empty_list_when_no_series(self, client: TestClient):
        """Returns [] when arena dir exists but contains no series subdirs."""
        response = client.get("/api/arena")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_arena_returns_sorted_summaries(self, data_home: Path, client: TestClient):
        """Returns summaries sorted by started_iso desc."""
        _make_series_json(data_home, "older", started_iso="2026-04-20T10:00:00Z")
        _make_series_json(data_home, "newer", started_iso="2026-04-22T10:00:00Z")

        response = client.get("/api/arena")
        assert response.status_code == 200
        items = response.json()
        assert len(items) == 2
        assert items[0]["series_id"] == "newer"
        assert items[1]["series_id"] == "older"

    def test_get_arena_summary_shape(self, data_home: Path, client: TestClient):
        """Each summary has the expected keys."""
        _make_series_json(data_home, "test-series", score={"team_a": 2, "team_b": 1, "ties": 0})
        response = client.get("/api/arena")
        item = response.json()[0]
        for key in ("series_id", "format", "status", "config_name", "started_iso", "completed_iso", "score"):
            assert key in item, f"Missing key: {key}"


# ───────────────────────────────────────────────────────────────────
# GET /api/arena/{series_id}
# ───────────────────────────────────────────────────────────────────

class TestGetArenaSeries:
    def test_get_series_returns_200_with_full_data(self, data_home: Path, client: TestClient):
        """Returns full series.json including matches array."""
        matches = [{"match_number": 1, "match_id": "m1", "result": "team_a",
                    "final_score": {"team_a": 2, "team_b": 0}}]
        _make_series_json(data_home, "my-series", matches=matches)

        response = client.get("/api/arena/my-series")
        assert response.status_code == 200
        data = response.json()
        assert data["series_id"] == "my-series"
        assert len(data["matches"]) == 1
        assert data["matches"][0]["match_id"] == "m1"

    def test_get_series_returns_404_for_missing_series(self, client: TestClient):
        """Returns 404 when series directory does not exist."""
        response = client.get("/api/arena/nonexistent-series")
        assert response.status_code == 404

    def test_get_series_returns_404_for_missing_series_json(self, data_home: Path, client: TestClient):
        """Returns 404 when directory exists but series.json is absent."""
        s_dir = series_dir(data_home / "arena", "no-json")
        s_dir.mkdir(parents=True)
        # No series.json written
        response = client.get("/api/arena/no-json")
        assert response.status_code == 404


# ───────────────────────────────────────────────────────────────────
# POST /api/arena
# ───────────────────────────────────────────────────────────────────

class TestPostArena:
    def test_post_arena_returns_201_with_series_id(self, data_home: Path, client: TestClient):
        """201 with series_id when config exists and subprocess spawns ok."""
        (data_home / "configs" / "5v5.yaml").write_text("match:\n  seed: 42\n", encoding="utf-8")

        fake_popen = mock.MagicMock()
        fake_popen.pid = 12345
        with mock.patch("subprocess.Popen", return_value=fake_popen):
            response = client.post("/api/arena", json={"config_name": "5v5", "format": "3-match"})

        assert response.status_code == 201
        body = response.json()
        assert "series_id" in body
        assert body["series_id"].startswith("series-")

    def test_post_arena_creates_series_json(self, data_home: Path, client: TestClient):
        """series.json is created on disk with status=running."""
        (data_home / "configs" / "5v5.yaml").write_text("match:\n  seed: 42\n", encoding="utf-8")

        fake_popen = mock.MagicMock()
        fake_popen.pid = 12345
        with mock.patch("subprocess.Popen", return_value=fake_popen):
            response = client.post("/api/arena", json={"config_name": "5v5", "format": "5-match"})

        series_id = response.json()["series_id"]
        s_dir = series_dir(data_home / "arena", series_id)
        data = read_series_json(s_dir)

        assert data["series_id"] == series_id
        assert data["status"] == "running"
        assert data["format"] == "5-match"
        assert data["config_name"] == "5v5"
        assert data["matches"] == []
        assert data["score"] == {"team_a": 0, "team_b": 0, "ties": 0}

    def test_post_arena_returns_404_when_config_missing(self, client: TestClient):
        """404 when config_name does not resolve to a file on disk."""
        response = client.post("/api/arena", json={"config_name": "ghost", "format": "3-match"})
        assert response.status_code == 404

    def test_post_arena_rejects_invalid_format(self, data_home: Path, client: TestClient):
        """422 when format is not '3-match' or '5-match'."""
        (data_home / "configs" / "5v5.yaml").write_text("match:\n  seed: 42\n", encoding="utf-8")
        response = client.post("/api/arena", json={"config_name": "5v5", "format": "7-match"})
        assert response.status_code == 422

    def test_post_arena_spawns_subprocess_with_arena_id(self, data_home: Path, client: TestClient):
        """subprocess.Popen is called with --arena-id flag."""
        (data_home / "configs" / "5v5.yaml").write_text("match:\n  seed: 42\n", encoding="utf-8")

        fake_popen = mock.MagicMock()
        fake_popen.pid = 99
        with mock.patch("subprocess.Popen", return_value=fake_popen) as mock_popen:
            response = client.post("/api/arena", json={"config_name": "5v5", "format": "3-match"})

        assert response.status_code == 201
        call_args = mock_popen.call_args
        cmd = call_args[0][0]
        assert "--arena-id" in cmd
        assert "--season-length" in cmd
        # Verify season length is 3 for 3-match format
        idx = cmd.index("--season-length")
        assert cmd[idx + 1] == "3"

    def test_post_arena_season_length_5_for_5_match(self, data_home: Path, client: TestClient):
        """--season-length is 5 for '5-match' format."""
        (data_home / "configs" / "5v5.yaml").write_text("match:\n  seed: 42\n", encoding="utf-8")

        fake_popen = mock.MagicMock()
        fake_popen.pid = 99
        with mock.patch("subprocess.Popen", return_value=fake_popen) as mock_popen:
            response = client.post("/api/arena", json={"config_name": "5v5", "format": "5-match"})

        assert response.status_code == 201
        cmd = mock_popen.call_args[0][0]
        idx = cmd.index("--season-length")
        assert cmd[idx + 1] == "5"


# ───────────────────────────────────────────────────────────────────
# DELETE /api/arena/{series_id}
# ───────────────────────────────────────────────────────────────────

class TestDeleteArenaSeries:
    def test_delete_series_returns_204_and_removes_dir(self, data_home: Path, client: TestClient):
        """204 returned and series directory is removed."""
        _make_series_json(data_home, "to-delete")
        s_dir = series_dir(data_home / "arena", "to-delete")
        assert s_dir.is_dir()

        response = client.delete("/api/arena/to-delete")
        assert response.status_code == 204
        assert not s_dir.exists()

    def test_delete_series_returns_404_when_not_found(self, client: TestClient):
        """404 when series directory doesn't exist."""
        response = client.delete("/api/arena/ghost-series")
        assert response.status_code == 404

    def test_delete_series_cascade_removes_match_dirs(self, data_home: Path, client: TestClient):
        """cascade=true removes associated match directories."""
        match_id = "match-abc"
        match_dir = data_home / "matches" / f"match_{match_id}"
        match_dir.mkdir(parents=True)
        (match_dir / "meta.json").write_text(json.dumps({"match_id": match_id}), encoding="utf-8")

        matches = [{"match_number": 1, "match_id": match_id, "result": "team_a",
                    "final_score": {"team_a": 1, "team_b": 0}}]
        _make_series_json(data_home, "cascade-series", matches=matches)

        response = client.delete("/api/arena/cascade-series?cascade=true")
        assert response.status_code == 204
        # Both the series dir and the match dir must be gone
        assert not series_dir(data_home / "arena", "cascade-series").exists()
        assert not match_dir.exists()

    def test_delete_series_cascade_tolerates_missing_match_dir(self, data_home: Path, client: TestClient):
        """cascade=true succeeds even when a listed match dir is already gone."""
        matches = [{"match_number": 1, "match_id": "already-deleted", "result": "tie",
                    "final_score": {"team_a": 1, "team_b": 1}}]
        _make_series_json(data_home, "grace-series", matches=matches)

        response = client.delete("/api/arena/grace-series?cascade=true")
        assert response.status_code == 204

    def test_delete_series_no_cascade_leaves_match_dirs(self, data_home: Path, client: TestClient):
        """cascade=false (default) does NOT remove associated match dirs."""
        match_id = "keep-me"
        match_dir = data_home / "matches" / f"match_{match_id}"
        match_dir.mkdir(parents=True)

        matches = [{"match_number": 1, "match_id": match_id, "result": "team_b",
                    "final_score": {"team_a": 0, "team_b": 2}}]
        _make_series_json(data_home, "no-cascade-series", matches=matches)

        response = client.delete("/api/arena/no-cascade-series")
        assert response.status_code == 204
        # Match dir should still exist
        assert match_dir.exists()


# ───────────────────────────────────────────────────────────────────
# GET /api/arena/{series_id}/diff/{team}/{match_n}
# ───────────────────────────────────────────────────────────────────

class TestGetStrategyDiff:
    def _setup_strategy_files(self, data_home: Path, series_id: str, team: str,
                               versions: dict[int, str]) -> None:
        """Write strategy version files for a team in a series."""
        strat_dir = series_dir(data_home / "arena", series_id) / "strategies" / team
        strat_dir.mkdir(parents=True, exist_ok=True)
        for version, content in versions.items():
            (strat_dir / f"strategy_v{version}.py").write_text(content, encoding="utf-8")

    def test_diff_match_1_returns_empty_diff_from_none(self, data_home: Path, client: TestClient):
        """Match 1 diff has from_version=0 (no prior) and diff against empty."""
        _make_series_json(data_home, "diff-series")
        self._setup_strategy_files(data_home, "diff-series", "team_a", {
            1: "def decide(g, p, h):\n    return Hold()\n"
        })

        response = client.get("/api/arena/diff-series/diff/team_a/1")
        assert response.status_code == 200
        body = response.json()
        assert body["team"] == "team_a"
        assert body["from_version"] == 0
        assert body["to_version"] == 1
        assert isinstance(body["diff_text"], str)

    def test_diff_match_2_shows_changes(self, data_home: Path, client: TestClient):
        """Match 2 diff is a real unified diff between v1 and v2."""
        _make_series_json(data_home, "diff2-series")
        self._setup_strategy_files(data_home, "diff2-series", "team_b", {
            1: "def decide(g, p, h):\n    return Hold()\n",
            2: "def decide(g, p, h):\n    return Move(1, 0, p['speed'])\n",
        })

        response = client.get("/api/arena/diff2-series/diff/team_b/2")
        assert response.status_code == 200
        body = response.json()
        assert body["from_version"] == 1
        assert body["to_version"] == 2
        # Diff text must contain a removed line (-) and added line (+)
        assert "-" in body["diff_text"]
        assert "+" in body["diff_text"]

    def test_diff_returns_404_for_missing_series(self, client: TestClient):
        """404 when series doesn't exist."""
        response = client.get("/api/arena/ghost/diff/team_a/1")
        assert response.status_code == 404

    def test_diff_returns_404_for_missing_strategy_file(self, data_home: Path, client: TestClient):
        """404 when strategy_v<N>.py doesn't exist."""
        _make_series_json(data_home, "missing-strat")
        response = client.get("/api/arena/missing-strat/diff/team_a/3")
        assert response.status_code == 404

    def test_diff_returns_422_for_bad_team(self, data_home: Path, client: TestClient):
        """422 when team is not 'team_a' or 'team_b'."""
        _make_series_json(data_home, "bad-team-series")
        self._setup_strategy_files(data_home, "bad-team-series", "team_a", {1: "pass\n"})
        response = client.get("/api/arena/bad-team-series/diff/team_c/1")
        assert response.status_code == 422
