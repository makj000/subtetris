# Subtetris

A Tetris variant where blocks carry numbers and rows are cleared by **subtraction** instead of deletion.

Available on the [App Store](https://apps.apple.com/app/id) <!-- add your App ID here -->

---

## How It Works

Standard Tetris pieces fall onto a 10×20 board, but each cell carries a number (1–4). When a row fills up, the game subtracts the row's **minimum value** from every cell — cells that reach zero disappear, the rest survive and fall.

This creates cascading chain clears, surviving blocks tumbling down, and a puzzle-like layer on top of classic Tetris.

### Key Rules

- **Row clear:** subtract the row's minimum value; cells at 0 vanish
- **Survivors fall:** surviving cells drop an extra `minValue − 1` rows
- **Multi-row bonus:** clearing multiple rows simultaneously drops survivors an additional `clearedRows − 1` rows
- **Chains:** if falling survivors form new full rows, the process repeats with a ×1.5 chain multiplier
- **MAX # setting:** controls the range of numbers (1 = all ones, classic Tetris feel; 4 = numbers 1–4)
- **Score:** standard Tetris scoring × level; +1 per soft-drop row
- **Speed:** constant drop speed (NES Tetris level 1 pace, ~800ms)

---

## Controls

### Keyboard
| Key | Action |
|-----|--------|
| ← → | Move |
| ↓ | Soft drop (hold) |
| ↑ | Rotate |
| Space / P | Pause / Unpause |
| N | New game |
| S | Toggle sound |

### Mobile (touch)
| Gesture | Action |
|---------|--------|
| Tap board | Rotate |
| Flick left/right | Move |
| Drag down | Soft drop |
| PAUSE button | Pause / Resume |

---

## Tech Stack

- **Single HTML file** (`index.html`) — no framework, no build step
- **HTML5 Canvas** for the game board and piece preview
- **Web Audio API** for sound effects
- **Capacitor 6** for iOS app wrapping (`com.subtetris.app`)
- **DSEG7-Classic** font for the LED-style score display

---

## Project Structure

```
index.html          # Entire game — HTML, CSS, JS in one file
capacitor.config.json
package.json
www/                # Capacitor web dir (copy of index.html for iOS build)
ios/                # Xcode project (Capacitor-generated)
changelog.txt       # Full version history
prompt.md           # Living design spec
```

---

## Development

```bash
# Serve locally
npm run serve
# → http://localhost:3456

# Sync to iOS
npm run cap:sync

# Open in Xcode
npm run cap:ios
```

---

## Building for iOS

1. `npm run cap:sync` — copies `index.html` to `www/` and syncs Capacitor
2. `npm run cap:ios` — opens Xcode
3. In Xcode: select your signing team, choose a device/simulator, hit Run

---

## Changelog

See [changelog.txt](changelog.txt) for full version history.

Current version: **v1.5.102**
