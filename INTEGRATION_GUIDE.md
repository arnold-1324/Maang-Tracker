"""
Integration Guide: Using the New PostgreSQL + RAG System in the Agent
Updated MaangMentorWithMemory to use PostgreSQL backend instead of SQLite
"""

# Example 1: Initialize Agent with New Memory System
# ====================================================

from maang_agent.agent import MaangMentorWithMemory
from memory.memory_manager import get_memory_manager
from memory.rag_engine import get_rag_engine
from cache.redis_manager import CacheManager

# Initialize for a user
user_id = "user-123"
mentor = MaangMentorWithMemory(user_id=user_id)

# The mentor now automatically uses:
# - PostgreSQL for all persistence
# - RAG engine for semantic memory retrieval
# - Redis for caching


# Example 2: Store Interview Conversation
# =========================================

def interview_conversation_example():
    """Example of storing interview conversation"""
    
    memory_manager = get_memory_manager(user_id)
    
    # Store interviewer's question
    memory_manager.store_conversation(
        topic="Dynamic Programming",
        context="interview",
        message="Given a string s, find the longest palindromic substring. Return its length.",
        message_type="question",
        relevance_keywords=["palindrome", "dp", "string"]
    )
    
    # Store user's response
    memory_manager.store_conversation(
        topic="Dynamic Programming",
        context="interview",
        message="I'll use DP with 2D table where dp[i][j] represents if substring s[i:j+1] is palindrome.",
        message_type="answer",
        relevance_keywords=["dp", "solution", "approach"]
    )
    
    # Store feedback
    memory_manager.store_conversation(
        topic="Dynamic Programming",
        context="interview",
        message="Good approach! Time: O(n²), Space: O(n²). Can you optimize space?",
        message_type="feedback",
        relevance_keywords=["optimization", "space-complexity"]
    )


# Example 3: Retrieve Relevant Context for Interview
# ===================================================

def retrieve_interview_context_example():
    """Retrieve context for better interview performance"""
    
    memory_manager = get_memory_manager(user_id)
    rag_engine = get_rag_engine()
    
    # Search for similar interview questions about DP
    similar_interviews = memory_manager.search_memories(
        query="longest palindromic substring dynamic programming",
        topic="Dynamic Programming",
        context="interview",
        top_k=5
    )
    
    print("Similar past interview questions:")
    for mem in similar_interviews:
        print(f"  - {mem['message'][:100]}... (similarity: {mem['similarity']:.2f})")
    
    # Get interview preparation context
    interview_context = memory_manager.get_interview_context(interview_id="current")
    
    return {
        "similar_questions": similar_interviews,
        "context": interview_context
    }


# Example 4: Retrieve Training Context
# =====================================

def retrieve_training_context_example():
    """Retrieve context for training sessions"""
    
    memory_manager = get_memory_manager(user_id)
    
    # Get training context for a topic
    training_context = memory_manager.get_training_context(topic_id="topic-123")
    
    print(f"Training Progress:")
    print(f"  Status: {training_context['status']}")
    print(f"  Problems Solved: {training_context['problems_solved']}")
    print(f"  Progress: {training_context['progress_percentage']:.1f}%")


# Example 5: Use Cache to Speed Up Common Queries
# ================================================

def cache_usage_example():
    """Use Redis cache for frequently accessed data"""
    
    cache = CacheManager()
    
    # Cache user statistics
    user_stats = {
        "problems_solved": 150,
        "topics_completed": 5,
        "interviews_completed": 8,
        "average_score": 7.2
    }
    
    cache.set(
        key=f"user_stats:{user_id}",
        value=user_stats,
        ttl=3600  # Cache for 1 hour
    )
    
    # Retrieve from cache
    cached_stats = cache.get(f"user_stats:{user_id}")
    print(f"Cached user stats: {cached_stats}")


# Example 6: Update Agent to Use New System
# ==========================================

"""
Modifications needed in maang_agent/agent.py:

OLD (SQLite):
```python
from memory.db import CacheManager, get_weaknesses

class MaangMentorWithMemory:
    def __init__(self, user_id: str):
        self.memory_manager = get_memory_manager()  # SQLite
```

NEW (PostgreSQL + RAG):
```python
from memory.memory_manager import get_memory_manager, PostgreSQLMemoryManager
from memory.rag_engine import get_rag_engine

class MaangMentorWithMemory:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.memory_manager = get_memory_manager(user_id)  # PostgreSQL
        self.rag_engine = get_rag_engine()  # RAG system
        self.cache = CacheManager()  # Redis
```

Usage in interview flow:

```python
def start_interview(self, interview_id: str, mode: str):
    # Get RAG context from past experiences
    context = self.memory_manager.get_interview_context(interview_id)
    
    # Get relevant training materials
    materials = self.rag_engine.retrieve_for_interview(
        user_id=self.user_id,
        interview_mode=mode
    )
    
    # Store conversation for future retrieval
    def on_message(role: str, message: str):
        self.memory_manager.store_conversation(
            topic=interview_type,
            context="interview",
            message=message,
            message_type="assistant" if role == "interviewer" else "user"
        )
    
    return context, materials
```
"""


