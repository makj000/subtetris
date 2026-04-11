#!/bin/bash
# Generates all required iOS app icon sizes from a single source PNG.
# Usage: ./generate-icons.sh source.png
# Requires: ImageMagick (brew install imagemagick)

SOURCE="${1:-icon-1024.png}"

if ! command -v magick &>/dev/null; then
  echo "ImageMagick not found. Install with: brew install imagemagick"
  exit 1
fi

if [ ! -f "$SOURCE" ]; then
  echo "Source image '$SOURCE' not found."
  echo "Create a 1024×1024 PNG of your app icon and pass it as the first argument."
  exit 1
fi

sizes=(20 29 40 57 58 60 76 80 87 114 120 152 167 180 1024)

for s in "${sizes[@]}"; do
  magick "$SOURCE" -resize "${s}x${s}" "icon-${s}.png"
  echo "  → icon-${s}.png"
done

echo "Done! Copy all icon-*.png into your Xcode project's Assets.xcassets/AppIcon.appiconset/"
