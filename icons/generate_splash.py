#!/usr/bin/env python3
"""
Generate Subtetris launch-screen splash images.

Run from the project root:
    python3 icons/generate_splash.py

Outputs (in icons/):
    splash-2732x2732.png     2732×2732  Master launch screen (all sizes derived from this)

    iPhone splash images (named by display size):
    splash-6.9inch.png       1320×2868  iPhone 16 Pro Max
    splash-6.5inch.png       1242×2688  iPhone 11 Pro Max / XS Max
    splash-6.3inch.png       1206×2622  iPhone 16 Pro
    splash-6.1inch.png       1179×2556  iPhone 16 / 15 / 14
    splash-5.5inch.png       1242×2208  iPhone 8 Plus / 7 Plus
    splash-4.7inch.png        750×1334  iPhone SE (3rd gen) / 8 / 7
    splash-4.0inch.png        640×1136  iPhone SE (1st gen) / 5s
    splash-3.5inch.png        640×960   iPhone 4s

    iPad splash images:
    splash-2048x2732.png    2048×2732   iPad Pro 12.9" @2x
    splash-2064x2752.png    2064×2752   iPad Pro 13" @2x

Also copies all splash images to:
    ios/App/App/Assets.xcassets/Splash.imageset/
"""

import json
import os
import random
import shutil
import subprocess
import sys
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
import numpy as np
arr_raw = np.array(raw)

# Find bottom of content (trim trailing navy)
nav = np.array(NAVY)
content_h = rh
for y in range(rh - 1, 0, -1):
    if np.abs(arr_raw[y, :, :3].astype(int) - nav).max(axis=1).max() > 15:
        content_h = y + 1
        break

screenshot = raw.crop((0, 0, rw, content_h))
print(f"Source image: {rw}×{content_h}px (trimmed from {rh}px)")

# ── Helper ─────────────────────────────────────────────────────────────────
def composite(img, target_w, target_h):
    """Scale img to fit within target dimensions, centred on navy canvas."""
    sw, sh = img.size
    scale  = min(target_w / sw, target_h / sh)
    new_w, new_h = int(sw * scale), int(sh * scale)
    scaled = img.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new('RGB', (target_w, target_h), NAVY)
    canvas.paste(scaled, ((target_w - new_w) // 2, (target_h - new_h) // 2))
    return canvas

SCRIPT_DIR.mkdir(exist_ok=True)

# ── Master splash ──────────────────────────────────────────────────────────
master_path = SCRIPT_DIR / 'splash-2732x2732.png'
composite(screenshot, 2732, 2732).save(master_path, optimize=True)
print(f"  ✓ icons/splash-2732x2732.png  (2732×2732)")

# ── Derived splash sizes ───────────────────────────────────────────────────
# iPhone splashes: derive from screenshot (portrait source) so content fills height.
# iPad splashes: derive from square master (landscape-safe source).
master = Image.open(master_path)

# iPhone splashes named by display size (width × height in device pixels)
IPHONE_SPLASHES = {
    'splash-6.9inch.png': (1320, 2868),  # iPhone 16 Pro Max
    'splash-6.5inch.png': (1242, 2688),  # iPhone 11 Pro Max / XS Max
    'splash-6.3inch.png': (1206, 2622),  # iPhone 16 Pro
    'splash-6.1inch.png': (1179, 2556),  # iPhone 16 / 15 / 14
    'splash-5.5inch.png': (1242, 2208),  # iPhone 8 Plus / 7 Plus
    'splash-4.7inch.png': (750,  1334),  # iPhone SE (3rd gen) / 8 / 7
    'splash-4.0inch.png': (640,  1136),  # iPhone SE (1st gen) / 5s
    'splash-3.5inch.png': (640,   960),  # iPhone 4s
}

# iPad splashes (kept for Xcode asset catalog compatibility)
IPAD_SPLASHES = {
    'splash-2048x2732.png': (2048, 2732),  # iPad Pro 12.9" @2x
    'splash-2064x2752.png': (2064, 2752),  # iPad Pro 13" @2x
}

# iPhone splashes use the portrait screenshot as source (avoids big top/bottom margins
# that result from compositing a square master into a portrait canvas).
for name, (w, h) in IPHONE_SPLASHES.items():
    composite(screenshot, w, h).save(SCRIPT_DIR / name, optimize=True)
    print(f"  ✓ icons/{name}  ({w}×{h})")

# iPad splashes use the portrait screenshot as source (same as iPhones) so content
# fills the height without big top/bottom margins.
for name, (w, h) in IPAD_SPLASHES.items():
    composite(screenshot, w, h).save(SCRIPT_DIR / name, optimize=True)
    print(f"  ✓ icons/{name}  ({w}×{h})")

# ── Copy all splash images to Xcode Splash.imageset ───────────────────────
SPLASH_FILES = (
    ['splash-2732x2732.png']
    + list(IPHONE_SPLASHES.keys())
    + list(IPAD_SPLASHES.keys())
)

SPLASH_DIR.mkdir(parents=True, exist_ok=True)
for name in SPLASH_FILES:
    img_path = SCRIPT_DIR / name
    if img_path.exists():
        shutil.copy2(img_path, SPLASH_DIR / name)
        print(f"  ✓ Copied → Splash.imageset/{name}")
    else:
        print(f"  ! Missing {img_path} — skipping")

# Remove stale files no longer referenced
for stale in [
    'splash-2732x2732-1.png', 'splash-2732x2732-2.png',
    'splash-390x844.png', 'splash-1242x2688.png', 'splash-1284x2778.png',
    'screenshot-6.7inch.png', 'screenshot-6.5inch.png',
]:
    p = SPLASH_DIR / stale
    if p.exists():
        p.unlink()
        print(f"  ✓ Removed stale Splash.imageset/{stale}")

# Remove old screenshot files from icons/ directory
for stale in ['screenshot-6.7inch.png', 'screenshot-6.5inch.png']:
    p = SCRIPT_DIR / stale
    if p.exists():
        p.unlink()
        print(f"  ✓ Removed stale icons/{stale}")

# Write Contents.json
# Maps each display-size splash to the nearest Xcode idiom/scale slot.
# Xcode only needs representative entries; extra files are ignored unless referenced.
contents = {
    "images": [
        # iPhone @2x slots (375pt / 414pt logical → 2x)
        {"filename": "splash-4.7inch.png", "idiom": "iphone", "scale": "2x"},
        # iPhone @3x slots (various logical sizes → 3x)
        {"filename": "splash-6.9inch.png", "idiom": "iphone", "scale": "3x"},
        # iPad @2x slots
        {"filename": "splash-2048x2732.png", "idiom": "ipad", "scale": "2x"},
        # Universal fallback
        {"filename": "splash-2732x2732.png", "idiom": "universal", "scale": "3x"},
    ],
    "info": {"author": "xcode", "version": 1},
}
(SPLASH_DIR / 'Contents.json').write_text(json.dumps(contents, indent=2) + '\n')
print("  ✓ Wrote   Splash.imageset/Contents.json")

print("\nDone.")
print("iPhone splash images named by display size are in icons/splash-*.inch.png")
print("All splash images copied to ios/App/App/Assets.xcassets/Splash.imageset/")
print("Run ./update_mobile_app.sh to sync launch screen to iOS.")
