#!/usr/bin/env python3
"""
Generate Subtetris App Store screenshots and launch-screen splash images.

Run from the project root:
    python3 icons/gen_splash.py

Outputs (in icons/):
    screenshot-6.7inch.png   1290×2796  iPhone 15 Pro Max — required by App Store
    screenshot-6.5inch.png   1242×2688  iPhone 11 Pro Max — required by App Store
    splash-2732x2732.png     2732×2732  Universal launch screen / iPad

Also copies launch-screen image to:
    ios/App/App/Assets.xcassets/Splash.imageset/
        splash.png, splash-2732x2732.png,
        splash-2732x2732-1.png, splash-2732x2732-2.png
"""

import subprocess, os, json, random, sys
from pathlib import Path
from PIL import Image

# ── Paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent          # icons/
PROJECT_ROOT = SCRIPT_DIR.parent              # project root
INDEX_HTML   = PROJECT_ROOT / 'index.html'
SPLASH_DIR   = PROJECT_ROOT / 'ios/App/App/Assets.xcassets/Splash.imageset'
CHROME       = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
TMP_HTML     = '/tmp/subtetris_ss_gen.html'
TMP_RAW      = '/tmp/subtetris_ss_raw.png'

# ── App Store target sizes ─────────────────────────────────────────────────
SIZES = {
    'screenshot-6.7inch.png': (1290, 2796),   # iPhone 15 Pro Max (required)
    'screenshot-6.5inch.png': (1242, 2688),   # iPhone 11 Pro Max (required)
    'splash-2732x2732.png':   (2732, 2732),   # Launch screen / iPad
}

NAVY = (10, 22, 40)   # #0a1628

# ── Board state ────────────────────────────────────────────────────────────
random.seed(7)

ROWS, COLS = 20, 10
I_COL   = 5   # column the I-piece drops into
PIECE_Y = 3   # piece.y (occupies rows 3–6 in col 5)

def rnum():
    return random.randint(1, 4)

def make_board():
    b = [[None]*COLS for _ in range(ROWS)]

    # Jagged pile top — each column starts at a different row
    col_start = {
        0: 9,   # low valley
        1: 6,   # high peak
        2: 8,
        3: 5,   # highest peak
        4: 7,   # left canyon wall
        5: 10,  # I-piece slot — clear above row 10
        6: 7,   # right canyon wall
        7: 5,   # high peak
        8: 9,   # low valley
        9: 7,
    }

    for col in range(COLS):
        top = col_start[col]
        for row in range(top, ROWS):
            if col == I_COL and row < 10:
                continue  # keep I-piece canyon clear
            density = 0.85 if row == top else (0.92 if row <= top + 2 else 0.97)
            if random.random() < density:
                b[row][col] = {'num': rnum()}

    # Guarantee canyon walls are solid at rows 7–9
    for row in range(7, 10):
        for wall_col in [I_COL - 1, I_COL + 1]:
            if b[row][wall_col] is None:
                b[row][wall_col] = {'num': rnum()}

    # Ensure col 5 is blocked at row 10 (piece lands here)
    if b[10][I_COL] is None:
        b[10][I_COL] = {'num': 2}

    return b

board_state = make_board()
BOARD_JS = json.dumps(board_state)

# Vertical I-piece (value 1 = light orange) at column 5
PIECE_JS = json.dumps({
    'type': 'I',
    'matrix': [[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]],
    'rot': 1,
    'x': I_COL - 1,   # matrix col 1 lands on board col I_COL
    'y': PIECE_Y,
})

# Next piece: S-piece
NEXT_JS = json.dumps({
    'type': 'S',
    'matrix': [[0,2,2],[2,2,0],[0,0,0]],
    'rot': 0,
    'x': 3, 'y': 0,
})

# ── Build modified HTML ────────────────────────────────────────────────────
with open(INDEX_HTML) as f:
    html = f.read()

