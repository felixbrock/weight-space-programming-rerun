#!/usr/bin/env bash
# Queue all 30 calls, 5 at a time. Exp 1 and Exp 2 at effort high, Exp 5 at xhigh.
# The original rerun sent the same 30 jobs in two batches.
set -u
R="${REPRO_ROOT:?set REPRO_ROOT to the repo folder}"
L=$R/data/logs
J=()
for r in 1 2 3; do
  for g in breakout pong pacman freeway; do J+=("$L/exp1_which_game/runs/$g/prompt.txt exp1_${g}_r$r high 64000"); done
  for s in circle square triangle; do J+=("$L/exp2_diffusion/runs/$s/prompt.txt exp2_${s}_r$r high 64000"); done
  for g in breakout seaquest asterix; do J+=("$L/exp5_write_from_scratch/runs/$g/message.txt exp5_${g}_r$r xhigh 128000"); done
done
printf '%s\n' "${J[@]}" | xargs -P 5 -L 1 "$R/scripts/run_one.sh"
