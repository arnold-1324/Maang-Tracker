"""
Google AI Agent Memory Persistence Module
Handles memory storage, conversation history, and topic tracking for MAANG Mentor
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class AgentMemoryManager:
    """Manages persistent memory for the MAANG Mentor AI agent"""
    
    def __init__(self, db_path: str = "maang_agent_memory.db"):
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        """Initialize memory database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversation history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata JSON,
                INDEX idx_user_session (user_id, session_id),
                INDEX idx_timestamp (timestamp)
            )
        """)
        
        # Topic coverage tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topic_coverage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT DEFAULT 'learning',
                proficiency_level INTEGER DEFAULT 1,
                problems_solved INTEGER DEFAULT 0,
                last_reviewed DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, topic, category),
                INDEX idx_user_category (user_id, category)
            )
        """)
        
        # Performance metrics and progress
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                date DATE NOT NULL,
                problems_attempted INTEGER DEFAULT 0,
                problems_solved INTEGER DEFAULT 0,
                avg_difficulty REAL DEFAULT 0.0,
                time_spent_minutes INTEGER DEFAULT 0,
                interview_sessions INTEGER DEFAULT 0,
                system_design_sessions INTEGER DEFAULT 0,
                behavioral_sessions INTEGER DEFAULT 0,
                avg_score REAL DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, date),
                INDEX idx_user_date (user_id, date)
            )
        """)
        
        # Learning path and recommendations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_path (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                week_number INTEGER NOT NULL,
                primary_focus TEXT NOT NULL,
                recommended_topics JSON,
                target_problems INTEGER,
                completed_problems INTEGER DEFAULT 0,
                status TEXT DEFAULT 'not_started',
                start_date DATETIME,
                end_date DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, week_number),
                INDEX idx_user_week (user_id, week_number)
            )
        """)
        
        # Session context and performance
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interview_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                interview_id TEXT NOT NULL,
                mode TEXT NOT NULL,
                company_role TEXT,
                difficulty TEXT,
                topic TEXT,
                time_spent_minutes INTEGER,
                score REAL,
                feedback TEXT,
                ai_assessment TEXT,
                strengths JSON,
                weaknesses JSON,
                recommendations JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_interview (user_id, interview_id),
                INDEX idx_user_mode (user_id, mode)
            )
        """)
        
        # Mastery tracking for problems
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS problem_mastery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                problem_id TEXT NOT NULL,
                problem_name TEXT NOT NULL,
                category TEXT NOT NULL,
                first_attempt_date DATETIME,
                attempts INTEGER DEFAULT 0,
                optimal_solution_found BOOLEAN DEFAULT FALSE,
                time_to_solve_minutes INTEGER,
                mastery_level INTEGER DEFAULT 1,
                follow_up_questions_answered INTEGER DEFAULT 0,
                verified_date DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, problem_id),
                INDEX idx_user_category (user_id, category)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ==================== Conversation Management ====================
    
    def store_conversation(
        self, 
        user_id: str, 
        session_id: str, 
        role: str, 
        message: str, 
        metadata: Optional[Dict] = None
    ) -> int:
        """Store a message in conversation history"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conversation_history (user_id, session_id, role, message, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, session_id, role, message, json.dumps(metadata or {})))
        
        conn.commit()
        msg_id = cursor.lastrowid
        conn.close()
        return msg_id
    
    def get_conversation_history(
        self, 
        user_id: str, 
        session_id: Optional[str] = None, 
        limit: int = 50
    ) -> List[Dict]:
        """Retrieve conversation history"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute("""
                SELECT * FROM conversation_history 
                WHERE user_id = ? AND session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, session_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM conversation_history 
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # ==================== Topic Coverage Tracking ====================
    
    def track_topic_coverage(
        self, 
        user_id: str, 
        topic: str, 
        category: str,
        status: str = "learning",
        proficiency_level: int = 1
    ) -> int:
        """Track a topic in the user's learning path"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO topic_coverage 
            (user_id, topic, category, status, proficiency_level)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, topic, category) DO UPDATE SET
                status = ?,
                proficiency_level = ?,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, topic, category, status, proficiency_level, status, proficiency_level))
        
        conn.commit()
        topic_id = cursor.lastrowid
        conn.close()
        return topic_id
    
    def get_topic_coverage(self, user_id: str, category: Optional[str] = None) -> List[Dict]:
        """Get all topics covered by user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT * FROM topic_coverage 
                WHERE user_id = ? AND category = ?
                ORDER BY proficiency_level DESC, updated_at DESC
            """, (user_id, category))
        else:
            cursor.execute("""
                SELECT * FROM topic_coverage 
                WHERE user_id = ?
                ORDER BY category, proficiency_level DESC
            """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def update_topic_proficiency(
        self, 
        user_id: str, 
        topic: str, 
        category: str, 
        proficiency_level: int,
        increment_problems: int = 0
    ):
        """Update proficiency level for a topic"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE topic_coverage 
            SET proficiency_level = ?,
                problems_solved = problems_solved + ?,
                last_reviewed = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND topic = ? AND category = ?
        """, (proficiency_level, increment_problems, user_id, topic, category))
        
        conn.commit()
        conn.close()
    
    # ==================== Progress Analytics ====================
    
    def record_daily_progress(
        self, 
        user_id: str, 
        date: str,
        problems_attempted: int = 0,
        problems_solved: int = 0,
        avg_difficulty: float = 0.0,
        time_spent_minutes: int = 0,
        interview_sessions: int = 0,
        system_design_sessions: int = 0,
        behavioral_sessions: int = 0,
        avg_score: float = 0.0
    ):
        """Record daily learning analytics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO progress_analytics 
            (user_id, date, problems_attempted, problems_solved, avg_difficulty, 
             time_spent_minutes, interview_sessions, system_design_sessions, 
             behavioral_sessions, avg_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, date) DO UPDATE SET
                problems_attempted = problems_attempted + ?,
                problems_solved = problems_solved + ?,
                avg_difficulty = ?,
                time_spent_minutes = time_spent_minutes + ?,
                interview_sessions = interview_sessions + ?,
                system_design_sessions = system_design_sessions + ?,
                behavioral_sessions = behavioral_sessions + ?,
                avg_score = ?
        """, (user_id, date, problems_attempted, problems_solved, avg_difficulty, 
              time_spent_minutes, interview_sessions, system_design_sessions, 
              behavioral_sessions, avg_score,
              problems_attempted, problems_solved, avg_difficulty, 
              time_spent_minutes, interview_sessions, system_design_sessions, 
              behavioral_sessions, avg_score))
        
        conn.commit()
        conn.close()
    
    def get_progress_analytics(self, user_id: str, days: int = 30) -> List[Dict]:
        """Get progress analytics for last N days"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM progress_analytics 
            WHERE user_id = ? AND date >= date('now', '-' || ? || ' days')
            ORDER BY date DESC
        """, (user_id, days))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # ==================== Learning Path Management ====================
    
    def create_learning_path(
        self, 
        user_id: str, 
        week_number: int, 
        primary_focus: str,
        recommended_topics: List[str],
        target_problems: int
    ):
        """Create a week's learning path"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO learning_path 
            (user_id, week_number, primary_focus, recommended_topics, target_problems)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, week_number) DO UPDATE SET
                primary_focus = ?,
                recommended_topics = ?,
                target_problems = ?,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, week_number, primary_focus, json.dumps(recommended_topics), 
              target_problems, primary_focus, json.dumps(recommended_topics), target_problems))
        
        conn.commit()
        conn.close()
    
    def get_learning_path(self, user_id: str, week_number: Optional[int] = None) -> List[Dict]:
        """Get learning path for user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if week_number:
            cursor.execute("""
                SELECT * FROM learning_path 
                WHERE user_id = ? AND week_number = ?
            """, (user_id, week_number))
        else:
            cursor.execute("""
                SELECT * FROM learning_path 
                WHERE user_id = ?
                ORDER BY week_number
            """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            row_dict = dict(row)
            row_dict['recommended_topics'] = json.loads(row_dict['recommended_topics'])
            result.append(row_dict)
        return result
    
    # ==================== Interview Context Storage ====================
    
    def store_interview_context(
        self, 
        user_id: str, 
        interview_id: str, 
        mode: str,
        company_role: Optional[str],
        difficulty: Optional[str],
        topic: Optional[str],
        time_spent_minutes: int,
        score: float,
        feedback: str,
        ai_assessment: str,
        strengths: List[str],
        weaknesses: List[str],
        recommendations: List[str]
    ):
        """Store complete interview session context"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO interview_context 
            (user_id, interview_id, mode, company_role, difficulty, topic, 
             time_spent_minutes, score, feedback, ai_assessment, strengths, weaknesses, recommendations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, interview_id, mode, company_role, difficulty, topic,
              time_spent_minutes, score, feedback, ai_assessment,
              json.dumps(strengths), json.dumps(weaknesses), json.dumps(recommendations)))
        
        conn.commit()
        conn.close()
    
    def get_interview_history(self, user_id: str, mode: Optional[str] = None) -> List[Dict]:
        """Get interview performance history"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if mode:
            cursor.execute("""
                SELECT * FROM interview_context 
                WHERE user_id = ? AND mode = ?
                ORDER BY created_at DESC
            """, (user_id, mode))
        else:
            cursor.execute("""
                SELECT * FROM interview_context 
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            row_dict = dict(row)
            row_dict['strengths'] = json.loads(row_dict['strengths'] or '[]')
            row_dict['weaknesses'] = json.loads(row_dict['weaknesses'] or '[]')
            row_dict['recommendations'] = json.loads(row_dict['recommendations'] or '[]')
            result.append(row_dict)
        return result
    
    # ==================== Problem Mastery Tracking ====================
    
    def track_problem_attempt(
        self, 
        user_id: str, 
        problem_id: str, 
        problem_name: str,
        category: str,
        time_to_solve_minutes: Optional[int] = None,
        optimal_solution_found: bool = False
    ):
        """Track problem attempt and mastery"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO problem_mastery 
            (user_id, problem_id, problem_name, category, first_attempt_date, 
             time_to_solve_minutes, optimal_solution_found, attempts, mastery_level)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, 1, 1)
            ON CONFLICT(user_id, problem_id) DO UPDATE SET
                attempts = attempts + 1,
                time_to_solve_minutes = CASE WHEN ? < time_to_solve_minutes THEN ? ELSE time_to_solve_minutes END,
                optimal_solution_found = CASE WHEN ? = 1 THEN 1 ELSE optimal_solution_found END,
                mastery_level = CASE WHEN attempts >= 2 THEN 2 WHEN attempts >= 3 THEN 3 ELSE mastery_level END
        """, (user_id, problem_id, problem_name, category, time_to_solve_minutes, 
              optimal_solution_found, 
              time_to_solve_minutes or 0, time_to_solve_minutes or 0, optimal_solution_found))
        
        conn.commit()
        conn.close()
    
    def get_problem_mastery(self, user_id: str, category: Optional[str] = None) -> List[Dict]:
        """Get mastery level for problems"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT * FROM problem_mastery 
                WHERE user_id = ? AND category = ?
                ORDER BY mastery_level DESC, attempts DESC
            """, (user_id, category))
        else:
            cursor.execute("""
                SELECT * FROM problem_mastery 
                WHERE user_id = ?
                ORDER BY category, mastery_level DESC
            """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def verify_mastery(self, user_id: str, problem_id: str, follow_up_questions: int = 0):
        """Verify mastery through follow-up questions"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE problem_mastery 
            SET follow_up_questions_answered = follow_up_questions_answered + ?,
                mastery_level = CASE 
                    WHEN follow_up_questions_answered >= 3 THEN 3
                    ELSE mastery_level
                END,
                verified_date = CURRENT_TIMESTAMP
            WHERE user_id = ? AND problem_id = ?
        """, (follow_up_questions, user_id, problem_id))
        
        conn.commit()
        conn.close()
    
    # ==================== Summary and Insights ====================
    
    def get_user_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user learning summary"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Total problems solved
        cursor.execute("""
            SELECT COUNT(*) as total FROM problem_mastery WHERE user_id = ?
        """, (user_id,))
        total_problems = cursor.fetchone()['total']
        
        # Mastery breakdown
        cursor.execute("""
            SELECT mastery_level, COUNT(*) as count FROM problem_mastery 
            WHERE user_id = ? GROUP BY mastery_level
        """, (user_id,))
        mastery_breakdown = {row['mastery_level']: row['count'] for row in cursor.fetchall()}
        
        # Topics covered
        cursor.execute("""
            SELECT COUNT(DISTINCT topic) as count FROM topic_coverage WHERE user_id = ?
        """, (user_id,))
        topics_covered = cursor.fetchone()['count']
        
        # Interview statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_interviews,
                AVG(score) as avg_score,
                MAX(score) as best_score,
                SUM(time_spent_minutes) as total_time
            FROM interview_context WHERE user_id = ?
        """, (user_id,))
        interview_stats = dict(cursor.fetchone())
        
        conn.close()
        
        return {
            'total_problems_solved': total_problems,
            'mastery_breakdown': mastery_breakdown,
            'topics_covered': topics_covered,
            'interview_statistics': interview_stats
        }


# Global instance
_memory_manager = None

def get_memory_manager() -> AgentMemoryManager:
    """Get or create the global memory manager instance"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = AgentMemoryManager()
    return _memory_manager
