# memory/db.py
import sqlite3
import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
import bcrypt

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

# ===== CACHING LAYER =====
class CacheManager:
    """High-performance caching with TTL support"""
    
    @staticmethod
    def get(key: str, user_id: Optional[int] = None) -> Optional[Any]:
        """Get cached value if not expired"""
        conn = get_conn()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT cache_value, expires_at FROM cache_store 
            WHERE cache_key = ? AND (user_id = ? OR user_id IS NULL)
            AND expires_at > datetime('now')
        """, (key, user_id))
        
        row = cur.fetchone()
        if row:
            # Update hit count
            cur.execute("UPDATE cache_store SET hit_count = hit_count + 1 WHERE cache_key = ?", (key,))
            conn.commit()
            conn.close()
            return json.loads(row['cache_value'])
        
        conn.close()
        return None
    
    @staticmethod
    def set(key: str, value: Any, ttl_seconds: int = 3600, user_id: Optional[int] = None):
        """Set cache with TTL"""
        conn = get_conn()
        cur = conn.cursor()
        
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        
        cur.execute("""
            INSERT OR REPLACE INTO cache_store (cache_key, cache_value, user_id, expires_at)
            VALUES (?, ?, ?, ?)
        """, (key, json.dumps(value), user_id, expires_at))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def invalidate(key: str, user_id: Optional[int] = None):
        """Invalidate specific cache entry"""
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM cache_store WHERE cache_key = ? AND (user_id = ? OR user_id IS NULL)", (key, user_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def invalidate_user(user_id: int):
        """Invalidate all cache for a user"""
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM cache_store WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    
    @staticmethod
    def cleanup_expired():
        """Remove expired cache entries"""
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM cache_store WHERE expires_at < datetime('now')")
        conn.commit()
        conn.close()

# ===== USER MANAGEMENT =====
def create_user(username: str, email: str, password: str, full_name: Optional[str] = None) -> Optional[int]:
    """Create new user with hashed password"""
    conn = get_conn()
    cur = conn.cursor()
    
    # Hash password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        cur.execute("""
            INSERT INTO users (username, email, password_hash, full_name)
            VALUES (?, ?, ?, ?)
        """, (username, email, password_hash, full_name))
        
        user_id = cur.lastrowid
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None  # User already exists

def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """Authenticate user and return user data"""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM users WHERE email = ? AND is_active = 1", (email,))
    row = cur.fetchone()
    
    if row and bcrypt.checkpw(password.encode('utf-8'), row['password_hash'].encode('utf-8')):
        # Update last login
        cur.execute("UPDATE users SET last_login = datetime('now') WHERE id = ?", (row['id'],))
        conn.commit()
        conn.close()
        
        return {
            'id': row['id'],
            'email': row['email'],
            'full_name': row['full_name'],
            'created_at': row['created_at']
        }
    
    conn.close()
    return None

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, email, full_name, created_at, last_login FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

# ===== USER CREDENTIALS =====
def save_user_credentials(user_id: int, platform: str, username: str, 
                          encrypted_token: Optional[str] = None, session_cookie: Optional[str] = None):
    """Save or update user credentials for external platforms"""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT OR REPLACE INTO user_credentials 
        (user_id, platform, username, encrypted_token, session_cookie, last_synced, sync_status)
        VALUES (?, ?, ?, ?, ?, datetime('now'), 'pending')
    """, (user_id, platform, username, encrypted_token, session_cookie))
    
    conn.commit()
    conn.close()
    
    # Invalidate user cache
    CacheManager.invalidate_user(user_id)

def get_user_credentials(user_id: int, platform: str) -> Optional[Dict]:
    """Get user credentials for a platform"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM user_credentials 
        WHERE user_id = ? AND platform = ?
    """, (user_id, platform))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def update_sync_status(user_id: int, platform: str, status: str):
    """Update sync status for platform"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE user_credentials 
        SET sync_status = ?, last_synced = datetime('now')
        WHERE user_id = ? AND platform = ?
    """, (status, user_id, platform))
    conn.commit()
    conn.close()

# ===== USER PROGRESS =====
def update_user_progress(user_id: int, topic_id: int, progress_data: Dict):
    """Update user progress on a topic"""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT OR REPLACE INTO user_progress 
        (user_id, topic_id, status, progress_percentage, problems_solved, 
         total_problems, started_at, completed_at, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        user_id, topic_id,
        progress_data.get('status', 'in_progress'),
        progress_data.get('progress_percentage', 0),
        progress_data.get('problems_solved', 0),
        progress_data.get('total_problems', 0),
        progress_data.get('started_at'),
        progress_data.get('completed_at')
    ))
    
    conn.commit()
    conn.close()
    
    # Invalidate cache
    CacheManager.invalidate(f"user_progress_{user_id}", user_id)

