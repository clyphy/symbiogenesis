#!/usr/bin/env python3
"""Read-only: compare old NAA trees to the canonical one, find references and live processes."""
import os, hashlib, subprocess, re, time

H = "/home/wayfinder/"
CANON = H + "projects/symbiogenesis/core/NAA"
OTHERS = [H + "NAA", H + "core/NAA", H + "Documents/GitHub/NAA",
          H + "Documents/GitHub/symbiogenesis/core/NAA",
          H + "projects/symbiogenesis/_legacy_archive/NAA_no_core_2026-09-22/NAA"]
SKIP = {"node_modules", ".git", "venv", "__pycache__", ".cache"}

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def scan(root):
    d = {}
    for dp, dn, fn in os.walk(root):
        dn[:] = [x for x in dn if x not in SKIP]
        for f in fn:
            p = os.path.join(dp, f)
            if os.path.islink(p):
                continue
            try:
                st = os.stat(p)
                if st.st_size > 100 * 1024 * 1024:
                    continue
                d[os.path.relpath(p, root)] = (st.st_size, sha(p), st.st_mtime)
            except OSError:
                pass
    return d

def ts(t):
    return time.strftime("%m-%d %H:%M", time.localtime(t))

canon = scan(CANON)
chash = {v[1] for v in canon.values()}
print("CANON %s: %d files" % (CANON.replace(H, "~/"), len(canon)))
for o in OTHERS:
    if not os.path.isdir(o):
        print("\n[absent] " + o.replace(H, "~/"))
        continue
    t = scan(o)
    ident, dup, differ, missing = 0, 0, [], []
    for rel, (sz, h, mt) in t.items():
        c = canon.get(rel)
        if c and c[1] == h:
            ident += 1
        elif c:
            differ.append((rel, sz, c[0], mt, c[2]))
        elif h in chash:
            dup += 1
        else:
            missing.append((rel, sz, mt))
    print("\n=== %s: %d files | identical %d | same content elsewhere in canon %d | DIFFER %d | MISSING from canon %d"
          % (o.replace(H, "~/"), len(t), ident, dup, len(differ), len(missing)))
    for rel, so, sc, mo, mc in sorted(differ, key=lambda x: -x[1])[:12]:
        print("  differ  %-55s other=%dB(%s) canon=%dB(%s) %s" % (rel[:55], so, ts(mo), sc, ts(mc),
              "OTHER NEWER" if mo > mc else "canon newer"))
    for rel, sz, mt in sorted(missing, key=lambda x: -x[1])[:15]:
        print("  missing %-55s %dB (%s)" % (rel[:55], sz, ts(mt)))

print("\n=== REFERENCES to non-canonical NAA paths (scripts, units, shell rc)")
pat = re.compile(r"(/home/wayfinder|~|\$HOME)/(NAA|core/NAA|Documents/GitHub/[\w./-]*NAA)")
roots = [CANON, H + ".config/systemd/user", H + ".config/autostart", H + ".config/fish"]
files = [H + n for n in (".bashrc", ".profile", ".bash_profile", ".zshrc", ".tmux.conf")]
for r in roots:
    for dp, dn, fn in os.walk(r):
        dn[:] = [x for x in dn if x not in SKIP]
        for f in fn:
            if f.endswith((".sh", ".py", ".service", ".timer", ".fish", ".conf", ".desktop")):
                files.append(os.path.join(dp, f))
hits = 0
for p in files:
    try:
        if os.path.getsize(p) > 1_000_000:
            continue
        for i, line in enumerate(open(p, errors="ignore"), 1):
            if pat.search(line) and "projects/symbiogenesis/core/NAA" not in line:
                print("  %s:%d: %s" % (p.replace(H, "~/"), i, line.strip()[:110]))
                hits += 1
                if hits >= 40:
                    raise StopIteration
    except StopIteration:
        break
    except OSError:
        pass
print("  (hits shown: %d)" % hits)

print("\n=== RUNNING processes mentioning NAA/whisper/weave/ollama")
ps = subprocess.run(["ps", "-eo", "pid,etime,args"], capture_output=True, text=True).stdout.splitlines()
for l in ps:
    if re.search(r"utonomy|whisper|weave|ollama|shift_resonance", l) and "compare_trees" not in l:
        print("  " + l[:150])

print("\n=== SCHEDULERS")
for p in (H + ".config/systemd/user", "/var/spool/cron", "/etc/cron.d"):
    try:
        print("  %s: %s" % (p.replace(H, "~/"), os.listdir(p)))
    except OSError as e:
        print("  %s: %s" % (p.replace(H, "~/"), e.strerror))
cr = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
print("  crontab -l rc=%d out=%r err=%r" % (cr.returncode, cr.stdout[:300], cr.stderr[:100]))
