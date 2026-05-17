# Minusfall — Game Prompt

Build a single-file HTML5 canvas game called **Minusfall** — a falling-block puzzle where blocks carry numbers and rows are cleared by subtraction instead of deletion.

---

## Core Concept

Minusfall is a falling-block puzzle where blocks carry numbers and rows are cleared by **subtraction** instead of deletion.

---

## Pieces & Numbers

- Seven tetromino pieces (I, O, T, S, Z, J, L), each cell carrying a number
- **MAX # setting (1–4):** controls the range of numbers on block cells
  - MAX=1 → all cells are 1 (plays like a classic falling-block game visually; numbers hidden)
  - MAX=2 → cells are randomly 1 or 2. Etc.
- Ghost piece shown

---

## Row Clearing

When a row is full:
1. Find the row's minimum value; subtract it from every cell
2. Cells that reach 0 vanish, leaving empty cells
3. Trigger cascade (see below)

---

## Cascade Gravity

After cells vanish, blocks above fall to fill gaps. The process repeats until no full rows remain.

**Per-wave fall sequence:**

1. **Seed fallers** — the single block directly above each vanished cell falls one row. Blocks at or below the cleared row never move.
2. **Expand to neighbors** — determine all co-falling blocks before moving anything. Uses **`cluster` mode** (fixed):
   - A block falls if adjacent (4-directional) to any block already falling, unless it is self-grounded (unbroken stack in its own column from its row to the floor). Propagate via column-first DFS — exhaust upward within the column before expanding sideways.
3. **Move** — all decided blocks fall exactly 1 row simultaneously
4. **Re-check** — if the same row is now full again, repeat from step 1 (chain; bonus score). Otherwise **restart scanning from row 0** — cascade may have filled rows above the cleared row, so scanning must not advance past them.
5. **Final settle** — after no more full rows remain, one BFS pass drops any residual floating blocks (ground-mode safety net)

---

## Scoring & Progression

- Score: standard line-clear scoring × level. +1 per soft-drop row
- Multi-row chains: rows processed top-to-bottom; each additional chain depth awards bonus score
- Level increases every 10 lines cleared
- Drop speed is **constant** (NES level-1 pace, ~800ms) — does not change with level

---

## Clearing Animation

Highlight row → subtract & remove zeroed cells → animate falling blocks (ease-out curve, 150ms pause between waves).

Timing scales with **animation speed** setting (`animSpeed`):
- **ON (med):** 175ms per phase (default)
- **OFF (fast):** instant (0ms delays)

`animDelay(ms)` controls `setTimeout` durations; `animDuration(ms)` controls render interpolation denominators — both must use the same scale factor so animations complete fully before the next phase fires.

---

## Visual Design

- **Background:** navy blue (`#0a1628`)
- **Panels/UI:** dark navy (`#0d1f3c`), borders `#1e3a5f`
- **Block colors by number** (all in the orange→red spectrum, darkening with value):
  - 1: `hsl(30, 85%, 65%)` light orange — dark text `rgba(0,0,0,0.75)`
  - 2: `hsl(22, 90%, 44%)` burnt orange — light text `rgba(255,255,255,0.92)`
  - 3: `hsl(14, 88%, 27%)` dark reddish-brown — light text
  - 4: `hsl(6, 80%, 15%)` near-black red — light text
- Numbers drawn on blocks (hidden when MAX=1 — plays like a classic falling-block game visually)
- Blocks have a highlight bevel (top/left lighter, bottom/right darker)
- Row-clearing highlight: yellow overlay `rgba(255, 220, 100, 0.3)` on the target row
- GAME OVER / PAUSE popup: semi-transparent overlay at top of board, below border

---

## Desktop Layout

Sidebar (130px wide, height matches canvas — 600px default, 663px when sum bar shown; set dynamically by `setSumBar`):
- Title "MINUSFALL" (font-size 16px, letter-spacing 2px) + version below; a small `?` beside the version opens an info popup with Support and Privacy links
- Score — DSEG7 20px, dual-layer display (record in navy, current in orange); expands beyond 5 digits dynamically
- Level + Lines (side by side) — same dual-layer digit display; Level min 2 digits, Lines min 3 digits
- Next piece preview canvas (120×90, `flex: none`) — blocks drawn at BLOCK px size
- **MAX #** — single cycling button, always active (burnt orange), label "MAX n", cycles 4→3→2→1→4
- **Anim speed** selector: 2 buttons `[ON][OFF]` — active one highlighted burnt orange; ON = 175ms per phase, OFF = instant
- NEW GAME button (burnt orange style)
- **PAUSE button** (`#pause-btn`) below NEW GAME — navy blue (`#1a3a6a`/`#2a5498`) at rest; switches to burnt orange and label "RESUME" while paused; grayed out (opacity 0.35, no pointer events) when game over. Calls `togglePause()`.
- **SAVE REPLAY button** (`#replay-btn`) below PAUSE — subtle dark style (`#071020`, `#1e3a5f`), rounded bottom corners. Calls `downloadReplay()`; no-ops if `replayLog` is empty.
- Controls cheatsheet (font-size 10px, line-height 1.6, `flex: 2`)
- Bottom row: `[SUM][🔊]` side by side — `#sum-btn` (left half) toggles sum bar; `#snd-btn` (right half) toggles sound. SUM is lit (`#0d1f3c` bg, `#7ab8d4` text) when active, dim (`#071020`, `#556`) when off.

