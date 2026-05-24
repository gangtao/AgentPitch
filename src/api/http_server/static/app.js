// agent_pitch browser frontend — broadcast viewer.
// Adapted from prototypes/ui/viewer.jsx to vanilla DOM (per ADR-0010,
// no framework). Keeps all production data sources: /api/match,
// /api/match/ticks, /api/match/key-events, /api/strategy/{team_id}.
//
// Field is rendered to <canvas> with the broadcast palette; chyron,
// statbug, seasonbug, goal flash, scrubber, event ticker, code panel
// and status bar are HTML overlays.

// Field dimensions — start at the most-common 100×60 default, but get
// overwritten from meta.field_width / meta.field_height on first
// /api/match fetch (the engine writes these per-match as of 2026-04-25).
// Letting these be mutable means a 5v5 60×40 pitch renders with the right
// aspect ratio and player coordinates instead of a stretched 100×60.
let FIELD_W = 100;
let FIELD_H = 60;

// ── Mutable state ────────────────────────────────────────────────────
let allTicks = [];
let currentTick = 0;
let realTickToIdx = new Map();   // realTick → idx in allTicks (sparse)
let firstRealTick = 0;
let lastRealTick = 0;
let playing = false;
let lastTimestamp = 0;
let playSpeed = 1;               // multiplier on the 10 ticks/sec base rate
let teamFilter = "all";          // all | team_a | team_b
let _tickRate = 10;
let _totalTicks = 0;
let _phaseTransitions = [];
let _playerLabels = {};          // player_id → "A #4"
let _playerNumbers = {};         // player_id → jersey number
let _eventRows = [];             // cached extracted event rows
let _activeFx = [];              // [{kind, startTick, lifetime, ...}]
let _lastFxScannedTick = -1;     // newest tick we've already extracted fx for
let _matchId = "";
let _seed = "—";
let _logDir = "—";
let _teamADisplay = "TEAM A";
let _teamBDisplay = "TEAM B";

// ── DOM handles ─────────────────────────────────────────────────────
const canvas = document.getElementById("field-canvas");
const ctx = canvas.getContext("2d");
// Hide the canvas until meta.json lands so we never paint a frame at the
// default 100×60 aspect for a non-default pitch (e.g. 5v5 60×40). loadMeta
// flips this back to "visible" once FIELD_W/FIELD_H are synced.
canvas.style.visibility = "hidden";
// Logical (CSS-pixel) canvas size. Set by _resizeCanvas() on init and
// on window resize. Drawing code uses these instead of canvas.width /
// canvas.height (which now hold the DPR-scaled BACKING STORE size).
let cssW = 800;
let cssH = 480;
let _devicePixelRatio = 1;

function _resizeCanvas() {
  // Compute the canvas's display size from pitch-stage's available space,
  // then write it back as inline width/height. This is more reliable than
  // CSS aspect-ratio + max-* constraints, which can produce overflow when
  // grid/flex sizing hasn't settled — particularly on the first paint
  // after navigation. The canvas is guaranteed to fit within pitch-stage
  // (minus padding) and never spills into the scrub bar below.
  const stage = canvas.parentElement;  // .pitch-stage
  const stageRect = stage ? stage.getBoundingClientRect() : null;
  if (stageRect && stageRect.width > 0 && stageRect.height > 0) {
    const cs = getComputedStyle(stage);
    const padX = parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight);
    const padY = parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom);
    const availW = Math.max(100, stageRect.width  - padX);
    const availH = Math.max(60,  stageRect.height - padY);
    // Aspect from FIELD_W/FIELD_H (per-match values written by engine in meta).
    const aspect = FIELD_W / FIELD_H;
    // Fit-within: pick whichever dimension is the binding constraint.
    let w = availW, h = w / aspect;
    if (h > availH) { h = availH; w = h * aspect; }
    cssW = Math.round(w);
    cssH = Math.round(h);
    canvas.style.width  = cssW + "px";
    canvas.style.height = cssH + "px";
  } else {
    // Layout not ready — fall back to HTML attrs so we don't produce a
    // 0-byte backing store on first call.
    cssW = Math.max(100, canvas.width || 800);
    cssH = Math.max(60,  canvas.height || 480);
  }
  const dpr = window.devicePixelRatio || 1;
  _devicePixelRatio = dpr;
  // Backing store sized for crisp pixels on Retina / 4K.
  canvas.width  = cssW * dpr;
  canvas.height = cssH * dpr;
  // All drawing happens in CSS-pixel coordinates; the transform
  // upscales those onto the high-DPI backing store.
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}

// Debounced resize / repaint helper. Used by both the window resize
// listener and the ResizeObserver below.
let _resizeTimer = null;
function _scheduleRepaint() {
  if (_resizeTimer) clearTimeout(_resizeTimer);
  _resizeTimer = setTimeout(() => {
    _resizeCanvas();
    if (allTicks.length > 0) {
      const idx = realTickToIdx.get(currentTick);
      if (idx !== undefined) paintTick(idx);
    }
  }, 50);
}
window.addEventListener("resize", _scheduleRepaint);

// Observe the PITCH-STAGE (not the canvas itself) so we react to layout
// changes from font swaps / nav pin toggles / window resize, without the
// observer becoming a recursive feedback loop on our own canvas resizes.
if (typeof ResizeObserver !== "undefined") {
  const stage = canvas.parentElement;
  if (stage) new ResizeObserver(_scheduleRepaint).observe(stage);
}
const matchTitle = document.getElementById("match-title");
const teamAName = document.getElementById("team-a-name");
const teamBName = document.getElementById("team-b-name");
const teamAModel = document.getElementById("team-a-model");
const teamBModel = document.getElementById("team-b-model");
const scoreTeamA = document.getElementById("score-team-a");
const scoreTeamB = document.getElementById("score-team-b");
const clockCur = document.getElementById("clock-cur");
const clockTot = document.getElementById("clock-tot");
const bugSeed = document.getElementById("bug-seed");
const bugTickRate = document.getElementById("bug-tick-rate");
const bugPossession = document.getElementById("bug-possession");
const bugCarrier = document.getElementById("bug-carrier");
const goalFlash = document.getElementById("goal-flash");
const goalChyron = document.getElementById("goal-chyron");
const scrub = document.getElementById("scrub-bar");
const scrubFill = document.getElementById("scrub-fill");
const scrubMarkers = document.getElementById("scrub-markers");
const tickDisplay = document.getElementById("tick-display");
const playPauseBtn = document.getElementById("play-pause");
const speedPill = document.getElementById("speed-pill");
const eventList = document.getElementById("event-log-list");
const eventsCount = document.getElementById("events-count");
const filterPills = document.getElementById("filter-pills");
const sbLog = document.getElementById("sb-log");
const sbSeed = document.getElementById("sb-seed");
const sbApi = document.getElementById("sb-api");
if (sbApi) sbApi.textContent = `API · ${window.location.host}`;

// ============================================================================
// Field Renderer (Canvas) — broadcast palette
// ============================================================================

// Goal mouth y-extent is derived per-frame from FIELD_H + _goalHeight (both
// updated from meta.json on /api/match fetch). Real FIFA goal width is 7.32m.
let _goalHeight = 7.32;
const NET_DEPTH_PX = 10;

// FIFA pitch markings (center circle, penalty area, etc.) are specified in
// real-world meters at the standard 100×60 pitch. On smaller configs they
// must shrink proportionally or they overflow the field. Scale by FIELD_W/100
// so a 60×40 pitch gets markings ~60% the size of a real one — preserves
// the visual layout of a "downsized real pitch" without cluttering it.
function _markingScale() { return FIELD_W / 100; }

