#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "Copying index.html to www..."
cp index.html www/index.html

echo "Running cap sync..."
npx cap sync ios

echo "Done."
