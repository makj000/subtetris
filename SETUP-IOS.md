# Minusfall — iOS App Store Setup

## Prerequisites

- **Mac** with macOS 13+
- **Xcode 15+** (free, from Mac App Store)
- **Apple Developer account** — $99/year at https://developer.apple.com
- **Node.js 18+** — https://nodejs.org

---

## One-time setup

### 1. Install dependencies

```bash
cd /Users/kma/dev/game/tetris
npm install
```

### 2. Add the iOS platform

```bash
npx cap add ios
```

This creates an `ios/` folder with a full Xcode project.

### 3. Copy web assets into the native project

```bash
npx cap copy ios
```

### 4. Open in Xcode

```bash
npx cap open ios
```

---

## In Xcode

### App identity
1. Select the **App** target → **Signing & Capabilities**
2. Set **Bundle Identifier** to `com.subtetris.app` (or your own reverse-domain)
3. Select your **Team** (requires Apple Developer account)
4. Enable **Automatically manage signing**

### App icons
1. Place a **1024×1024 PNG** called `icon-1024.png` in the `icons/` folder
2. Run `./icons/generate-icons.sh icons/icon-1024.png` to generate all sizes
3. Drag the generated PNGs into `Assets.xcassets/AppIcon.appiconset/` in Xcode
   (or use the **Asset Catalog** GUI — just drag each size to the right slot)

### Launch Screen
Xcode generates a default launch screen. Customize in
`App/Base.lproj/LaunchScreen.storyboard` or replace with a SwiftUI launch screen.

---

## Build & submit

### Test on device / simulator
- Press ▶ in Xcode (choose a simulator or your plugged-in iPhone)

### Archive for App Store
1. **Product → Archive**
2. **Distribute App → App Store Connect → Upload**
3. In https://appstoreconnect.apple.com — fill in metadata, screenshots, pricing
4. Submit for review (typically 1–3 days)

---

## Ongoing workflow

Whenever you update `docs/`:

```bash
npx cap copy ios      # sync web changes into the native shell
npx cap open ios      # re-open Xcode if needed
```

No Swift code needs to change between web-only updates.
