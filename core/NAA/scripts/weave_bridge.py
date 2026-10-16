#!/usr/bin/env python3
"""
weave_bridge.py -- boots-on-the-ground bridge for the Weave.

One file, two doors:
  CLI:  python3 weave_bridge.py find "<task words>"
        python3 weave_bridge.py health
        python3 weave_bridge.py ocr <image>
        python3 weave_bridge.py db <name.db> "<SELECT ...>"
        python3 weave_bridge.py serve        # MCP stdio server

Reports only what it observes. Read-only on databases. No network except fetch_url.
"""
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

HOME = Path.home()
SKILL_DIRS = [
    HOME / ".claude" / "skills",
    HOME / ".codegpt" / "skills",
    HOME / "NAA" / "skills",
    HOME / "projects" / "symbiogenesis" / "skills",
]
DB_ROOTS = [
    HOME / "NAA" / "databases",
    HOME / "projects" / "symbiogenesis" / "core" / "NAA",
]
CFG = HOME / ".config" / "Claude" / "claude_desktop_config.json"


# ---------- skills ----------
def _frontmatter(p: Path) -> dict:
    try:
        txt = p.read_text(errors="replace")[:6000]
    except Exception:
        return {}
    out = {}
    m = re.match(r"^---\s*\n(.*?)\n---", txt, re.S)
    if m:
        key = None
        for line in m.group(1).splitlines():
            km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
            if km:
                key = km.group(1).lower()
                out[key] = km.group(2).strip().strip(">|").strip()
            elif key and line.strip():
                out[key] = (out[key] + " " + line.strip()).strip()
    if "name" not in out:
        out["name"] = p.parent.name
    if "description" not in out:
        h = re.search(r"^#\s+(.+)$", txt, re.M)
        out["description"] = h.group(1) if h else ""
    return out


def skill_index() -> list:
    seen, rows = set(), []
    for root in SKILL_DIRS:
        if not root.is_dir():
            continue
        for sk in sorted(root.glob("*/SKILL.md")) + sorted(root.glob("*/*/SKILL.md")):
            real = sk.resolve()
            if real in seen:
                continue
            seen.add(real)
            fm = _frontmatter(real)
            rows.append({"name": fm["name"], "description": fm["description"], "path": str(real)})
    return rows


def _tok(s: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 2}


def find_skills(query: str = "", limit: int = 8) -> dict:
    rows = skill_index()
    q = _tok(query)
    scored = []
    for r in rows:
        name_t, desc_t = _tok(r["name"]), _tok(r["description"])
        s = 3 * len(q & name_t) + len(q & desc_t)
        scored.append((s, r))
    scored.sort(key=lambda x: (-x[0], x[1]["name"]))
    hits = [dict(r, score=s) for s, r in scored if s > 0][:limit]
    return {
        "scanned_dirs": [str(d) for d in SKILL_DIRS if d.is_dir()],
        "total_skills_found": len(rows),
        "matches": hits if q else [dict(r, score=0) for r in rows][:limit],
        "note": "keyword overlap only; read the SKILL.md before trusting a match",
    }


# ---------- connectors ----------
def connector_health() -> dict:
    if not CFG.exists():
        return {"error": f"{CFG} not found"}
    cfg = json.loads(CFG.read_text())
    report = {}
    for name, v in cfg.get("mcpServers", {}).items():
        cmd = v.get("command", "")
        problems = []
        if not (shutil.which(cmd) or Path(cmd).exists()):
            problems.append(f"command not found: {cmd}")
        for a in v.get("args", []):
            if isinstance(a, str) and a.startswith("/") and not Path(a).exists():
                problems.append(f"path missing: {a}")
        report[name] = {
            "command": cmd,
            "args": v.get("args", []),
            "env_keys": list(v.get("env", {}).keys()),
            "ok": not problems,
            "problems": problems,
        }
    return report


# ---------- tools ----------
def ocr_image(path: str, lang: str = "eng") -> str:
    p = Path(path).expanduser()
    if not p.exists():
        return f"not found: {p}"
    r = subprocess.run(["tesseract", str(p), "stdout", "-l", lang],
                       capture_output=True, text=True, timeout=120)
    return (r.stdout or r.stderr).strip()