// Returns the half (1 or 2) the given REAL tick falls in.
function getHalfForTick(realTick) {
  let half = 1;
  for (const t of _phaseTransitions) {
    if (t.tick > realTick) break;
    if (t.old_phase === "half_time" && t.new_phase === "kick_off") half = 2;
  }
  return half;
}

function paintTick(tickIdx) {
  const t = allTicks[tickIdx];
  if (!t) return;

  // First-paint init: sync the backing store to display size × DPR.
  // Cheap on subsequent calls (only re-syncs when the rect changes).
  const rect = canvas.getBoundingClientRect();
  if (Math.round(rect.width) !== cssW || Math.round(rect.height) !== cssH ||
      window.devicePixelRatio !== _devicePixelRatio) {
    _resizeCanvas();
  }

  // Background — dark broadcast green with mown stripes.
  ctx.fillStyle = "#1f3a2a";
  ctx.fillRect(0, 0, cssW, cssH);
  const stripeW = cssW / 10;
  ctx.fillStyle = "#23422f";
  for (let i = 0; i < 10; i += 2) {
    ctx.fillRect(i * stripeW, 0, stripeW, cssH);
  }

  // Field markings (white, semi-transparent)
  const sx = cssW / FIELD_W;
  const sy = cssH / FIELD_H;
  ctx.strokeStyle = "rgba(232, 237, 241, 0.85)";
  ctx.lineWidth = 1.5;

  // Scale FIFA-meter constants to the actual pitch size (100×60 reference).
  const scale = _markingScale();
  const centerCircleR = 9.15 * scale;
  const goalAreaDepth = 5.5 * scale;
  const penaltyDepth = 16.5 * scale;
  const penaltySpotDist = 11.0 * scale;
  const penaltyArcRadius = 9.15 * scale;
  // Goal mouth y-extent — centered on the field, span = engine's goal_height.
  // (Engine writes goal_height into meta.json as of 2026-04-25; viewer falls
  // back to FIFA real-world 7.32m if the field doesn't have it.)
  const goalCenterY = FIELD_H / 2;
  const goalTopY    = goalCenterY + _goalHeight / 2;  // larger y = lower-on-screen
  const goalBottomY = goalCenterY - _goalHeight / 2;

  // Outer boundary
  ctx.strokeRect(0, 0, cssW, cssH);
  // Center line
  ctx.beginPath();
  ctx.moveTo(cssW / 2, 0);
  ctx.lineTo(cssW / 2, cssH);
  ctx.stroke();
  // Center circle
  ctx.beginPath();
  ctx.arc(cssW / 2, cssH / 2, centerCircleR * sx, 0, Math.PI * 2);
  ctx.stroke();
  ctx.fillStyle = "rgba(232, 237, 241, 0.85)";
  ctx.beginPath();
  ctx.arc(cssW / 2, cssH / 2, 2, 0, Math.PI * 2);
  ctx.fill();

  // Per-end markings
  const goalAreaY1 = (goalBottomY - goalAreaDepth) * sy;
  const goalAreaY2 = (goalTopY    + goalAreaDepth) * sy;
  const penaltyY1  = (goalBottomY - penaltyDepth) * sy;
  const penaltyY2  = (goalTopY    + penaltyDepth) * sy;
  const fieldCenterYpx = goalCenterY * sy;

  ctx.strokeRect(0, goalAreaY1, goalAreaDepth * sx, goalAreaY2 - goalAreaY1);
  ctx.strokeRect(cssW - goalAreaDepth * sx, goalAreaY1, goalAreaDepth * sx, goalAreaY2 - goalAreaY1);
  ctx.strokeRect(0, penaltyY1, penaltyDepth * sx, penaltyY2 - penaltyY1);
  ctx.strokeRect(cssW - penaltyDepth * sx, penaltyY1, penaltyDepth * sx, penaltyY2 - penaltyY1);

  ctx.beginPath(); ctx.arc(penaltySpotDist * sx, fieldCenterYpx, 2, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.arc(cssW - penaltySpotDist * sx, fieldCenterYpx, 2, 0, Math.PI * 2); ctx.fill();

  const arcHalf = Math.acos((penaltyDepth - penaltySpotDist) / penaltyArcRadius);
  const arcRpx = penaltyArcRadius * sx;
  ctx.beginPath();
  ctx.arc(penaltySpotDist * sx, fieldCenterYpx, arcRpx, -arcHalf, arcHalf);
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(cssW - penaltySpotDist * sx, fieldCenterYpx, arcRpx,
          Math.PI - arcHalf, Math.PI + arcHalf);
  ctx.stroke();

  // Goal mouths — defending team's tint at low alpha; bright posts on the inner edge.
  const goalTopPx    = goalTopY    * sy;
  const goalBottomPx = goalBottomY * sy;
  const half = getHalfForTick(currentTick);
  const leftDefender = half === 1 ? "team_a" : "team_b";
  const rightDefender = half === 1 ? "team_b" : "team_a";
  const goalTint = (team) => team === "team_a"
    ? "rgba(242, 164, 75, 0.30)"   // orange (Team A)
    : "rgba(176, 140, 255, 0.30)"; // purple (Team B)
  ctx.fillStyle = goalTint(leftDefender);
  ctx.fillRect(0, goalBottomPx, NET_DEPTH_PX, goalTopPx - goalBottomPx);
  ctx.fillStyle = goalTint(rightDefender);
  ctx.fillRect(cssW - NET_DEPTH_PX, goalBottomPx, NET_DEPTH_PX, goalTopPx - goalBottomPx);
  ctx.strokeStyle = "white"; ctx.lineWidth = 3;
  ctx.beginPath(); ctx.moveTo(NET_DEPTH_PX, goalBottomPx); ctx.lineTo(NET_DEPTH_PX, goalTopPx); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(cssW - NET_DEPTH_PX, goalBottomPx); ctx.lineTo(cssW - NET_DEPTH_PX, goalTopPx); ctx.stroke();

  // FX overlay (passes/shots/tackles/saves) — drawn UNDER players so dots
  // sit on top of trajectory lines and pulse rings.
  _renderFx(currentTick);

  // Players
  const positions = t.player_positions || {};
  const PLAYER_RADIUS = 13;
  // `ball_possession` is the TEAM id ("team_a"/"team_b"), not a player id.
  // The carrying player is the one whose position equals ball_position
  // (per BPS: while carried, ball position is snapped to carrier's pos).
  // Identify them by scanning that team's players for the closest match.
  const possessingTeam = t.ball_possession;
  let carrier = null;
  if (possessingTeam && t.ball_position) {
    const [bx, by] = t.ball_position;
    let bestDistSq = Infinity;
    for (const pid of Object.keys(positions)) {
      if (!pid.startsWith(possessingTeam)) continue;
      const p = positions[pid];
      const d = (p[0] - bx) ** 2 + (p[1] - by) ** 2;
      if (d < bestDistSq) { bestDistSq = d; carrier = pid; }
    }
    // Only treat as carrier when the player is essentially ON the ball
    // (≤0.5u). A team in possession but with the ball mid-pass should
    // NOT highlight any player as the carrier.
    if (bestDistSq > 0.25) carrier = null;
  }
  for (const playerId of Object.keys(positions)) {
    const pos = positions[playerId];
    if (!pos) continue;
    const team = playerId.startsWith("team_a") ? "team_a" : "team_b";
    const cx = (pos[0] / FIELD_W) * cssW;
    const cy = (pos[1] / FIELD_H) * cssH;
    // Carrier highlight ring (drawn first so the dot sits on top)
    if (carrier && playerId === carrier) {
      ctx.beginPath();
      ctx.arc(cx, cy, PLAYER_RADIUS + 4, 0, Math.PI * 2);
      ctx.strokeStyle = "rgba(255, 255, 255, 0.85)";
      ctx.lineWidth = 2;
      ctx.stroke();
    }
    // Player dot
    ctx.beginPath();
    ctx.arc(cx, cy, PLAYER_RADIUS, 0, Math.PI * 2);
    ctx.fillStyle = team === "team_a" ? "#f2a44b" : "#b08cff";
    ctx.fill();
    // Black outline ring (matches prototype's box-shadow ring)
    ctx.strokeStyle = "rgba(0, 0, 0, 0.55)";
    ctx.lineWidth = 2;
    ctx.stroke();
    // Jersey number (dark on light Team A, dark on light Team B)
    const num = _playerNumbers[playerId] !== undefined
      ? _playerNumbers[playerId]
      : (parseInt(playerId.split("_").pop(), 10) + 1);
    ctx.fillStyle = team === "team_a" ? "#1a0f04" : "#110820";
    ctx.font = "bold 13px 'Space Grotesk', -apple-system, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(String(num), cx, cy);
  }

  // Ball — when carried, offset to the side of the carrier in their
  // direction of motion so the jersey number stays visible. Direction
  // is inferred from the carrier's position delta vs the previous tick;
  // when stationary, default to "toward opponent goal".
  if (t.ball_position) {
    let [bx, by] = t.ball_position;
    if (carrier && positions[carrier]) {
      const carrierPos = positions[carrier];
      let dx = 0, dy = 0;
      const prev = allTicks[tickIdx - 1];
      if (prev && prev.player_positions && prev.player_positions[carrier]) {
        const prevPos = prev.player_positions[carrier];
        dx = carrierPos[0] - prevPos[0];
        dy = carrierPos[1] - prevPos[1];
      }
      const mag = Math.hypot(dx, dy);
      if (mag < 1e-3) {
        // Stationary carrier — point toward opponent goal so the ball
        // sits on the attacking side of the dot.
        const towardRight = carrier.startsWith("team_a")
          ? getHalfForTick(currentTick) === 1
          : getHalfForTick(currentTick) === 2;
        dx = towardRight ? 1 : -1;
        dy = 0;
      } else {
        dx /= mag; dy /= mag;
      }
      // Offset by ~PLAYER_RADIUS in field units. PLAYER_RADIUS is in
      // pixels, so convert back: radius_units = PLAYER_RADIUS * FIELD_W / cssW.
      const offsetUnits = (PLAYER_RADIUS + 4) * FIELD_W / cssW;
      bx = carrierPos[0] + dx * offsetUnits;
      by = carrierPos[1] + dy * offsetUnits;
    }
    const bcx = (bx / FIELD_W) * cssW;
    const bcy = (by / FIELD_H) * cssH;
    ctx.font = "13px sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("⚽", bcx, bcy);
  }

  // Score overlay
  if (t.score) {
    const sa = t.score.team_a !== undefined ? t.score.team_a : t.score[0];
    const sb = t.score.team_b !== undefined ? t.score.team_b : t.score[1];
    scoreTeamA.textContent = sa;
    scoreTeamB.textContent = sb;
  }

  // Statbug — possession (team) + carrier (player, if anyone is on the ball)
  const possText = possessingTeam
    ? (possessingTeam === "team_a" ? _teamADisplay : _teamBDisplay)
    : "LOOSE";
  bugPossession.textContent = possText;
  bugPossession.style.color = possessingTeam
    ? (possessingTeam === "team_a" ? "var(--a)" : "var(--b)")
    : "var(--ink-dim)";
  bugCarrier.textContent = carrier
    ? "#" + (_playerNumbers[carrier] || carrier.split("_").pop())
    : "—";
}

// Seek to a REAL tick number.
function seekToTick(realTick) {
  if (allTicks.length === 0) return;
  const clamped = Math.max(firstRealTick, Math.min(lastRealTick, realTick));
  let idx = realTickToIdx.get(clamped);
  let resolvedTick = clamped;
  if (idx === undefined) {
    for (let off = 1; off <= lastRealTick - firstRealTick; off++) {
      if (realTickToIdx.has(clamped + off)) {
        idx = realTickToIdx.get(clamped + off); resolvedTick = clamped + off; break;
      }
      if (realTickToIdx.has(clamped - off)) {
        idx = realTickToIdx.get(clamped - off); resolvedTick = clamped - off; break;
      }
    }
    if (idx === undefined) return;
  }
  currentTick = resolvedTick;
  _syncFxQueue(currentTick);
  paintTick(idx);
  tickDisplay.textContent = `T${String(currentTick).padStart(4, "0")} / ${String(lastRealTick).padStart(4, "0")}`;
  scrub.value = currentTick;
  const span = lastRealTick - firstRealTick || 1;
  const pct = ((currentTick - firstRealTick) / span) * 100;
  scrubFill.style.width = `${pct}%`;
  // Match clock
  clockCur.textContent = _formatMMSS(currentTick);
  clockTot.textContent = _formatMMSS(_totalTicks - 1 || lastRealTick);
  window.dispatchEvent(new CustomEvent("renderer:tickChanged", { detail: { tick: currentTick } }));
}

function _formatMMSS(tick) {
  const totalSec = Math.max(0, Math.floor(tick / _tickRate));
  const m = Math.floor(totalSec / 60);
  const s = totalSec % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

// ── Visual FX overlay ───────────────────────────────────────────────
// Two effect families:
//   - Trajectory: pass = thin team-coloured dashed line passer→landing
//                 shot = thick line shooter→approx target with arrowhead
//   - Pulse ring: tackle / save / block at the actor's position, colour
//                 by outcome (green=success, amber=blocked, red=failed)
// Effects live ~10 ticks (1s @ 10 t/s) and fade linearly.

const FX_LIFETIME = 10;

// Map an action's outcome to a ring colour.
function _outcomeColour(action, result, details) {
  if (action === "Tackle") {
    if (result === "controlled") return "#4bdc8b";  // green
    if (result === "blocked")    return "#f2c14b";  // amber
    if (result === "failed")     return "#ff6b6b";  // red
    return "#9aa4ad";                               // grey
  }
  if (details && details.goalkeeper_save === "success") return "#4bdc8b";
  if (details && details.goalkeeper_save === "blocked") return "#f2c14b";
  if (details && details.shot_deflection)               return "#f2c14b";
  return "#9aa4ad";
}

// Walk all actions on `tick`, push fx into `_activeFx`. Idempotent for
// a given tick (caller must avoid re-scanning the same tick).
function _scanTickFx(tick) {
  const idx = realTickToIdx.get(tick);
  if (idx === undefined) return;
  const t = allTicks[idx];
  const positions = t.player_positions || {};
  for (const a of (t.actions || [])) {
    const pid = a.player_id;
    const team = a.team;
    const result = a.result;
    const details = a.details || {};
    const pos = positions[pid];

    // Pass — trajectory from passer to landing.
    if (a.action === "Pass" && result === "ok" && pos) {
      const land = Array.isArray(details.landing_pos) ? details.landing_pos
                 : Array.isArray(details.target_pos)  ? details.target_pos : null;
      if (land) {
        _activeFx.push({
          kind: "pass", team,
          x1: pos[0], y1: pos[1], x2: land[0], y2: land[1],
          startTick: tick, lifetime: FX_LIFETIME,
        });
      }
    }
    // Shot — trajectory from shooter toward goal direction. Use the next
    // available tick's ball position as the direction proxy (ball was
    // just kicked, so its motion vector points along the shot path).
    if (a.action === "Shoot" && result === "ok" && pos) {
      let target = null;
      // Look up to 5 ticks ahead for a ball position to define direction.
      for (let off = 1; off <= 5; off++) {
        const next = allTicks[idx + off];
        if (next && next.ball_position) {
          target = next.ball_position; break;
        }
      }
      if (target) {
        _activeFx.push({
          kind: "shot", team,
          x1: pos[0], y1: pos[1], x2: target[0], y2: target[1],
          startTick: tick, lifetime: FX_LIFETIME,
        });
      }
    }
    // Tackle — pulse at tackler position.
    if (a.action === "Tackle" && pos &&
        (result === "controlled" || result === "blocked" || result === "failed")) {
      _activeFx.push({
        kind: "ring", team, color: _outcomeColour("Tackle", result, details),
        x: pos[0], y: pos[1],
        startTick: tick, lifetime: FX_LIFETIME,
      });
    }
    // Save (success / parry) — pulse at GK position.
    if ((details.goalkeeper_save === "success" || details.goalkeeper_save === "blocked") && pos) {
      _activeFx.push({
        kind: "ring", team, color: _outcomeColour(null, null, details),
        x: pos[0], y: pos[1],
        startTick: tick, lifetime: FX_LIFETIME,
      });
    }
    // Defender block (BPS shot deflection) — pulse at blocker position.
    if (details.shot_deflection && pos) {
      _activeFx.push({
        kind: "ring", team, color: _outcomeColour(null, null, details),
        x: pos[0], y: pos[1],
        startTick: tick, lifetime: FX_LIFETIME,
      });
    }
  }
}

// Sync the fx queue with the current tick:
//   - forward jump: scan any unseen ticks in (_lastFxScannedTick, tick]
//   - backward jump: nuke the queue and rebase
function _syncFxQueue(tick) {
  if (tick < _lastFxScannedTick) {
    _activeFx = [];
    _lastFxScannedTick = tick - 1;
  }
  // Skip large catch-ups (e.g. a long scrub forward) — only scan the
  // window of ticks whose effects could still be alive at `tick`.
  const start = Math.max(_lastFxScannedTick + 1, tick - FX_LIFETIME);
  for (let s = start; s <= tick; s++) _scanTickFx(s);
  _lastFxScannedTick = Math.max(_lastFxScannedTick, tick);
  // Prune expired
  _activeFx = _activeFx.filter((fx) => tick - fx.startTick <= fx.lifetime);
}

// Render the active fx queue onto the canvas. Called from paintTick.
function _renderFx(tick) {
  if (_activeFx.length === 0) return;
  for (const fx of _activeFx) {
    const age = tick - fx.startTick;
    if (age < 0 || age > fx.lifetime) continue;
    const t01 = age / fx.lifetime;          // 0..1
    const alpha = Math.max(0, 1 - t01);     // linear fade
    const teamColor = fx.team === "team_a" ? "#f2a44b" : "#b08cff";
    if (fx.kind === "pass") {
      const x1 = (fx.x1 / FIELD_W) * cssW;
      const y1 = (fx.y1 / FIELD_H) * cssH;
      const x2 = (fx.x2 / FIELD_W) * cssW;
      const y2 = (fx.y2 / FIELD_H) * cssH;
      ctx.save();
      ctx.globalAlpha = alpha * 0.85;
      ctx.strokeStyle = teamColor;
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
      // Small dot at landing
      ctx.setLineDash([]);
      ctx.fillStyle = teamColor;
      ctx.beginPath(); ctx.arc(x2, y2, 3, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
    } else if (fx.kind === "shot") {
      const x1 = (fx.x1 / FIELD_W) * cssW;
      const y1 = (fx.y1 / FIELD_H) * cssH;
      const x2 = (fx.x2 / FIELD_W) * cssW;
      const y2 = (fx.y2 / FIELD_H) * cssH;
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.strokeStyle = teamColor;
      ctx.lineWidth = 3;
      ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
      // Arrowhead at the destination end
      const ang = Math.atan2(y2 - y1, x2 - x1);
      const ah = 9;  // arrowhead length
      ctx.fillStyle = teamColor;
      ctx.beginPath();
      ctx.moveTo(x2, y2);
      ctx.lineTo(x2 - ah * Math.cos(ang - Math.PI / 6), y2 - ah * Math.sin(ang - Math.PI / 6));
      ctx.lineTo(x2 - ah * Math.cos(ang + Math.PI / 6), y2 - ah * Math.sin(ang + Math.PI / 6));
      ctx.closePath(); ctx.fill();
      ctx.restore();
    } else if (fx.kind === "ring") {
      const cx = (fx.x / FIELD_W) * cssW;
      const cy = (fx.y / FIELD_H) * cssH;
      // Ring expands from PLAYER_RADIUS+2 to PLAYER_RADIUS+22 over lifetime.
      const r = 15 + 22 * t01;
      ctx.save();
      ctx.globalAlpha = alpha * 0.9;
      ctx.strokeStyle = fx.color;
      ctx.lineWidth = 2.5;
      ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.stroke();
      ctx.restore();
    }
  }
}

// ── Playback loop ───────────────────────────────────────────────────
function loop(ts) {
  if (playing && allTicks.length > 0) {
    const deltaMs = Math.min(200, ts - lastTimestamp);
    // 10 ticks/sec base × playSpeed → tick interval = 100 / playSpeed ms
    if (deltaMs >= 100 / playSpeed) {
      let next = currentTick + 1;
      while (next <= lastRealTick && !realTickToIdx.has(next)) next++;
      if (next > lastRealTick) {
        playing = false;
        playPauseBtn.textContent = "▶";
      } else {
        seekToTick(next);
      }
      lastTimestamp = ts;
    }
  }
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

playPauseBtn.addEventListener("click", () => {
  playing = !playing;
  playPauseBtn.textContent = playing ? "❚❚" : "▶";
  if (playing) lastTimestamp = performance.now();
});

scrub.addEventListener("input", () => seekToTick(parseInt(scrub.value)));

// Speed pill — pick playback rate
speedPill.addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-speed]");
  if (!btn) return;
  playSpeed = parseFloat(btn.dataset.speed);
  speedPill.querySelectorAll("button").forEach((b) =>
    b.classList.toggle("active", b === btn));
});

window.addEventListener("keydown", (e) => {
  // Skip when focus is in any text-input element — otherwise this handler
  // eats space (and arrow keys) inside textareas, name inputs, the LLM
  // prompt box, etc. `INPUT` covers `<input>`; `TEXTAREA` covers
  // `<textarea>`; isContentEditable covers contenteditable divs.
  const t = e.target;
  if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
  if (e.code === "Space") {
    e.preventDefault();
    playPauseBtn.click();
  } else if (e.code === "ArrowLeft") {
    seekToTick(currentTick - (e.shiftKey ? 500 : 1));
  } else if (e.code === "ArrowRight") {
    seekToTick(currentTick + (e.shiftKey ? 500 : 1));
  }
});

// ============================================================================
// Event Log (ticker)
// ============================================================================

function _label(pid) { return _playerLabels[pid] || pid; }

function ingestRosters(teams) {
  if (!teams) return;
  for (const teamId of Object.keys(teams)) {
    const teamLetter = teamId === "team_a" ? "A" : "B";
    const teamData = teams[teamId];
    const players = Array.isArray(teamData) ? teamData : (teamData?.roster || []);
    for (const p of players) {
      const num = p.number;
      const numTag = num ? `#${num}` : "";
      _playerLabels[p.player_id] = p.name
        ? `${p.name} ${numTag}`.trim()
        : `${teamLetter} ${numTag}`.trim();
      _playerNumbers[p.player_id] = p.number;
    }
  }
}

function _setTeamDisplayNames(teams) {
  function nameFor(slot, fallback) {
    const td = teams && teams[slot];
    if (td && !Array.isArray(td) && td.name) return td.name;
    return fallback;
  }
  _teamADisplay = nameFor("team_a", "TEAM A");
  _teamBDisplay = nameFor("team_b", "TEAM B");
  if (teamAName) teamAName.textContent = _teamADisplay;
  if (teamBName) teamBName.textContent = _teamBDisplay;
}

function _refreshPlayerLabels(allTicksData) {
  for (const t of allTicksData) {
    for (const pid of Object.keys(t.player_positions || {})) {
      if (_playerLabels[pid]) continue;
      const teamLetter = pid.startsWith("team_a") ? "A" : "B";
      const idx = parseInt(pid.split("_").pop(), 10);
      const number = isNaN(idx) ? "?" : (idx + 1);
      _playerLabels[pid] = `${teamLetter} #${number}`;
      _playerNumbers[pid] = number;
    }
  }
}

function extractEventRows(allTicksData) {
  _refreshPlayerLabels(allTicksData);
  const rows = [];
  for (const t of allTicksData) {
    for (const a of (t.actions || [])) {
      const action = a.action;
      const result = a.result;
      const pid = a.player_id;
      const team = a.team;
      const details = a.details || {};

      if (details.goal_scored) {
        const scoredBy = details.scored_by || "?";
        const scoringTeam = details.goal_scored;
        const teamLetter = scoringTeam === "team_a" ? "A" : "B";
        rows.push({ tick: t.tick, team: scoringTeam, icon: "⚽",
          label: `GOAL by ${_label(scoredBy)} (Team ${teamLetter})`, cls: "ev-goal" });
        continue;
      }
      if (details.out_of_bounds) {
        const restart = details.restart_type;
        const restartTeam = details.restart_team;
        const kicker = details.kicker_id;
        if (restart) {
          const teamLetter = restartTeam === "team_a" ? "A" : restartTeam === "team_b" ? "B" : "?";
          const kTxt = kicker ? ` by ${_label(kicker)}` : ` (Team ${teamLetter})`;
          let icon = "🚩"; let label = "";
          if (restart === "throw_in") {
            const spot = details.restart_spot || details.position;
            const where = (Array.isArray(spot) && spot[1] <= 1) ? "top side"
                        : (Array.isArray(spot) && spot[1] >= 59) ? "bottom side" : "";
            icon = "🤾"; label = `THROW-IN${kTxt}${where ? " from " + where : ""}`;
          } else if (restart === "goal_kick") {
            icon = "🥅"; label = `GOAL KICK${kTxt}`;
          } else if (restart === "corner_kick") {
            const spot = details.restart_spot || details.position;
            let corner = "";
            if (Array.isArray(spot)) {
              const top = spot[1] <= 1; const left = spot[0] <= 1;
              corner = (top ? "top" : "bottom") + "-" + (left ? "left" : "right");
            }
            icon = "🚩"; label = `CORNER${kTxt}${corner ? " from " + corner : ""}`;
          } else {
            label = `RESTART (${restart})${kTxt}`;
          }
          rows.push({ tick: t.tick, team: restartTeam, icon, label, cls: "ev-oob" });
          continue;
        }
        const pos = details.position; const last = details.last_touched_by;
        let where = "";
        if (Array.isArray(pos)) {
          const isLeft = pos[0] <= 0.5; const isRight = pos[0] >= 99.5;
          const isTop = pos[1] >= 59.5; const isBottom = pos[1] <= 0.5;
          if (isLeft || isRight) where = " (end line)";
          else if (isTop || isBottom) where = " (side line)";
        }
        const fromTxt = last ? ` — last touched by ${_label(last)}` : "";
        rows.push({ tick: t.tick, team: null, icon: "🚩",
          label: `OUT OF BOUNDS${where}${fromTxt}`, cls: "ev-oob" });
        continue;
      }
      if (details.dribble_result) {
        const target = details.dribble_target;
        if (details.dribble_result === "success") {
          rows.push({ tick: t.tick, team, icon: "💨",
            label: `DRIBBLE by ${_label(pid)} past ${_label(target)} ✓`, cls: "ev-dribble-good" });
        } else {
          rows.push({ tick: t.tick, team, icon: "💨",
            label: `DRIBBLE by ${_label(pid)} stolen by ${_label(target)}`, cls: "ev-dribble-bad" });
        }
        continue;
      }
      if (details.shot_deflection) {
        const from = details.deflected_from;
        const fromTxt = from ? ` from ${_label(from)}'s shot` : "";
        rows.push({ tick: t.tick, team, icon: "🛑",
          label: `BLOCK by ${_label(pid)}${fromTxt}`, cls: "ev-deflection" });
        continue;
      }
      if (details.goalkeeper_save === "success") {
        const from = details.saved_from || "?";
        rows.push({ tick: t.tick, team, icon: "🛡",
          label: `SAVE by ${_label(pid)} from ${_label(from)}`, cls: "ev-save" });
        continue;
      }
      if (details.goalkeeper_save === "blocked") {
        const from = details.saved_from || "?";
        rows.push({ tick: t.tick, team, icon: "🥅",
          label: `PARRY by ${_label(pid)} from ${_label(from)} (loose ball)`, cls: "ev-save-blocked" });
        continue;
      }
      // Cooldown-blocked: action="Hold" (effective), intended_action=original intent.
      // Render as "[intended] by [pid] [on cooldown]" so it's clear the system
      // suppressed the action — not a defender block.
      if (result === "cooldown_blocked") {
        const intended = details.intended_action || action;
        let icon = "⏳"; let label = "";
        if (intended === "Shoot") {
          icon = "🎯"; label = `SHOT by ${_label(pid)} [on cooldown]`;
        } else if (intended === "Pass") {
          icon = "→"; label = `PASS by ${_label(pid)} [on cooldown]`;
        } else if (intended === "Tackle") {
          icon = "⚔"; label = `TACKLE by ${_label(pid)} [on cooldown]`;
        } else {
          label = `${intended} by ${_label(pid)} [on cooldown]`;
        }
        rows.push({ tick: t.tick, team, icon, label, cls: "ev-blocked" });
        continue;
      }
      if (action === "Shoot") {
        const power = details.effective_power || details.power || "?";
        rows.push({ tick: t.tick, team, icon: "🎯",
          label: `SHOT by ${_label(pid)} (power=${power})`,
          cls: "ev-shot" });
        continue;
      }
      if (action === "Pass") {
        let target = "";
        const pos = Array.isArray(details.landing_pos) ? details.landing_pos
                  : Array.isArray(details.target_pos)  ? details.target_pos : null;
        if (pos) target = ` → (${pos[0].toFixed(1)},${pos[1].toFixed(1)})`;
        rows.push({ tick: t.tick, team, icon: "→",
          label: `PASS by ${_label(pid)}${target}`,
          cls: "ev-pass" });
        continue;
      }
      if (details.ball_pickup === "success") {
        rows.push({ tick: t.tick, team, icon: "●",
          label: `PICKUP by ${_label(pid)}`, cls: "ev-pickup" });
        continue;
      }
      if (details.ball_pickup === "failed") {
        const reason = details.reason || "?";
        rows.push({ tick: t.tick, team, icon: "○",
          label: `PICKUP failed by ${_label(pid)} (${reason})`, cls: "ev-pickup-bad" });
        continue;
      }
      if (action === "Tackle") {
        let suffix = ""; let cls = "ev-tackle";
        if (result === "controlled") { suffix = " ✓ (won possession)"; cls = "ev-tackle-good"; }
        else if (result === "blocked") { suffix = " ⚡ (deflected — loose)"; cls = "ev-tackle-blocked"; }
        else if (result === "no_op_carrier_changed") suffix = " (carrier moved)";
        else if (result === "out_of_range") suffix = " (out of range)";
        rows.push({ tick: t.tick, team, icon: "⚔",
          label: `TACKLE by ${_label(pid)}${suffix}`, cls });
        continue;
      }
    }
  }
  return rows;
}

function extractPhaseTransitionRows(transitions) {
  if (!transitions) return [];
  const rows = [];
  const PHASE_DISPLAY = {
    "kick_off":     { icon: "⏱", label: "KICK-OFF",   cls: "ev-phase" },
    "in_play":      { icon: null, label: null,        cls: null },
    "goal_scored":  { icon: null, label: null,        cls: null },
    "half_time":    { icon: "☕", label: "HALF-TIME", cls: "ev-phase-major" },
    "full_time":    { icon: "🏁", label: "FULL-TIME", cls: "ev-phase-major" },
    "pre_match":    { icon: null, label: null,        cls: null },
  };
  for (const pt of transitions) {
    const disp = PHASE_DISPLAY[pt.new_phase];
    if (!disp || !disp.label) continue;
    rows.push({ tick: pt.tick, team: null, icon: disp.icon, label: disp.label, cls: disp.cls });
  }
  return rows;
}

function _filterRow(ev) {
  if (teamFilter === "all") return true;
  // Always show team-agnostic phase / OOB rows so users keep their bearings.
  if (!ev.team) return ev.cls && (ev.cls.startsWith("ev-phase") || ev.cls === "ev-oob");
  return ev.team === teamFilter;
}

function renderEventRows() {
  eventList.innerHTML = "";
  const visible = _eventRows.filter(_filterRow);
  eventsCount.textContent = `${visible.length}/${_eventRows.length}`;
  if (visible.length === 0) {
    const placeholder = document.createElement("div");
    placeholder.className = "evt placeholder";
    placeholder.textContent = "(no events match filter)";
    eventList.appendChild(placeholder);
    return;
  }
  for (const ev of visible) {
    const row = document.createElement("div");
    row.className = `evt ${ev.cls || ""}`;
    row.dataset.tick = ev.tick;
    row.dataset.team = ev.team || "";

    const tEl = document.createElement("span"); tEl.className = "t";
    tEl.textContent = `T${String(ev.tick).padStart(4, "0")}`;
    const iEl = document.createElement("span"); iEl.className = "ico";
    iEl.textContent = ev.icon || "•";
    const txtEl = document.createElement("span"); txtEl.className = "txt";
    if (ev.team) {
      const tag = document.createElement("span");
      tag.className = `team-tag ${ev.team}`;
      txtEl.appendChild(tag);
    }
    txtEl.appendChild(document.createTextNode(ev.label));

    row.append(tEl, iEl, txtEl);
    row.addEventListener("click", () => {
      seekToTick(ev.tick);
      eventList.querySelectorAll(".evt.selected").forEach((el) => el.classList.remove("selected"));
      row.classList.add("selected");
      window.dispatchEvent(new CustomEvent("eventLog:tickSelected", {
        detail: { tick: ev.tick, team: ev.team }
      }));
    });
    eventList.appendChild(row);
  }
}

filterPills.addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-filter]");
  if (!btn) return;
  teamFilter = btn.dataset.filter;
  filterPills.querySelectorAll("button").forEach((b) =>
    b.classList.toggle("active", b === btn));
  renderEventRows();
});

