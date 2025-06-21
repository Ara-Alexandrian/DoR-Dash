"""
User service layer for DoR-Dash.
Handles user management operations.
"""
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.core.security import get_password_hash
from app.db.models.user import User, UserRole

class UserService:
    """Service class for user management operations."""
    
    @staticmethod
    def get_all_users(db: Session) -> List[User]:
        """Get all users from database."""
        return db.query(User).all()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username or email."""
        return db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
    
    @staticmethod
    def create_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        full_name: str,
        role: UserRole = UserRole.STUDENT
    ) -> User:
        """
        Create a new user.
        
        Args:
            db: Database session
            username: Unique username
            email: Unique email address
            password: Plain text password
            full_name: User's full name
            role: User role (default: STUDENT)
            
        Returns:
            Created user object
            
        Raises:
            HTTPException: If username or email already exists
        """
        # Check if username already exists
        if UserService.get_user_by_username(db, username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check if email already exists
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role.value
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"Created new user: {username} ({role.value})")
        return user
    
    @staticmethod
    def update_user(
        db: Session,
        user: User,
        **kwargs
    ) -> User:
        """
        Update user information.
        
        Args:
            db: Database session
            user: User object to update
            **kwargs: Fields to update
            
        Returns:
            Updated user object
        """
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"Updated user: {user.username}")
        return user
    
    @staticmethod
    def delete_user(db: Session, user: User) -> bool:
        """
        Delete a user.
        
        Args:
            db: Database session
            user: User object to delete
            
        Returns:
            True if deletion successful
        """
        db.delete(user)
        db.commit()
        
        logger.info(f"Deleted user: {user.username}")
        return True
    
    @staticmethod
    def validate_user_exists(db: Session, user_id: int) -> User:
        """
        Validate that user exists and return it.
        
        Args:
            db: Database session
            user_id: User ID to validate
            
        Returns:
            User object
            
        Raises:
            HTTPException: If user not found
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    @staticmethod
    def get_students(db: Session) -> List[User]:
        """Get all users with STUDENT role."""
        return db.query(User).filter(User.role == UserRole.STUDENT.value).all()
    
    @staticmethod
    def get_faculty(db: Session) -> List[User]:
        """Get all users with FACULTY role."""
        return db.query(User).filter(User.role == UserRole.FACULTY.value).all()
    
    @staticmethod
    def is_admin(user: User) -> bool:
        """Check if user has admin role."""
        return user.role == UserRole.ADMIN.value
    
    @staticmethod
    def is_faculty_or_admin(user: User) -> bool:
        """Check if user has faculty or admin role."""
        return user.role in [UserRole.FACULTY.value, UserRole.ADMIN.value]