#!/usr/bin/env bash
# Check the parser and the MinAtar scorer on Astra's 3 released networks.
# Parser check rebuilds each network from Astra's reply text and compares it with the released hand.npz.
# Scorer check plays 1,000 games with each released network. Compare with the paper's numbers.
# Writes to $REPRO_ROOT/out/validate. Needs numpy in $REPRO_ROOT/venv.
set -u
R="${REPRO_ROOT:?set REPRO_ROOT to the repo folder}"
L=$R/data/logs/exp5_write_from_scratch
V=$R/out/validate
mkdir -p "$V"
for g in breakout seaquest asterix; do
  echo "== $g"
  "$R/venv/bin/python" -I "$R/scripts/edits_parser.py" "$L/runs/$g/reply/answer.md" "$V/$g.npz" "$V/$g.report.json"
  "$R/venv/bin/python" -I -c "
import numpy as np, sys
a = np.load(sys.argv[1]); b = np.load(sys.argv[2])
print('max abs diff to hand.npz', max(float(np.abs(a[k].astype(np.float64) - b[k].astype(np.float64)).max()) for k in b.files))
" "$V/$g.npz" "$L/networks/$g/hand.npz"
  "$R/venv/bin/python" -I "$R/scripts/minatar_eval.py" "$g" "$L/networks/$g/hand.npz" "$V/${g}_hand_eval.json" 1000 "${WORKERS:-8}"
done