window.addEventListener("renderer:tickChanged", (e) => {
  const t = e.detail.tick;
  eventList.querySelectorAll(".evt.proximity").forEach((el) => el.classList.remove("proximity"));
  const items = [...eventList.querySelectorAll(".evt[data-tick]")];
  if (items.length === 0) return;
  let closest = items[0];
  let closestDist = Math.abs(parseInt(items[0].dataset.tick) - t);
  for (const item of items.slice(1)) {
    const d = Math.abs(parseInt(item.dataset.tick) - t);
    if (d < closestDist) { closest = item; closestDist = d; }
  }
  closest.classList.add("proximity");
  if (playing) {
    closest.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }
});

// ── Goal flash overlay ──────────────────────────────────────────────
let _lastGoalTick = -1;
window.addEventListener("renderer:tickChanged", () => {
  const intTick = Math.floor(currentTick);
  for (const ev of _eventRows) {
    if (ev.cls === "ev-goal" && ev.tick <= intTick && ev.tick > _lastGoalTick) {
      _lastGoalTick = ev.tick;
      _showGoalFx(ev);
      break;
    }
  }
  if (intTick < _lastGoalTick) _lastGoalTick = intTick;
});

function _showGoalFx(ev) {
  const side = ev.team === "team_a" ? "a" : "b";
  goalFlash.className = `goal-flash ${side}`;
  goalFlash.style.setProperty("--fx", side === "a" ? "82%" : "18%");
  goalFlash.hidden = false;
  // Re-trigger the CSS animation by removing+adding the class.
  goalFlash.style.animation = "none"; void goalFlash.offsetWidth;
  goalFlash.style.animation = "";
  goalChyron.hidden = false;
  goalChyron.querySelector(".word").className = `word ${side}`;
  goalChyron.querySelector(".word").textContent = "GOAL";
  goalChyron.querySelector(".sub").textContent = ev.label;
  goalChyron.style.animation = "none"; void goalChyron.offsetWidth;
  goalChyron.style.animation = "";
  setTimeout(() => { goalFlash.hidden = true; goalChyron.hidden = true; }, 1900);
}

