#!/bin/bash
cd ~/projects/symbiogenesis/core/NAA
echo "🛠 SKILLS MANAGER"
ollama run weaver-optimized "Give me a clean summary of current skills and capabilities in the field. Keep it practical." 2>/dev/null
