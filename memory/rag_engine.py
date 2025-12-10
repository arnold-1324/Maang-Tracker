"""
RAG-based Memory System with Vector Embeddings
Retrieves relevant context for agents using semantic search
"""

import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from config.settings import config
from cache.redis_manager import CacheManager

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Represents a memory entry with embedding"""
    id: str
    user_id: str
    topic: str
    context: str
    message: str
    embedding: np.ndarray
    relevance_keywords: List[str]
    created_at: datetime
    access_count: int = 0


class EmbeddingService:
    """Generates embeddings using sentence-transformers"""
    
    _model = None
    
    @classmethod
    def initialize(cls):
        """Initialize embedding model"""
        if cls._model is not None:
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            
            model_name = config.EMBEDDING_MODEL
            logger.info(f"Loading embedding model: {model_name}")
            cls._model = SentenceTransformer(model_name)
            logger.info("Embedding model loaded successfully")
            
        except ImportError:
            logger.error("sentence-transformers package not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise
    
    @classmethod
    def embed(cls, text: str) -> np.ndarray:
        """Generate embedding for text"""
        if cls._model is None:
            cls.initialize()
        
        try:
            embedding = cls._model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    @classmethod
    def embed_batch(cls, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts"""
        if cls._model is None:
            cls.initialize()
        
        try:
            embeddings = cls._model.encode(texts, convert_to_numpy=True)
            return [embedding for embedding in embeddings]
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            raise
    
    @classmethod
    def similarity(cls, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Reshape for sklearn
        e1 = embedding1.reshape(1, -1)
        e2 = embedding2.reshape(1, -1)
        
        similarity = cosine_similarity(e1, e2)[0][0]
        return float(similarity)


class RAGMemoryEngine:
    """
    RAG engine for retrieving relevant conversation context
    Uses vector similarity search to find most relevant memories
    """
    
    def __init__(self, db_session=None, cache_manager: CacheManager = None):
        """Initialize RAG engine"""
        self.db_session = db_session
        self.cache_manager = cache_manager or CacheManager()
        self.embedding_service = EmbeddingService()
        self.embedding_service.initialize()
    
    def store_memory(
        self,
        user_id: str,
        topic: str,
        context: str,
        message: str,
        relevance_keywords: List[str] = None,
        message_type: str = "general"
    ) -> str:
        """
        Store a conversation entry with embedding
        
        Args:
            user_id: User ID
            topic: Topic/subject of the memory
            context: Context (interview, training, session, etc)
            message: The actual message to store
            relevance_keywords: Keywords for categorization
            message_type: Type of message (question, answer, feedback, etc)
        
        Returns:
            Memory entry ID
        """
        try:
            # Generate embedding
            embedding = self.embedding_service.embed(message)
            
            # Store to database (pseudo-code - actual depends on session)
            memory_id = self._store_to_db(
                user_id=user_id,
                topic=topic,
                context=context,
                message=message,
                embedding=embedding,
                relevance_keywords=relevance_keywords or [],
                message_type=message_type
            )
            
            # Also cache for quick access
            cache_key = f"memory:{user_id}:{topic}"
            self.cache_manager.increment_counter(cache_key)
            
            logger.info(f"Stored memory {memory_id} for user {user_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise
    
    def retrieve_context(
        self,
        user_id: str,
        query: str,
        topic: str = None,
        context: str = None,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories using semantic search
        
        Args:
            user_id: User ID
            query: Search query/text
            topic: Filter by topic (optional)
            context: Filter by context (optional)
            top_k: Number of results to return
        
        Returns:
            List of relevant memory entries with similarity scores
        """
        try:
            top_k = top_k or config.RAG_TOP_K
            
            # Check cache first
            cache_key = f"rag:{user_id}:{query[:50]}"
            cached = self.cache_manager.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for RAG query: {cache_key}")
                return cached
            
            # Generate query embedding
            query_embedding = self.embedding_service.embed(query)
            
            # Retrieve from database (pseudo-code)
            results = self._search_memories(
                user_id=user_id,
                query_embedding=query_embedding,
                topic=topic,
                context=context,
                top_k=top_k
            )
            
            # Cache results
            self.cache_manager.set(
                cache_key,
                results,
                ttl=config.CACHE_TTL_SHORT
            )
            
            logger.info(f"Retrieved {len(results)} memories for user {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return []
    
    def retrieve_for_interview(
        self,
        user_id: str,
        interview_mode: str,
        company: str = None,
        difficulty: str = None
    ) -> Dict[str, Any]:
        """
        Retrieve relevant context for an interview session
        
        Args:
            user_id: User ID
            interview_mode: Mode (coding, system_design, behavioral)
            company: Target company (optional)
            difficulty: Difficulty level (optional)
        
        Returns:
            Contextualized data for interview
        """
        try:
            context_data = {
                "past_interviews": [],
                "relevant_topics": [],
                "weaknesses": [],
                "strengths": [],
                "suggested_problems": [],
                "ai_tips": []
            }
            
            # Retrieve past interviews
            past_interviews = self._get_past_interviews(
                user_id, interview_mode, top_k=5
            )
            context_data["past_interviews"] = past_interviews
            
            # Retrieve relevant topics
            query = f"{interview_mode} {company or ''} {difficulty or ''}".strip()
            topics = self.retrieve_context(
                user_id, query, topic=interview_mode, top_k=3
            )
            context_data["relevant_topics"] = topics
            
            # Get weaknesses in this area
            weaknesses = self._get_user_weaknesses(user_id, interview_mode)
            context_data["weaknesses"] = weaknesses
            
            # Get strengths
            strengths = self._get_user_strengths(user_id, interview_mode)
            context_data["strengths"] = strengths
            
            return context_data
            
        except Exception as e:
            logger.error(f"Failed to retrieve interview context: {e}")
            return {}
    
    def retrieve_for_training(
        self,
        user_id: str,
        topic: str
    ) -> Dict[str, Any]:
        """
        Retrieve relevant context for training sessions
        
        Args:
            user_id: User ID
            topic: Training topic
        
        Returns:
            Training context and recommendations
        """
        try:
            context_data = {
                "topic_progress": {},
                "past_attempts": [],
                "common_mistakes": [],
                "recommended_resources": [],
                "next_problems": []
            }
            
            # Get topic progress
            progress = self._get_topic_progress(user_id, topic)
            context_data["topic_progress"] = progress
            
            # Get past attempts on this topic
            attempts = self.retrieve_context(
                user_id, topic, topic=topic, top_k=10
            )
            context_data["past_attempts"] = attempts
            
            # Get common mistakes
            mistakes = self._get_common_mistakes(user_id, topic)
            context_data["common_mistakes"] = mistakes
            
            return context_data
            
        except Exception as e:
            logger.error(f"Failed to retrieve training context: {e}")
            return {}
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Split text into chunks for embedding
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
        
        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or config.RAG_CHUNK_SIZE
        overlap = overlap or config.RAG_CHUNK_OVERLAP
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start = end - overlap
        
        return chunks
    
    # Private helper methods (to be implemented with actual DB calls)
    def _store_to_db(self, **kwargs) -> str:
        """Store memory to database"""
        # Pseudo-implementation
        import uuid
        return str(uuid.uuid4())
    
    def _search_memories(self, user_id: str, query_embedding: np.ndarray, 
                        topic: str = None, context: str = None, top_k: int = 5) -> List[Dict]:
        """Search memories using vector similarity"""
        # This would query PostgreSQL with pgvector similarity
        # SELECT * FROM conversation_memory 
        # WHERE user_id = $1
        # ORDER BY embedding <-> $2 LIMIT $3
        return []
    
    def _get_past_interviews(self, user_id: str, interview_mode: str, top_k: int = 5) -> List[Dict]:
        """Get past interview sessions"""
        return []
    
    def _get_user_weaknesses(self, user_id: str, category: str) -> List[Dict]:
        """Get identified weaknesses"""
        return []
    
    def _get_user_strengths(self, user_id: str, category: str) -> List[Dict]:
        """Get identified strengths"""
        return []
    
    def _get_topic_progress(self, user_id: str, topic: str) -> Dict:
        """Get progress on a topic"""
        return {}
    
    def _get_common_mistakes(self, user_id: str, topic: str) -> List[Dict]:
        """Get common mistakes in a topic"""
        return []


# Global RAG engine instance
_rag_engine: Optional[RAGMemoryEngine] = None


def get_rag_engine() -> RAGMemoryEngine:
    """Get or create RAG engine singleton"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGMemoryEngine()
    return _rag_engine