// ── Scrub markers (goal pips) ───────────────────────────────────────
function renderScrubMarkers() {
  scrubMarkers.innerHTML = "";
  const span = lastRealTick - firstRealTick || 1;
  for (const ev of _eventRows) {
    if (ev.cls !== "ev-goal") continue;
    const pct = ((ev.tick - firstRealTick) / span) * 100;
    const m = document.createElement("div");
    const side = ev.team === "team_a" ? "a" : "b";
    m.className = `scrub-marker goal ${side}`;
    m.style.left = `${pct}%`;
    m.title = `GOAL · T${ev.tick}`;
    scrubMarkers.appendChild(m);
  }
}

// ============================================================================
// Bootstrap — fetch all data on load
// ============================================================================

function _deriveSeed(matchId) {
  // Match IDs commonly look like "iter11v4_r6_seed600" — pull the trailing seed.
  const m = /seed(\d+)/i.exec(matchId || "");
  return m ? m[1] : "—";
}

// Read the active match_id from the URL hash (e.g. #/matches/<id>) so the
// API serves data for THAT specific match instead of the generic "latest".
function _activeMatchIdFromHash() {
  const hash = window.location.hash.slice(1);
  const parts = hash.split("/").filter(p => p);
  // Expected: ['matches', '<id>'] or ['matches', 'new'] or ['matches']
  if (parts.length >= 2 && parts[0] === "matches" && parts[1] !== "new") {
    return parts[1];
  }
  return "";
}
function _matchQuery() {
  const id = _activeMatchIdFromHash();
  return id ? `?match_id=${encodeURIComponent(id)}` : "";
}

