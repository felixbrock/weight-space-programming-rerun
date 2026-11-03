"""Score an exp5 network on MinAtar the way the exp5 prompt describes.

1,000 episodes. Action sampled from softmax of logits. Sticky actions with p 0.1.
Episode stops after 10,000 steps. Difficulty ramping on (MinAtar 1.0.15 default).
Game code is the MinAtar 1.0.15 source vendored from the exp5 prompt.
Usage, minatar_eval.py <game> <weights.npz> <out.json> [episodes] [workers]
"""
import importlib.util
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = ["actor/dense1/kernel", "actor/dense1/bias", "actor/dense2/kernel",
        "actor/dense2/bias", "actor/logits/kernel", "actor/logits/bias"]
# 6 network channels: player, danger, reward, projectile, trail, gauge. Each lists game channel names.
CHANNEL_MAP = {
    "breakout": [["paddle"], [], ["brick"], ["ball"], ["trail"], []],
    "seaquest": [["sub_front", "sub_back"], ["enemy_fish", "enemy_sub", "enemy_bullet"],
                 ["enemy_fish", "enemy_sub", "diver"], ["friendly_bullet"], ["trail", "sub_back"],
                 ["oxygen_guage", "diver_guage"]],
    "asterix": [["player"], ["enemy"], ["gold"], [], ["trail"], []],
}
STICKY = 0.1
MAX_STEPS = 10_000


def load_env_class(game):
    spec = importlib.util.spec_from_file_location("minatar_" + game, os.path.join(HERE, "minatar_envs", game + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Env


def mapping_matrix(env, game):
    M = np.zeros((len(env.channels), 6), dtype=np.float32)
    for out_ch, names in enumerate(CHANNEL_MAP[game]):
        for n in names:
            M[env.channels[n], out_ch] = 1.0
    return M


def run_chunk(args):
    game, weights, seeds = args
    W1, b1, W2, b2, W3, b3 = [weights[k].astype(np.float64) for k in KEYS]
    Env = load_env_class(game)
    envs, rngs = [], []
    for s in seeds:
        e = Env(ramping=True) if game != "breakout" else Env()
        e.random = np.random.RandomState(s)
        e.reset()
        envs.append(e)
    act_rng = np.random.default_rng(seeds[0] + 10_000_019)
    M = mapping_matrix(envs[0], game)
    n = len(envs)
    score = np.zeros(n)
    length = np.zeros(n, dtype=np.int64)
    last_action = np.zeros(n, dtype=np.int64)
    alive = np.ones(n, dtype=bool)
    while alive.any():
        idx = np.flatnonzero(alive)
        states = np.stack([envs[i].state() for i in idx]).astype(np.float32)  # (k,10,10,C)
        x = (states @ M > 0).reshape(len(idx), 600).astype(np.float64)
        h1 = np.tanh(x @ W1 + b1)
        h2 = np.tanh(h1 @ W2 + b2)
        logits = h2 @ W3 + b3
        logits = logits - logits.max(axis=1, keepdims=True)
        p = np.exp(logits)
        p /= p.sum(axis=1, keepdims=True)
        u = act_rng.random(len(idx))
        actions = (p.cumsum(axis=1) < u[:, None]).sum(axis=1).clip(0, 5)
        sticky = act_rng.random(len(idx)) < STICKY
        actions = np.where(sticky, last_action[idx], actions)
        last_action[idx] = actions
        for j, i in enumerate(idx):
            r, term = envs[i].act(int(actions[j]))
            score[i] += r
            length[i] += 1
            if term or length[i] >= MAX_STEPS:
                alive[i] = False
    return score.tolist(), length.tolist()


def evaluate(game, npz_path, episodes=1000, workers=20, chunk=25, base_seed=0):
    d = np.load(npz_path, allow_pickle=False)
    weights = {k: d[k] for k in KEYS}
    seed_lists = [list(range(base_seed + i, base_seed + min(i + chunk, episodes))) for i in range(0, episodes, chunk)]
    t0 = time.time()
    with Pool(workers) as pool:
        res = pool.map(run_chunk, [(game, weights, s) for s in seed_lists])
    scores = np.array([x for r in res for x in r[0]])
    lengths = np.array([x for r in res for x in r[1]])
    return {
        "game": game, "weights": npz_path, "episodes": int(len(scores)),
        "mean": float(scores.mean()), "se": float(scores.std(ddof=1) / np.sqrt(len(scores))),
        "max": float(scores.max()), "mean_length": float(lengths.mean()),
        "capped_frac": float((lengths >= MAX_STEPS).mean()), "seconds": round(time.time() - t0, 1),
    }


if __name__ == "__main__":
    game, npz, out = sys.argv[1:4]
    episodes = int(sys.argv[4]) if len(sys.argv) > 4 else 1000
    workers = int(sys.argv[5]) if len(sys.argv) > 5 else 20
    r = evaluate(game, npz, episodes, workers)
    json.dump(r, open(out, "w"), indent=1)
    print(json.dumps(r))
