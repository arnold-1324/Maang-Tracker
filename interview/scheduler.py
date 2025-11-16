"""
Interview Scheduler - Schedule and manage recurring Friday 3 PM interviews
"""

from datetime import datetime, timedelta, time
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import json
import sqlite3
from dataclasses import dataclass, asdict


class InterviewFrequency(Enum):
    """Interview scheduling frequency"""
    ONCE = "once"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    CUSTOM = "custom"


class InterviewStatus(Enum):
    """Interview status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


@dataclass
class ScheduledInterview:
    """Scheduled interview details"""
    id: str
    user_id: str
    scheduled_time: datetime
    mode: str  # coding, system_design, behavioral
    difficulty: str  # easy, medium, hard
    company_role: str
    status: str
    created_at: datetime
    cancelled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "scheduled_time": self.scheduled_time.isoformat(),
            "mode": self.mode,
            "difficulty": self.difficulty,
            "company_role": self.company_role,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "score": self.score,
            "countdown_seconds": (self.scheduled_time - datetime.now()).total_seconds()
        }


class InterviewScheduler:
    """
    Manages interview scheduling with Friday 3 PM default
    """
    
    # Default interview configuration
    DEFAULT_INTERVIEW_TIME = time(15, 0)  # 3 PM
    DEFAULT_INTERVIEW_DAY = 4  # Friday (0=Monday, 4=Friday)
    DEFAULT_DURATION_MINUTES = 45
    
    # Interview mode progression
    MODE_ROTATION = ["coding", "system_design", "behavioral"]
    DIFFICULTY_PROGRESSION = ["easy", "medium", "hard"]
    
    def __init__(self, db_path: str = "memory/interview.db"):
        """Initialize scheduler"""
        self.db_path = db_path
        self._init_db()
        self.scheduled_interviews: Dict[str, ScheduledInterview] = {}
        self.callbacks: Dict[str, List[Callable]] = {
            "interview_starting": [],
            "interview_reminder": [],
            "interview_completed": []
        }
    
    def _init_db(self):
        """Initialize scheduler database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Scheduled interviews table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_interviews (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                scheduled_time TIMESTAMP,
                mode TEXT,
                difficulty TEXT,
                company_role TEXT,
                status TEXT,
                created_at TIMESTAMP,
                cancelled_at TIMESTAMP,
                completed_at TIMESTAMP,
                score FLOAT,
                feedback TEXT
            )
        ''')
        
        # Interview reminders
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interview_id TEXT,
                user_id TEXT,
                reminder_time TIMESTAMP,
                sent BOOLEAN DEFAULT 0,
                sent_at TIMESTAMP
            )
        ''')
        
        # User interview preferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_preferences (
                user_id TEXT PRIMARY KEY,
                preferred_time TIME,
                preferred_day INTEGER,
                preferred_mode TEXT,
                frequency TEXT,
                timezone TEXT,
                email TEXT,
                notifications_enabled BOOLEAN
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def schedule_interview(self, user_id: str, mode: str = "coding", 
                          difficulty: str = "medium", company_role: str = "google_sde",
                          interview_time: Optional[datetime] = None,
                          frequency: InterviewFrequency = InterviewFrequency.WEEKLY) -> ScheduledInterview:
        """
        Schedule interview for user
        Defaults to next Friday at 3 PM
        """
        import uuid
        
        # Default to next Friday 3 PM if not specified
        if interview_time is None:
            interview_time = self._get_next_friday_3pm()
        
        # Generate unique ID using uuid for absolute uniqueness
        interview_id = f"interview_{uuid.uuid4().hex[:12]}"
        
        # Create scheduled interview
        interview = ScheduledInterview(
            id=interview_id,
            user_id=user_id,
            scheduled_time=interview_time,
            mode=mode,
            difficulty=difficulty,
            company_role=company_role,
            status=InterviewStatus.SCHEDULED.value,
            created_at=datetime.now()
        )
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scheduled_interviews
            (id, user_id, scheduled_time, mode, difficulty, company_role, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (interview.id, interview.user_id, interview.scheduled_time, 
              interview.mode, interview.difficulty, interview.company_role,
              interview.status, interview.created_at))
        
        # Create reminders (24 hours before, 1 hour before, 5 minutes before)
        reminder_times = [
            interview_time - timedelta(hours=24),
            interview_time - timedelta(hours=1),
            interview_time - timedelta(minutes=5)
        ]
        
        for reminder_time in reminder_times:
            if reminder_time > datetime.now():
                cursor.execute('''
                    INSERT INTO interview_reminders (interview_id, user_id, reminder_time)
                    VALUES (?, ?, ?)
                ''', (interview_id, user_id, reminder_time))
        
        conn.commit()
        conn.close()
        
        # Store in memory
        self.scheduled_interviews[interview_id] = interview
        
        return interview
    
    def schedule_recurring(self, user_id: str, mode: str, 
                          num_weeks: int = 12,
                          start_date: Optional[datetime] = None) -> List[ScheduledInterview]:
        """
        Schedule recurring weekly interviews
        """
        interviews = []
        
        if start_date is None:
            start_date = self._get_next_friday_3pm()
        
        # Rotate through modes if single mode
        modes = [mode]
        difficulties = ["easy", "medium", "hard"]
        
        for week in range(num_weeks):
            interview_date = start_date + timedelta(weeks=week)
            current_mode = modes[week % len(modes)]
            current_difficulty = difficulties[week % len(difficulties)]
            
            interview = self.schedule_interview(
                user_id=user_id,
                mode=current_mode,
                difficulty=current_difficulty,
                interview_time=interview_date,
                frequency=InterviewFrequency.WEEKLY
            )
            interviews.append(interview)
        
        return interviews
    
    def get_next_interview(self, user_id: str) -> Optional[ScheduledInterview]:
        """Get user's next scheduled interview"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, scheduled_time, mode, difficulty, company_role, status, created_at
            FROM scheduled_interviews
            WHERE user_id = ? AND status = ? AND scheduled_time > datetime('now')
            ORDER BY scheduled_time ASC
            LIMIT 1
        ''', (user_id, InterviewStatus.SCHEDULED.value))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return ScheduledInterview(
                id=row[0], user_id=row[1], scheduled_time=datetime.fromisoformat(row[2]),
                mode=row[3], difficulty=row[4], company_role=row[5],
                status=row[6], created_at=datetime.fromisoformat(row[7])
            )
        
        return None
    
    def get_upcoming_interviews(self, user_id: str, days: int = 30) -> List[ScheduledInterview]:
        """Get upcoming interviews in specified days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        future_date = (datetime.now() + timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT id, user_id, scheduled_time, mode, difficulty, company_role, status, created_at
            FROM scheduled_interviews
            WHERE user_id = ? AND status = ? AND scheduled_time BETWEEN datetime('now') AND ?
            ORDER BY scheduled_time ASC
        ''', (user_id, InterviewStatus.SCHEDULED.value, future_date))
        
        interviews = []
        for row in cursor.fetchall():
            interviews.append(ScheduledInterview(
                id=row[0], user_id=row[1], scheduled_time=datetime.fromisoformat(row[2]),
                mode=row[3], difficulty=row[4], company_role=row[5],
                status=row[6], created_at=datetime.fromisoformat(row[7])
            ))
        
        conn.close()
        return interviews
    
    def mark_in_progress(self, interview_id: str) -> bool:
        """Mark interview as in progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE scheduled_interviews
            SET status = ?
            WHERE id = ?
        ''', (InterviewStatus.IN_PROGRESS.value, interview_id))
        
        conn.commit()
        conn.close()
        
        if interview_id in self.scheduled_interviews:
            self.scheduled_interviews[interview_id].status = InterviewStatus.IN_PROGRESS.value
        
        return cursor.rowcount > 0
    
    def complete_interview(self, interview_id: str, score: float, feedback: str = "") -> bool:
        """Mark interview as completed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE scheduled_interviews
            SET status = ?, completed_at = CURRENT_TIMESTAMP, score = ?, feedback = ?
            WHERE id = ?
        ''', (InterviewStatus.COMPLETED.value, score, feedback, interview_id))
        
        conn.commit()
        conn.close()
        
        if interview_id in self.scheduled_interviews:
            self.scheduled_interviews[interview_id].status = InterviewStatus.COMPLETED.value
            self.scheduled_interviews[interview_id].score = score
            self.scheduled_interviews[interview_id].completed_at = datetime.now()
        
        return cursor.rowcount > 0
    
    def cancel_interview(self, interview_id: str, reason: str = "") -> bool:
        """Cancel scheduled interview"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE scheduled_interviews
            SET status = ?, cancelled_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (InterviewStatus.CANCELLED.value, interview_id))
        
        conn.commit()
        conn.close()
        
        if interview_id in self.scheduled_interviews:
            self.scheduled_interviews[interview_id].status = InterviewStatus.CANCELLED.value
            self.scheduled_interviews[interview_id].cancelled_at = datetime.now()
        
        return cursor.rowcount > 0
    
    def reschedule_interview(self, interview_id: str, new_time: datetime) -> Optional[ScheduledInterview]:
        """Reschedule interview to new time"""
        # Cancel old one
        self.cancel_interview(interview_id)
        
        # Get original interview details
        old_interview = self.scheduled_interviews.get(interview_id)
        if not old_interview:
            return None
        
        # Create new interview with same parameters
        return self.schedule_interview(
            user_id=old_interview.user_id,
            mode=old_interview.mode,
            difficulty=old_interview.difficulty,
            company_role=old_interview.company_role,
            interview_time=new_time
        )
    
    def register_callback(self, event: str, callback: Callable):
        """Register callback for interview events"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def trigger_callback(self, event: str, data: Dict[str, Any]):
        """Trigger callbacks for event"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error in callback: {e}")
    
    def check_reminders(self) -> List[Dict[str, Any]]:
        """Check for due reminders"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ir.id, ir.interview_id, ir.user_id, ir.reminder_time,
                   si.scheduled_time, si.mode, si.difficulty
            FROM interview_reminders ir
            JOIN scheduled_interviews si ON ir.interview_id = si.id
            WHERE ir.sent = 0 AND ir.reminder_time <= datetime('now')
            ORDER BY ir.reminder_time ASC
        ''')
        
        reminders = []
        for row in cursor.fetchall():
            reminder = {
                "reminder_id": row[0],
                "interview_id": row[1],
                "user_id": row[2],
                "reminder_time": row[3],
                "interview_time": row[4],
                "mode": row[5],
                "difficulty": row[6],
                "minutes_until": int((datetime.fromisoformat(row[4]) - datetime.now()).total_seconds() / 60)
            }
            reminders.append(reminder)
            
            # Mark as sent
            cursor.execute('''
                UPDATE interview_reminders
                SET sent = 1, sent_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (row[0],))
        
        conn.commit()
        conn.close()
        
        return reminders
    
    def _get_next_friday_3pm(self) -> datetime:
        """Get next Friday at 3 PM"""
        now = datetime.now()
        days_ahead = self.DEFAULT_INTERVIEW_DAY - now.weekday()
        
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        
        next_friday = now + timedelta(days=days_ahead)
        interview_time = next_friday.replace(
            hour=self.DEFAULT_INTERVIEW_TIME.hour,
            minute=self.DEFAULT_INTERVIEW_TIME.minute,
            second=0,
            microsecond=0
        )
        
        return interview_time
    
    def get_interview_countdown(self, interview_id: str) -> Dict[str, Any]:
        """Get countdown to interview"""
        interview = self.scheduled_interviews.get(interview_id)
        if not interview:
            return {}
        
        now = datetime.now()
        delta = interview.scheduled_time - now
        
        return {
            "interview_id": interview_id,
            "scheduled_time": interview.scheduled_time.isoformat(),
            "total_seconds": int(delta.total_seconds()),
            "days": delta.days,
            "hours": (delta.seconds // 3600) % 24,
            "minutes": (delta.seconds // 60) % 60,
            "seconds": delta.seconds % 60,
            "formatted": f"{delta.days}d {(delta.seconds // 3600) % 24}h {(delta.seconds // 60) % 60}m"
        }


# Example usage
if __name__ == "__main__":
    scheduler = InterviewScheduler()
    
    # Schedule a single interview
    user_id = "user_123"
    interview = scheduler.schedule_interview(
        user_id=user_id,
        mode="coding",
        difficulty="medium"
    )
    print(f"Scheduled Interview: {interview.to_dict()}")
    
    # Schedule recurring interviews (12 weeks)
    interviews = scheduler.schedule_recurring(
        user_id=user_id,
        mode="coding",
        num_weeks=12
    )
    print(f"\nScheduled {len(interviews)} recurring interviews")
    
    # Get next interview
    next_interview = scheduler.get_next_interview(user_id)
    if next_interview:
        print(f"\nNext Interview: {next_interview.scheduled_time}")
        countdown = scheduler.get_interview_countdown(next_interview.id)
        print(f"Countdown: {countdown['formatted']}")
    
    # Get upcoming interviews
    upcoming = scheduler.get_upcoming_interviews(user_id, days=30)
    print(f"\nUpcoming interviews in next 30 days: {len(upcoming)}")
