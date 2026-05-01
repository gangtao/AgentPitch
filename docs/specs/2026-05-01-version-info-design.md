# Version Info Design

**Date:** 2026-05-01  
**Status:** Approved

## Goal

Surface a consistent version string — derived from the latest git tag — in three places: the CLI (`--version`), the UI status bar, and the Docker image. The version source of truth is git tags; `setuptools-scm` derives it at install/build time.

## Version Source: setuptools-scm

Replace the static `version = "0.1.0"` in `pyproject.toml` with dynamic derivation via `setuptools-scm`:

- Add `setuptools-scm` to `[build-system].requires`
- Set `dynamic = ["version"]` under `[project]`
- Add `[tool.setuptools_scm]` with `fallback_version = "0.0.0.dev0"` (used when `.git` is absent or the tree has no tags)
- Create the initial git tag `v0.1.0` to anchor the first release
- Re-install locally: `pip install -e .`

After this, `importlib.metadata.version("agent-pitch")` returns the tag-derived version everywhere (CLI, server, tests). The existing `/api/health` endpoint already calls this — no change needed there.

## Docker: Version Build Arg

Without `.git` in the Docker build context, `setuptools-scm` cannot read tags and falls back to `0.0.0.dev0`. Fix by injecting the version at build time:

**Dockerfile** — add before the `pip install` line:
```dockerfile
ARG VERSION=0.0.0.dev0
ENV SETUPTOOLS_SCM_PRETEND_VERSION=${VERSION}
```

`setuptools-scm` respects `SETUPTOOLS_SCM_PRETEND_VERSION`; it uses the env var value instead of querying git.

**`release.yml`** — pass the version to `docker/build-push-action`:
```yaml
build-args: |
  VERSION=${{ steps.meta.outputs.version }}
```

`steps.meta.outputs.version` comes from the existing `docker/metadata-action` step and is already stripped of the `v` prefix (e.g., `0.1.0`). No extra extraction step needed.

## UI Status Bar

The `<footer class="status-bar">` in `index.html` contains a hardcoded span:
```html
<span>PYTHON 3.11 · agent-pitch</span>
```

Changes:
- Add `id="sb-version"` to that span
- In `shell.js`, after the first successful health check response, read `data.version` and update the span text to `PYTHON 3.11 · agent-pitch v{version}`
- If the health check fails the span stays as `PYTHON 3.11 · agent-pitch` (graceful fallback — no error shown)
- Only update once (on the first successful response); no need to re-update on every tick

## CLI `--version`

In `src/cli.py`, intercept `--version` / `-V` before the subcommand dispatch block:

```python
import importlib.metadata

if cmd in ("--version", "-V"):
    version = importlib.metadata.version("agent-pitch")
    print(f"agent-pitch {version}")
    sys.exit(0)
```

Also add `--version` and `-V` to the `--help` output listing.

## Files Changed

| File | Change |
|------|--------|
| `pyproject.toml` | Remove static `version`, add `dynamic`, add `setuptools-scm` build dep, add `[tool.setuptools_scm]` |
| `Dockerfile` | Add `ARG VERSION` + `ENV SETUPTOOLS_SCM_PRETEND_VERSION` before `pip install` |
| `.github/workflows/release.yml` | Add `build-args` to `docker/build-push-action` step |
| `src/cli.py` | Add `--version` / `-V` handling |
| `src/api/http_server/static/index.html` | Add `id="sb-version"` to the version span |
| `src/api/http_server/static/shell.js` | Update version span text on first successful health check |

## Out of Scope

- Changing the `/api/health` response shape (already returns `version`)
- Modifying CI (`ci.yml`) — it installs from source with no tag requirement
- Adding version to Docker image labels (already handled by `docker/metadata-action`)