Canvas: 300×600 when sum bar hidden (default), 300×663 when shown. `boardTop` variable (0 or 33) offsets all board rendering; `showSumBar` boolean gates drawing and canvas resize. `setSumBar(bool)` updates both, resizes canvas/sidebar, and syncs button states.

**Sum bar** — one block per column, mirrored above and below the board:
- Value: sum of all locked cell numbers in that column (does not include the active falling piece)
- Color: `hsl(215, 65%, L%)` where L = `55 - 51 * (sum / 80)` — 55% (sum=0, light steel-blue) → 4% (sum=80, near-black navy). Max possible sum = 20 rows × 4 MAX = 80.
- Text: sum value shown when > 0; opacity scales with sum (`0.4 + 0.5 * t`) so heavier columns are more legible
- Divider: 3px `#4a7ab8` bright line on the board-facing edge of each bar (bottom of top bar, top of bottom bar)
- Top bar: cells at y=0..30, divider at y=30..33; Bottom bar: divider at y=633..636, cells at y=636..663
- GAME OVER / PAUSE overlay `top` is set dynamically by `setSumBar`: `boardTop + 2` px (2px when hidden, 35px when shown)
- **Sum Bar control** — desktop: `#sum-btn` (left half of bottom row, next to `#snd-btn`); mobile: `#mob-sum` in top bar next to `#mob-snd`. No button in the touch grid.

---

## Mobile Layout (`@media (max-width: 600px)`)

**Top bar (88px tall, fixed):**
- Left: "MINUSFALL" + version stacked, small `?` beside the version, then Score | Lvl | Lines stats row below (dual-layer digit display, same as desktop)
- Center-right: `#mob-sum` SUM toggle (36×36px, `#1a3a6a`/burnt-orange when active, id `mob-sum`) then `#mob-snd` 🔊/🔇 sound toggle (36×36px, `#1a3a6a`, id `mob-snd`) — both sit between the brand and the next preview
- Right: NEXT piece preview canvas (96×72px CSS, 120×90 buffer)

**Game board:**
- Fills all remaining height between top bar and controls
- Canvas centered horizontally, `height: 100%; width: auto` to preserve 1:2 aspect ratio (no distortion)
- `touch-action: none` on canvas

**Gesture hint bar** (between board and controls):
- Text: "swipe for left/right/drop, tap for rotate"
- `border-top: 1px solid #1e3a5f`; dark background; small centered monospace text

**Bottom touch controls — 2×7 grid:**
```
Row 1: [←][→][PAUSE][MAX][NEW][ANIM][↺]
Row 2: [  ][  ][    ][   ][   ][    ][▼]
```
**Layout rules:**
- `#touch-ctrl`: `display: grid; grid-template-columns: repeat(7, 50px); grid-template-rows: repeat(2, 50px); gap: 4px; justify-content: center`
- All buttons are **50×50px squares** — positioned via `grid-column`/`grid-row` inline styles
- ANIM (`tc-slo`) at `grid-column: 6; grid-row: 1` — toggles ON↔OFF; always navy blue; label "ANIM\nON" or "ANIM\nOFF"
- Sound toggle moved to top bar (`mob-snd`)
- MAX cycles 4→3→2→1→4, label "MAX n"; default MAX 4
- **Row 2 columns 1–6 must remain empty (tc-blank).** Only `▼` at col 7 row 2 is used. The six left squares are reserved for a future ad banner — do not place any buttons there.

**Button styles:**
- `.tc-btn` (base): 50×50px, font-size 22px, **light navy blue** `#1a3a6a`, border `#2a5498`
- `.tc-btn.active`: burnt orange `#7a3510`, border `#c87941`, text `#ffd0a0`
- `.tc-action`: burnt orange — ← → ↺ ▼
- `.tc-txt`: `font-size: 9px; letter-spacing: 0.5px` — MAX, PAUSE, NEW, ANIM

**Canvas gesture controls (on board itself):**
- Tap (< ~18px movement): rotate
- Flick left/right (horizontal dominant): move left/right
- Drag down (vertical dominant, > ~25px): activate soft drop; release deactivates

---

## Keyboard Controls

| Key | Action |
|-----|--------|
| ← → | Move |
| ↓ | Soft drop (hold) |
| ↑ | Rotate |
| Space / P | Pause / Unpause |
| N | New game |
| Enter / Space | Restart after game over |

Wall kicks: try offsets `[0, -1, 1, -2, 2]` on rotate.

---

## Rotation Stability Rules

All rotations are 90° clockwise. `rotatePiece()` computes `idealX` then tries wall-kick offsets `[0, -1, 1, -2, 2]`.

