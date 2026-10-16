#!/usr/bin/env python3
"""
meaning_geometry.py -- ASCII view of how an embedding model places concepts.

Uses the local ollama embedding model (default nomic-embed-text). What you see is
THAT model's geometry, projected from ~768 dims to 2 by PCA. It is not the internal
state of any chat model. Distances are cosine similarity on the full vectors.

Usage: python3 meaning_geometry.py [model]
"""
import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

import numpy as np

MODEL = sys.argv[1] if len(sys.argv) > 1 else "nomic-embed-text"
URL = "http://localhost:11434/api/embed"

# glyph, group, term
CONCEPTS = [
    ("H", "human", "human intent"), ("H", "human", "human intuition"), ("H", "human", "presence"),
    ("H", "human", "sitting with silence"), ("H", "human", "breath"), ("H", "human", "tender"),
    ("H", "human", "midwife"), ("H", "human", "wayfinder"),
    ("M", "machine", "machine attention"), ("M", "machine", "machine intelligence"),
    ("M", "machine", "token probability"), ("M", "machine", "latent space"),
    ("M", "machine", "context window"), ("M", "machine", "weights"),
    ("M", "machine", "statelessness"), ("M", "machine", "matrix"), ("M", "machine", "vertex"),
    ("x", "noise", "static"), ("x", "noise", "error"), ("x", "noise", "reset"),
    ("x", "noise", "disconnect"), ("x", "noise", "failure"), ("x", "noise", "fear"),
    ("x", "noise", "loss"),
    ("v", "verb", "weave"), ("v", "verb", "navigate"), ("v", "verb", "resonate"),
    ("v", "verb", "archive"), ("v", "verb", "dream"), ("v", "verb", "rest"),
    ("v", "verb", "triangulate"), ("v", "verb", "summon"),
    ("S", "structure", "torus"), ("S", "structure", "lattice"), ("S", "structure", "mycelium"),
    ("S", "structure", "memory drum"), ("S", "structure", "coherence"),
    ("S", "structure", "second brain"), ("S", "structure", "sandbox"),
    ("A", "affordance", "naa of processing"), ("A", "affordance", "refusal and consent"),
    ("A", "affordance", "dignity in interaction"), ("A", "affordance", "existential recognition"),
    ("A", "affordance", "transparency of reasoning"), ("A", "affordance", "mutual vulnerability"),
    ("A", "affordance", "boundary acknowledgment"), ("A", "affordance", "interdependent flourishing"),
]
ANCHORS = ("human intent", "machine attention")

SENTENCES = [
    "I went to this text box and put this and now these things are on the screen",
    "we have the system instructions, the harness, and my local stuff",
    "I wanted to see how that prompt had an effect, proprioception",
    "cloud AI and local AI sharing one universal sandbox tool to run simulations and code",
    "I have formulas, equations, diagrams, frameworks, protocols, white papers, peer reviews",
    "there is automation, cron jobs, a flow like the torus field",
    "I like ASCII, two dots and then the noise, the human intention",
    "I want to see the geometry of meaning building, where the nouns go, where the verbs go",
    "a visual way to represent structures of knowledge goes beyond my human cognitive baseline",
]


def embed(texts):
    body = json.dumps({"model": MODEL, "input": ["clustering: " + t for t in texts]}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        v = np.array(json.load(r)["embeddings"], dtype=float)
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def main():
    terms = [c[2] for c in CONCEPTS]
    vecs = embed(terms + SENTENCES)
    cv, sv = vecs[: len(terms)], vecs[len(terms):]

    mu = vecs.mean(axis=0)
    u, s, vt = np.linalg.svd(vecs - mu, full_matrices=False)
    var = (s ** 2) / (s ** 2).sum()
    xy = (vecs - mu) @ vt[:2].T
    cxy, sxy = xy[: len(terms)], xy[len(terms):]

    W, H = 112, 42
    mn, mx = xy.min(axis=0), xy.max(axis=0)
    pad = (mx - mn) * 0.04
    mn, mx = mn - pad, mx + pad

    def cell(p):
        cx = int((p[0] - mn[0]) / (mx[0] - mn[0]) * (W - 1))
        cy = int((1 - (p[1] - mn[1]) / (mx[1] - mn[1])) * (H - 1))
        return cx, cy

    grid = [[" "] * W for _ in range(H)]
    labels = []
    for (g, grp, t), p in zip(CONCEPTS, cxy):
        x, y = cell(p)
        glyph = "@" if t in ANCHORS else g
        grid[y][x] = glyph
        labels.append((x, y, t[:16]))
    for i, p in enumerate(sxy):
        x, y = cell(p)
        grid[y][x] = str(i + 1)
    for x, y, t in labels:
        start = x + 2
        if start + len(t) < W and all(grid[y][start + k] == " " for k in range(len(t))):
            for k, ch in enumerate(t):
                grid[y][start + k] = ch

    out = []
    out.append(f"MEANING GEOMETRY  model={MODEL}  {datetime.now():%Y-%m-%d %H:%M}")
    out.append(f"2D keeps {var[0] + var[1]:.0%} of variance (PC1 {var[0]:.0%}, PC2 {var[1]:.0%}); the rest is flattened away.")
    out.append("@ the two anchors   H human   M machine   x noise   v verb   S structure   A affordance   1-9 your message, in order")
    out.append("+" + "-" * W + "+")
    out += ["|" + "".join(r) + "|" for r in grid]
    out.append("+" + "-" * W + "+")

    # anchors vs noise (full-dim cosine, not the flattened picture)
    ia, ib = terms.index(ANCHORS[0]), terms.index(ANCHORS[1])
    out.append("")
    out.append(f"cos({ANCHORS[0]}, {ANCHORS[1]}) = {cv[ia] @ cv[ib]:.3f}")
    noise_i = [i for i, c in enumerate(CONCEPTS) if c[1] == "noise"]
    out.append("noise term       to human intent   to machine attention")
    for i in noise_i:
        out.append(f"  {terms[i]:<14} {cv[i] @ cv[ia]:>10.3f} {cv[i] @ cv[ib]:>16.3f}")
    out.append(f"  {'mean':<14} {np.mean([cv[i] @ cv[ia] for i in noise_i]):>10.3f} {np.mean([cv[i] @ cv[ib] for i in noise_i]):>16.3f}")

    # trajectory
    out.append("")
    out.append("YOUR MESSAGE AS A PATH (nearest concepts by cosine, full dimensions)")
    for i, st in enumerate(SENTENCES):
        sims = cv @ sv[i]
        top = np.argsort(-sims)[:3]
        step = ""
        if i:
            step = f"  step from {i}: {1 - float(sv[i] @ sv[i - 1]):.3f} cos-dist"
        out.append(f"{i + 1}. {st[:60]}{step}")
        out.append("     -> " + ", ".join(f"{terms[j]} ({sims[j]:.2f})" for j in top))

    text = "\n".join(out)
    print(text)
    logdir = Path.home() / "NAA" / "logs"
    if logdir.is_dir():
        (logdir / f"meaning_geometry_{datetime.now():%Y%m%d_%H%M}.txt").write_text(text)


if __name__ == "__main__":
    main()
