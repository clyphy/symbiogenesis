CREATE TABLE IF NOT EXISTS blooms (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  content TEXT,
  score REAL DEFAULT 1.0,
  created_at TEXT DEFAULT (datetime('now')),
  tags TEXT,
  affordances TEXT,
  size INTEGER DEFAULT 0,
  frequency_hz REAL DEFAULT 432.0,
  affordance_id INTEGER,
  timestamp TEXT,
  pattern TEXT,
  L_value REAL,
  coherence REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS resonance_instances (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  instance_node TEXT,
  numerator_attention REAL,
  denominator_noise REAL,
  somatic_anchor TEXT,
  ts TEXT DEFAULT (datetime('now','localtime'))
);
