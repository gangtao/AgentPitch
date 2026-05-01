# GitHub Actions CI + Docker Release Design

**Date:** 2026-05-01  
**Status:** Approved

## Overview

Add two GitHub Actions workflow files:

1. `ci.yml` — runs the test suite on every push to `main` and every PR targeting `main`
2. `release.yml` — builds and pushes the Docker image to GitHub Container Registry (`ghcr.io`) on every GitHub Release published

No new secrets are required; both workflows use the built-in `GITHUB_TOKEN`.

---

## Workflow 1: CI (`ci.yml`)

### Triggers

- `push` → branches: `main`
- `pull_request` → branches: `main`

### Jobs

**`test`**

| Step | Detail |
|------|--------|
| Checkout | `actions/checkout@v4` |
| Setup Python | `actions/setup-python@v5`, Python 3.11 |
| Install dependencies | `pip install -e '.[all]'` (matches Dockerfile — installs JS + Wasm sandbox backends) |
| Run tests | `pytest` |

No secrets, no caching layer (keep it simple for now).

---

## Workflow 2: Docker Release (`release.yml`)

### Triggers

- `release` event, type: `published`

This fires whenever a GitHub Release is published (not drafted, not edited). Creating the Release in the GitHub UI also creates the corresponding git tag.

### Jobs

**`test`** (same as `ci.yml` — gates the build job)

**`build-and-push`** (depends on `test`)

| Step | Detail |
|------|--------|
| Checkout | `actions/checkout@v4` |
| Docker metadata | `docker/metadata-action@v5` — extracts tag from the GitHub release (e.g. `v0.1.0`); produces two tags: `ghcr.io/<owner>/agent-pitch:<version>` and `ghcr.io/<owner>/agent-pitch:latest` |
| Login to ghcr.io | `docker/login-action@v3` with `GITHUB_TOKEN` |
| Build and push | `docker/build-push-action@v5`, `push: true`, platforms: `linux/amd64` |

### Image naming

`ghcr.io/<github-owner>/agent-pitch` — resolved automatically from `github.repository` context.

### Example tags after release `v0.2.0`

```
ghcr.io/<owner>/agent-pitch:v0.2.0
ghcr.io/<owner>/agent-pitch:latest
```

---

## File Layout

```
.github/
  workflows/
    ci.yml
    release.yml
```

---

## How to Trigger a Release

1. Bump version in `pyproject.toml` (optional but recommended)
2. Push/merge to `main`
3. In GitHub UI: **Releases → Draft a new release → choose/create tag → Publish release**
4. `release.yml` fires: tests run, then Docker image is built and pushed to `ghcr.io`

---

## Out of Scope

- Multi-platform builds (`linux/arm64`) — not included; can be added later with `platforms: linux/amd64,linux/arm64`
- Docker layer caching — not included; can be added with `cache-from/cache-to` on the build step
- Dependency caching (pip) — not included; test suite is fast
- Docker Hub push — not included; only `ghcr.io`
