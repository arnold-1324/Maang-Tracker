"""
Interview Simulation Engine - Real-time coding, system design, and behavioral interviews
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import random
from dataclasses import dataclass, asdict
import hashlib


class InterviewMode(Enum):
    """Interview types"""
    CODING = "coding"
    SYSTEM_DESIGN = "system_design"
    BEHAVIORAL = "behavioral"


class CompanyRole(Enum):
    """Company and role combinations"""
    GOOGLE_SDE = "google_sde"
    GOOGLE_SENIOR = "google_senior"
    META_E4 = "meta_e4"
    META_E5 = "meta_e5"
    AMAZON_L5 = "amazon_l5"
    AMAZON_L6 = "amazon_l6"
    APPLE_ICT3 = "apple_ict3"
    APPLE_ICT4 = "apple_ict4"
    MICROSOFT_L63 = "microsoft_l63"
    MICROSOFT_L64 = "microsoft_l64"


@dataclass
class TestCase:
    """Test case for coding problems"""
    id: str
    input_data: str
    expected_output: str
    is_public: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CodingProblem:
    """Coding interview problem"""
    id: str
    title: str
    description: str
    difficulty: str  # easy, medium, hard
    topic: str  # arrays, dp, graphs, etc.
    leetcode_url: str
    test_cases: List[TestCase]
    time_limit_minutes: int = 45
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty,
            "topic": self.topic,
            "leetcode_url": self.leetcode_url,
            "test_cases": [tc.to_dict() for tc in self.test_cases],
            "time_limit_minutes": self.time_limit_minutes
        }


class InterviewSimulationEngine:
    """Core engine for interview simulation"""
    
    # Problem database (sample problems)
    CODING_PROBLEMS = {
        "two-sum": CodingProblem(
            id="two-sum",
            title="Two Sum",
            description="Given an array of integers nums and an integer target, return the indices of the two numbers that add up to target.\n\nConstraints:\n- 2 <= nums.length <= 10^4\n- -10^9 <= nums[i] <= 10^9\n- -10^9 <= target <= 10^9",
            difficulty="easy",
            topic="arrays",
            leetcode_url="https://leetcode.com/problems/two-sum/",
            test_cases=[
                TestCase("1", "nums = [2,7,11,15], target = 9", "[0,1]"),
                TestCase("2", "nums = [3,2,4], target = 6", "[1,2]"),
                TestCase("3", "nums = [3,3], target = 6", "[0,1]")
            ]
        ),
        "merge-intervals": CodingProblem(
            id="merge-intervals",
            title="Merge Intervals",
            description="Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping intervals.\n\nReturn an array of the non-overlapping intervals that cover all the intervals in the input.",
            difficulty="medium",
            topic="arrays",
            leetcode_url="https://leetcode.com/problems/merge-intervals/",
            test_cases=[
                TestCase("1", "intervals = [[1,3],[2,6],[8,10],[15,18]]", "[[1,6],[8,10],[15,18]]"),
                TestCase("2", "intervals = [[1,4],[4,5]]", "[[1,5]]")
            ]
        ),
        "max-product-subarray": CodingProblem(
            id="max-product-subarray",
            title="Maximum Product Subarray",
            description="Given an integer array nums, find a contiguous non-empty subarray that has the largest product.\n\nReturn the maximum product.",
            difficulty="medium",
            topic="dp",
            leetcode_url="https://leetcode.com/problems/maximum-product-subarray/",
            test_cases=[
                TestCase("1", "nums = [2,3,-2,4]", "6"),
                TestCase("2", "nums = [-2]", "-2")
            ]
        ),
        "median-two-sorted-arrays": CodingProblem(
            id="median-two-sorted-arrays",
            title="Median of Two Sorted Arrays",
            description="Given two sorted arrays nums1 and nums2, return the median of the two sorted arrays.\n\nThe overall run time complexity should be O(log(min(m,n))).",
            difficulty="hard",
            topic="binary-search",
            leetcode_url="https://leetcode.com/problems/median-of-two-sorted-arrays/",
            test_cases=[
                TestCase("1", "nums1 = [1,3], nums2 = [2]", "2.0"),
                TestCase("2", "nums1 = [1,2], nums2 = [3,4]", "2.5")
            ]
        )
    }
    
    SYSTEM_DESIGN_TOPICS = {
        "url-shortener": {
            "title": "Design URL Shortener (like TinyURL)",
            "requirements": [
                "Convert long URL to short URL",
                "Convert short URL back to original URL",
                "Handle millions of URLs",
                "Scalability and database choice",
                "Caching strategy",
                "Rate limiting"
            ],
            "company_specific": {
                CompanyRole.GOOGLE_SDE: "Focus on distributed systems, load balancing",
                CompanyRole.META_E4: "Emphasize trade-offs, database design",
                CompanyRole.AMAZON_L5: "Focus on scalability, monitoring"
            }
        },
        "cache-system": {
            "title": "Design Cache System (LRU)",
            "requirements": [
                "Implement get and put operations",
                "O(1) time complexity",
                "Evict least recently used items",
                "Thread safety",
                "Memory constraints"
            ],
            "company_specific": {
                CompanyRole.GOOGLE_SENIOR: "Focus on concurrency patterns",
                CompanyRole.META_E5: "Advanced data structures"
            }
        },
        "chat-system": {
            "title": "Design Chat System",
            "requirements": [
                "One-on-one messaging",
                "Group messaging",
                "Message delivery guarantees",
                "Presence and online status",
                "Notification system",
                "Scalability to millions of users"
            ],
            "company_specific": {
                CompanyRole.AMAZON_L6: "Real-time systems, microservices"
            }
        }
    }
    
    BEHAVIORAL_QUESTIONS = {
        "tell-me-about-yourself": "Tell me about yourself and your background in software engineering.",
        "conflict-resolution": "Describe a situation where you had a conflict with a colleague. How did you resolve it?",
        "leadership": "Give an example of when you led a team or took initiative on a project.",
        "failure": "Tell me about a time you failed. What did you learn from it?",
        "technical-challenge": "Describe your most challenging technical problem you've solved.",
        "collaboration": "How do you approach collaboration with non-technical stakeholders?"
    }
    
    def __init__(self, db_path: str = "memory/interview.db"):
        """Initialize interview engine"""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize interview database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Interview sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                mode TEXT,
                company_role TEXT,
                problem_id TEXT,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                duration_minutes INTEGER,
                status TEXT,
                score FLOAT,
                feedback TEXT
            )
        ''')
        
        # Code submissions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                user_id TEXT,
                code TEXT,
                language TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                test_passed INTEGER,
                test_failed INTEGER,
                execution_time_ms FLOAT
            )
        ''')
        
        # Chat history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                user_id TEXT,
                speaker TEXT,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                mode TEXT,
                difficulty TEXT,
                problems_solved INTEGER,
                problems_attempted INTEGER,
                avg_score FLOAT,
                total_hours FLOAT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_coding_problem(self, problem_id: str) -> Optional[Dict[str, Any]]:
        """Get coding problem by ID"""
        if problem_id in self.CODING_PROBLEMS:
            return self.CODING_PROBLEMS[problem_id].to_dict()
        return None
    
    def get_coding_problems_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """Get problems by difficulty"""
        return [
            problem.to_dict()
            for problem in self.CODING_PROBLEMS.values()
            if problem.difficulty == difficulty
        ]
    
    def get_system_design_problem(self, topic: str, company_role: CompanyRole = None) -> Optional[Dict[str, Any]]:
        """Get system design problem with company-specific guidance"""
        if topic not in self.SYSTEM_DESIGN_TOPICS:
            return None
        
        problem = self.SYSTEM_DESIGN_TOPICS[topic].copy()
        
        # Add company-specific guidance
        if company_role and "company_specific" in problem:
            problem["company_guidance"] = problem["company_specific"].get(company_role, "")
        
        return problem
    
    def get_behavioral_question(self, question_id: str = None) -> Dict[str, str]:
        """Get behavioral question"""
        if question_id and question_id in self.BEHAVIORAL_QUESTIONS:
            return {
                "id": question_id,
                "question": self.BEHAVIORAL_QUESTIONS[question_id]
            }
        
        # Return random question
        random_id = random.choice(list(self.BEHAVIORAL_QUESTIONS.keys()))
        return {
            "id": random_id,
            "question": self.BEHAVIORAL_QUESTIONS[random_id]
        }
    
    def validate_code(self, code: str, language: str, test_cases: List[TestCase]) -> Dict[str, Any]:
        """
        Validate code against test cases
        In production, would use actual code execution
        """
        # Simulate code validation
        result = {
            "passed": 0,
            "failed": 0,
            "execution_time_ms": random.uniform(10, 500),
            "test_results": []
        }
        
        # Simple heuristic: check if code contains key patterns
        has_solution = len(code.strip()) > 50 and "{" in code
        
        for i, test_case in enumerate(test_cases):
            if has_solution:
                # Simulate 80% pass rate for non-empty solutions
                passed = random.random() > 0.2
            else:
                passed = False
            
            result["test_results"].append({
                "test_case_id": test_case.id,
                "passed": passed,
                "input": test_case.input_data[:50] + "..." if len(test_case.input_data) > 50 else test_case.input_data,
                "expected": test_case.expected_output[:50] + "..." if len(test_case.expected_output) > 50 else test_case.expected_output
            })
            
            if passed:
                result["passed"] += 1
            else:
                result["failed"] += 1
        
        return result
    
    def create_session(self, user_id: str, mode: InterviewMode, 
                      company_role: CompanyRole = None, problem_id: str = None) -> Dict[str, Any]:
        """Create new interview session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO interview_sessions (user_id, mode, company_role, problem_id, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, mode.value, company_role.value if company_role else None, problem_id, "active"))
        
        conn.commit()
        session_id = cursor.lastrowid
        conn.close()
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "mode": mode.value,
            "started_at": datetime.now().isoformat()
        }
    
    def submit_code(self, session_id: int, user_id: str, code: str, 
                   language: str, test_cases: List[TestCase]) -> Dict[str, Any]:
        """Submit code for testing"""
        # Validate code
        validation = self.validate_code(code, language, test_cases)
        
        # Store submission
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO code_submissions 
            (session_id, user_id, code, language, test_passed, test_failed, execution_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, user_id, code[:5000], language, 
              validation["passed"], validation["failed"], validation["execution_time_ms"]))
        
        conn.commit()
        submission_id = cursor.lastrowid
        conn.close()
        
        return {
            "submission_id": submission_id,
            "validation": validation,
            "timestamp": datetime.now().isoformat()
        }
    
    def add_chat_message(self, session_id: int, user_id: str, 
                        speaker: str, message: str):
        """Add message to interview chat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO interview_chat (session_id, user_id, speaker, message)
            VALUES (?, ?, ?, ?)
        ''', (session_id, user_id, speaker, message))
        
        conn.commit()
        conn.close()
    
    def get_chat_history(self, session_id: int) -> List[Dict[str, Any]]:
        """Get chat history for session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT speaker, message, timestamp FROM interview_chat
            WHERE session_id = ?
            ORDER BY timestamp ASC
        ''', (session_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "speaker": row[0],
                "message": row[1],
                "timestamp": row[2]
            })
        
        conn.close()
        return messages
    
    def end_session(self, session_id: int, score: float, feedback: str = "") -> Dict[str, Any]:
        """End interview session and calculate score"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE interview_sessions
            SET end_time = CURRENT_TIMESTAMP, status = ?, score = ?, feedback = ?
            WHERE id = ?
        ''', ("completed", score, feedback, session_id))
        
        conn.commit()
        
        # Get session details
        cursor.execute('SELECT * FROM interview_sessions WHERE id = ?', (session_id,))
        session = cursor.fetchone()
        conn.close()
        
        return {
            "session_id": session_id,
            "score": score,
            "feedback": feedback,
            "completed_at": datetime.now().isoformat()
        }
    
    def get_user_metrics(self, user_id: str) -> Dict[str, Any]:
        """Get user performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT mode, difficulty, COUNT(*) as attempts, 
                   SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as solved
            FROM interview_sessions
            WHERE user_id = ?
            GROUP BY mode, difficulty
        ''', (user_id,))
        
        metrics = {
            "coding": {"easy": {}, "medium": {}, "hard": {}},
            "system_design": {"total": {}},
            "behavioral": {"total": {}}
        }
        
        for row in cursor.fetchall():
            mode, difficulty, attempts, solved = row
            # Process metrics...
        
        conn.close()
        return metrics
    
    def get_schedule_for_friday(self) -> Dict[str, Any]:
        """Get Friday interview schedule (3 PM)"""
        today = datetime.now()
        days_until_friday = (4 - today.weekday()) % 7  # 4 is Friday
        if days_until_friday == 0 and today.hour >= 15:
            days_until_friday = 7
        
        next_friday = today + timedelta(days=days_until_friday)
        interview_time = next_friday.replace(hour=15, minute=0, second=0)
        
        return {
            "next_interview": interview_time.isoformat(),
            "date": next_friday.strftime("%Y-%m-%d"),
            "time": "15:00",
            "timezone": "IST",
            "countdown_seconds": int((interview_time - today).total_seconds()),
            "interview_id": f"interview_{next_friday.strftime('%Y%m%d')}"
        }


# Example usage
if __name__ == "__main__":
    engine = InterviewSimulationEngine()
    
    # Get a coding problem
    problem = engine.get_coding_problem("two-sum")
    print("Problem:", problem["title"])
    print("Difficulty:", problem["difficulty"])
    
    # Get system design problem
    sd_problem = engine.get_system_design_problem("url-shortener", CompanyRole.GOOGLE_SDE)
    print("\nSystem Design:", sd_problem["title"])
    
    # Get behavioral question
    bq = engine.get_behavioral_question()
    print("\nBehavioral:", bq["question"])
    
    # Get Friday schedule
    schedule = engine.get_schedule_for_friday()
    print("\nNext Interview:", schedule["date"], "at", schedule["time"])
