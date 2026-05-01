"""End-to-end tests for the strategy library sidecar wiring (ADR-0023).

Covers the HTTP surface — GET list, GET single, POST create (manual + LLM),
PUT (preserve+bump, create-as-PUT, legacy upgrade), DELETE pairing — plus
the CLI baseline-loader sidecar lookup.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.http_server.app import create_app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client(tmp_path):
    app = create_app(log_dir=str(tmp_path), seed_defaults=False)
    return TestClient(app)


def _strategies_dir(tmp_path: Path) -> Path:
    return tmp_path / "strategies"


# ---------------------------------------------------------------------------
# POST /api/strategies — create with no meta → manual defaults
# ---------------------------------------------------------------------------


class TestPostCreatesSidecar:
    def test_post_without_meta_writes_manual_sidecar(self, client, tmp_path):
        r = client.post("/api/strategies", json={"name": "no-meta"})
        assert r.status_code == 201
        meta = r.json()["meta"]
        assert meta["provider"] == "manual"
        assert meta["model"] == "hand-written"
        assert meta["created_by"] == "manual"
        assert meta["created_at"]
        assert meta["last_modified_at"] == meta["created_at"]
        # Sidecar file actually exists with the same fields.
        sidecar = _strategies_dir(tmp_path) / "no-meta.meta.json"
        assert sidecar.exists()
        on_disk = json.loads(sidecar.read_text())
        assert on_disk["provider"] == "manual"
        assert on_disk["created_by"] == "manual"

    def test_post_with_manual_meta_persists_fields(self, client, tmp_path):
        r = client.post("/api/strategies", json={
            "name": "manual-pair",
            "source": "def decide(g,p,h): return Hold()\n",
            "meta": {"provider": "manual", "model": "hand-written", "created_by": "manual"},
        })
        assert r.status_code == 201
        meta = r.json()["meta"]
        assert meta["provider"] == "manual"
        assert meta["created_by"] == "manual"
        assert "prompt" not in meta  # optional fields dropped when None
        assert "template_version" not in meta

    def test_post_with_llm_meta_persists_prompt_and_template(self, client, tmp_path):
        r = client.post("/api/strategies", json={
            "name": "llm-pair",
            "source": "def decide(g,p,h): return Hold()\n",
            "meta": {
                "provider":         "anthropic",
                "model":            "claude-sonnet-4-6",
                "created_by":       "llm",
                "prompt":           "Aggressive midfield press.",
                "template_version": "2.5",
            },
        })
        assert r.status_code == 201
        meta = r.json()["meta"]
        assert meta["provider"] == "anthropic"
        assert meta["model"] == "claude-sonnet-4-6"
        assert meta["created_by"] == "llm"
        assert meta["prompt"] == "Aggressive midfield press."
        assert meta["template_version"] == "2.5"

    def test_post_llm_with_empty_prompt_accepted(self, client):
        # Per ADR-0023 amendment 2026-04-26: empty prompt is valid for LLM.
        # /api/strategies/generate allows it (USER INTENT fallback), so the
        # save flow must accept it too — otherwise an empty-prompt generation
        # produces code that can't be persisted.
        r = client.post("/api/strategies", json={
            "name": "empty-prompt-llm",
            "source": "def decide(g,p,h): return Hold()\n",
            "meta": {
                "provider":         "anthropic",
                "model":            "claude-sonnet-4-6",
                "created_by":       "llm",
                "prompt":           "",
                "template_version": "2.5",
            },
        })
        assert r.status_code == 201
        assert r.json()["meta"]["created_by"] == "llm"

    def test_post_llm_without_template_version_rejected(self, client):
        # template_version stays required — it's always known at generation time.
        r = client.post("/api/strategies", json={
            "name": "no-tmpl-llm",
            "source": "def decide(g,p,h): return Hold()\n",
            "meta": {
                "provider":   "anthropic",
                "model":      "claude-sonnet-4-6",
                "created_by": "llm",
                "prompt":     "some prompt",
            },
        })
        assert r.status_code == 400
        assert "template_version" in r.json()["detail"]


# ---------------------------------------------------------------------------
# GET endpoints — meta surfaces in responses
# ---------------------------------------------------------------------------


class TestGetIncludesMeta:
    def test_get_list_returns_meta_per_entry(self, client, tmp_path):
        client.post("/api/strategies", json={
            "name": "alpha", "source": "def decide(g,p,h): return Hold()\n",
            "meta": {"provider": "openai", "model": "gpt-4o", "created_by": "llm",
                     "prompt": "x", "template_version": "2.5"},
        })
        client.post("/api/strategies", json={"name": "beta"})

        r = client.get("/api/strategies")
        assert r.status_code == 200
        rows = {row["name"]: row for row in r.json()}
        assert rows["alpha"]["meta"]["provider"] == "openai"
        assert rows["alpha"]["meta"]["created_by"] == "llm"
        assert rows["beta"]["meta"]["provider"] == "manual"

    def test_get_single_returns_meta(self, client):
        client.post("/api/strategies", json={
            "name": "solo", "source": "def decide(g,p,h): return Hold()\n",
            "meta": {"provider": "anthropic", "model": "claude-sonnet-4-6",
                     "created_by": "llm", "prompt": "x", "template_version": "2.5"},
        })
        r = client.get("/api/strategies/solo")
        assert r.status_code == 200
        body = r.json()
        assert body["meta"]["provider"] == "anthropic"
        assert body["meta"]["template_version"] == "2.5"

    def test_get_legacy_file_reports_unknown_meta(self, client, tmp_path):
        # Drop a .py without a sidecar — predates ADR-0023.
        d = _strategies_dir(tmp_path)
        d.mkdir(parents=True)
        (d / "legacy.py").write_text("def decide(g,p,h): return Hold()\n")

        r = client.get("/api/strategies/legacy")
        assert r.status_code == 200
        assert r.json()["meta"]["provider"] == "unknown"

        rows = {row["name"]: row for row in client.get("/api/strategies").json()}
        assert rows["legacy"]["meta"]["provider"] == "unknown"


# ---------------------------------------------------------------------------
# PUT semantics — preserve+bump, create-as-PUT, legacy upgrade
# ---------------------------------------------------------------------------


class TestPutPreservesProvenance:
    def test_put_existing_llm_preserves_provider_and_keeps_created_by(self, client):
        # Per ADR-0023: "Stay llm" — created_by does NOT flip on edit.
        client.post("/api/strategies", json={
            "name": "edit-me",
            "source": "def decide(g,p,h): return Hold()\n",
            "meta": {"provider": "anthropic", "model": "claude-sonnet-4-6",
                     "created_by": "llm", "prompt": "x", "template_version": "2.5"},
        })
        original_meta = client.get("/api/strategies/edit-me").json()["meta"]
        original_created_at = original_meta["created_at"]

        # PUT with new source (sleep tiny window to differentiate timestamps).
        import time as _t
        _t.sleep(1.1)
        r = client.put("/api/strategies/edit-me",
                       json={"source": "def decide(g,p,h): return Move((1.0,0.0))\n"})
        assert r.status_code == 200
        meta = r.json()["meta"]
        assert meta["provider"] == "anthropic"
        assert meta["model"] == "claude-sonnet-4-6"
        assert meta["created_by"] == "llm"
        assert meta["prompt"] == "x"
        assert meta["template_version"] == "2.5"
        assert meta["created_at"] == original_created_at
        assert meta["last_modified_at"] != original_created_at

    def test_put_create_writes_manual_sidecar(self, client, tmp_path):
        r = client.put("/api/strategies/freshly-put",
                       json={"source": "def decide(g,p,h): return Hold()\n"})
        assert r.status_code == 200
        meta = r.json()["meta"]
        assert meta["provider"] == "manual"
        assert meta["created_by"] == "manual"
        # Sidecar on disk.
        assert (_strategies_dir(tmp_path) / "freshly-put.meta.json").exists()

    def test_put_on_legacy_file_synthesizes_unknown_sidecar(self, client, tmp_path):
        d = _strategies_dir(tmp_path)
        d.mkdir(parents=True)
        (d / "legacy-edit.py").write_text("def decide(g,p,h): return Hold()\n")

        r = client.put("/api/strategies/legacy-edit",
                       json={"source": "def decide(g,p,h): return Move((1,0))\n"})
        assert r.status_code == 200
        meta = r.json()["meta"]
        # Legacy upgrade: provider stays unknown (we don't fabricate a guess),
        # created_by defaults to manual, last_modified_at is set.
        assert meta["provider"] == "unknown"
        assert meta["created_by"] == "manual"
        assert meta["last_modified_at"]
        assert (d / "legacy-edit.meta.json").exists()


# ---------------------------------------------------------------------------
# DELETE — removes both files
# ---------------------------------------------------------------------------


class TestDeletePairing:
    def test_delete_removes_both_files(self, client, tmp_path):
        client.post("/api/strategies", json={"name": "delete-me"})
        d = _strategies_dir(tmp_path)
        assert (d / "delete-me.py").exists()
        assert (d / "delete-me.meta.json").exists()

        r = client.delete("/api/strategies/delete-me")
        assert r.status_code == 204
        assert not (d / "delete-me.py").exists()
        assert not (d / "delete-me.meta.json").exists()

    def test_delete_legacy_without_sidecar(self, client, tmp_path):
        d = _strategies_dir(tmp_path)
        d.mkdir(parents=True)
        (d / "legacy-del.py").write_text("def decide(g,p,h): return Hold()\n")
        # No sidecar.
        r = client.delete("/api/strategies/legacy-del")
        assert r.status_code == 204
        assert not (d / "legacy-del.py").exists()


# ---------------------------------------------------------------------------
# /api/strategies/generate — provider/model/prompt echo
# ---------------------------------------------------------------------------


class TestSeedDefaults:
    def test_seed_defaults_writes_baseline_sidecar(self, tmp_path):
        """First-start seeding writes both `baseline.py` and `baseline.meta.json`.

        Per ADR-0023 — a fresh data-dir must produce a sidecar so the baseline
        doesn't surface as `unknown` in match meta.
        """
        # seed_defaults=True triggers _seed_default_data() during create_app.
        app = create_app(log_dir=str(tmp_path), seed_defaults=True)
        # Expose to satisfy mypy / linter — app is intentionally constructed
        # for its side-effect on disk.
        assert app is not None

        baseline_py = tmp_path / "strategies" / "baseline.py"
        baseline_meta = tmp_path / "strategies" / "baseline.meta.json"

        # baseline.py only seeds when the source path exists in this checkout.
        if not baseline_py.exists():
            pytest.skip("baseline source not present in this checkout")

        assert baseline_meta.exists(), "baseline.meta.json must be seeded next to baseline.py"
        meta = json.loads(baseline_meta.read_text())
        assert meta["provider"] == "baseline"
        assert meta["model"] == "hand-written"
        assert meta["created_by"] == "manual"
        assert meta["created_at"]
        assert meta["last_modified_at"] == meta["created_at"]


class TestGenerateEcho:
    def test_generate_returns_provenance_for_save(self, client, tmp_path, monkeypatch):
        """Mock the subprocess so we don't actually call an LLM. Verify the
        endpoint echoes provider/model/prompt back to the caller for the
        subsequent POST /api/strategies (per ADR-0023 frontend contract)."""
        import asyncio

        async def fake_create_subprocess_exec(*args, **kwargs):
            class FakeProc:
                async def communicate(self):
                    payload = json.dumps({
                        "ok":               True,
                        "code":             "def decide(g,p,h): return Hold()\n",
                        "template_version": "2.5",
                    })
                    return (payload.encode("utf-8"), b"")

                def kill(self): pass
                async def wait(self): pass
            return FakeProc()

        monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_create_subprocess_exec)

        r = client.post("/api/strategies/generate", json={
            "name":     "ignored",  # subprocess doesn't save; name is placeholder
            "prompt":   "Be aggressive in midfield.",
            "provider": "anthropic",
            "model":    "claude-sonnet-4-6",
        })
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert body["code"]
        assert body["provider"] == "anthropic"
        assert body["model"] == "claude-sonnet-4-6"
        assert body["prompt"] == "Be aggressive in midfield."
        assert body["template_version"] == "2.5"