def get_user_progress(user_id: int) -> List[Dict]:
    """Get all progress for a user with caching"""
    cache_key = f"user_progress_{user_id}"
    cached = CacheManager.get(cache_key, user_id)
    if cached:
        return cached
    
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT up.*, rt.name as topic_name, rt.category
        FROM user_progress up
        JOIN roadmap_topics rt ON up.topic_id = rt.id
        WHERE up.user_id = ?
        ORDER BY up.last_updated DESC
    """, (user_id,))
    
    rows = cur.fetchall()
    conn.close()
    
    result = [dict(row) for row in rows]
    CacheManager.set(cache_key, result, ttl_seconds=300, user_id=user_id)  # 5 min cache
    return result

# ===== PROBLEM STATUS =====
def update_problem_status(user_id: int, problem_id: int, status: str, 
                         time_taken: Optional[int] = None, notes: Optional[str] = None):
    """Update user's status on a specific problem"""
    conn = get_conn()
    cur = conn.cursor()
    
    solved_at = datetime.now() if status == 'solved' else None
    
    cur.execute("""
        INSERT INTO user_problem_status 
        (user_id, problem_id, status, attempts, last_attempted, solved_at, time_taken_minutes, notes)
        VALUES (?, ?, ?, 1, datetime('now'), ?, ?, ?)
        ON CONFLICT(user_id, problem_id) DO UPDATE SET
            status = excluded.status,
            attempts = attempts + 1,
            last_attempted = datetime('now'),
            solved_at = excluded.solved_at,
            time_taken_minutes = excluded.time_taken_minutes,
            notes = excluded.notes
    """, (user_id, problem_id, status, solved_at, time_taken, notes))
    
    conn.commit()
    conn.close()
    
    # Invalidate cache
    CacheManager.invalidate(f"user_problems_{user_id}", user_id)

# ===== WEAKNESS ANALYSIS =====
def save_weakness_analysis(user_id: int, analysis_data: Dict):
    """Save AI-generated weakness analysis"""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO weakness_analysis 
        (user_id, topic_id, weakness_type, weakness_name, severity_score, 
         confidence, evidence, recommendations, ai_analysis)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        analysis_data.get('topic_id'),
        analysis_data.get('weakness_type'),
        analysis_data.get('weakness_name'),
        analysis_data.get('severity_score', 0),
        analysis_data.get('confidence', 0),
        json.dumps(analysis_data.get('evidence', {})),
        json.dumps(analysis_data.get('recommendations', [])),
        analysis_data.get('ai_analysis', '')
    ))
    
    conn.commit()
    conn.close()
    
    CacheManager.invalidate(f"weaknesses_{user_id}", user_id)

def get_user_weaknesses(user_id: int) -> List[Dict]:
    """Get user weaknesses with caching"""
    cache_key = f"weaknesses_{user_id}"
    cached = CacheManager.get(cache_key, user_id)
    if cached:
        return cached
    
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM weakness_analysis 
        WHERE user_id = ? AND resolved_at IS NULL
        ORDER BY severity_score DESC
        LIMIT 20
    """, (user_id,))
    
    rows = cur.fetchall()
    conn.close()
    
    result = [dict(row) for row in rows]
    CacheManager.set(cache_key, result, ttl_seconds=600, user_id=user_id)  # 10 min cache
    return result

# ===== ROADMAP TOPICS =====
def get_all_topics() -> List[Dict]:
    """Get all roadmap topics with global caching"""
    cache_key = "all_topics"
    cached = CacheManager.get(cache_key)
    if cached:
        return cached
    
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM roadmap_topics ORDER BY priority DESC, name")
    rows = cur.fetchall()
    conn.close()
    
    result = [dict(row) for row in rows]
    CacheManager.set(cache_key, result, ttl_seconds=3600)  # 1 hour cache
    return result

def create_topic(name: str, category: str, **kwargs) -> int:
    """Create a new roadmap topic"""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO roadmap_topics (name, category, difficulty, priority, description, estimated_hours, prerequisites)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name, category,
        kwargs.get('difficulty'),
        kwargs.get('priority', 0),
        kwargs.get('description'),
        kwargs.get('estimated_hours'),
        json.dumps(kwargs.get('prerequisites', []))
    ))
    
    topic_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    CacheManager.invalidate("all_topics")
    return int(topic_id) if topic_id is not None else 0

# ===== BACKWARD COMPATIBILITY =====
def get_weaknesses(limit=20):
    """Legacy function for old routes - returns empty list"""
    return []

def insert_snapshot(source: str, key: str, data: dict):
    """Legacy function - no-op in new system"""
    pass

def upsert_weakness(topic: str, score: int):
    """Legacy function - no-op in new system"""
    pass


def save_user_focus(user_id, topic_data):
    """Save or update user's current focus topic"""
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO user_focus (user_id, topic_id, topic_name, topic_emoji, topic_color, set_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(user_id) DO UPDATE SET
                topic_id = excluded.topic_id,
                topic_name = excluded.topic_name,
                topic_emoji = excluded.topic_emoji,
                topic_color = excluded.topic_color,
                set_at = datetime('now')
        """, (
            user_id,
            topic_data.get('id'),
            topic_data.get('name'),
            topic_data.get('emoji'),
            topic_data.get('color')
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving user focus: {e}")
        return False
    finally:
        conn.close()

def get_user_focus(user_id):
    """Get user's current focus topic"""
    conn = get_conn()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT topic_id, topic_name, topic_emoji, topic_color
            FROM user_focus
            WHERE user_id = ?
        """, (user_id,))
        
        row = cur.fetchone()
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'emoji': row[2],
                'color': row[3]
            }
        return None
    finally:
        conn.close()