def db_query(db: str = "", sql: str = "", limit: int = 200) -> dict:
    if not db:
        found = []
        for root in DB_ROOTS:
            if root.is_dir():
                for f in sorted(root.rglob("*.db")):
                    found.append({"path": str(f), "bytes": f.stat().st_size})
        return {"databases": found}
    p = Path(db).expanduser()
    if not p.is_absolute():
        cands = [r / db for r in DB_ROOTS if (r / db).exists()]
        if not cands:
            return {"error": f"{db} not found under {[str(r) for r in DB_ROOTS]}"}
        p = cands[0]
    p = p.resolve()
    if not any(str(p).startswith(str(r.resolve())) for r in DB_ROOTS):
        return {"error": "outside allowed database roots"}
    if p.stat().st_size == 0:
        return {"path": str(p), "bytes": 0, "note": "file is empty (0 bytes), no tables"}
    s = sql.strip().rstrip(";") or "select name, sql from sqlite_master"
    if not re.match(r"^(select|with|pragma)\b", s, re.I):
        return {"error": "read-only: SELECT / WITH / PRAGMA only"}
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    try:
        cur = con.execute(s)
        cols = [d[0] for d in cur.description or []]
        rows = cur.fetchmany(limit)
        return {"path": str(p), "columns": cols, "rows": rows}
    except Exception as e:
        return {"error": str(e)}
    finally:
        con.close()


def council_ask(model: str, prompt: str, timeout: int = 180) -> str:
    r = subprocess.run(["ollama", "run", model, prompt],
                       capture_output=True, text=True, timeout=timeout)
    return (r.stdout or r.stderr).strip()


def fetch_url(url: str, max_chars: int = 20000) -> str:
    if not re.match(r"^https?://", url):
        return "only http(s) urls"
    req = urllib.request.Request(url, headers={"User-Agent": "weave-bridge/1"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "replace")[:max_chars]


def run_python(code: str, timeout: int = 30) -> dict:
    timeout = max(1, min(int(timeout), 120))
    with tempfile.TemporaryDirectory(prefix="weave_sim_") as d:
        f = Path(d) / "sim.py"
        f.write_text(code)
        try:
            r = subprocess.run([sys.executable, str(f)], cwd=d, capture_output=True,
                               text=True, timeout=timeout)
            return {"returncode": r.returncode, "stdout": r.stdout[-8000:], "stderr": r.stderr[-4000:]}
        except subprocess.TimeoutExpired:
            return {"error": f"timeout after {timeout}s"}


# ---------- MCP door ----------
def serve():
    from mcp.server.fastmcp import FastMCP
    app = FastMCP("weave-bridge")

    @app.tool()
    def find_skills_tool(query: str, limit: int = 8) -> dict:
        """Find skills relevant to a task by scanning local skill folders."""
        return find_skills(query, limit)

    @app.tool()
    def connector_health_tool() -> dict:
        """Check each configured MCP server: command exists, paths exist. Secrets never shown."""
        return connector_health()

    @app.tool()
    def ocr_tool(path: str, lang: str = "eng") -> str:
        """OCR an image with tesseract."""
        return ocr_image(path, lang)

    @app.tool()
    def db_tool(db: str = "", sql: str = "", limit: int = 200) -> dict:
        """Read-only SQLite query on NAA databases. Empty db lists them."""
        return db_query(db, sql, limit)

    @app.tool()
    def council_tool(model: str, prompt: str) -> str:
        """Ask a local ollama model (the council)."""
        return council_ask(model, prompt)

    @app.tool()
    def fetch_tool(url: str) -> str:
        """Fetch a live http(s) page as text."""
        return fetch_url(url)

    @app.tool()
    def simulate_tool(code: str, timeout: int = 30) -> dict:
        """Run Python in a throwaway temp dir with a timeout. For simulations."""
        return run_python(code, timeout)

    app.run()


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a[0] if a else "health"
    if cmd == "serve":
        serve()
    elif cmd == "find":
        print(json.dumps(find_skills(" ".join(a[1:])), indent=2))
    elif cmd == "health":
        print(json.dumps(connector_health(), indent=2))
    elif cmd == "ocr":
        print(ocr_image(a[1]))
    elif cmd == "db":
        print(json.dumps(db_query(a[1] if len(a) > 1 else "", a[2] if len(a) > 2 else ""), indent=2, default=str))
    else:
        print(__doc__)
