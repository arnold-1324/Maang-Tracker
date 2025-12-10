"""
SQLAlchemy database models for Maang-Tracker
Replaces SQLite schema with PostgreSQL tables
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float, 
    ForeignKey, UniqueConstraint, Index, JSON, Enum, LargeBinary
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, UUID, JSONB
from datetime import datetime
import enum
import uuid

Base = declarative_base()


# ============= ENUMS =============
class InterviewMode(str, enum.Enum):
    CODING = "coding"
    SYSTEM_DESIGN = "system_design"
    BEHAVIORAL = "behavioral"


class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TopicCategory(str, enum.Enum):
    DSA = "dsa"
    SYSTEM_DESIGN = "system_design"
    BEHAVIORAL = "behavioral"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"


class ProblemStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    ATTEMPTED = "attempted"
    SOLVED = "solved"
    REVIEWED = "reviewed"


class SyncStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


# ============= CORE TABLES =============
class User(Base):
    """User authentication and profile"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    bio = Column(Text)
    avatar_url = Column(String(512))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True, index=True)
    is_admin = Column(Boolean, default=False)
    
    # Relationships
    credentials = relationship("UserCredential", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    problem_status = relationship("UserProblemStatus", back_populates="user", cascade="all, delete-orphan")
    system_design = relationship("SystemDesignProgress", back_populates="user", cascade="all, delete-orphan")
    weaknesses = relationship("WeaknessAnalysis", back_populates="user", cascade="all, delete-orphan")
    interviews = relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")
    memory_entries = relationship("ConversationMemory", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_created', 'created_at'),
    )


class UserCredential(Base):
    """External platform credentials (LeetCode, GitHub, etc)"""
    __tablename__ = "user_credentials"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    platform = Column(String(50), nullable=False)  # 'leetcode', 'github', etc
    platform_username = Column(String(255), nullable=False)
    encrypted_token = Column(Text)
    session_cookie = Column(Text)
    
    # Sync metadata
    last_synced = Column(DateTime)
    sync_status = Column(String(20), default='pending')
    sync_error = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="credentials")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'platform', name='unique_user_platform'),
        Index('idx_credential_platform', 'platform'),
        Index('idx_credential_sync', 'last_synced'),
    )


# ============= ROADMAP & TOPICS =============
class RoadmapTopic(Base):
    """Learning roadmap topics (shared across users)"""
    __tablename__ = "roadmap_topics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)  # dsa, system_design, behavioral
    difficulty = Column(String(20))  # beginner, intermediate, advanced
    priority = Column(Integer, default=0)
    description = Column(Text)
    estimated_hours = Column(Integer)
    prerequisites = Column(JSONB, default=[])  # JSON array of topic IDs
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    problems = relationship("TopicProblem", back_populates="topic", cascade="all, delete-orphan")
    user_progress = relationship("UserProgress", back_populates="topic", cascade="all, delete-orphan")
    weaknesses = relationship("WeaknessAnalysis", back_populates="topic")
    
    __table_args__ = (
        Index('idx_topic_category', 'category'),
        Index('idx_topic_difficulty', 'difficulty'),
    )


class TopicProblem(Base):
    """Problems/questions linked to topics"""
    __tablename__ = "topic_problems"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey('roadmap_topics.id', ondelete='CASCADE'), nullable=False)
    platform = Column(String(50), nullable=False)  # 'leetcode', 'gfg', 'custom'
    problem_slug = Column(String(255), nullable=False)
    problem_title = Column(String(255), nullable=False)
    difficulty = Column(String(20), nullable=False)
    problem_url = Column(String(512))
    tags = Column(JSONB, default=[])
    description = Column(Text)
    solution_notes = Column(Text)
    
    # Relationships
    topic = relationship("RoadmapTopic", back_populates="problems")
    user_status = relationship("UserProblemStatus", back_populates="problem", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('platform', 'problem_slug', name='unique_platform_problem'),
        Index('idx_problem_difficulty', 'difficulty'),
        Index('idx_problem_platform', 'platform'),
    )


class UserProgress(Base):
    """User progress on topics"""
    __tablename__ = "user_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey('roadmap_topics.id', ondelete='CASCADE'), nullable=False)
    
    status = Column(String(20), default='not_started')  # not_started, in_progress, completed
    progress_percentage = Column(Float, default=0.0)
    problems_solved = Column(Integer, default=0)
    total_problems = Column(Integer, default=0)
    
    # Timestamps
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    topic = relationship("RoadmapTopic", back_populates="user_progress")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'topic_id', name='unique_user_topic'),
        Index('idx_progress_status', 'status'),
    )


