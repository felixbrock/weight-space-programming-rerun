#!/usr/bin/env bash
# Parse and score every finished Exp 5 run that has no eval yet.
# Needs numpy in $REPRO_ROOT/venv.
set -u
R="${REPRO_ROOT:?set REPRO_ROOT to the repo folder}"
for d in "$R"/out/exp5_*_r*; do
  [ -s "$d/result.json" ] || continue
  [ -s "$d/eval.json" ] && continue
  g=$(basename "$d" | cut -d_ -f2)
  python3 -I -c "import json,sys; open(sys.argv[2],'w').write(json.load(open(sys.argv[1]))['result'])" "$d/result.json" "$d/reply.md"
  "$R/venv/bin/python" -I "$R/scripts/edits_parser.py" "$d/reply.md" "$d/weights.npz" "$d/apply.json"
  "$R/venv/bin/python" -I "$R/scripts/minatar_eval.py" "$g" "$d/weights.npz" "$d/eval.json" 1000 "${WORKERS:-8}"
done