// Poll /api/matches/<id>/status until the match completes, the subprocess
// exits, or we hit the safety cap. Each successful "completed" / "exited"
// triggers a single reloadLiveViewer() so the rest of the app picks up the
// fully-written meta.json. While running, the overlay shows live tick
// progress (tick X / Y · NN%) plus elapsed time so the user knows the
// engine is alive — particularly important for slow 11v11 matches that can
// run a minute or more after spawn.
// Generation token. Bumped by reloadLiveViewer() — every poll iteration
// captures its myGen at start and bails out if the global counter has
// changed (= the user navigated to a different match). Without this, two
// polls run in parallel after a fast nav and race to call reloadLiveViewer.
window._pollGen = window._pollGen || 0;

async function _pollMatchStatus(matchId, showWaiting) {
  const POLL_MS = 1500;
  // 30-min ceiling — bumped from 15 to cover LLM-generated 11v11 + PMEP
  // runs that can take 10-15 min for the engine itself plus several minutes
  // of post-match evolution. The user can always navigate away to abort.
  const MAX_POLLS = 1200;
  const myGen = window._pollGen;
  for (let i = 0; i < MAX_POLLS; i++) {
    // Cancellation: if the user navigated to a different match (or back to
    // the list), bail silently. The new context owns its own poll loop.
    if (window._pollGen !== myGen) return;

    let status;
    try {
      const resp = await fetch(`/api/matches/${encodeURIComponent(matchId)}/status`);
      if (window._pollGen !== myGen) return;          // cancellation check after await
      if (!resp.ok) {
        showWaiting(`Status check failed (HTTP ${resp.status}) — retrying…`);
        await new Promise(r => setTimeout(r, POLL_MS));
        continue;
      }
      status = await resp.json();
      if (window._pollGen !== myGen) return;
    } catch (e) {
      if (window._pollGen !== myGen) return;
      showWaiting(`Status check errored — retrying…`);
      await new Promise(r => setTimeout(r, POLL_MS));
      continue;
    }

    const fmtElapsed = (sec) => {
      if (sec == null) return "0s";
      const m = Math.floor(sec / 60), s = sec % 60;
      return m > 0 ? `${m}m ${s}s` : `${s}s`;
    };
    const p = status.progress || {};
    // Prefer the top-level elapsed_sec (always present once the process
    // is tracked, even before events.jsonl appears). Fall back to the
    // progress-block value for older server builds.
    const elapsed = fmtElapsed(status.elapsed_sec ?? p.elapsed_sec);

    if (status.state === "completed") {
      // meta.json is on disk — reload to pick it up.
      if (typeof window.reloadLiveViewer === "function") window.reloadLiveViewer();
      return;
    }
    if (status.state === "exited") {
      const code = status.exit_code != null ? ` (exit ${status.exit_code})` : "";
      showWaiting(`Engine exited without writing match data${code} — check server terminal`);
      return;
    }
    if (status.state === "unknown") {
      // Server doesn't know about this match (likely restart). Fall back to
      // a couple more polls then give up — meta.json may still appear.
      showWaiting(`Match "${matchId}" — no engine record (server may have restarted)…`);
    } else if (status.state === "running") {
      if (p.total_ticks > 0 && p.current_tick > 0) {
        showWaiting(
          `Match "${matchId}" — running · tick ${p.current_tick} / ${p.total_ticks}` +
          ` (${p.percent}%) · elapsed ${elapsed}`
        );
      } else {
        showWaiting(`Match "${matchId}" — engine starting · elapsed ${elapsed}`);
      }
    }
    await new Promise(r => setTimeout(r, POLL_MS));
  }
  showWaiting(`Timed out polling match status (30 min) — check server terminal`);
}

