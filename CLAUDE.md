# Subtetris — Game Prompt

Build a single-file HTML5 canvas game called **Subtetris** — a Tetris variant where blocks carry numbers and rows are cleared by subtraction instead of deletion.

---

## Game Mechanics

- Standard Tetris pieces (I, O, T, S, Z, J, L), each cell carrying a number
- **MAX # setting (1–4):** controls the range of numbers assigned to block cells. MAX=1 means all cells are 1 (classic Tetris feel). MAX=2 means cells are randomly 1 or 2. Etc.
- **Row clearing:** when a row is full, subtract the row's minimum value from every cell. Cells that reach 0 disappear.
- **Cascade gravity:** after cells disappear, blocks above fall into the gaps. Re-evaluate rows and repeat until no full rows remain.
- Slow-motion clearing animation: highlight row (500ms) → subtract & remove zeroed cells (500ms) → animate falling blocks (500ms per wave, 150ms pause between waves, ease-out curve).
- Score: standard Tetris scoring multiplied by level. +1 per soft-drop row.
- Level increases every 10 lines cleared. Drop speed is **constant** (does not change with level).
- Ghost piece shown.

---

## Falling Rules

1. **Active piece** — falls one row at a time on the drop timer; player can soft-drop with a swipe down.

2. **Row clear** - process rows one at a time, scanning downward. For each full row found:
2.1. **Zeroed blocks** - Determine the row's minimum value, subtract it from every cell. Cells that reach 0 vanish immediately, leaving empty cells.
2.2. **Falling column** - Only the single block directly above each zeroed cell falls by one row into the gap. Higher blocks in the same column do not fall automatically — they are subject to rule 2.2.1. Blocks at the cleared row or below are never moved.
2.2.1. **Neighboring co-falling blocks** — Decide ALL blocks that will fall in this wave (the single blocks from 2.2 plus all eligible neighbors) before moving anything. Behavior depends on the **Support Model** setting:
- **`ground` mode (default):** A neighboring block falls only if it has no path to the ground through any series of connected blocks (i.e. it is "hanging"). BFS from the bottom row determines which blocks are grounded; all others are hanging and fall.
- **`cluster` mode:** A neighboring block falls if it is adjacent (4-directional) to any block already in the falling set, unless it is self-grounded (its own column has an unbroken stack of blocks from that block's row all the way down to the floor — no gaps below it within the same column). Propagate using column-first DFS: fully exhaust all eligible blocks upward within the current column before expanding horizontally to adjacent columns. Keep expanding until no new adjacent non-self-grounded blocks are found.
2.3. **Move** - All decided blocks fall by exactly 1 row simultaneously.
2.4. **Re-check same row** - After the fall, check if the same row is full again (blocks that fell into it may have filled it). If full, repeat from 2.1 for this row (chain depth increases, awarding bonus score). If not full, advance to the row below and check it. Continue scanning downward until no more full rows are found.
2.5. **Final settle** - After no more full rows remain, run one BFS-based hanging-block pass to drop any residual floating blocks (ground mode safety net).

3. **Multi-row clear bonus** — when multiple rows get full, calculate one row at a time from the top, and there should be extra score awarded.

---

## Visual Design

- **Background:** navy blue (`#0a1628`)
- **Panels/UI:** dark navy (`#0d1f3c`), borders `#1e3a5f`
- **Block colors by number:**
  - 1: light burnt orange `hsl(22, 85%, 62%)` — dark text
  - 2: dark burnt orange `hsl(22, 85%, 34%)` — light text
  - 3: steel blue `hsl(195, 75%, 42%)` — light text
  - 4: forest green `hsl(145, 60%, 36%)` — light text
- Numbers drawn on blocks (hidden when MAX=1 — plays like classic Tetris visually)
- Blocks have a highlight bevel (top/left lighter, bottom/right darker)
- Row-clearing highlight: yellow overlay `rgba(255, 220, 100, 0.3)` on the target row
- GAME OVER / PAUSE popup: semi-transparent overlay at top of board, below border

---

## Desktop Layout

Sidebar (130px wide, same height as board):
- Title "SUBTETRIS" + version below in small text
- Score (right-aligned)
- Level + Lines (side by side)
- Next piece preview canvas (120×90) — blocks drawn at the same size as board blocks (BLOCK px)
- MAX # selector: 4 buttons [1][2][3][4] — active one highlighted burnt orange
- **Support Model** toggle: 2 buttons `[GND][CLU]` — active one highlighted burnt orange; `GND` = `ground` mode, `CLU` = `cluster` mode; default `GND`; label "SUPPORT" above in same style as other sidebar labels
- NEW GAME button (rounded bottom corners, burnt orange style)
- Controls cheatsheet

Canvas: 300×600 (10 cols × 20 rows × 30px blocks), border `#1e3a5f`.

---

## Mobile Layout (`@media (max-width: 600px)`)

**Top bar (60px tall, fixed):**
- Left: "SUBTETRIS" + version stacked below in small text
- Center (flex: 1, centered): Score | Lvl | Lines stats
- Right: NEXT piece preview canvas — fills almost full bar height (80×80 buffer, CSS sized to fill bar via `align-self: stretch; padding: 2px 0`)

**Game board:**
- Fills all remaining height between top bar and controls
- Canvas centered horizontally, `height: 100%; width: auto` to preserve 1:2 aspect ratio (no distortion)
- `touch-action: none` on canvas

**Gesture hint bar** (between board and controls):
- Text: "swipe for left/right/drop, tap for rotate"
- `border-top: 1px solid #1e3a5f`; dark background; small centered monospace text

**Bottom touch controls — 2×7 grid:**
```
Row 1: [←][→][MAX][PAUSE][NEW][↺][▼]
Row 2: [  ][  ][  ][ 🔊 ][SUPP][  ][  ]
```
**Layout rules:**
- `#touch-ctrl`: `display: grid; grid-template-columns: repeat(7, 50px); grid-template-rows: repeat(2, 50px); gap: 4px; justify-content: center`
- All buttons are **50×50px squares** — positioned via `grid-column`/`grid-row` inline styles
- 🔊 sits at `grid-column: 4; grid-row: 2` (centered below PAUSE)
- SUPP sits at `grid-column: 5; grid-row: 2` (below NEW); cycles `GND`↔`CLU` on tap; label "SUPP\nGND" or "SUPP\nCLU" (two lines, `.tc-txt` style); default `GND`
- MAX cycles downward: 4→3→2→1→4

**Button styles:**
- `.tc-btn` (base): 50×50px, font-size 22px, **light navy blue** `#1a3a6a`, border `#2a5498`
- `.tc-action`: **burnt orange** `#7a3510`, border `#c87941`, text `#ffd0a0` — ← → ↺ ▼
- `.tc-txt`: `font-size: 9px; letter-spacing: 0.5px` — MAX, PAUSE, NEW GAME
- 🔊 / 🔇 toggles sound; MAX cycles 1→2→3→4→1, label "MAX n"; default MAX 4

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

## Tech Notes

- Single HTML file; DSEG7-Classic font loaded from jsDelivr CDN for score display
- Score display: two overlaid divs — record (navy `#1e3a5c`) behind, current score (burnt orange `#d4863c`) on top. Current score color is `#071020` (invisible) when score = 0, switching to burnt orange once scoring begins
- Drop speed is constant at NES level-1 pace (~800ms); `nesInterval()` lookup table exists but `dropInterval` is only set at game start, never updated on level-up
- High score persisted in `localStorage` key `subtetris_hi`
- Support model state: `let supportModel = 'ground'` — values `'ground'` | `'cluster'`; toggled by sidebar buttons and mobile SUPP button; can be changed mid-game
- Single HTML file, no dependencies
- Canvas scaled by CSS on mobile (buffer stays 300×600, CSS fills available height)
- **Preview piece uses the same block size as the board** (pass `BLOCK` as `nb` to `drawPreview`); preview canvas is 120×90 to accommodate all piece shapes
- **Blocks must always be square**: canvas CSS must use `height: 100%; width: auto; max-width: 100%` to preserve the 1:2 (width:height) aspect ratio — never `width: 100%; height: 100%` which stretches independently
- `requestAnimationFrame` game loop
- Async clearing chain via `setTimeout` (no blocking)
- `cascadeFall()` moves only one row at a time per wave, repeats until settled
- Bump patch version (in HTML title, sidebar, and mobile header) on every code change
- Serve via `python3 -m http.server 3456`
