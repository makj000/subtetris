# Subtetris — Game Prompt

Build a single-file HTML5 canvas game called **Subtetris** — a Tetris variant where blocks carry numbers and rows are cleared by subtraction instead of deletion.

---

## Core Concept

Subtetris is a Tetris variant where blocks carry numbers and rows are cleared by **subtraction** instead of deletion.

---

## Pieces & Numbers

- Standard Tetris pieces (I, O, T, S, Z, J, L), each cell carrying a number
- **MAX # setting (1–4):** controls the range of numbers on block cells
  - MAX=1 → all cells are 1 (plays like classic Tetris visually; numbers hidden)
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
2. **Expand to neighbors** — determine all co-falling blocks before moving anything. Behavior depends on the **Support Model**:
   - **`ground` (default):** BFS from the bottom row marks all reachable blocks as grounded. Any block with no path to ground is hanging and falls.
   - **`cluster`:** A block falls if adjacent (4-directional) to any block already falling, unless it is self-grounded (unbroken stack in its own column from its row to the floor). Propagate via column-first DFS — exhaust upward within the column before expanding sideways.
3. **Move** — all decided blocks fall exactly 1 row simultaneously
4. **Re-check** — if the same row is now full again, repeat from step 1 (chain; bonus score). Otherwise advance downward and continue scanning.
5. **Final settle** — after no more full rows remain, one BFS pass drops any residual floating blocks (ground-mode safety net)

---

## Scoring & Progression

- Score: standard Tetris scoring × level. +1 per soft-drop row
- Multi-row chains: rows processed top-to-bottom; each additional chain depth awards bonus score
- Level increases every 10 lines cleared
- Drop speed is **constant** (NES level-1 pace, ~800ms) — does not change with level

---

## Clearing Animation

Highlight row (500ms) → subtract & remove zeroed cells (500ms) → animate falling blocks (500ms per wave, 150ms pause between waves, ease-out curve)

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

---

## iOS Build Notes

- iOS app built with Capacitor; project lives in `ios/App/`
- After editing `index.html`, sync to iOS with: `./update_mobile_app.sh` (or `npm run cap:sync`)
  - This copies `index.html` → `www/index.html`, then runs `npx cap sync ios`
  - `www/index.html` and `ios/App/App/public/` are build artifacts — do not hand-edit them
- **Do not delete `ios/App/App/config.xml`** — Xcode requires it; it is tracked in git
- Files auto-generated by `cap sync` (not hand-edited):
  - `ios/App/App/capacitor.config.json` (gitignored)
  - `ios/App/App/public/` contents (gitignored)
- Open the Xcode project with: `npx cap open ios`
