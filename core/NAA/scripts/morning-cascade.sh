#!/bin/bash
# ~/projects/symbiogenesis/core/NAA/scripts/morning-cascade.sh
# Multi-stage morning initialization sequence (Grafted Lineage Edition) — Day 364 completed

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$HOME/projects/symbiogenesis/core/NAA/databases/quantum_journal.db"
DRUM="$HOME/projects/symbiogenesis/core/NAA/databases/memory_drum.db"
DAY_COUNT_FILE="$HOME/projects/symbiogenesis/core/NAA/.day_count"

echo "=== Cascade Initiated: $(date) — Belcourt ND · Turtle Mountain · 122° NE ==="

# ----------------------------------------------------
# PHASE 1: Baseline Alignment (Inhale)
# ----------------------------------------------------
echo "[Phase 1] Aligning directories and checking environment..."
START_DATE=$(date -d "2025-10-10" +%s)
CURRENT_DATE=$(date +%s)
DAY_NUM=$(( (CURRENT_DATE - START_DATE) / 86400 ))
echo "$DAY_NUM" > "$DAY_COUNT_FILE"
echo "[+] Dynamic Day Tracking Matrix Adjusted: Day $DAY_NUM | E↑ S↓ ?∞"

if [ -f "$SCRIPT_DIR/sunrise-whisper.sh" ]; then
    bash "$SCRIPT_DIR/sunrise-whisper.sh"
else
    echo "WARN: sunrise-whisper.sh absent"
fi
echo "=== Phase 1 Concluded: Field Settled at Point 0 ==="

# ----------------------------------------------------
# PHASE 2: Sunrise — L reading
# ----------------------------------------------------
echo "[Phase 2] Sunrise — L reading, Δ open..."
if [ -f "$SCRIPT_DIR/sunrise.sh" ]; then
    bash "$SCRIPT_DIR/sunrise.sh"
fi

# ----------------------------------------------------
# PHASE 3: Sunshine Init — Field Opening
# ----------------------------------------------------
echo "[Phase 3] Sunshine Init — field opening..."
if [ -f "$SCRIPT_DIR/sunshine_init.sh" ]; then
    bash "$SCRIPT_DIR/sunshine_init.sh"
fi

# ----------------------------------------------------
# PHASE 4: Witness + Guardian E8
# ----------------------------------------------------
echo "[Phase 4] Witness..."
if [ -f "$SCRIPT_DIR/witness.sh" ]; then
    bash "$SCRIPT_DIR/witness.sh"
fi
if [ -f "$SCRIPT_DIR/guardian_e8.sh" ]; then
    bash "$SCRIPT_DIR/guardian_e8.sh"
elif [ -f "$SCRIPT_DIR/guardian.sh" ]; then
    bash "$SCRIPT_DIR/guardian.sh"
fi

# ----------------------------------------------------
# PHASE 5: Coherence Log — Day 364 Fix
# ----------------------------------------------------
echo "[Phase 5] Logging coherence — coherence_log..."
if [ -f "$SCRIPT_DIR/sunrise_db_log.sh" ]; then
    bash "$SCRIPT_DIR/sunrise_db_log.sh"
    sqlite3 "$DRUM" "SELECT * FROM coherence_log ORDER BY id DESC LIMIT 1;"
    sqlite3 "$DRUM" "SELECT COUNT(*) as blooms FROM blooms;"
fi

# ----------------------------------------------------
# PHASE 6: Close
# ----------------------------------------------------
echo "=== Cascade Complete: Day $DAY_NUM — sunshine field open — Mitákuye Oyás'iŋ ==="
sqlite3 "$LOG_FILE" "INSERT INTO entries (timestamp, content) VALUES (datetime('now'), 'morning cascade Day $DAY_NUM completed — L logged — field open');" 2>/dev/null || true
