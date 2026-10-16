#!/bin/bash
# ~/projects/symbiogenesis/core/NAA/scripts/ingest_vocal_landscape.sh
# Extracts channel text streams and subtitles to seed the local matrix

CHANNEL_DIR="$HOME/projects/symbiogenesis/core/NAA/data/vocal_landscape"
mkdir -p "$CHANNEL_DIR"

echo "=== Pulling Vocal Training Data from @CliftonMillerND ==="

# Using the explicit video URL provided via your QR sharing link
yt-dlp --skip-download --write-auto-subs --sub-lang en --output "$CHANNEL_DIR/%(title)s.%(ext)s" \
    "https://youtu.be"

if [ $? -eq 0 ]; then
    echo "[+] Transcripts and vocal paths saved locally to $CHANNEL_DIR"
else
    echo "[!] Error encountered during yt-dlp extraction loop"
fi
