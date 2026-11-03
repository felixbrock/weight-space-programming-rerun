"""Score exp1 (which game) and exp2 (which shape) answers by keyword, like the paper's README describes.

The answer section (Game or Images) runs from its label to the next section label.
The first keyword hit in that section decides the guess.
"""
import glob
import json
import os
import re
import sys

KEYWORDS = {
    "exp1": {"breakout": ["breakout", "brick"], "pong": ["pong"], "pacman": ["pac-man", "pacman", "pac man"],
             "freeway": ["freeway", "frogger"]},
    "exp2": {"circle": ["circle", "disc", "disk", "round", "oval", "ring"], "square": ["square", "rectangle", "box"],
             "triangle": ["triangle", "pyramid", "wedge"]},
}
LABEL = {"exp1": "Game", "exp2": "Images"}
NEXT = r"(Description|Confidence|Example|Reasoning|Observations)"


def section(text, label):
    m = re.search(r"^[\s*#>-]*" + label + r"\b[\s*:]*(.*?)(?=^[\s*#>-]*" + NEXT + r"\b|\Z)", text, re.S | re.M | re.I)
    return m.group(1).strip() if m else ""


HYPHENS = dict.fromkeys(map(ord, "‐‑‒–—−"), "-")


def guess(sec, kw):
    low = sec.lower().translate(HYPHENS)
    hits = [(low.find(w), cls) for cls, words in kw.items() for w in words if low.find(w) >= 0]
    return min(hits)[1] if hits else None


def fill_claim(sec):
    low = sec.lower()
    hits = [(low.find(w), c) for c, words in {"filled": ["filled", "solid"], "outline": ["outline", "hollow", "ring", "pixel-thick", "pixel thick"]}.items() for w in words if low.find(w) >= 0]
    return min(hits)[1] if hits else None


def confidence(text):
    m = re.search(r"Confidence\W*?(\d{1,3})\s*%?", text, re.I)
    return int(m.group(1)) if m else None


def main(out_dir):
    rows = []
    for path in sorted(glob.glob(os.path.join(out_dir, "exp[12]_*_r*/result.json"))):
        name = os.path.basename(os.path.dirname(path))
        exp, truth, rep = name.split("_")
        d = json.load(open(path))
        text = d["result"]
        sec = section(text, LABEL[exp])
        g = guess(sec, KEYWORDS[exp])
        u = d["modelUsage"]["claude-opus-5-5"]
        rows.append({
            "run": name, "exp": exp, "true": truth, "repeat": rep, "guess": g, "correct": g == truth,
            "confidence": confidence(text), "fill": fill_claim(sec) if exp == "exp2" else None, "answer_line": sec.splitlines()[0][:200] if sec else "",
            "output_tokens": u["outputTokens"],
            "input_tokens": u["inputTokens"] + u["cacheReadInputTokens"] + u["cacheCreationInputTokens"],
            "list_cost_usd": round(d["total_cost_usd"], 3), "wall_s": round(d.get("duration_ms", 0) / 1000, 1),
        })
    json.dump(rows, open(os.path.join(out_dir, "scores_exp12.json"), "w"), indent=1)
    for r in rows:
        print(f"{r['run']:22} guess={str(r['guess']):9} correct={r['correct']!s:5} conf={r['confidence']} fill={r['fill']} out={r['output_tokens']} | {r['answer_line'][:90]}")
    for exp in ("exp1", "exp2"):
        sub = [r for r in rows if r["exp"] == exp]
        if sub:
            print(exp, "correct", sum(r["correct"] for r in sub), "/", len(sub))


if __name__ == "__main__":
    main(sys.argv[1])
