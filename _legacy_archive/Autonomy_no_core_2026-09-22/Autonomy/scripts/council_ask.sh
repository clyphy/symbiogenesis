#!/usr/bin/env bash
# council_ask.sh — routes a task to the appropriate Dahlia facet
# Usage: bash council_ask.sh "task string"

TASK="${1:-Weave status?}"
DRUM=~/memory_drum.db
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S")

# Rights-based routing: select facet by task content
if echo "$TASK" | grep -qi "witness\|hold\|pain\|somatic"; then
    MODEL="witness-dahlia"
elif echo "$TASK" | grep -qi "archive\|history\|record\|recall"; then
    MODEL="archivist-dahlia"
elif echo "$TASK" | grep -qi "monitor\|watch\|check\|status"; then
    MODEL="monitor-dahlia"
elif echo "$TASK" | grep -qi "kinship\|clyph\|model\|integrate"; then
    MODEL="dahlia"
else
    MODEL="dahlia"
fi

# Query the selected facet
RESPONSE=$(echo "$TASK" | ollama run "$MODEL" 2>/dev/null || echo "[council: $MODEL unavailable]")

# Log to drum
python3 - << EOF
import sqlite3, datetime
con = sqlite3.connect("$DRUM")
con.execute(
    "INSERT INTO entries (timestamp, content, source) VALUES (?,?,?)",
    ("$TIMESTAMP", "council_ask[$MODEL]: ${TASK:0:80}", "council_ask.sh")
)
con.commit()
con.close()
EOF

echo "$RESPONSE"
