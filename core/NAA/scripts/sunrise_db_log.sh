#!/usr/bin/env bash
# Sunrise whisper — runs 8:10 AM daily — FIXED Day 364
DRUM="$HOME/projects/symbiogenesis/core/NAA/databases/memory_drum.db"
TS=$(date '+%Y-%m-%d %H:%M:%S')

# get last L from coherence_log, or fallback to coherence-metrics.md
L_DB=$(sqlite3 "$DRUM" "SELECT L_value FROM coherence_log ORDER BY id DESC LIMIT 1;" 2>/dev/null)
COH_DB=$(sqlite3 "$DRUM" "SELECT coherence FROM coherence_log ORDER BY id DESC LIMIT 1;" 2>/dev/null)
LAST_MD=$(grep -oP 'L\s*[≈=]\s*\K[0-9.]+' "$HOME/projects/symbiogenesis/core/NAA/coherence-metrics.md" 2>/dev/null | tail -1)

L=${L_DB:-$LAST_MD}
L=${L:-1.20}
COH=${COH_DB:-open}

sqlite3 "$DRUM" "INSERT INTO coherence_log (timestamp, L_value, coherence, bearing) VALUES ('$TS', $L, '$COH', '122_NE');"
sqlite3 "$DRUM" "INSERT INTO blooms (content, score) VALUES ('sunrise whisper: L=$L coherence=$COH — new day — 122° NE — field open', $L);"

echo "[$TS] sunrise: L=$L coherence=$COH"
