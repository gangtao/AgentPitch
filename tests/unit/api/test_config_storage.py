"""Tests for Storage tab HTTP endpoints."""
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from fastapi.testclient import TestClient

from src.api.http_server.app import create_app


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def client(temp_dir):
    """Create a FastAPI test client with a temporary log directory."""
    app = create_app(log_dir=str(temp_dir), seed_defaults=False)
    return TestClient(app)


class TestGetConfigStorageSection:
    """Test GET /api/config includes storage data."""

    def test_includes_storage_section_with_defaults(self, client, temp_dir):
        """GET /api/config includes storage.data_home, .subdirs, .free_bytes."""
        response = client.get("/api/config")
        assert response.status_code == 200

        data = response.json()
        assert "storage" in data

        storage = data["storage"]
        assert "data_home" in storage
        assert "subdirs" in storage
        assert "free_bytes" in storage

        # Should default to the temp_dir when no storage-settings.yaml exists.
        # Compare resolved paths on both sides to handle macOS /var → /private/var.
        assert Path(storage["data_home"]).resolve() == temp_dir.resolve()
        assert isinstance(storage["free_bytes"], int)
        assert storage["free_bytes"] >= 0

    def test_storage_data_home_matches_server_data_dir(self, client, temp_dir):
        """Per the 2026-04-24 simplification, data_home is fixed at server
        startup (--data-dir flag) and cannot be overridden by a yaml file
        in the data dir. Even if storage-settings.yaml exists, it's ignored."""
        # Write a storage-settings.yaml that would have overridden things
        # under the old design — confirm it's now ignored.
        settings_file = temp_dir / "storage-settings.yaml"
        with open(settings_file, 'w') as f:
            yaml.safe_dump({"data_home": "/some/other/path"}, f)

        response = client.get("/api/config")
        assert response.status_code == 200

        storage = response.json()["storage"]
        # data_home should match the server's data dir (temp_dir), not the
        # yaml override.
        assert Path(storage["data_home"]).resolve() == temp_dir.resolve()

    def test_includes_subdirectory_stats(self, client, temp_dir):
        """GET /api/config includes computed subdirectory statistics."""
        # Create some test directories and files
        matches_dir = temp_dir / "matches"
        matches_dir.mkdir()
        (matches_dir / "test_match.jsonl").write_text("test data")

        strategies_dir = temp_dir / "strategies"
        strategies_dir.mkdir()
        (strategies_dir / "strategy.py").write_text("def decide(): pass")

        response = client.get("/api/config")
        assert response.status_code == 200

        subdirs = response.json()["storage"]["subdirs"]

        # Should include standard subdirectories
        assert "matches/" in subdirs
        assert "strategies/" in subdirs
        assert "configs/" in subdirs
        assert "arena/" in subdirs

        # Should include special files (even if they don't exist)
        assert "global-defaults.yaml" in subdirs
        assert "llm-providers.yaml" in subdirs
        assert ".secrets.json" in subdirs

        # Check that existing directories show stats
        matches_stats = subdirs["matches/"]
        assert matches_stats["entries"] == 1  # One file created
        assert matches_stats["size_mb"] >= 0  # tiny file rounds to 0.0 MB at 1 decimal

    def test_cache_returns_same_values_within_30s(self, client, temp_dir):
        """Cache returns same subdirectory values within 30 seconds."""
        with patch('time.time', return_value=1000.0):
            response1 = client.get("/api/config")
            subdirs1 = response1.json()["storage"]["subdirs"]

        # Same time bucket (within 30s)
        with patch('time.time', return_value=1015.0):
            response2 = client.get("/api/config")
            subdirs2 = response2.json()["storage"]["subdirs"]

        assert subdirs1 == subdirs2

        # Different time bucket (after 30s) should recompute
        with patch('time.time', return_value=1031.0):
            response3 = client.get("/api/config")
            subdirs3 = response3.json()["storage"]["subdirs"]

        # Should be computed fresh (though values might be the same if no changes)
        assert "matches/" in subdirs3


class TestPutConfigStorage:
    """Storage tab is read-only as of 2026-04-24 — PUT now returns 405.

    The data directory is fixed at server startup via
    `agent-pitch serve --data-dir <path>`. The UI cannot change it.
    """

    def test_put_returns_405_method_not_allowed(self, client, temp_dir):
        """PUT /api/config/storage rejects all writes with 405."""
        new_data_home = temp_dir / "new_data"
        new_data_home.mkdir()

        response = client.put(
            "/api/config/storage",
            json={"data_home": str(new_data_home.resolve())},
        )
        assert response.status_code == 405
        assert "read-only" in response.json()["detail"].lower()

    def test_settings_file_not_created_after_put(self, client, temp_dir):
        """No storage-settings.yaml file is written by the rejected PUT."""
        new_data_home = temp_dir / "no_persist"
        new_data_home.mkdir()
        client.put("/api/config/storage", json={"data_home": str(new_data_home.resolve())})
        assert not (temp_dir / "storage-settings.yaml").exists()

    def test_path_with_dotdot_returns_422(self, client, temp_dir):
        """PUT /api/config/storage with .. in path returns 422."""
        bad_path = str(temp_dir / ".." / "bad")

        response = client.put("/api/config/storage",
                            json={"data_home": bad_path})
        assert response.status_code == 422
        # FastAPI 422 returns a list of error dicts under "detail"
        errors = response.json()["detail"]
        assert any(".." in err.get("msg", "") for err in errors)

    def test_unwritable_path_returns_422(self, client, temp_dir):
        """PUT /api/config/storage with unwritable path returns 422."""
        # Try to use a path that doesn't exist with unwritable parent
        if os.name != 'nt':  # Skip on Windows where permission model is different
            readonly_dir = temp_dir / "readonly"
            readonly_dir.mkdir(mode=0o444)  # Read-only directory
            bad_path = readonly_dir / "subdir"

            response = client.put("/api/config/storage",
                                json={"data_home": str(bad_path)})
            assert response.status_code == 422
            # Either "not writable" or "not accessible (permission denied)"
            # depending on whether the unreadable parent triggers a PermissionError
            errors = response.json()["detail"]
            assert any(
                ("not writable" in err.get("msg", ""))
                or ("not accessible" in err.get("msg", ""))
                or ("permission denied" in err.get("msg", "").lower())
                for err in errors
            )

    def test_empty_path_returns_422(self, client, temp_dir):
        """PUT /api/config/storage with empty path returns 422."""
        response = client.put("/api/config/storage",
                            json={"data_home": ""})
        assert response.status_code == 422

    def test_invalid_json_returns_422(self, client, temp_dir):
        """PUT /api/config/storage with invalid JSON returns 422."""
        response = client.put("/api/config/storage",
                            json={"invalid": "field"})
        assert response.status_code == 422

    def test_valid_path_still_returns_405(self, client, temp_dir):
        """Even a perfectly valid path is rejected — Storage is read-only."""
        response = client.put(
            "/api/config/storage",
            json={"data_home": str(temp_dir.resolve())},
        )
        assert response.status_code == 405


class TestStorageConfigIntegration:
    """Integration tests for storage config flow (now read-only)."""

    def test_get_returns_server_data_dir_unchanged_by_put_attempts(self, client, temp_dir):
        """PUT attempts return 405; GET continues to return the server's --data-dir."""
        client.put("/api/config/storage", json={"data_home": "/some/other/path"})

        get_response = client.get("/api/config")
        assert get_response.status_code == 200
        storage = get_response.json()["storage"]
        # data_home is still the server's data_dir (temp_dir), unchanged.
        assert Path(storage["data_home"]).resolve() == temp_dir.resolve()