class UserProblemStatus(Base):
    """User-specific problem status"""
    __tablename__ = "user_problem_status"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    problem_id = Column(UUID(as_uuid=True), ForeignKey('topic_problems.id', ondelete='CASCADE'), nullable=False)
    
    status = Column(String(20), default='not_started')  # not_started, attempted, solved, reviewed
    attempts = Column(Integer, default=0)
    time_taken_minutes = Column(Integer)
    
    # Code and notes
    last_submitted_code = Column(Text)
    notes = Column(Text)
    
    # Timestamps
    last_attempted = Column(DateTime)
    solved_at = Column(DateTime)
    
    # Performance metrics
    tests_passed = Column(Integer, default=0)
    tests_total = Column(Integer, default=0)
    time_complexity = Column(String(50))
    space_complexity = Column(String(50))
    
    # Relationships
    user = relationship("User", back_populates="problem_status")
    problem = relationship("TopicProblem", back_populates="user_status")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'problem_id', name='unique_user_problem'),
        Index('idx_problem_status', 'status'),
    )


# ============= SYSTEM DESIGN & WEAKNESSES =============
class SystemDesignProgress(Base):
    """System design learning progress"""
    __tablename__ = "system_design_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    design_name = Column(String(255), nullable=False)
    category = Column(String(100))  # scalability, database, caching, etc.
    
    status = Column(String(20), default='not_started')
    notes = Column(Text)
    diagram_url = Column(String(512))
    
    # Ratings
    completeness_score = Column(Float)  # 0-10
    quality_score = Column(Float)  # 0-10
    
    # Timestamps
    completed_at = Column(DateTime)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="system_design")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'design_name', name='unique_user_design'),
    )


class WeaknessAnalysis(Base):
    """AI-powered weakness analysis"""
    __tablename__ = "weakness_analysis"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey('roadmap_topics.id', ondelete='SET NULL'))
    
    weakness_type = Column(String(50), nullable=False)  # topic, pattern, concept
    weakness_name = Column(String(255), nullable=False)
    severity_score = Column(Float, default=0.0)  # 0-10 scale
    confidence = Column(Float, default=0.0)  # AI confidence 0-1
    
    # Analysis
    evidence = Column(JSONB)  # Failed problems, time taken, etc
    recommendations = Column(JSONB)  # Suggested problems, resources
    ai_analysis = Column(Text)
    
    # Status
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="weaknesses")
    topic = relationship("RoadmapTopic", back_populates="weaknesses")
    
    __table_args__ = (
        Index('idx_weakness_severity', 'severity_score'),
        Index('idx_weakness_type', 'weakness_type'),
    )


# ============= INTERVIEW SYSTEM =============
class InterviewSession(Base):
    """Interview sessions"""
    __tablename__ = "interview_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    mode = Column(String(50), nullable=False)  # coding, system_design, behavioral
    title = Column(String(255))
    company = Column(String(255))
    role = Column(String(255))
    difficulty = Column(String(20))
    
    # Status and timing
    status = Column(String(20), default='active')  # active, completed, paused, abandoned
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    duration_minutes = Column(Integer)
    
    # Results
    score = Column(Float)
    feedback = Column(Text)
    strengths = Column(JSONB)
    improvements = Column(JSONB)
    
    # Relationships
    user = relationship("User", back_populates="interviews")
    chat_history = relationship("InterviewChat", back_populates="session", cascade="all, delete-orphan")
    code_submissions = relationship("CodeSubmission", back_populates="session", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_interview_status', 'status'),
        Index('idx_interview_user', 'user_id'),
    )


