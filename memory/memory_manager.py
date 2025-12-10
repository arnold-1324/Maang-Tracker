"""
Updated Memory Manager for PostgreSQL and RAG integration
Replaces the old SQLite-based memory system
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from config.database import DatabaseManager
from database.models import (
    ConversationMemory, VectorEmbedding, InterviewSession,
    UserProgress, WeaknessAnalysis
)
from memory.rag_engine import EmbeddingService
from cache.redis_manager import CacheManager

logger = logging.getLogger(__name__)


class PostgreSQLMemoryManager:
    """
    Memory manager using PostgreSQL + RAG
    Stores and retrieves conversation memories with semantic search
    """
    
    def __init__(self, user_id: str = None):
        """Initialize memory manager for a user"""
        self.user_id = user_id
        self.db_manager = DatabaseManager()
        self.embedding_service = EmbeddingService()
        self.embedding_service.initialize()
        self.cache = CacheManager()
    
    def store_conversation(
        self,
        topic: str,
        context: str,
        message: str,
        message_type: str = "general",
        relevance_keywords: List[str] = None
    ) -> str:
        """
        Store a conversation message with embedding
        
        Args:
            topic: Topic of conversation
            context: Context (interview, training, etc)
            message: The message content
            message_type: Type of message (question, answer, feedback)
            relevance_keywords: Keywords for filtering
        
        Returns:
            Memory entry ID
        """
        try:
            with DatabaseManager.get_session_context() as session:
                # Generate embedding
                embedding_vector = self.embedding_service.embed(message)
                
                # Create memory entry
                memory = ConversationMemory(
                    user_id=self.user_id,
                    topic=topic,
                    context=context,
                    message=message,
                    embedding=embedding_vector.tobytes(),  # Store as bytes
                    relevance_keywords=relevance_keywords or [],
                    message_type=message_type,
                    created_at=datetime.utcnow()
                )
                
                session.add(memory)
                session.commit()
                
                # Also create vector embedding record
                vec_embedding = VectorEmbedding(
                    memory_id=memory.id,
                    vector=embedding_vector.tolist(),  # Store as array
                    model_name='sentence-transformers/all-MiniLM-L6-v2'
                )
                session.add(vec_embedding)
                session.commit()
                
                logger.info(f"Stored memory {memory.id} for user {self.user_id}")
                
                # Invalidate cache
                self.cache.delete(f"memory:{self.user_id}:{topic}")
                
                return str(memory.id)
                
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")
            raise
    
    def search_memories(
        self,
        query: str,
        topic: str = None,
        context: str = None,
        top_k: int = 5,
        similarity_threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Search memories using semantic similarity
        
        Args:
            query: Search query
            topic: Filter by topic
            context: Filter by context
            top_k: Number of results
            similarity_threshold: Minimum similarity score
        
        Returns:
            List of similar memories
        """
        try:
            # Check cache first
            cache_key = f"search:{self.user_id}:{query[:30]}:{topic}"
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for search: {query[:30]}")
                return cached
            
            with DatabaseManager.get_session_context() as session:
                # Generate query embedding
                query_embedding = self.embedding_service.embed(query)
                
                # Get all user memories
                query_obj = session.query(ConversationMemory).filter(
                    ConversationMemory.user_id == self.user_id
                )
                
                if topic:
                    query_obj = query_obj.filter(ConversationMemory.topic == topic)
                if context:
                    query_obj = query_obj.filter(ConversationMemory.context == context)
                
                memories = query_obj.all()
                
                # Calculate similarities
                results = []
                for memory in memories:
                    import numpy as np
                    memory_embedding = np.frombuffer(memory.embedding, dtype=np.float32)
                    
                    # Cosine similarity
                    similarity = self.embedding_service.similarity(
                        query_embedding,
                        memory_embedding
                    )
                    
                    if similarity >= similarity_threshold:
                        results.append({
                            "id": str(memory.id),
                            "topic": memory.topic,
                            "context": memory.context,
                            "message": memory.message,
                            "type": memory.message_type,
                            "similarity": float(similarity),
                            "created_at": memory.created_at.isoformat(),
                            "access_count": memory.access_count
                        })
                
                # Sort by similarity
                results = sorted(results, key=lambda x: x['similarity'], reverse=True)[:top_k]
                
                # Update access counts
                for result in results:
                    mem = session.query(ConversationMemory).filter(
                        ConversationMemory.id == result['id']
                    ).first()
                    if mem:
                        mem.access_count += 1
                        mem.accessed_at = datetime.utcnow()
                session.commit()
                
                # Cache results
                self.cache.set(cache_key, results, ttl=3600)
                
                logger.info(f"Found {len(results)} similar memories for query: {query[:30]}")
                return results
                
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    def get_interview_context(self, interview_id: str) -> Dict[str, Any]:
        """Get RAG context for interview preparation"""
        try:
            with DatabaseManager.get_session_context() as session:
                # Get past interviews
                past_interviews = session.query(InterviewSession).filter(
                    and_(
                        InterviewSession.user_id == self.user_id,
                        InterviewSession.id != interview_id,
                        InterviewSession.status == 'completed'
                    )
                ).order_by(desc(InterviewSession.ended_at)).limit(5).all()
                
                # Get weaknesses
                weaknesses = session.query(WeaknessAnalysis).filter(
                    WeaknessAnalysis.user_id == self.user_id,
                    WeaknessAnalysis.resolved_at.is_(None)
                ).order_by(desc(WeaknessAnalysis.severity_score)).limit(5).all()
                
                context = {
                    "past_interviews": len(past_interviews),
                    "weaknesses": [
                        {
                            "weakness": w.weakness_name,
                            "severity": w.severity_score,
                            "recommendations": w.recommendations or []
                        }
                        for w in weaknesses
                    ]
                }
                
                return context
                
        except Exception as e:
            logger.error(f"Failed to get interview context: {e}")
            return {}
    
    def get_training_context(self, topic_id: str) -> Dict[str, Any]:
        """Get RAG context for training"""
        try:
            with DatabaseManager.get_session_context() as session:
                # Get topic progress
                progress = session.query(UserProgress).filter(
                    and_(
                        UserProgress.user_id == self.user_id,
                        UserProgress.topic_id == topic_id
                    )
                ).first()
                
                context = {
                    "status": progress.status if progress else "not_started",
                    "problems_solved": progress.problems_solved if progress else 0,
                    "progress_percentage": progress.progress_percentage if progress else 0
                }
                
                return context
                
        except Exception as e:
            logger.error(f"Failed to get training context: {e}")
            return {}
    
    def clear_old_memories(self, days: int = 90) -> int:
        """Clear old memories (older than specified days)"""
        try:
            from datetime import timedelta
            
            with DatabaseManager.get_session_context() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                count = session.query(ConversationMemory).filter(
                    and_(
                        ConversationMemory.user_id == self.user_id,
                        ConversationMemory.created_at < cutoff_date
                    )
                ).delete()
                
                session.commit()
                logger.info(f"Deleted {count} old memories for user {self.user_id}")
                
                return count
                
        except Exception as e:
            logger.error(f"Failed to clear old memories: {e}")
            return 0


# Global instance
_memory_manager: Optional[PostgreSQLMemoryManager] = None


def get_memory_manager(user_id: str = None) -> PostgreSQLMemoryManager:
    """Get memory manager instance"""
    global _memory_manager
    if _memory_manager is None or (user_id and _memory_manager.user_id != user_id):
        _memory_manager = PostgreSQLMemoryManager(user_id)
    return _memory_manager