### S and Z pieces — vertical state consistency

Both vertical states (rot 1 and rot 3) must occupy the **same pair of board columns**. Without correction, the 90° CW rotation formula places content in the right half of the 3×3 bounding box for state 1 and the left half for state 3, causing a 1-column wobble.

Fix: apply an x-delta to `idealX` based on the incoming rotation state:

| Entering state | x-delta |
|---|---|
| 0 | 0 |
| 1 | 0 |
| 2 | 0 |
| 3 | +1 |
| 0 (from 3) | −1 |

Implemented as `ROT_X_DELTA = { S: [-1,0,0,+1], Z: [-1,0,0,+1], L: [-1,0,0,+1], J: [-1,0,0,+1] }` keyed by `newRot = (piece.rot + 1) % 4`. A full 360° cycle returns to the exact original x — no drift.

### I-piece — vertical column consistency

The existing special-case logic in `rotatePiece()` (checking `m[1][0]`, `m[2][0]`, `m[0][2]`) already produces correct column stability: both vertical states (rot 1 and rot 3) land on the same board column. **Do not change this logic.**

### Other pieces (T, O)

No x-delta needed — `idealX = piece.x` is correct for all their rotation states. T has the same mathematical asymmetry but its four states are all visually distinct so no correction is applied.

---

## Tech Notes

- Single HTML file; DSEG7-Classic font loaded from jsDelivr CDN for score display
- Score display: two overlaid divs — record (navy `#1e3a5c`) behind, current score (burnt orange `#d4863c`) on top. Current score color is `#071020` (invisible) when score = 0, switching to burnt orange once scoring begins
- Drop speed is constant at NES level-1 pace (~800ms); `nesInterval()` lookup table exists but `dropInterval` is only set at game start, never updated on level-up
- Records persisted in `localStorage`: `subtetris_hi` (score), `subtetris_hi_lvl` (level), `subtetris_hi_lines` (lines); all updated in `endGame()`
- `renderScoreDigits(elId, cur, rec, minPad=5)` — dual-layer digit display (record in navy `#1e3a5c`, current in orange `#d4863c`); digit count = max(cur digits, rec digits, minPad); used for score (minPad=5), level (minPad=2), lines (minPad=3)
- Support model is fixed to `cluster`: `const supportModel = 'cluster'` — no UI controls
- Single HTML file, no dependencies
- Canvas scaled by CSS on mobile (buffer is 300×600 when sum bar hidden, 300×663 when shown; CSS `height: 100%; width: auto` preserves the aspect ratio either way)
- **Preview piece uses the same block size as the board** (pass `BLOCK` as `nb` to `drawPreview`); preview canvas is 120×90 to accommodate all piece shapes
- **Blocks must always be square**: canvas CSS must use `height: 100%; width: auto; max-width: 100%` — never `width: 100%; height: 100%` which stretches independently
- `requestAnimationFrame` game loop
- Async clearing chain via `setTimeout` (no blocking)
- `applyColumnFall(zeroedCols, fullRow, onDone, gen)` — cluster-mode cascade for one cleared row; `applyGravityUntilStable(onDone, gen)` — BFS final-settle pass after all rows processed. Both move one row at a time per wave and repeat until settled.
- **Replay recording** — every game is silently recorded. `replaySpawn(p)` logs each piece at spawn; `replayLock()` appends `{t, piece, nums, moves, rot, col}` to `replayLog` on lock. `downloadReplay()` serialises `replayLog` as a `.jsonl` file (one JSON object per line: header + one entry per piece) and triggers a browser download. Format: `minusfall-replay/v1`. Played back in `replay.html`.
- **`gameGen` counter** — incremented by `startGame()`; every `setTimeout` callback in `lock()`/`step()`/`applyGravityUntilStable()` captures `myGen = gameGen` at call time and returns early if `gameGen !== myGen`. Prevents stale callbacks from overwriting the new game's state or calling `endGame()` after NEW is pressed mid-clearing-chain
- **Always bump the patch version** (in sidebar and mobile header — the `<title>` tag has no version) on every turn that makes any code change to `docs/index.html` — do this as the final step of that turn
- **Always update CLAUDE.md** in the same turn as any change that affects game mechanics, UI, layout, or architecture — keep it the source of truth
- Serve via `python3 -m http.server 3456`

---

## iOS Build Notes

- iOS app built with Capacitor; project lives in `ios/App/`
- After editing `docs/index.html` or other files in `docs/`, sync to iOS with: `./update_mobile_app.sh` (or `npm run cap:sync`)
  - Capacitor uses `webDir: "docs"` and copies the `docs/` web root into the iOS bundle
  - `ios/App/App/public/` contents are build artifacts — do not hand-edit them
- **Do not delete `ios/App/App/config.xml`** — Xcode requires it; it is tracked in git
- Files auto-generated by `cap sync` (not hand-edited):
  - `ios/App/App/capacitor.config.json` (gitignored)
  - `ios/App/App/public/` contents (gitignored)
- Open the Xcode project with: `npx cap open ios`