class InterviewChat(Base):
    """Interview chat messages"""
    __tablename__ = "interview_chat"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('interview_sessions.id', ondelete='CASCADE'), nullable=False)
    
    role = Column(String(20), nullable=False)  # user, interviewer, system
    message = Column(Text, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    tokens_used = Column(Integer)
    
    # Relationships
    session = relationship("InterviewSession", back_populates="chat_history")


class CodeSubmission(Base):
    """Code submissions during interviews"""
    __tablename__ = "code_submissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('interview_sessions.id', ondelete='CASCADE'), nullable=False)
    
    language = Column(String(50), nullable=False)
    code = Column(Text, nullable=False)
    
    # Execution results
    is_submitted = Column(Boolean, default=False)
    passed_tests = Column(Integer)
    total_tests = Column(Integer)
    execution_time_ms = Column(Integer)
    memory_mb = Column(Float)
    
    # Analysis
    time_complexity = Column(String(100))
    space_complexity = Column(String(100))
    feedback = Column(Text)
    
    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("InterviewSession", back_populates="code_submissions")


# ============= RAG MEMORY SYSTEM =============
class ConversationMemory(Base):
    """RAG-based conversation memory with embeddings"""
    __tablename__ = "conversation_memory"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Content
    topic = Column(String(255), nullable=False)
    context = Column(String(50))  # interview, training, session, etc
    message = Column(Text, nullable=False)
    
    # Vector embedding (384-dim for MiniLM)
    embedding = Column(LargeBinary)  # Stored as pickle or numpy bytes
    
    # Metadata
    relevance_keywords = Column(ARRAY(String), default=[])
    message_type = Column(String(50))  # question, answer, feedback, etc
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    accessed_at = Column(DateTime)
    access_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="memory_entries")
    
    __table_args__ = (
        Index('idx_memory_user_topic', 'user_id', 'topic'),
        Index('idx_memory_context', 'context'),
        Index('idx_memory_created', 'created_at'),
    )


class VectorEmbedding(Base):
    """Pre-computed vector embeddings for RAG"""
    __tablename__ = "vector_embeddings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    memory_id = Column(UUID(as_uuid=True), ForeignKey('conversation_memory.id', ondelete='CASCADE'))
    
    # Embedding vector (384-dimensional for MiniLM model)
    vector = Column(ARRAY(Float), nullable=False)
    model_name = Column(String(100), default='sentence-transformers/all-MiniLM-L6-v2')
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_embedding_vector', 'vector', postgresql_using='ivfflat', postgresql_with={'ops': {'vector': 'vector_cosine_ops'}}),
    )


# ============= CACHING =============
class CacheEntry(Base):
    """Redis cache metadata (for persistence)"""
    __tablename__ = "cache_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    cache_value = Column(Text, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    hit_count = Column(Integer, default=0)
    
    __table_args__ = (
        Index('idx_cache_expiry', 'expires_at'),
    )


