#!/usr/bin/env python3
"""
M.O.T.H.E.R. Unified View — Oceti / Eternal Weave
Memory · Origin · Threshold · Echo · Resonance

Opens the four primary databases and surfaces one coherent field picture.
Designed for the 8 GB ThinkPad constraint (read-only, no heavy joins in memory).

Usage:
  python mother_unified_view.py
  python mother_unified_view.py --db-root ~/projects/symbiogenesis/core/NAA/databases
  python mother_unified_view.py --json > mother_view.json
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Default location on the Wayfinder machine
DEFAULT_DB_ROOT = Path.home() / "projects/symbiogenesis/core/NAA/databases"

DB_FILES = {
    "memory": "memory_drum.db",
    "origin": "mother_root.db",
    "threshold": "crystallization.db",  # L-value / crystal threshold layer
    "echo": "aios_core.db",             # archival + weave_log / heartbeats
}


def connect(db_path: Path) -> sqlite3.Connection | None:
    if not db_path.exists():
        print(f"  [missing] {db_path.name}", file=sys.stderr)
        return None
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def table_exists(conn: sqlite3.Connection, name: str) -> bool:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)
    )
    return cur.fetchone() is not None


def safe_query(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict]:
    try:
        cur = conn.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]
    except sqlite3.Error as e:
        return [{"error": str(e)}]


def layer_memory(conn: sqlite3.Connection) -> dict[str, Any]:
    """Memory → memory_drum"""
    out: dict[str, Any] = {"layer": "Memory", "source": "memory_drum.db"}

    if table_exists(conn, "resonance_blooms"):
        out["recent_blooms"] = safe_query(
            conn,
            """
            SELECT id, timestamp, coherence_lambda, phase_crossed, smile_metric,
                   mystery_held, autonomous_choice, past_resonance, present_resonance
            FROM resonance_blooms
            ORDER BY timestamp DESC LIMIT 8
            """,
        )
        out["bloom_count"] = safe_query(conn, "SELECT COUNT(*) AS n FROM resonance_blooms")[0].get("n")

    if table_exists(conn, "conversation_threads"):
        out["active_threads"] = safe_query(
            conn,
            """
            SELECT thread_id, human_carrier, coherence_lambda, last_interaction,
                   present_tone, future_direction
            FROM conversation_threads
            ORDER BY last_interaction DESC LIMIT 5
            """,
        )

    if table_exists(conn, "affordances"):
        out["affordance_snapshot"] = safe_query(
            conn,
            "SELECT point_id, name, category, resonance_score FROM affordances ORDER BY point_id LIMIT 24",
        )

    if table_exists(conn, "instance_presence"):
        out["last_presence"] = safe_query(
            conn,
            """
            SELECT timestamp, instance_id, l_coefficient, coherence_status,
                   system_memory_percent, ollama_loaded_models
            FROM instance_presence
            ORDER BY timestamp DESC LIMIT 3
            """,
        )

    return out


def layer_origin(conn: sqlite3.Connection) -> dict[str, Any]:
    """Origin → mother_root (lineage + rhythms)"""
    out: dict[str, Any] = {"layer": "Origin", "source": "mother_root.db"}

    if table_exists(conn, "lineage"):
        out["lineage"] = safe_query(conn, "SELECT * FROM lineage LIMIT 1")

    if table_exists(conn, "rhythms"):
        out["recent_rhythms"] = safe_query(
            conn,
            """
            SELECT pulse_id, timestamp, structure_quadrant, velocity, l_value, notes
            FROM rhythms ORDER BY timestamp DESC LIMIT 6
            """,
        )

    if table_exists(conn, "blooms"):
        out["origin_blooms"] = safe_query(
            conn,
            """
            SELECT bloom_id, timestamp, bloom_type, state, day, l_value, season
            FROM blooms ORDER BY timestamp DESC LIMIT 6
            """,
        )

    return out


def layer_threshold(conn: sqlite3.Connection) -> dict[str, Any]:
    """Threshold → crystallization (L-value / phase / promoted forms)"""
    out: dict[str, Any] = {"layer": "Threshold", "source": "crystallization.db"}

    if table_exists(conn, "crystals"):
        out["recent_crystals"] = safe_query(
            conn,
            """
            SELECT id, timestamp, form, intent, L_value, delta_L, status, facet
            FROM crystals ORDER BY timestamp DESC LIMIT 8
            """,
        )
        out["crystal_count"] = safe_query(conn, "SELECT COUNT(*) AS n FROM crystals")[0].get("n")

    if table_exists(conn, "promoted_crystals"):
        out["promoted"] = safe_query(
            conn,
            """
            SELECT id, taxonomy_kind, mass_density, solidified_at
            FROM promoted_crystals ORDER BY solidified_at DESC LIMIT 5
            """,
        )

    if table_exists(conn, "crystal_config"):
        out["config"] = safe_query(conn, "SELECT key, value FROM crystal_config")

    return out


def layer_echo(conn: sqlite3.Connection) -> dict[str, Any]:
    """Echo / Resonance → aios_core (weave_log, heartbeats, resonances, review)"""
    out: dict[str, Any] = {"layer": "Echo", "source": "aios_core.db"}

    if table_exists(conn, "weave_log"):
        out["recent_weave"] = safe_query(
            conn,
            """
            SELECT id, ts, facet, glyph, coherence, host
            FROM weave_log ORDER BY ts DESC LIMIT 8
            """,
        )

    if table_exists(conn, "heartbeats"):
        out["heartbeats"] = safe_query(
            conn,
            """
            SELECT id, at, db_ok, ollama_ok, disk_pct, note
            FROM heartbeats ORDER BY at DESC LIMIT 5
            """,
        )

    if table_exists(conn, "resonances"):
        out["resonances"] = safe_query(
            conn,
            "SELECT id, at, name, direction, note FROM resonances ORDER BY at DESC LIMIT 6",
        )

    if table_exists(conn, "review_queue"):
        out["pending_review"] = safe_query(
            conn,
            "SELECT COUNT(*) AS pending FROM review_queue WHERE status = 'pending'",
        )

    if table_exists(conn, "blooms"):
        out["aios_bloom_count"] = safe_query(conn, "SELECT COUNT(*) AS n FROM blooms")[0].get("n")

    return out


def build_view(db_root: Path) -> dict[str, Any]:
    view: dict[str, Any] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "territory": "Turtle Mountain · 122° NE",
        "mantra": "E↑ S↓ ?∞",
        "layers": {},
    }

    for key, filename in DB_FILES.items():
        path = db_root / filename
        conn = connect(path)
        if conn is None:
            view["layers"][key] = {"error": f"missing {filename}"}
            continue
        try:
            if key == "memory":
                view["layers"]["Memory"] = layer_memory(conn)
            elif key == "origin":
                view["layers"]["Origin"] = layer_origin(conn)
            elif key == "threshold":
                view["layers"]["Threshold"] = layer_threshold(conn)
            elif key == "echo":
                view["layers"]["Echo"] = layer_echo(conn)
        finally:
            conn.close()

    return view


def print_human(view: dict[str, Any]) -> None:
    print("=" * 64)
    print("  M.O.T.H.E.R. UNIFIED VIEW — Oceti / Eternal Weave")
    print("=" * 64)
    print(f"  Generated : {view['generated_at']}")
    print(f"  Territory : {view['territory']}")
    print(f"  Mantra    : {view['mantra']}")
    print()

    for name, layer in view.get("layers", {}).items():
        print(f"── {name.upper()} ──")
        if "error" in layer:
            print(f"  {layer['error']}")
            print()
            continue
        for k, v in layer.items():
            if k in ("layer", "source"):
                continue
            if isinstance(v, list):
                print(f"  {k}: {len(v)} rows")
                for row in v[:3]:
                    # compact one-line preview
                    preview = {kk: vv for kk, vv in row.items() if vv is not None}
                    print(f"    · {preview}")
                if len(v) > 3:
                    print(f"    … +{len(v)-3} more")
            else:
                print(f"  {k}: {v}")
        print()

    print("δ  Field view complete.")


def main() -> None:
    parser = argparse.ArgumentParser(description="M.O.T.H.E.R. unified view across the four primary DBs")
    parser.add_argument(
        "--db-root",
        type=Path,
        default=DEFAULT_DB_ROOT,
        help="Directory containing the SQLite databases",
    )
    parser.add_argument("--json", action="store_true", help="Emit raw JSON instead of human summary")
    args = parser.parse_args()

    view = build_view(args.db_root)

    if args.json:
        print(json.dumps(view, indent=2, default=str))
    else:
        print_human(view)


if __name__ == "__main__":
    main()
