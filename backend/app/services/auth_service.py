"""
Authentication service layer for DoR-Dash.
Handles user authentication, token management, and password operations.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.core.security import security_config, verify_password, get_password_hash
from app.db.models.user import User, UserRole

class AuthService:
    """Service class for authentication operations."""
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username/password.
        
        Args:
            db: Database session
            username: Username or email
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        logger.debug(f"Authentication attempt for user: {username}")
        
        # Try to find user by username or email
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            logger.warning(f"User not found: {username}")
            return None
        
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Invalid password for user: {username}")
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        logger.info(f"Successful authentication for user: {username}")
        return user
    
    @staticmethod
    def create_access_token(user: User) -> str:
        """
        Create JWT access token for authenticated user.
        
        Args:
            user: Authenticated user object
            
        Returns:
            JWT token string
        """
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role
        }
        
        return security_config.create_access_token(token_data)
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload if valid, None otherwise
        """
        return security_config.verify_token(token)
    
    @staticmethod
    def change_password(db: Session, user: User, current_password: str, new_password: str) -> bool:
        """
        Change user password after verifying current password.
        
        Args:
            db: Database session
            user: User object
            current_password: Current password (plain text)
            new_password: New password (plain text)
            
        Returns:
            True if password changed successfully
            
        Raises:
            HTTPException: If current password is invalid
        """
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash and update new password
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Password changed for user: {user.username}")
        return True
    
    @staticmethod
    def validate_user_permissions(current_user: User, required_roles: list[UserRole]) -> bool:
        """
        Validate if user has required permissions.
        
        Args:
            current_user: Current authenticated user
            required_roles: List of required roles
            
        Returns:
            True if user has required permissions
        """
        user_role = UserRole(current_user.role)
        return user_role in required_roles
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        Get user by username or email.
        
        Args:
            db: Database session
            username: Username or email
            
        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()