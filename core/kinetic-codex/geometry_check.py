#!/usr/bin/env python3
"""Calibration for meaning_geometry.py: do the groups mean anything, or is 0.7 just this model's baseline?
Adds unrelated CONTROL words, then compares. Read-only except for one output file."""
import sys, itertools
import numpy as np
sys.path.insert(0, "/home/wayfinder/projects/symbiogenesis/core/NAA/scripts")
sys.argv = [sys.argv[0]]
import meaning_geometry as mg

CONTROLS = ["bicycle", "tax return", "granite", "umbrella", "soup", "railway timetable", "sandpaper",
            "invoice", "parking lot", "wheat harvest", "plumbing", "bank holiday", "carpet",
            "hedge trimmer", "shipping container", "thermostat", "spreadsheet", "gravel",
            "bus schedule", "dishwasher", "wrench", "lawn mower", "postage stamp", "doorknob"]

terms = [c[2] for c in mg.CONCEPTS]
groups = [c[1] for c in mg.CONCEPTS]
V = mg.embed(terms + CONTROLS)
cv, ctl = V[: len(terms)], V[len(terms):]
S = cv @ cv.T
n = len(terms)
out = []

def mean_offdiag(M):
    k = M.shape[0]
    return (M.sum() - np.trace(M)) / (k * (k - 1))

base = mean_offdiag(ctl @ ctl.T)
out.append("1. BASELINE: mean cosine between %d UNRELATED words (bicycle, soup, gravel...) = %.3f" % (len(CONTROLS), base))
ia, ib = terms.index(mg.ANCHORS[0]), terms.index(mg.ANCHORS[1])
anchor = float(cv[ia] @ cv[ib])
allpairs = [float(S[i, j]) for i in range(n) for j in range(i + 1, n)]
pct = 100.0 * np.mean([anchor > p for p in allpairs])
out.append("2. cos(human intent, machine attention) = %.3f; higher than %.0f%% of all concept pairs" % (anchor, pct))
out.append("   controls vs the two anchors: mean cos = %.3f" % np.mean([float(ctl[k] @ cv[i]) for k in range(len(CONTROLS)) for i in (ia, ib)]))

out.append("3. NOISE words vs anchors, compared with CONTROL words vs anchors")
ni = [i for i, g in enumerate(groups) if g == "noise"]
for name, idx in (("human intent", ia), ("machine attention", ib)):
    nz = np.mean([float(cv[i] @ cv[idx]) for i in ni])
    ct = np.mean([float(ctl[k] @ cv[idx]) for k in range(len(CONTROLS))])
    out.append("   to %-18s noise=%.3f  control=%.3f  gap=%+.3f" % (name, nz, ct, nz - ct))

out.append("4. WITHIN-group vs BETWEEN-group mean cosine (does the labeling hold?)")
for g in sorted(set(groups)):
    ii = [i for i, x in enumerate(groups) if x == g]
    jj = [i for i, x in enumerate(groups) if x != g]
    within = np.mean([S[a, b] for a in ii for b in ii if a != b])
    between = np.mean([S[a, b] for a in ii for b in jj])
    out.append("   %-10s n=%2d within=%.3f between=%.3f gap=%+.3f" % (g, len(ii), within, between, within - between))

S2 = S.copy()
np.fill_diagonal(S2, -1)
nn = S2.argmax(axis=1)
purity = np.mean([groups[i] == groups[nn[i]] for i in range(n)])
sizes = [groups.count(g) for g in set(groups)]
chance = sum(s * (s - 1) for s in sizes) / (n * (n - 1))
out.append("5. NEAREST-NEIGHBOR PURITY: %.0f%% of terms have their nearest term in the same group (chance = %.0f%%)" % (100 * purity, 100 * chance))
bad = [(terms[i], terms[nn[i]]) for i in range(n) if groups[i] != groups[nn[i]]]
out.append("   cross-group nearest pairs (first 10): " + "; ".join("%s~%s" % b for b in bad[:10]))

out.append("6. FIVE strongest concept-concept pairs ACROSS different groups")
cross = sorted(((S[i, j], terms[i], terms[j]) for i in range(n) for j in range(i + 1, n) if groups[i] != groups[j]), reverse=True)[:5]
for s, a, b in cross:
    out.append("   %.3f  %s ~ %s" % (s, a, b))

text = "\n".join(out)
print(text)
open("/home/wayfinder/second-brain/geometry_check_20261004.txt", "w").write(text)
