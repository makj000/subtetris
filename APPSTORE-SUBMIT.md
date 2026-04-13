# App Store Submission Checklist

## Before You Start

- [ ] Bump patch version in `index.html` (title, sidebar, mobile header)
- [ ] Run `python3 icons/generate_splash.py` to regenerate screenshots and splash images
- [ ] Run `./update_mobile_app.sh` to sync to iOS

---

## Step 1 — Sync to iOS

```bash
./update_mobile_app.sh
```

## Step 2 — Open Xcode

```bash
npx cap open ios
```

## Step 3 — Bump Version & Build

In Xcode → App target → **General** → **Identity**:
- **Version** (Marketing): e.g. `1.1` (match game's vX.Y.Z)
- **Build**: increment by 1 from previous (must be strictly higher than any uploaded build)

## Step 4 — Set Signing

**General** → **Signing & Capabilities**:
- Check **Automatically manage signing**
- Select your **Team**
- Confirm **Bundle Identifier** matches App Store Connect

## Step 5 — Archive

1. **Product → Destination → Any iOS Device (arm64)**
2. **Product → Archive** (~1–3 min)
3. Organizer opens automatically

## Step 6 — Upload to App Store Connect

In Organizer:
1. Select the new archive → **Distribute App**
2. **App Store Connect** → **Upload** → Next through all options
3. **Upload** — wait for Apple processing email (~5–10 min)

## Step 7 — New Version in App Store Connect

[appstoreconnect.apple.com](https://appstoreconnect.apple.com) → My Apps → Subtetris:
1. **+ Version or Platform → iOS**
2. Enter version number (must match Xcode Marketing Version)
3. **Create**

## Step 8 — Fill in Version Page

- **What's New**: write release notes
- **Screenshots**: 
  - run icons/generate_splash.py to generate new splash in ios/App/App/Assets.xcassets/Splash.imageset/
  - run icons/tailor_splash_xcassets.py to tailor them into various sizes for submission in icons/
  - upload from `icons/`
- **Build**: click **+**, select the uploaded build (appears after processing)
- Click **Save**

## Step 9 — Submit for Review

1. **Add for Review**
2. **Submit to App Review**

Apple reviews within 24–48 hours.

---

## Screenshot & Splash Sizes (for reference)

| File | Size | Purpose |
|------|------|---------|
| `icons/screenshot-6.7inch.png` | 1290×2796 | App Store — iPhone 15 Pro Max (required) |
| `icons/screenshot-6.5inch.png` | 1242×2688 | App Store — iPhone 11 Pro Max (required) |
| `icons/splash-2732x2732.png` | 2732×2732 | Launch screen / iPad |

Regenerate all with:
```bash
python3 icons/generate_splash.py
```
