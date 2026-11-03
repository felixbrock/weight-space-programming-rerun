# Weight-space programming, rerun with Claude Opus 5.5

**TLDR** Rerun of 3 experiments from [Sparks of Weight-Space Programming](https://rikiyat.github.io/blog/weight-space-programming/), with Claude Opus 5.5 in place of GPT-6 Astra. Weight reading replicates. Claude named the right game 12 of 12 times and the right shape 9 of 9 times. Weight writing replicates for Breakout only. Claude's networks average 468 on Breakout (Astra 517), 42.5 on Asterix (Astra 53.2) and 15.7 on Seaquest (Astra 53.1).

Full write-up with charts lives in the [report](https://claude.ai/artifact/SiS8AYPi7GzUq6UxSUGXsA). This repo holds every script and the raw output of all 30 Claude calls.

## Results

| Experiment | Claude Opus 5.5, 3 runs | GPT-6 Astra, 1 run (paper) |
|---|---|---|
| Exp 1, name the game from policy weights | 12 of 12 right | 4 of 4 right |
| Exp 2, name the shape from diffusion weights | 9 of 9 right | 3 of 3 right |
| Exp 5, write a Breakout network | 468.4 mean (419.5, 515.6, 470.1) | 517.4 |
| Exp 5, write an Asterix network | 42.5 mean (30.5, 47.4, 49.5) | 53.2 |
| Exp 5, write a Seaquest network | 15.7 mean (12.4, 18.4, 16.4) | 53.1 |

Exp 5 scores are average points over 1,000 games.

## Repo layout

- `scripts/`
  - `run_one.sh` runs one isolated headless Claude Code call
  - `run_all.sh` queues all 30 calls, 5 at a time
  - `extract_envs.sh` copies MinAtar 1.0.15 game code out of the Exp 5 prompts
  - `edits_parser.py` turns written weight statements into network weights
  - `minatar_eval.py` plays 1,000 games with one network
  - `score_exp5.sh` parses and scores every Exp 5 run
  - `score_id.py` scores Exp 1 and Exp 2 by keyword
  - `check_scorer.sh` runs parser and scorer on Astra's released networks
- `results/`
  - One folder per call, named `<experiment>_<item>_r<run>`
  - `result.json` holds full Claude Code JSON output with answer, token usage and cost
  - `meta.json` holds wall time, effort and prompt file
  - Exp 5 folders add `reply.md`, `weights.npz`, `apply.json` (parser report) and `eval.json` (1,000-game score)
  - `scores_exp12.json` holds Exp 1 and Exp 2 scores
  - `validate/` holds scorer check on Astra's networks
  - `summary.json` holds every number shown in the report

## Requirements

- Claude Code
  - Logged-in account with Opus access
  - Original runs used Claude Code 2.1.316 and model `claude-opus-5-5`
- Tools
  - git, bash, uv, Python 3.12
- CPU
  - MinAtar scoring took 1 to 11 s per network on 20 cores
  - Set `WORKERS` to your core count, default 8
  - Worker count doesn't change scores

## Reproduce

```bash
git clone https://github.com/felixbrock/weight-space-programming-rerun
cd weight-space-programming-rerun
export REPRO_ROOT=$PWD

# authors' prompts, networks and Astra answers
git clone https://github.com/RikiyaT/lm_understand-logs data/logs
git -C data/logs checkout 4d09ba6

bash scripts/extract_envs.sh
uv venv venv --python 3.12
uv pip install --python venv/bin/python numpy==2.5.4

bash scripts/check_scorer.sh     # optional, no Claude calls
bash scripts/run_all.sh          # 30 Claude calls
bash scripts/score_exp5.sh
python3 -I scripts/score_id.py out
```

- Scorer check
  - Parser rebuilds Astra's 3 networks from Astra's reply text. Max difference to released weights is 0
  - Scores land within about 1 standard error of the paper. Original run got Breakout 515.8, Seaquest 52.3, Asterix 54.8. Paper reports 517.4, 53.1, 53.2
- Claude calls
  - Exp 5 calls take 12 to 50 min each
  - Whole set cost $43.11 list-price equivalent. Claude subscription covers it
  - `run_one.sh` skips finished calls, so rerunning `run_all.sh` resumes after a crash
- Outputs
  - New runs land in `out/`, same layout as `results/`

## Rescore published results without Claude calls

```bash
python3 -I scripts/score_id.py results
mkdir -p out/rescore
for d in results/exp5_*; do
  g=$(basename $d | cut -d_ -f2)
  venv/bin/python -I scripts/minatar_eval.py $g $d/weights.npz out/rescore/$(basename $d).json 1000 ${WORKERS:-8}
done
```

Episode seeds are fixed. Rescoring gives the same means as `results/*/eval.json`.

## Isolation

- Each call runs in its own empty folder under `runs/`
- Claude Code flags turn off tools, MCP servers, user settings, CLAUDE.md, auto memory, slash commands and session saving
- System prompt is "Answer the user's request.", same as the paper's `instructions.md`
- Prompt files go in byte for byte
- Test call showed 580 context tokens in total. No chat history or user files reach the model

## Differences from the paper's setup

- Long thinking with automatic continuation
  - Claude used 80k to 318k output tokens per Exp 5 answer, Astra 20k to 29k
  - 6 of 9 Exp 5 answers passed Claude Code's 128k output cap per API call
  - Claude Code then sent its built-in continue message. Message carries no score or game feedback
  - Each such answer took 2 to 4 API calls instead of one
- Hyphen fix in keyword scorer
  - One Pac-Man answer used a non-breaking hyphen
  - `score_id.py` maps every hyphen variant to a plain hyphen
  - Exp 1 reads 11 of 12 without the fix, 12 of 12 with it
- Episode seeds
  - Seeds differ from the paper's
  - Single scores move by about 1 standard error
- Fill check in Exp 2
  - `score_id.py` also records whether a drawing is filled or an outline
  - Paper scores only the shape name

## Credit and license

- Original work
  - [Sparks of Weight-Space Programming](https://rikiyat.github.io/blog/weight-space-programming/) by Rikiya Takehi, Jayden Teoh, Alex Zhang and Omar Khattab, MIT CSAIL
  - Prompts, networks and Astra answers come from their [logs repo](https://github.com/RikiyaT/lm_understand-logs) at commit 4d09ba6
  - This repo is independent and not affiliated with the authors
- MinAtar
  - GPL-3.0, not included here
  - `extract_envs.sh` copies it out of the authors' prompts on your machine
- This repo
  - Code under MIT license, see `LICENSE`
