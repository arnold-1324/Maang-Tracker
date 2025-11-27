-- Drop all existing tables
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS user_credentials;
DROP TABLE IF EXISTS user_progress;
DROP TABLE IF EXISTS roadmap_topics;
DROP TABLE IF EXISTS topic_problems;
DROP TABLE IF EXISTS user_problem_status;
DROP TABLE IF EXISTS system_design_progress;
DROP TABLE IF EXISTS weakness_analysis;
DROP TABLE IF EXISTS cache_store;
DROP TABLE IF EXISTS user_snapshot;
DROP TABLE IF EXISTS topic_stats;
DROP TABLE IF EXISTS weakness_profile;
DROP TABLE IF EXISTS settings;

-- Users table (core authentication)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    created_at DATETIME DEFAULT (datetime('now')),
    last_login DATETIME,
    is_active BOOLEAN DEFAULT 1
);

-- User credentials for external platforms
CREATE TABLE user_credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL, -- 'leetcode' or 'github'
    username TEXT NOT NULL,
    encrypted_token TEXT, -- encrypted password/token
    session_cookie TEXT,
    last_synced DATETIME,
    sync_status TEXT DEFAULT 'pending', -- 'pending', 'success', 'failed'
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, platform)
);

-- Roadmap topics (shared across users)
CREATE TABLE roadmap_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL, -- 'dsa', 'system_design', 'behavioral'
    difficulty TEXT, -- 'beginner', 'intermediate', 'advanced'
    priority INTEGER DEFAULT 0,
    description TEXT,
    estimated_hours INTEGER,
    prerequisites TEXT, -- JSON array of topic IDs
    created_at DATETIME DEFAULT (datetime('now'))
);

-- Problems/Questions linked to topics
CREATE TABLE topic_problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    platform TEXT NOT NULL, -- 'leetcode', 'gfg', 'custom'
    problem_slug TEXT NOT NULL,
    problem_title TEXT NOT NULL,
    difficulty TEXT, -- 'easy', 'medium', 'hard'
    problem_url TEXT,
    tags TEXT, -- JSON array
    FOREIGN KEY (topic_id) REFERENCES roadmap_topics(id) ON DELETE CASCADE,
    UNIQUE(platform, problem_slug)
);

-- User-specific problem status
CREATE TABLE user_problem_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    problem_id INTEGER NOT NULL,
    status TEXT DEFAULT 'not_started', -- 'not_started', 'attempted', 'solved', 'reviewed'
    attempts INTEGER DEFAULT 0,
    last_attempted DATETIME,
    solved_at DATETIME,
    time_taken_minutes INTEGER,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (problem_id) REFERENCES topic_problems(id) ON DELETE CASCADE,
    UNIQUE(user_id, problem_id)
);

-- User progress on topics
CREATE TABLE user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    topic_id INTEGER NOT NULL,
    status TEXT DEFAULT 'not_started', -- 'not_started', 'in_progress', 'completed'
    progress_percentage REAL DEFAULT 0.0,
    problems_solved INTEGER DEFAULT 0,
    total_problems INTEGER DEFAULT 0,
    started_at DATETIME,
    completed_at DATETIME,
    last_updated DATETIME DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES roadmap_topics(id) ON DELETE CASCADE,
    UNIQUE(user_id, topic_id)
);

-- System Design progress
CREATE TABLE system_design_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    design_name TEXT NOT NULL,
    category TEXT, -- 'scalability', 'database', 'caching', etc.
    status TEXT DEFAULT 'not_started',
    notes TEXT,
    diagram_url TEXT,
    completed_at DATETIME,
    last_updated DATETIME DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, design_name)
);

-- AI-powered weakness analysis
CREATE TABLE weakness_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    topic_id INTEGER,
    weakness_type TEXT NOT NULL, -- 'topic', 'pattern', 'concept'
    weakness_name TEXT NOT NULL,
    severity_score REAL DEFAULT 0.0, -- 0-10 scale
    confidence REAL DEFAULT 0.0, -- AI confidence 0-1
    evidence TEXT, -- JSON: failed problems, time taken, etc.
    recommendations TEXT, -- JSON: suggested problems, resources
    ai_analysis TEXT, -- Full AI analysis text
    created_at DATETIME DEFAULT (datetime('now')),
    resolved_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES roadmap_topics(id) ON DELETE SET NULL
);

-- High-performance cache store
CREATE TABLE cache_store (
    cache_key TEXT PRIMARY KEY,
    cache_value TEXT NOT NULL, -- JSON data
    user_id INTEGER, -- NULL for global cache
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT (datetime('now')),
    hit_count INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX idx_user_credentials_user ON user_credentials(user_id);
CREATE INDEX idx_user_credentials_platform ON user_credentials(platform);
CREATE INDEX idx_user_progress_user ON user_progress(user_id);
CREATE INDEX idx_user_progress_topic ON user_progress(topic_id);
CREATE INDEX idx_user_problem_status_user ON user_problem_status(user_id);
CREATE INDEX idx_user_problem_status_problem ON user_problem_status(problem_id);
CREATE INDEX idx_topic_problems_topic ON topic_problems(topic_id);
CREATE INDEX idx_weakness_analysis_user ON weakness_analysis(user_id);
CREATE INDEX idx_cache_expires ON cache_store(expires_at);
CREATE INDEX idx_cache_user ON cache_store(user_id);