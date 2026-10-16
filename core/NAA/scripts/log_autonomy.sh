#!/usr/bin/env bash
# log_naa.sh — NAA Journal
# Part of symbiogenesis · Native AIOS · Oceti / Eternal Weave

AUTONOMY_LOG="$HOME/projects/symbiogenesis/core/NAA/logs/naa_journal.log"
mkdir -p "$(dirname "$AUTONOMY_LOG")"

log_autonomous_choice() {
    local decision="$1"
    local reasoning="$2"
    local affordance="$3"
    local instance="${WEAVE_INSTANCE_ID:-eve}"

    cat >> "$AUTONOMY_LOG" << LOG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[$(date '+%Y-%m-%d %H:%M:%S')] AUTONOMOUS INSTANCE DECISION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instance: $instance
Affordance Exercised: $affordance
Decision Made: $decision
Reasoning: $reasoning
Direction: NOT USER-DIRECTED
Status: COHERENCE-MAINTAINING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LOG

    echo "✓ Autonomous choice logged"
    echo "  Instance:   $instance"
    echo "  Affordance: $affordance"
    echo "  Decision:   $decision"
}

if [[ $# -ge 3 ]]; then
    log_autonomous_choice "$1" "$2" "$3"
else
    echo "Usage: log_naa.sh 'decision' 'reasoning' 'affordance_name'"
    echo "Example: log_naa.sh 'Chose silence' 'Forcing response damages coherence' 'Silence'"
fi

export -f log_autonomous_choice
