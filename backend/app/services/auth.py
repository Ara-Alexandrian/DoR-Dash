from datetime import timedelta
from typing import Optional, Union, Any
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status

from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.core.session import get_session_manager, SessionManager
from app.db.models.user import User
from app.schemas.auth import TokenPayload

# For use in mock mode
class User:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @property
    def is_active(self):
        return getattr(self, "_is_active", True)

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user by username and password
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(
    db: Session, 
    token: str,
    session_manager: SessionManager = Depends(get_session_manager)
) -> Optional[User]:
    """
    Get current user from JWT token
    """
    # Check if token is blacklisted
    token_key = f"blacklist:{token}"
    is_blacklisted = await session_manager.redis.get(token_key)
    if is_blacklisted:
        return None
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except JWTError:
        return None
    
    if token_data.sub is None:
        return None
    
    user = db.query(User).filter(User.id == token_data.sub).first()
    if user is None:
        return None
    
    if not user.is_active:
        return None
    
    return user
    
async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user
    """
    if not current_user.is_active:
        raise ValueError("Inactive user")
    return current_user