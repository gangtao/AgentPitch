# GitHub Actions CI + Docker Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two GitHub Actions workflows — one that runs tests on every push/PR, and one that builds and pushes a Docker image to ghcr.io on every GitHub Release.

**Architecture:** Two independent workflow files in `.github/workflows/`. `ci.yml` runs `pytest` on `ubuntu-latest` with Python 3.11. `release.yml` re-runs tests then builds and pushes to `ghcr.io/<owner>/agent-pitch` using only the built-in `GITHUB_TOKEN` — no extra secrets needed.

**Tech Stack:** GitHub Actions, docker/metadata-action@v5, docker/login-action@v3, docker/build-push-action@v5, actions/checkout@v4, actions/setup-python@v5

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `.github/workflows/ci.yml` | Create | Run test suite on push to main + PRs |
| `.github/workflows/release.yml` | Create | Build + push Docker image on GitHub Release published |

---

### Task 1: Create `.github/workflows/ci.yml`

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Create the workflows directory**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Write `ci.yml`**

Create `.github/workflows/ci.yml` with this exact content:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -e '.[all]'

      - name: Run tests
        run: pytest
```

- [ ] **Step 3: Validate YAML syntax locally**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml')); print('YAML valid')"
```

Expected output:
```
YAML valid
```

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add CI workflow (pytest on push and PRs)"
```

---

### Task 2: Create `.github/workflows/release.yml`

**Files:**
- Create: `.github/workflows/release.yml`

- [ ] **Step 1: Write `release.yml`**

Create `.github/workflows/release.yml` with this exact content:

```yaml
name: Release

on:
  release:
    types: [published]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -e '.[all]'

      - name: Run tests
        run: pytest

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Extract Docker metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=semver,pattern={{version}}
            type=raw,value=latest

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

- [ ] **Step 2: Validate YAML syntax locally**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml')); print('YAML valid')"
```

Expected output:
```
YAML valid
```

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/release.yml
git commit -m "ci: add release workflow (Docker image push to ghcr.io on GitHub Release)"
```

---

### Task 3: Verify end-to-end setup

- [ ] **Step 1: Confirm both files are tracked by git**

```bash
git log --oneline -3
```

Expected: two new commits visible — one for each workflow file.

- [ ] **Step 2: Confirm file structure**

```bash
find .github -type f
```

Expected:
```
.github/workflows/ci.yml
.github/workflows/release.yml
```

- [ ] **Step 3: Confirm image name resolution**

The image will be `ghcr.io/<owner>/<repo>` where `<owner>/<repo>` comes from `github.repository`. For this repo the published image will be:

```
ghcr.io/gangtao/agent-pitch:v<version>
ghcr.io/gangtao/agent-pitch:latest
```

No action needed — just confirm the GitHub remote org/user name matches expectations.

```bash
git remote get-url origin
```

---

## How to trigger a release (post-implementation reference)

1. Merge changes to `main`
2. In the GitHub UI: **Releases → Draft a new release**
3. Create a new tag (e.g. `v0.2.0`) and fill in release notes
4. Click **Publish release**
5. The `release.yml` workflow fires: tests run first, then the Docker image is built and pushed to `ghcr.io`
