#!/usr/bin/env bash
# Copy the MinAtar 1.0.15 game source out of each Exp 5 prompt into scripts/minatar_envs.
# The first python block of each prompt is that game's source file.
set -u
R="${REPRO_ROOT:?set REPRO_ROOT to the repo folder}"
mkdir -p "$R/scripts/minatar_envs"
for g in breakout seaquest asterix; do
  awk '/^```python/{f=1;next} /^```/{if(f){f=0;exit}} f' \
    "$R/data/logs/exp5_write_from_scratch/runs/$g/message.txt" > "$R/scripts/minatar_envs/$g.py"
done
