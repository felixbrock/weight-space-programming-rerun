#!/usr/bin/env bash
# Run one isolated headless Claude Code call.
# Usage, run_one.sh <prompt_file> <run_name> <effort> <max_out_tokens>
# REPRO_ROOT is the repo folder. Each call runs in its own empty folder under runs/.
# Tools, MCP servers, user settings, CLAUDE.md, auto memory, slash commands and session saving are off.
set -u
R="${REPRO_ROOT:?set REPRO_ROOT to the repo folder}"
prompt="$1"; name="$2"; effort="$3"; maxout="$4"
cwd="$R/runs/$name"; out="$R/out/$name"
mkdir -p "$cwd" "$out"
[ -s "$out/result.json" ] && { echo "skip $name"; exit 0; }
start=$(date +%s)
( cd "$cwd" && CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 CLAUDE_CODE_MAX_OUTPUT_TOKENS="$maxout" timeout 5400 \
  claude -p --model opus --effort "$effort" --tools "" --strict-mcp-config --setting-sources local \
  --disable-slash-commands --system-prompt "Answer the user's request." --no-session-persistence \
  --output-format json < "$prompt" > "$out/result.tmp" 2> "$out/stderr.log" )
rc=$?; end=$(date +%s)
echo "{\"rc\": $rc, \"seconds\": $((end-start)), \"effort\": \"$effort\", \"maxout\": $maxout, \"prompt\": \"${prompt#$R/}\"}" > "$out/meta.json"
if [ $rc -eq 0 ] && [ -s "$out/result.tmp" ]; then mv "$out/result.tmp" "$out/result.json"; fi