async function bootstrap() {
  const waitingOverlay = document.getElementById("match-waiting-overlay");
  const waitingSubtitle = document.getElementById("waiting-subtitle");
  const showWaiting = (subtitle) => {
    if (waitingOverlay) {
      waitingOverlay.hidden = false;
      if (waitingSubtitle && subtitle) waitingSubtitle.textContent = subtitle;
    }
  };
  const hideWaiting = () => {
    if (waitingOverlay) waitingOverlay.hidden = true;
  };

  let meta = null;
  try {
    const r = await fetch(`/api/match${_matchQuery()}`);
    // 202 = match queued but engine subprocess hasn't created meta.json yet.
    // Poll /api/matches/<id>/status (rather than blind retry) so we can:
    //   1. tell "still running" from "subprocess crashed"
    //   2. show real progress (tick X / Y) instead of a generic spinner
    //   3. only time out when the subprocess is actually gone
    if (r.status === 202) {
      const stub = await r.json();
      matchTitle.textContent = stub.match_id;
      showWaiting(`Match "${stub.match_id}" — engine starting…`);
      _pollMatchStatus(stub.match_id, showWaiting);
      return;
    }
    window._matchStartingRetries = 0;
    hideWaiting();
    if (r.ok) {
      meta = await r.json();
      _matchId = meta.match_id || "";
      // Prefer explicit meta.seed (engine writes it as of 2026-04-24);
      // fall back to deriving from match_id for legacy logs.
      _seed = (meta.seed !== undefined && meta.seed !== null)
        ? String(meta.seed)
        : _deriveSeed(_matchId);
      matchTitle.textContent = _matchId || "—";
      bugSeed.textContent = _seed;
      sbSeed.textContent = `DETERMINISTIC · SEED ${_seed}`;
      const _dataDir = meta.data_dir || "data";
      sbLog.textContent = `LOG · ${_dataDir}/matches/match_${_matchId}`;
      if (meta.final_score) {
        scoreTeamA.textContent = meta.final_score.team_a;
        scoreTeamB.textContent = meta.final_score.team_b;
      }
      ingestRosters(meta.teams);
      _setTeamDisplayNames(meta.teams);
      _phaseTransitions = meta.phase_transitions || [];
      if (typeof meta.tick_rate === "number") {
        _tickRate = meta.tick_rate;
        bugTickRate.textContent = `${_tickRate}/s`;
      }
      if (typeof meta.total_ticks === "number") _totalTicks = meta.total_ticks;

      // Per-match field dimensions + goal mouth (engine writes these as of
      // 2026-04-25). Update the module-level FIELD_W/FIELD_H/_goalHeight so
      // all coordinate math + field markings use the right pitch, AND resync
      // the canvas aspect-ratio + status-bar pitch text so the canvas itself
      // is shaped correctly for non-100×60 configs (5v5 with 60×40 surfaced
      // the bug; FIFA-meter markings overflowing the small pitch surfaced
      // the goal-height/marking-scale bug).
      if (typeof meta.field_width === "number" && typeof meta.field_height === "number") {
        FIELD_W = meta.field_width;
        FIELD_H = meta.field_height;
        if (typeof meta.goal_height === "number") _goalHeight = meta.goal_height;
        // Canvas dimensions are now JS-controlled in _resizeCanvas — no CSS
        // aspect-ratio dance. Just clear any stale inline aspect-ratio from
        // earlier builds and let the resize compute the new size.
        if (canvas) canvas.style.aspectRatio = "";
        const sbField = document.getElementById("sb-field");
        if (sbField) sbField.textContent = `FIELD · ${FIELD_W}×${FIELD_H}m`;
        // _resizeCanvas() reads the live aspect-ratio from CSS via the
        // computed bounding rect, so a fresh resize trigger picks up the
        // new dims without us recomputing widths/heights manually here.
        if (typeof _resizeCanvas === "function") _resizeCanvas();
      }
      // Meta is loaded — reveal the canvas. Even legacy meta without
      // field_width/field_height is fine here: the defaults (100×60) will
      // match those matches' actual pitch.
      canvas.style.visibility = "visible";
      // Strategy provenance per team in the chyron's small mono slot.
      // Per ADR-0023, provider/model in `meta.strategies[team]` is sourced
      // from the strategy's sidecar — so it's truthful for LLM-generated
      // library strategies (no longer collapsed to "baseline"). Special-case
      // `provider === "baseline"`: the seeded baseline.py shows just its
      // file stem (provider+model are uninformative). Legacy matches without
      // strategies meta fall back to a roster-size hint.
      const rosterSize = (teamId) => (meta.teams && meta.teams[teamId] || []).length;
      // Language tag — added 2026-04-26 so JS vs Python strategies are
      // distinguishable in the live chyron. Legacy meta without `language`
      // is assumed Python (the only language pre-2026-04-26).
      const langTag = (s) => {
        const lang = s && s.language;
        if (lang === "javascript") return " · JS";
        if (lang === "rust")       return " · RS";
        if (lang === "python")     return " · PY";
        return "";  // unknown — omit rather than mislabel
      };
      const formatStrategy = (teamId) => {
        const s = meta.strategies && meta.strategies[teamId];
        const n = rosterSize(teamId);
        const playersHint = n ? ` · ${n}P` : "";
        if (!s || s.provider === "unknown") {
          return n ? `${n} PLAYERS` : "—";
        }
        if (s.provider === "baseline") {
          return `${s.name || "baseline"}${playersHint}${langTag(s)}`;
        }
        const head = (s.model && s.model !== "unknown") ? `${s.provider}/${s.model}` : s.provider;
        const ver = (typeof s.version === "number" && s.version > 0) ? ` · v${s.version}` : "";
        return `${head}${ver}${playersHint}${langTag(s)}`;
      };
      teamAModel.textContent = formatStrategy("team_a");
      teamBModel.textContent = formatStrategy("team_b");
    } else {
      matchTitle.textContent = "(no match data — start a simulation)";
    }
  } catch (err) {
    matchTitle.textContent = "(server error)";
  }

  if (meta) {
    try {
      const q = _matchQuery();
      const sep = q ? "&" : "?";
      const r = await fetch(`/api/match/ticks${q}${sep}limit=10000`);
      if (r.ok) {
        const data = await r.json();
        allTicks = data.ticks || [];
        realTickToIdx = new Map();
        allTicks.forEach((t, i) => realTickToIdx.set(t.tick, i));
        if (allTicks.length > 0) {
          firstRealTick = allTicks[0].tick;
          lastRealTick = allTicks[allTicks.length - 1].tick;
          if (typeof meta.final_tick === "number") {
            lastRealTick = Math.max(lastRealTick, meta.final_tick);
          }
          scrub.min = firstRealTick;
          scrub.max = lastRealTick;
          // Build event rows BEFORE first paint so goal markers appear.
          _eventRows = [
            ...extractPhaseTransitionRows(_phaseTransitions),
            ...extractEventRows(allTicks),
          ].sort((a, b) => a.tick - b.tick);
          renderEventRows();
          renderScrubMarkers();
          seekToTick(firstRealTick);
        }
      }
    } catch (err) { /* ignore */ }
  }

  // Optional fallback: if the per-action extraction yielded nothing
  // (e.g. very old log format), pull /api/match/key-events for a
  // minimal feed. Production rows come from extractEventRows above.
  if (meta && _eventRows.length === 0) {
    try {
      const r = await fetch(`/api/match/key-events${_matchQuery()}`);
      if (r.ok) {
        const data = await r.json();
        const rows = (data.key_events || []).map((kf) => ({
          tick: kf.tick, team: null, icon: "•",
          label: kf.event_type || "EVENT", cls: "ev-phase",
        }));
        if (rows.length) {
          _eventRows = rows.sort((a, b) => a.tick - b.tick);
          renderEventRows();
        }
      }
    } catch (_) { /* ignore */ }
  }

}

