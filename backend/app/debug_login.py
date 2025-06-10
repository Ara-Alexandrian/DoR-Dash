#!/usr/bin/env python3

import os
import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Add the backend directory to the path  
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.core.security import verify_password, get_password_hash
from app.db.models.user import User as UserModel

def debug_login():
    """Debug the login process step by step"""
    
    print("🔍 Debugging login process...")
    
    # Test database connection
    try:
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI_SYNC)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as db:
            print("✅ Database connection successful")
            
            # Check if cerebro user exists
            user = db.query(UserModel).filter(UserModel.username == "cerebro").first()
            
            if not user:
                print("❌ User 'cerebro' not found in database")
                return
            
            print(f"✅ User 'cerebro' found:")
            print(f"   - ID: {user.id}")
            print(f"   - Username: {user.username}")
            print(f"   - Email: {user.email}")
            print(f"   - Role: {user.role}")
            print(f"   - Active: {user.is_active}")
            print(f"   - Hashed Password: {user.hashed_password[:20]}...")
            
            # Test password verification
            try:
                password_valid = verify_password("123", user.hashed_password)
                print(f"✅ Password verification: {password_valid}")
            except Exception as e:
                print(f"❌ Password verification failed: {e}")
                return
            
            # Test hashing a new password
            try:
                test_hash = get_password_hash("123")
                print(f"✅ New password hash: {test_hash[:20]}...")
            except Exception as e:
                print(f"❌ Password hashing failed: {e}")
                return
                
            print("✅ All login components working correctly")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_login()