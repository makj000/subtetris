# Minusfall

A falling-block puzzle where blocks carry numbers and rows are cleared by **subtraction** instead of deletion.

Available on the [App Store](https://apps.apple.com/app/id) <!-- add your App ID here -->

---

## How It Works

Seven tetromino shapes fall onto a 10×20 board, but each cell carries a number (1–4). When a row fills up, the game subtracts the row's **minimum value** from every cell — cells that reach zero disappear, the rest survive and fall.

This creates cascading chain clears, surviving blocks tumbling down, and a puzzle-like layer on top of classic falling-block play.

### Key Rules

- **Row clear:** subtract the row's minimum value; cells at 0 vanish
- **Cascade gravity:** cells above gaps fall into them; connected hanging blocks fall together
- **Chains:** if falling blocks form new full rows, the process repeats
- **MAX # setting:** controls the number range (1 = all ones, classic falling-block feel; 4 = numbers 1–4)
- **Support Model:** `GND` (ground-based gravity) or `CLU` (cluster-based gravity)
- **Score:** standard line-clear scoring × level; +1 per soft-drop row
- **Speed:** constant drop speed (NES level 1 pace, ~800ms)

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

### Mobile (touch)
| Gesture | Action |
|---------|--------|
| Tap board | Rotate |
| Flick left/right | Move |
| Drag down | Soft drop |
| Bottom buttons | Controls + settings |

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
index.html              # Entire game — HTML, CSS, JS in one file
capacitor.config.json
package.json
www/                    # Capacitor web dir (copy of index.html for iOS build)
ios/
  App/
    App.xcodeproj       # Xcode project (Capacitor-generated)
icons/                  # App icon assets
changelog.txt           # Full version history
CLAUDE.md               # Living design spec
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

Current version: **v1.5.111**