bootstrap();

// Public export for testability
window.seekToTick = seekToTick;

// Tracks the match_id of the most recent reloadLiveViewer call so we can
// detect when the user navigates to a DIFFERENT match (and reset retry state).
let _lastReloadedMatchId = "";

// Public re-init: matches.js calls this when navigating to a different
// #/matches/<id> URL so the live viewer re-fetches data for THAT match
// instead of staying on whichever match was active at page load.
window.reloadLiveViewer = function reloadLiveViewer() {
  console.log(`[app.js] reloadLiveViewer() — match_id from hash: "${_activeMatchIdFromHash()}"`);
  // Cancel any in-flight _pollMatchStatus loops bound to the previous match.
  // Polls capture window._pollGen at start and bail when it changes.
  window._pollGen = (window._pollGen || 0) + 1;
  // If user navigates to a different match while we're mid-retry-loop for
  // another, reset the retry counter so the new match starts fresh.
  if (_lastReloadedMatchId !== _activeMatchIdFromHash()) {
    window._matchStartingRetries = 0;
    _lastReloadedMatchId = _activeMatchIdFromHash();
  }

  // ── Reset ALL per-match state so the new match doesn't show ghost
  //    data from the previous one. Without this the user sees:
  //    - previous match's events in the right-side feed
  //    - previous match's scrubber position + total ticks
  //    - previous match's player dots painted on the canvas
  //    - previous match's score / clock / possession / carrier text
  //    until /api/match returns and the first real paint runs.

  // Tick cache + index
  allTicks = [];
  realTickToIdx = new Map();
  _eventRows = [];
  _phaseTransitions = [];
  firstRealTick = 0;
  lastRealTick = 0;
  _totalTicks = 0;
  _matchId = "";
  _seed = "—";
  // Playback state — without this, a new match might start mid-playback
  // (carrier-over from `playing=true` or a stale playhead).
  currentTick = 0;
  playing = false;
  if (playPauseBtn) playPauseBtn.textContent = "▶";
  // Cancel a stale resize debounce from the previous match. Without this,
  // a queued _resizeCanvas + paintTick can fire after we've cleared
  // allTicks but before the new match's first real paint, causing a brief
  // flash of the wrong frame.
  if (_resizeTimer) { clearTimeout(_resizeTimer); _resizeTimer = null; }
  // Playback rate + event-log filter — both are user preferences but
  // resetting per-match avoids "why is my new match playing at 4×?" surprise.
  // Also re-syncs the .speed-pill / .filter-pills .active class so the UI
  // visually matches the reset state.
  playSpeed = 1;
  teamFilter = "all";
  document.querySelectorAll("#speed-pill button").forEach(b =>
    b.classList.toggle("active", b.dataset.speed === "1"));
  document.querySelectorAll("#filter-pills button").forEach(b =>
    b.classList.toggle("active", b.dataset.filter === "all"));
  // FX queue + roster cache
  _activeFx = [];
  _lastFxScannedTick = -1;
  _playerLabels = {};

  // Reset chyron + scoreboard text to the initial loading state.
  matchTitle.textContent = "loading…";
  bugSeed.textContent = "—";
  scoreTeamA.textContent = "—";
  scoreTeamB.textContent = "—";
  _teamADisplay = "TEAM A";
  _teamBDisplay = "TEAM B";
  if (teamAName)   teamAName.textContent   = "TEAM A";
  if (teamBName)   teamBName.textContent   = "TEAM B";
  if (teamAModel)  teamAModel.textContent  = "—";
  if (teamBModel)  teamBModel.textContent  = "—";
  if (clockCur)    clockCur.textContent    = "00:00";
  if (clockTot)    clockTot.textContent    = "00:00";
  if (bugPossession) bugPossession.textContent = "—";
  if (bugCarrier)    bugCarrier.textContent    = "—";

  // Reset scrubber visual state.
  if (scrubFill)    scrubFill.style.width   = "0%";
  if (scrubMarkers) scrubMarkers.innerHTML  = "";
  if (scrub) { scrub.value = 0; scrub.max = 0; }
  if (tickDisplay)  tickDisplay.textContent = "T0000 / 0000";

  // Reset event log to placeholder so the previous match's events disappear.
  const eventLogList = document.getElementById("event-log-list");
  if (eventLogList) {
    eventLogList.innerHTML = '<div class="evt placeholder">(no events yet)</div>';
  }
  const eventsCount = document.getElementById("events-count");
  if (eventsCount) eventsCount.textContent = "0/0";

  // Wipe the canvas — without this the new match's first delayed paint
  // sits on top of the previous match's last frame.
  if (ctx && canvas) ctx.clearRect(0, 0, canvas.width, canvas.height);

  bootstrap();
};
