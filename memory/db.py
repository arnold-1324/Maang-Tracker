# memory/db.py
import sqlite3
import json
import os

DB_PATH = os.getenv("SQLITE_PATH", "./memory.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    sql = open(os.path.join(os.path.dirname(__file__), "sqlite_schema.sql")).read()
    cur.executescript(sql)
    conn.commit()
    conn.close()

def insert_snapshot(source: str, key: str, data: dict):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO user_snapshot (source, key, data) VALUES (?, ?, ?)",
                (source, key, json.dumps(data)))
    conn.commit()
    conn.close()

def get_latest_snapshot(source: str, key: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_snapshot WHERE source=? AND key=? ORDER BY created_at DESC LIMIT 1", (source, key))
    row = cur.fetchone()
    conn.close()
    return json.loads(row["data"]) if row else None

def upsert_weakness(topic: str, score: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO weakness_profile(topic, score) VALUES (?, ?) ON CONFLICT(topic) DO UPDATE SET score=?, last_seen=datetime('now')",
                (topic, score, score))
    conn.commit()
    conn.close()

def get_weaknesses(limit=20):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT topic, score, last_seen FROM weakness_profile ORDER BY score DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
