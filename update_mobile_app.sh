#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "Syncing docs/ to iOS..."
npx cap sync ios

echo "Done."
