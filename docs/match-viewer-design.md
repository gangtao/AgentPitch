# Match Viewer — Standalone HTML Design

**Date:** 2026-05-08  
**Status:** Approved

## Overview

A single self-contained `match-viewer.html` file that replays AgentPitch match data with no server dependency. Reuses rendering logic from the existing `app.js` / `match-stats.js` with server calls replaced by in-memory data injection. A companion `bundle_match.py` script produces a pre-baked version with match data embedded directly in the HTML.

## Goals

- Open the HTML file in any modern browser, no server required
- Full viewer feature parity: canvas pitch, scrubber/playback controls, event feed sidebar, match stats panel
- Two load modes: folder picker and bundled data
- Reuse the existing design system and rendering code to avoid logic duplication

## File Layout

```
tools/
  match-viewer.html         ← generic viewer (folder picker / drag-and-drop)
  bundle_match.py           ← bundling script
  match-viewer-bundled-<match_id>.html   ← generated output, gitignored
```

No changes to `src/`.

## Load Modes

### Mode A — Folder picker

The viewer opens with a loader screen. The user selects or drag-and-drops a match directory (e.g. `data/matches/match_league-20260502-1905-11228a-D17M2/`). The browser reads all files in the directory via `<input type="file" webkitdirectory>` or the drag-and-drop `DataTransferItem.webkitGetAsEntry()` API.

Required files in the folder:
- `meta.json`
- `events.jsonl`

Optional files (loaded if present):
- `strategy_team_a.*` (any extension)
- `strategy_team_b.*` (any extension)

Loader UI:

```
┌─────────────────────────────────────────────────────┐
│  A·P  AGENT PITCH · MATCH VIEWER                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│         LOAD A MATCH                                │
│                                                     │
│   [▶ SELECT MATCH FOLDER]                           │
│                                                     │
│   — or drag & drop the match folder here —         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

Once all required files are read, the loader is hidden and the viewer starts at tick 0.

### Mode B — Bundled data

When `window.BUNDLED_MATCH` is defined (injected by `bundle_match.py`), the loader screen is never shown. The viewer starts immediately with the embedded data. Shape:

```js
window.BUNDLED_MATCH = {
  meta: { /* parsed meta.json */ },
  ticks: [ /* array of parsed tick objects from events.jsonl */ ],
  strategies: {          // optional
    team_a: "...",
    team_b: "..."
  }
};
```

## Architecture

### Inlined assets (in order inside the HTML)

1. `<style>` — `design-system.css` + `app.css` + `match-stats.css` inlined verbatim
2. HTML body — loader screen div + match viewer DOM (copied from `index.html`'s `#section-matches` block: chyron, canvas/scrub, event feed, stats panel). No nav, no app shell chrome.
3. `<script type="module">` — adapted `app.js` + `match-stats.js` with server calls removed

### JS adaptations

The following server-dependent code in `app.js` is replaced:

| Original | Replacement |
|---|---|
| `loadMeta()` → `fetch('/api/match')` | `injectMeta(metaJson)` sets `FIELD_W/H`, tick rate, phase transitions, player labels |
| `loadTicks()` → `fetch('/api/match/ticks')` | `injectTicks(ticksArray)` populates `allTicks`, `realTickToIdx`, scrubber range |
| SSE streams (`/api/match/ticks/stream`, `/api/match/key-events/stream`) | Not wired up — no live mode, replay only |
| Strategy fetch → `fetch('/api/strategy/{team_id}')` | `injectStrategy(teamId, code)` populates the strategy panel if code is available |

`match-stats.js` currently calls `fetch('/api/match/stats')`. In the standalone viewer, stats are computed client-side from `allTicks` — iterating all ticks to aggregate shots, passes, tackles, possession per player/team — then passed to `window.matchStats.render(data)` directly, bypassing the fetch entirely.

### Data flow (Mode A)

```
Folder selected / dropped
  → FileReader reads meta.json     → injectMeta()      → canvas resized, labels set
  → FileReader reads events.jsonl  → injectTicks()     → scrubber range set
  → FileReader reads strategy_*    → injectStrategy()  → strategy panel populated (optional)
  → hideLoader()
  → startReplay()                  → playback loop starts at tick 0
```

### Data flow (Mode B)

```
Page load
  → window.BUNDLED_MATCH detected
  → injectMeta(BUNDLED_MATCH.meta)
  → injectTicks(BUNDLED_MATCH.ticks)
  → injectStrategy(...) if BUNDLED_MATCH.strategies present
  → startReplay()
```

## Bundling Tool (`bundle_match.py`)

```
python tools/bundle_match.py <match_dir>
# Example:
python tools/bundle_match.py data/matches/match_league-20260502-1905-11228a-D17M2
# → tools/match-viewer-bundled-match_league-20260502-1905-11228a-D17M2.html
```

Steps:
1. Read and parse `meta.json`
2. Read `events.jsonl`, parse each line into a list of tick dicts
3. Read strategy files if present
4. Read `tools/match-viewer.html`
5. Inject a `<script>window.BUNDLED_MATCH = ...;</script>` block immediately after `<body>`
6. Write the result to `tools/match-viewer-bundled-<match_id>.html`

Output size estimate: ~6–7MB for a 3000-tick match (6MB tick data + ~150KB viewer shell). Acceptable for local use.

## Browser Compatibility

- `webkitdirectory` on `<input type="file">`: Chrome, Firefox 50+, Safari 11.1+, Edge
- `DataTransferItem.webkitGetAsEntry()` for drag-and-drop folder: same support
- Google Fonts (`JetBrains Mono`, `Space Grotesk`) load from CDN; degrade to monospace/sans-serif if offline

## Out of Scope

- Live match streaming (SSE)
- Starting new matches
- Arena / Cup / League views
- API config or strategy generation
