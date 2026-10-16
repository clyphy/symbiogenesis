#!/usr/bin/env python3
"""Read-only inventory of every SQLite database under the weave folders."""
import os, sqlite3, time

H = "/home/wayfinder/"
ROOTS = ["projects", "Projects", "NAA", "oceti-weave", "Oceti-Weave", "weave",
         "TheWeave", "ai-projects", "core", "data", "substrate", "vessels", "labs",
         ".weave", "Documents/GitHub"]
SKIP_DIRS = {"node_modules", "venv", ".git", "__pycache__", ".cache"}
seen, sql, other = set(), [], []

for r in ROOTS:
    root = H + r
    if not os.path.isdir(root):
        continue
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            if not f.endswith((".db", ".sqlite", ".sqlite3")):
                continue
            p = os.path.join(dp, f)
            rp = os.path.realpath(p)
            if rp in seen:
                continue
            seen.add(rp)
            try:
                st = os.stat(rp)
                with open(rp, "rb") as fh:
                    head = fh.read(16)
            except OSError:
                continue
            mt = time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime))
            if not head.startswith(b"SQLite format 3"):
                other.append((rp, st.st_size))
                continue
            tabs = []
            try:
                con = sqlite3.connect("file:%s?mode=ro" % rp, uri=True, timeout=2)
                names = [x[0] for x in con.execute(
                    "select name from sqlite_master where type='table' and name not like 'sqlite_%'")]
                for t in names[:30]:
                    try:
                        n = con.execute('select count(*) from "%s"' % t).fetchone()[0]
                    except Exception:
                        n = "err"
                    tabs.append("%s=%s" % (t, n))
                con.close()
            except Exception as e:
                tabs = ["OPEN-ERROR:" + str(e)[:50]]
            sql.append((rp, st.st_size, mt, tabs))

sql.sort(key=lambda x: x[0])
out = ["# SQLite inventory (read-only, generated %s)" % time.strftime("%Y-%m-%d %H:%M"), ""]
for p, sz, mt, tabs in sql:
    out.append("## %s" % p.replace(H, "~/"))
    out.append("%d bytes, modified %s" % (sz, mt))
    out.append("tables: " + (", ".join(tabs) if tabs else "(none)"))
    out.append("")
out.append("## Not SQLite (named .db but a different format)")
dirs = {}
for p, sz in other:
    d = os.path.dirname(p).replace(H, "~/")
    dirs[d] = dirs.get(d, 0) + 1
for d, n in sorted(dirs.items()):
    out.append("- %s: %d files" % (d, n))
out.append("")
out.append("TOTAL sqlite=%d  non-sqlite=%d" % (len(sql), len(other)))
text = "\n".join(out)
open(H + "second-brain/db_inventory.md", "w").write(text)
print(text)
