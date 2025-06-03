import json
from typing import Any, Dict, Optional, TypeVar, Union
from redis.asyncio import Redis

T = TypeVar("T")

class RedisCache:
    """
    Utility class for caching data in Redis
    """
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """
        Set a key with value in Redis cache with expiration time (default 1 hour)
        
        Args:
            key: Redis key
            value: Value to cache (will be JSON serialized)
            expire: Expiration time in seconds, default 3600 (1 hour)
            
        Returns:
            bool: Success status
        """
        try:
            serialized = json.dumps(value)
            await self.redis.set(key, serialized, ex=expire)
            return True
        except Exception:
            # Log the error in a production environment
            return False
    
    async def get(self, key: str, default: Optional[T] = None) -> Union[Any, T]:
        """
        Get a value from Redis cache by key
        
        Args:
            key: Redis key
            default: Default value if key doesn't exist
            
        Returns:
            Value from cache or default
        """
        try:
            value = await self.redis.get(key)
            if value is None:
                return default
            return json.loads(value)
        except Exception:
            # Log the error in a production environment
            return default
    
    async def delete(self, key: str) -> bool:
        """
        Delete a key from Redis cache
        
        Args:
            key: Redis key
            
        Returns:
            bool: Success status
        """
        try:
            await self.redis.delete(key)
            return True
        except Exception:
            # Log the error in a production environment
            return False
    
    async def clear_pattern(self, pattern: str) -> bool:
        """
        Delete all keys matching pattern from Redis cache
        
        Args:
            pattern: Redis key pattern (e.g., "user:*")
            
        Returns:
            bool: Success status
        """
        try:
            cursor = 0
            while True:
                cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                if keys:
                    await self.redis.delete(*keys)
                if cursor == 0:
                    break
            return True
        except Exception:
            # Log the error in a production environment
            return False


async def get_cache(redis: Redis = None) -> RedisCache:
    """
    Dependency for getting RedisCache instance
    
    Args:
        redis: Redis client from dependency injection
        
    Returns:
        RedisCache: Instance of RedisCache
    """
    if redis is None:
        from app.core.redis import redis_client
        redis = redis_client
    
    return RedisCache(redis)