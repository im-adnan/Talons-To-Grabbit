#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLUGIN_DIR="$SCRIPT_DIR/../plugin"
YTDLP_DEST="$PLUGIN_DIR/yt-dlp"

echo "🦅 [Talons] Fetching latest upstream yt-dlp from GitHub (yt-dlp/yt-dlp)..."

TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Download the latest master branch source tarball
curl -sSL "https://github.com/yt-dlp/yt-dlp/archive/refs/heads/master.tar.gz" -o "$TEMP_DIR/yt-dlp.tar.gz"

# Extract archive
tar -xzf "$TEMP_DIR/yt-dlp.tar.gz" -C "$TEMP_DIR"

# Locate the extracted source directory
EXTRACTED_DIR=$(find "$TEMP_DIR" -mindepth 1 -maxdepth 1 -type d | head -n 1)

if [ -z "$EXTRACTED_DIR" ] || [ ! -d "$EXTRACTED_DIR/yt_dlp" ]; then
    echo "❌ Error: Could not find yt_dlp package in downloaded upstream archive."
    exit 1
fi

# Clean and update destination
rm -rf "$YTDLP_DEST"
mkdir -p "$YTDLP_DEST"

# Copy the core yt_dlp package and __main__.py
cp -R "$EXTRACTED_DIR/yt_dlp" "$YTDLP_DEST/"
if [ -f "$EXTRACTED_DIR/__main__.py" ]; then
    cp "$EXTRACTED_DIR/__main__.py" "$YTDLP_DEST/"
fi

# Copy license and version if present
if [ -f "$EXTRACTED_DIR/LICENSE" ]; then
    cp "$EXTRACTED_DIR/LICENSE" "$YTDLP_DEST/LICENSE"
fi

echo "✅ Successfully synced fresh upstream yt-dlp into $YTDLP_DEST"
