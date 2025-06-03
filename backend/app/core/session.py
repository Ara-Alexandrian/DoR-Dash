import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from redis.asyncio import Redis

from app.core.config import settings


class SessionManager:
    """
    Session manager using Redis for backend storage
    """
    def __init__(self, redis_client: Redis, prefix: str = "session:", expire: int = None):
        self.redis = redis_client
        self.prefix = prefix
        self.expire = expire or settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    
    def _get_key(self, session_id: str) -> str:
        """Get full Redis key for session"""
        return f"{self.prefix}{session_id}"
    
    async def create_session(self, data: Dict[str, Any] = None) -> str:
        """
        Create a new session with data and return session ID
        
        Args:
            data: Initial session data
            
        Returns:
            str: New session ID
        """
        session_id = str(uuid.uuid4())
        key = self._get_key(session_id)
        
        session_data = {
            "created_at": datetime.now().isoformat(),
            "last_access": datetime.now().isoformat(),
            "data": data or {}
        }
        
        await self.redis.set(key, json.dumps(session_data), ex=self.expire)
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data by session ID
        
        Args:
            session_id: Session ID
            
        Returns:
            dict: Session data or None if session doesn't exist
        """
        key = self._get_key(session_id)
        data = await self.redis.get(key)
        
        if not data:
            return None
        
        session_data = json.loads(data)
        
        # Update last access time
        session_data["last_access"] = datetime.now().isoformat()
        await self.redis.set(key, json.dumps(session_data), ex=self.expire)
        
        return session_data.get("data", {})
    
    async def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Update session data
        
        Args:
            session_id: Session ID
            data: New session data
            
        Returns:
            bool: Success status
        """
        key = self._get_key(session_id)
        session_json = await self.redis.get(key)
        
        if not session_json:
            return False
        
        session_data = json.loads(session_json)
        session_data["last_access"] = datetime.now().isoformat()
        session_data["data"] = data
        
        await self.redis.set(key, json.dumps(session_data), ex=self.expire)
        return True
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session
        
        Args:
            session_id: Session ID
            
        Returns:
            bool: Success status
        """
        key = self._get_key(session_id)
        deleted = await self.redis.delete(key)
        return deleted > 0


async def get_session_manager(redis: Redis = None) -> SessionManager:
    """
    Dependency for getting SessionManager instance
    
    Args:
        redis: Redis client from dependency injection
        
    Returns:
        SessionManager: Instance of SessionManager
    """
    if redis is None:
        from app.core.redis import redis_client
        redis = redis_client
    
    return SessionManager(redis)