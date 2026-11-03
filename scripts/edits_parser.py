"""Parse the exp5 "edits" language into MLP weights.

Spec source is the exp5 prompt. Only the last ```edits block counts. One statement per line.
'#' starts a comment. Lists may continue over lines. Ops are =, *=, +=, -=.
Unreadable statements are skipped and logged. Whitespace inside lists is tolerated.
"""
import ast
import json
import re
import sys

import numpy as np

SHAPES = {"W1": (600, 32), "b1": (32,), "W2": (32, 32), "b2": (32,), "W3": (32, 6), "b3": (6,)}
NPZ_KEYS = {
    "W1": "actor/dense1/kernel", "b1": "actor/dense1/bias",
    "W2": "actor/dense2/kernel", "b2": "actor/dense2/bias",
    "W3": "actor/logits/kernel", "b3": "actor/logits/bias",
}
STMT = re.compile(r"^\s*(W1|b1|W2|b2|W3|b3)\s*\[([^\]]*)\]\s*(\*=|\+=|-=|=)\s*(.+?)\s*$", re.S)
INT = re.compile(r"^\s*-?\d+\s*$")


def last_edits_block(text):
    starts = [m.end() for m in re.finditer(r"^[ \t]*```[ \t]*edits[ \t]*$", text, re.M)]
    if not starts:
        return None, False
    body = text[starts[-1]:]
    end = re.search(r"^[ \t]*```[ \t]*$", body, re.M)
    if end is None:
        return body, True
    return body[: end.start()], False


def statements(block):
    out, buf, depth = [], "", 0
    for raw in block.splitlines():
        line = raw.split("#", 1)[0]
        if not line.strip() and depth == 0:
            continue
        buf = (buf + " " + line) if buf else line
        depth = buf.count("[") - buf.count("]")
        if depth > 0 or buf.rstrip().endswith((",", "\\")):
            buf = buf.rstrip().rstrip("\\")
            continue
        out.append(buf.strip())
        buf, depth = "", 0
    if buf.strip():
        out.append(buf.strip())
    return out


def parse_index_part(p):
    p = p.strip()
    if INT.match(p):
        return int(p)
    if ":" in p:
        bits = p.split(":")
        if len(bits) > 3:
            raise ValueError("bad slice " + p)
        vals = []
        for b in bits:
            b = b.strip()
            if b == "":
                vals.append(None)
            elif INT.match(b):
                vals.append(int(b))
            else:
                raise ValueError("bad slice part " + b)
        return slice(*vals)
    raise ValueError("bad index " + p)


def check_numbers(v):
    a = np.asarray(v, dtype=float)
    if not np.all(np.isfinite(a)) or np.any(np.abs(a) > 1e6):
        raise ValueError("value out of range")
    return a


def apply_block(block):
    W = {k: np.zeros(s, dtype=np.float32) for k, s in SHAPES.items()}
    report = {"statements": 0, "applied": 0, "entries_written": 0, "errors": [], "reshaped": 0}
    for st in statements(block):
        report["statements"] += 1
        try:
            m = STMT.match(st)
            if not m:
                raise ValueError("not a statement")
            name, idx, op, val = m.groups()
            parts = [parse_index_part(p) for p in idx.split(",")]
            if len(parts) != len(SHAPES[name]):
                raise ValueError("index rank mismatch")
            key = tuple(parts) if len(parts) > 1 else parts[0]
            sel = W[name][key]
            sel_shape = np.shape(sel)
            v = check_numbers(ast.literal_eval(val.strip()))
            if v.ndim > 0 and v.shape != sel_shape:
                if v.size == int(np.prod(sel_shape)):
                    v = v.reshape(sel_shape)
                    report["reshaped"] += 1
                else:
                    raise ValueError(f"shape {v.shape} vs selection {sel_shape}")
            if op == "=":
                W[name][key] = v
            elif op == "*=":
                W[name][key] = sel * v
            elif op == "+=":
                W[name][key] = sel + v
            elif op == "-=":
                W[name][key] = sel - v
            report["applied"] += 1
            report["entries_written"] += int(np.prod(sel_shape)) if sel_shape else 1
        except Exception as e:  # skip unreadable statement, keep going
            report["errors"].append({"statement": st[:200], "error": str(e)[:200]})
    report["nonzero"] = {k: int((W[k] != 0).sum()) for k in W}
    report["nonzero_total"] = sum(report["nonzero"].values())
    report["max_abs"] = {k: float(np.abs(W[k]).max()) for k in W}
    return W, report


def main():
    reply_path, out_npz, out_report = sys.argv[1:4]
    text = open(reply_path, encoding="utf-8").read()
    block, cut = last_edits_block(text)
    if block is None:
        W = {k: np.zeros(s, dtype=np.float32) for k, s in SHAPES.items()}
        report = {"block": False, "statements": 0, "applied": 0, "errors": [], "cut_off": False}
    else:
        W, report = apply_block(block)
        report["block"] = True
        report["cut_off"] = cut
    np.savez(out_npz, **{NPZ_KEYS[k]: W[k] for k in W})
    json.dump(report, open(out_report, "w"), indent=1)
    print(json.dumps({k: report[k] for k in report if k != "errors"}), "errors:", len(report["errors"]))


if __name__ == "__main__":
    main()