inject = f"""
(function() {{
  // Widen touch buttons so bottom bar fills full viewport width
  // 7 × 68px + 6 × 4px gap = 500px = viewport width; height 68px = square
  const style = document.createElement('style');
  style.textContent = `
    #touch-ctrl {{
      grid-template-columns: repeat(7, 68px) !important;
      grid-template-rows: repeat(2, 68px) !important;
    }}
    .tc-btn {{
      width: 68px !important;
      height: 68px !important;
    }}
  `;
  document.head.appendChild(style);

  const __orig = startGame;
  startGame = function() {{
    __orig();
    const injectedBoard = {BOARD_JS};
    for (let r = 0; r < 20; r++)
      for (let c = 0; c < 10; c++)
        board[r][c] = injectedBoard[r][c];
    piece     = {PIECE_JS};
    nextPiece = {NEXT_JS};
    score = 2160; level = 3; lines = 22;
    updateUI();
    draw();
  }};
}})();
"""

target = 'startGame();\nrequestAnimationFrame'
modified_html = html.replace(target, inject + '\n' + target)

with open(TMP_HTML, 'w') as f:
    f.write(modified_html)

# ── Chrome headless screenshot ─────────────────────────────────────────────
# Chrome enforces min-width=500. VH=1295 gives content height ≈ 1196px.
# That content is 500px wide × 1196px tall — our source image.
print("Taking screenshot with Chrome headless...")
result = subprocess.run([
    CHROME,
    '--headless=new',
    f'--screenshot={TMP_RAW}',
    '--window-size=500,1295',
    '--hide-scrollbars',
    '--no-sandbox',
    '--disable-gpu',
    '--virtual-time-budget=2000',
    f'file://{TMP_HTML}',
], capture_output=True, timeout=30)

if result.returncode != 0 or not os.path.exists(TMP_RAW):
    print("Chrome failed:", result.stderr.decode()[:400])
    sys.exit(1)

# ── Load and crop to content ───────────────────────────────────────────────
raw = Image.open(TMP_RAW)
rw, rh = raw.size
arr_raw = __import__('numpy').array(raw)

# Find bottom of content (trim trailing navy)
nav = __import__('numpy').array(NAVY)
content_h = rh
for y in range(rh - 1, 0, -1):
    if __import__('numpy').abs(arr_raw[y, :, :3].astype(int) - nav).max(axis=1).max() > 15:
        content_h = y + 1
        break

src = raw.crop((0, 0, rw, content_h))
print(f"Source image: {rw}×{content_h}px (trimmed from {rh}px)")

# ── Composite into each target size ───────────────────────────────────────
def composite(src, target_w, target_h):
    """Scale src to fit within target dimensions, centre on navy canvas."""
    sw, sh = src.size
    scale = min(target_w / sw, target_h / sh)
    new_w = int(sw * scale)
    new_h = int(sh * scale)
    scaled = src.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new('RGB', (target_w, target_h), NAVY)
    x_off = (target_w - new_w) // 2
    y_off = (target_h - new_h) // 2
    canvas.paste(scaled, (x_off, y_off))
    return canvas

SCRIPT_DIR.mkdir(exist_ok=True)
generated = []

for filename, (tw, th) in SIZES.items():
    out_path = SCRIPT_DIR / filename
    img = composite(src, tw, th)
    img.save(out_path, optimize=True)
    generated.append((filename, tw, th))
    print(f"  ✓ icons/{filename}  ({tw}×{th})")

# ── Copy launch-screen image to Xcode Splash.imageset ─────────────────────
splash_src = SCRIPT_DIR / 'splash-2732x2732.png'
if SPLASH_DIR.exists() and splash_src.exists():
    for name in ['splash.png', 'splash-2732x2732.png',
                 'splash-2732x2732-1.png', 'splash-2732x2732-2.png']:
        dest = SPLASH_DIR / name
        import shutil
        shutil.copy2(splash_src, dest)
    print(f"  ✓ Copied to Splash.imageset/ (4 files)")
else:
    print(f"  ! Splash.imageset not found — skipping Xcode copy")

print("\nDone.")
print("Upload icons/screenshot-6.7inch.png and icons/screenshot-6.5inch.png")
print("to App Store Connect → App Screenshots.")
print("Run ./update_mobile_app.sh to sync launch screen to iOS.")