# Example 7: Search Similar Problems
# ===================================

def search_similar_problems_example():
    """Find similar problems using semantic search"""
    
    memory_manager = get_memory_manager(user_id)
    
    # Search for problems similar to a query
    query = "find minimum in rotated sorted array"
    
    similar = memory_manager.search_memories(
        query=query,
        topic="Binary Search",
        top_k=5,
        similarity_threshold=0.4
    )
    
    print(f"Problems similar to '{query}':")
    for item in similar:
        print(f"  - {item['message']}")
        print(f"    Similarity: {item['similarity']:.2f}")
        print(f"    Type: {item['type']}")
        print()


# Example 8: Clean Old Data
# ==========================

def cleanup_example():
    """Periodically clean old memories"""
    
    memory_manager = get_memory_manager(user_id)
    
    # Remove memories older than 90 days
    deleted_count = memory_manager.clear_old_memories(days=90)
    print(f"Deleted {deleted_count} old memories")


# Example 9: Integration with Interview Session
# ==============================================

def complete_interview_flow():
    """Complete example of interview with RAG integration"""
    
    user_id = "user-123"
    interview_id = "interview-456"
    
    # Initialize
    memory_manager = get_memory_manager(user_id)
    mentor = MaangMentorWithMemory(user_id)
    
    # Pre-interview: Get context
    context = memory_manager.get_interview_context(interview_id)
    print(f"Interview context retrieved. Past interviews: {context['past_interviews']}")
    
    # During interview: Store exchanges
    interview_exchanges = [
        ("interviewer", "Design a cache system for web applications"),
        ("user", "I would use Redis with LRU eviction..."),
        ("interviewer", "Good, what about consistency?"),
        ("user", "We need distributed consensus..."),
        ("interviewer", "How would you handle cache invalidation?"),
    ]
    
    for role, message in interview_exchanges:
        memory_manager.store_conversation(
            topic="System Design",
            context="interview",
            message=message,
            message_type="question" if role == "interviewer" else "answer"
        )
    
    # Post-interview: Search similar
    similar = memory_manager.search_memories(
        query="cache system design redis",
        top_k=3
    )
    print(f"Found {len(similar)} similar past questions")


# Example 10: RAG-Powered Agent Recommendations
# ==============================================

def rag_recommendations_example():
    """Use RAG to generate personalized recommendations"""
    
    rag_engine = get_rag_engine()
    memory_manager = get_memory_manager(user_id)
    
    # Get training context with RAG
    training_context = rag_engine.retrieve_for_training(
        user_id=user_id,
        topic="Dynamic Programming"
    )
    
    print("Training Recommendations:")
    print(f"  Topic Progress: {training_context['topic_progress']}")
    print(f"  Past Attempts: {len(training_context['past_attempts'])}")
    print(f"  Common Mistakes: {len(training_context['common_mistakes'])}")
    print(f"  Recommended Resources: {len(training_context['recommended_resources'])}")


# ============================================
# MIGRATION NOTES
# ============================================

"""
Key Changes from SQLite to PostgreSQL:

1. DATABASE
   - Was: SQLite file (memory.db)
   - Now: PostgreSQL with connection pooling
   - Benefit: Scalable, supports concurrent connections

2. MEMORY
   - Was: Simple in-memory caching + SQLite
   - Now: PostgreSQL + RAG with vector embeddings
   - Benefit: Semantic search, context-aware responses

3. CACHING
   - Was: Python dict in memory
   - Now: Redis distributed cache
   - Benefit: Shared cache across instances, persistent

4. SEARCH
   - Was: Text search only
   - Now: Semantic vector search (pgvector)
   - Benefit: Find similar problems/topics automatically

5. EMBEDDINGS
   - Was: No embeddings
   - Now: sentence-transformers embeddings stored in PostgreSQL
   - Benefit: Semantic understanding of content

6. DEPLOYMENT
   - Was: Standalone Python + SQLite
   - Now: Docker Compose with multiple services
   - Benefit: Production-ready, easy scaling


DATA MIGRATION STRATEGY:

1. Backup existing SQLite database
2. Export user data from SQLite
3. Run migrations to create PostgreSQL schema
4. Import historical data (optional)
5. Generate embeddings for existing conversations
6. Validate data integrity
7. Run new system in parallel
8. Gradually migrate traffic

See MIGRATION_GUIDE.md for detailed steps.
"""
