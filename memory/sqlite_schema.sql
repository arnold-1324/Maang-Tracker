CREATE TABLE IF NOT EXISTS user_snapshot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,        -- github | leetcode
    key TEXT NOT NULL,           -- username or repo_name
    data JSON NOT NULL,
    created_at DATETIME DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS topic_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    metric_name TEXT,
    metric_value REAL,
    updated_at DATETIME DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS weakness_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL UNIQUE,
    score INTEGER DEFAULT 0,       -- higher => weaker
    last_seen DATETIME DEFAULT (datetime('now'))
);