# ============= ANALYTICS & METRICS =============
class UserMetrics(Base):
    """Aggregated user metrics"""
    __tablename__ = "user_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    
    # Problem statistics
    total_problems_attempted = Column(Integer, default=0)
    total_problems_solved = Column(Integer, default=0)
    total_interviews = Column(Integer, default=0)
    average_interview_score = Column(Float)
    
    # Learning metrics
    topics_in_progress = Column(Integer, default=0)
    topics_completed = Column(Integer, default=0)
    total_hours_studied = Column(Float, default=0)
    
    # Performance
    easy_ratio = Column(Float)
    medium_ratio = Column(Float)
    hard_ratio = Column(Float)
    
    # Last updated
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ActivityLog(Base):
    """User activity logging"""
    __tablename__ = "activity_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(255))
    details = Column(JSONB)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_activity_user', 'user_id'),
        Index('idx_activity_action', 'action'),
    )
 
 #   = = = = = = = = = = = = =   J O B   A P P L I C A T I O N   T R A C K E R   = = = = = = = = = = = = =  
 c l a s s   J o b P o s t i n g ( B a s e ) :  
         " " " J o b   p o s t i n g s   c r a w l e d   o r   a d d e d   m a n u a l l y " " "  
         _ _ t a b l e n a m e _ _   =   " j o b _ p o s t i n g s "  
  
         i d   =   C o l u m n ( I n t e g e r ,   p r i m a r y _ k e y = T r u e ,   a u t o i n c r e m e n t = T r u e )  
         t i t l e   =   C o l u m n ( S t r i n g ( 2 5 5 ) ,   n u l l a b l e = F a l s e )  
         c o m p a n y   =   C o l u m n ( S t r i n g ( 2 5 5 ) ,   n u l l a b l e = F a l s e )  
         l o c a t i o n   =   C o l u m n ( S t r i n g ( 2 5 5 ) )  
         u r l   =   C o l u m n ( S t r i n g ( 5 1 2 ) ,   u n i q u e = T r u e )  
         d e s c r i p t i o n   =   C o l u m n ( T e x t )   #   F u l l   J D  
         s o u r c e   =   C o l u m n ( S t r i n g ( 5 0 ) )   #   L i n k e d I n ,   I n d e e d ,   e t c .  
         p o s t e d _ d a t e   =   C o l u m n ( D a t e T i m e )  
          
         c r e a t e d _ a t   =   C o l u m n ( D a t e T i m e ,   d e f a u l t = d a t e t i m e . u t c n o w )  
          
         #   R e l a t i o n s h i p s  
         a p p l i c a t i o n s   =   r e l a t i o n s h i p ( " J o b A p p l i c a t i o n " ,   b a c k _ p o p u l a t e s = " j o b " ,   c a s c a d e = " a l l ,   d e l e t e - o r p h a n " )  
          
         _ _ t a b l e _ a r g s _ _   =   (  
                 I n d e x ( ' i d x _ j o b _ c o m p a n y ' ,   ' c o m p a n y ' ) ,  
                 I n d e x ( ' i d x _ j o b _ u r l ' ,   ' u r l ' ) ,  
         )  
  
 c l a s s   J o b A p p l i c a t i o n ( B a s e ) :  
         " " " U s e r ' s   a p p l i c a t i o n s   t o   j o b s " " "  
         _ _ t a b l e n a m e _ _   =   " j o b _ a p p l i c a t i o n s "  
  
         i d   =   C o l u m n ( U U I D ( a s _ u u i d = T r u e ) ,   p r i m a r y _ k e y = T r u e ,   d e f a u l t = u u i d . u u i d 4 )  
         u s e r _ i d   =   C o l u m n ( U U I D ( a s _ u u i d = T r u e ) ,   F o r e i g n K e y ( ' u s e r s . i d ' ,   o n d e l e t e = ' C A S C A D E ' ) ,   n u l l a b l e = F a l s e )  
         j o b _ i d   =   C o l u m n ( I n t e g e r ,   F o r e i g n K e y ( ' j o b _ p o s t i n g s . i d ' ,   o n d e l e t e = ' C A S C A D E ' ) ,   n u l l a b l e = F a l s e )  
          
         s t a t u s   =   C o l u m n ( S t r i n g ( 5 0 ) ,   d e f a u l t = ' S a v e d ' )   #   S a v e d ,   A p p l i e d ,   I n t e r v i e w i n g ,   O f f e r ,   R e j e c t e d  
          
         #   R e s u m e   v e r s i o n s  
         o r i g i n a l _ r e s u m e _ p a t h   =   C o l u m n ( S t r i n g ( 5 1 2 ) )  
         o p t i m i z e d _ r e s u m e _ p a t h   =   C o l u m n ( S t r i n g ( 5 1 2 ) )  
          
         #   S c o r e s  
         o r i g i n a l _ a t s _ s c o r e   =   C o l u m n ( F l o a t ,   d e f a u l t = 0 . 0 )  
         o p t i m i z e d _ a t s _ s c o r e   =   C o l u m n ( F l o a t ,   d e f a u l t = 0 . 0 )  
          
         #   C o v e r   L e t t e r  
         c o v e r _ l e t t e r _ p a t h   =   C o l u m n ( S t r i n g ( 5 1 2 ) )  
          
         #   T r a c k i n g  
         a p p l i e d _ d a t e   =   C o l u m n ( D a t e T i m e )  
         l a s t _ s t a t u s _ c h e c k   =   C o l u m n ( D a t e T i m e )  
         n o t e s   =   C o l u m n ( T e x t )  
          
         #   R e l a t i o n s h i p s  
         u s e r   =   r e l a t i o n s h i p ( " U s e r " )  
         j o b   =   r e l a t i o n s h i p ( " J o b P o s t i n g " ,   b a c k _ p o p u l a t e s = " a p p l i c a t i o n s " )  
  
         _ _ t a b l e _ a r g s _ _   =   (  
                 U n i q u e C o n s t r a i n t ( ' u s e r _ i d ' ,   ' j o b _ i d ' ,   n a m e = ' u n i q u e _ a p p l i c a t i o n ' ) ,  
                 I n d e x ( ' i d x _ a p p _ s t a t u s ' ,   ' s t a t u s ' ) ,  
         )  
 