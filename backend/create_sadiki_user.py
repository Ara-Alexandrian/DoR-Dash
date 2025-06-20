#!/usr/bin/env python3
"""
Create user 'sadiki' with password 'test'
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import required modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.models.user import User as UserModel
from app.db.models.user import UserRole

def create_sadiki_user():
    """Create user 'sadiki' with password 'test'"""
    
    # Database connection
    DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        # Check if user already exists
        existing_user = db.query(UserModel).filter(UserModel.username == "sadiki").first()
        
        if existing_user:
            print("✅ User 'sadiki' already exists. Updating password...")
            # Update the existing user's password
            existing_user.hashed_password = get_password_hash("test")
            db.commit()
            print("✅ Password updated for user 'sadiki'")
        else:
            print("🔄 Creating new user 'sadiki'...")
            # Create new user
            new_user = UserModel(
                username="sadiki",
                email="sadiki@dor.edu",
                hashed_password=get_password_hash("test"),
                role=UserRole.STUDENT,  # Default role
                is_active=True
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            print(f"✅ User 'sadiki' created successfully with ID: {new_user.id}")
        
        # Verify the user was created/updated
        user = db.query(UserModel).filter(UserModel.username == "sadiki").first()
        if user:
            print(f"✅ Verification - User 'sadiki' found:")
            print(f"   - ID: {user.id}")
            print(f"   - Username: {user.username}")
            print(f"   - Email: {user.email}")
            print(f"   - Role: {user.role}")
            print(f"   - Active: {user.is_active}")
            print(f"   - Password hash: {user.hashed_password[:50]}...")
        else:
            print("❌ Error: User 'sadiki' not found after creation")

if __name__ == "__main__":
    create_sadiki_user()