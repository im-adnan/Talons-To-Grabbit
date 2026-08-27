#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$SCRIPT_DIR/.."
PLUGIN_DIR="$REPO_ROOT/plugin"
OUT_FILE="$SCRIPT_DIR/talons.gda"

echo "🦅 [Talons] Building Grabbit Plugin package..."

# Check if yt-dlp source is present, fetch if missing
if [ ! -d "$PLUGIN_DIR/yt-dlp/yt_dlp" ]; then
    echo "ℹ️  Upstream yt-dlp not found in plugin directory. Fetching now..."
    "$SCRIPT_DIR/fetch-ytdlp.sh"
fi

# Ensure executable permissions
chmod +x "$PLUGIN_DIR/run.sh" "$PLUGIN_DIR/extractor.py"

# Remove previous build if exists
rm -f "$OUT_FILE"

# Package plugin directory contents into .gda archive
(
    cd "$PLUGIN_DIR"
    zip -r -q "$OUT_FILE" . -x "*.DS_Store" -x "__pycache__/*" -x "*.pyc"
)

echo "✅ Created Grabbit plugin package: $OUT_FILE"
