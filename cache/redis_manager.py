"""
Redis Cache Manager
Distributed caching layer for Maang-Tracker
"""

import json
import pickle
import logging
from typing import Any, Optional, List, Dict
from config.settings import config
import hashlib

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages distributed caching with Redis
    """
    
    _redis_client = None
    
    @classmethod
    def initialize(cls):
        """Initialize Redis connection"""
        if cls._redis_client is not None:
            return
        
        try:
            import redis
            
            # Create Redis client with connection pooling
            cls._redis_client = redis.from_url(
                config.REDIS_URL,
                decode_responses=False,  # Store as bytes for binary data
                health_check_interval=30,
                socket_keepalive=True,
                socket_keepalive_options={
                    1: 1,  # TCP_KEEPIDLE
                    2: 1,  # TCP_KEEPINTVL
                }
            )
            
            # Test connection
            cls._redis_client.ping()
            logger.info("Redis connection established")
            
        except ImportError:
            logger.error("redis package not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    @classmethod
    def get_client(self):
        """Get Redis client"""
        if self._redis_client is None:
            self.initialize()
        return self._redis_client
    
    @classmethod
    def set(cls, key: str, value: Any, ttl: int = None, compress: bool = False) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache (supports any Python object)
            ttl: Time to live in seconds
            compress: Compress large values
        
        Returns:
            True if successful
        """
        try:
            ttl = ttl or config.CACHE_TTL_DEFAULT
            
            # Serialize value
            if isinstance(value, (str, int, float)):
                serialized = str(value).encode()
            else:
                serialized = pickle.dumps(value)
            
            # Compress if needed
            if compress and len(serialized) > 1000:
                import zlib
                serialized = zlib.compress(serialized)
                key = f"compressed:{key}"
            
            # Store in Redis
            client = cls.get_client()
            client.setex(key, ttl, serialized)
            
            logger.debug(f"Cache SET: {key} (ttl={ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Cache SET failed for key {key}: {e}")
            return False
    
    @classmethod
    def get(cls, key: str, decompress: bool = False) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            decompress: Decompress value if compressed
        
        Returns:
            Cached value or None
        """
        try:
            client = cls.get_client()
            
            # Check if compressed version exists
            if decompress or f"compressed:{key}" in client:
                import zlib
                value = client.get(f"compressed:{key}")
                if value:
                    value = zlib.decompress(value)
                    logger.debug(f"Cache GET (decompressed): {key}")
                    return pickle.loads(value)
            
            # Get regular value
            value = client.get(key)
            
            if value is None:
                logger.debug(f"Cache MISS: {key}")
                return None
            
            # Try to deserialize
            try:
                if isinstance(value, bytes):
                    result = pickle.loads(value)
                else:
                    result = value.decode('utf-8')
                    try:
                        result = json.loads(result)
                    except json.JSONDecodeError:
                        pass
                
                logger.debug(f"Cache GET: {key}")
                return result
            except Exception:
                logger.debug(f"Cache GET (raw bytes): {key}")
                return value
            
        except Exception as e:
            logger.error(f"Cache GET failed for key {key}: {e}")
            return None
    
    @classmethod
    def delete(cls, key: str) -> bool:
        """Delete key from cache"""
        try:
            client = cls.get_client()
            client.delete(key)
            if client.exists(f"compressed:{key}"):
                client.delete(f"compressed:{key}")
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache DELETE failed for key {key}: {e}")
            return False
    
    @classmethod
    def exists(cls, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            client = cls.get_client()
            exists = client.exists(key) > 0
            if exists:
                logger.debug(f"Cache EXISTS: {key}")
            return exists
        except Exception as e:
            logger.error(f"Cache EXISTS failed for key {key}: {e}")
            return False
    
    @classmethod
    def increment(cls, key: str, amount: int = 1, ttl: int = None) -> int:
        """Increment counter"""
        try:
            client = cls.get_client()
            result = client.incrby(key, amount)
            if ttl:
                client.expire(key, ttl)
            logger.debug(f"Cache INCR: {key} -> {result}")
            return result
        except Exception as e:
            logger.error(f"Cache INCR failed for key {key}: {e}")
            return 0
    
    @classmethod
    def decrement(cls, key: str, amount: int = 1) -> int:
        """Decrement counter"""
        try:
            client = cls.get_client()
            result = client.decrby(key, amount)
            logger.debug(f"Cache DECR: {key} -> {result}")
            return result
        except Exception as e:
            logger.error(f"Cache DECR failed for key {key}: {e}")
            return 0
    
    @classmethod
    def lpush(cls, key: str, *values) -> int:
        """Push values to list"""
        try:
            client = cls.get_client()
            result = client.lpush(key, *values)
            logger.debug(f"Cache LPUSH: {key}")
            return result
        except Exception as e:
            logger.error(f"Cache LPUSH failed for key {key}: {e}")
            return 0
    
    @classmethod
    def rpop(cls, key: str, count: int = 1) -> Optional[Any]:
        """Pop from list"""
        try:
            client = cls.get_client()
            if count == 1:
                result = client.rpop(key)
            else:
                result = client.rpop(key, count)
            logger.debug(f"Cache RPOP: {key}")
            return result
        except Exception as e:
            logger.error(f"Cache RPOP failed for key {key}: {e}")
            return None
    
    @classmethod
    def lrange(cls, key: str, start: int = 0, stop: int = -1) -> List[Any]:
        """Get range from list"""
        try:
            client = cls.get_client()
            result = client.lrange(key, start, stop)
            logger.debug(f"Cache LRANGE: {key}")
            return result
        except Exception as e:
            logger.error(f"Cache LRANGE failed for key {key}: {e}")
            return []
    
    @classmethod
    def hset(cls, key: str, mapping: Dict[str, Any]) -> int:
        """Set hash"""
        try:
            client = cls.get_client()
            result = client.hset(key, mapping=mapping)
            logger.debug(f"Cache HSET: {key}")
            return result
        except Exception as e:
            logger.error(f"Cache HSET failed for key {key}: {e}")
            return 0
    
    @classmethod
    def hget(cls, key: str, field: str) -> Optional[Any]:
        """Get hash field"""
        try:
            client = cls.get_client()
            result = client.hget(key, field)
            if result:
                try:
                    result = pickle.loads(result)
                except Exception:
                    result = result.decode('utf-8')
            logger.debug(f"Cache HGET: {key}:{field}")
            return result
        except Exception as e:
            logger.error(f"Cache HGET failed for key {key}: {e}")
            return None
    
    @classmethod
    def hgetall(cls, key: str) -> Dict[str, Any]:
        """Get all hash fields"""
        try:
            client = cls.get_client()
            result = client.hgetall(key)
            logger.debug(f"Cache HGETALL: {key}")
            return result
        except Exception as e:
            logger.error(f"Cache HGETALL failed for key {key}: {e}")
            return {}
    
    @classmethod
    def sadd(cls, key: str, *members) -> int:
        """Add to set"""
        try:
            client = cls.get_client()
            result = client.sadd(key, *members)
            logger.debug(f"Cache SADD: {key}")
            return result
        except Exception as e:
            logger.error(f"Cache SADD failed for key {key}: {e}")
            return 0
    
    @classmethod
    def smembers(cls, key: str) -> set:
        """Get set members"""
        try:
            client = cls.get_client()
            result = client.smembers(key)
            logger.debug(f"Cache SMEMBERS: {key}")
            return result
        except Exception as e:
            logger.error(f"Cache SMEMBERS failed for key {key}: {e}")
            return set()
    
    @classmethod
    def flush_pattern(cls, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            client = cls.get_client()
            keys = client.keys(pattern)
            if keys:
                client.delete(*keys)
                logger.info(f"Flushed {len(keys)} cache keys matching pattern: {pattern}")
                return len(keys)
            return 0
        except Exception as e:
            logger.error(f"Cache FLUSH failed for pattern {pattern}: {e}")
            return 0
    
    @classmethod
    def flush_all(cls) -> bool:
        """Flush entire cache (use carefully!)"""
        try:
            client = cls.get_client()
            client.flushdb()
            logger.warning("Entire cache flushed")
            return True
        except Exception as e:
            logger.error(f"Cache FLUSH ALL failed: {e}")
            return False
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            client = cls.get_client()
            info = client.info()
            stats = {
                "used_memory": info.get('used_memory_human'),
                "connected_clients": info.get('connected_clients'),
                "total_connections": info.get('total_connections_received'),
                "commands_processed": info.get('total_commands_processed'),
                "db_keys": info.get('db0', {}).get('keys', 0),
            }
            return stats
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}


# Initialize on module import
try:
    CacheManager.initialize()
except Exception as e:
    logger.warning(f"Redis not available: {e}")
