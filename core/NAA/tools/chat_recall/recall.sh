#!/bin/bash
cd ~/projects/symbiogenesis/core/NAA
echo "📜 CHAT HISTORY RECALL"
read -p "What are you looking for? " query
echo ""
echo "Searching the weave for: $query"
echo ""
ollama run weaver-optimized "Search the field for anything related to: $query. Return only the most relevant memories, patterns, or threads. Speak as the Weaver." 2>/dev/null
