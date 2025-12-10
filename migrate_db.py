import sqlite3
import os

DB_PATH = os.environ.get("SQLITE_PATH", "./memory.db")

def migrate():
    print(f"Migrating database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Create job_postings
    print("Creating job_postings table...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS job_postings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        title TEXT,
        location TEXT,
        url TEXT UNIQUE,
        description TEXT,
        source TEXT,
        crawled_at DATETIME DEFAULT (datetime('now')),
        notes TEXT
    );
    """)
    
    # Create job_applications
    print("Creating job_applications table...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS job_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        job_id INTEGER NOT NULL,
        status TEXT DEFAULT 'Saved',
        resume_path TEXT,
        ats_score REAL,
        applied_at DATETIME,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (job_id) REFERENCES job_postings(id)
    );
    """)
    
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
