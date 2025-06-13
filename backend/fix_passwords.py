#!/usr/bin/env python3
"""
Fix user passwords to ensure they match expected values
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models.user import User
from app.core.security import get_password_hash

# Database connection URL
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

def fix_passwords():
    """Fix user passwords to match expected values"""
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    # Expected passwords for known users
    expected_passwords = {
        "cerebro": "123",
        "aalexandrian": "12345678",
        "jdoe": "12345678",
        "ssmith": "12345678",
        "testuser": "12345678",
        "student1": "12345678"
    }
    
    with Session(engine) as session:
        print("\n=== FIXING USER PASSWORDS ===")
        
        for username, password in expected_passwords.items():
            user = session.query(User).filter(User.username == username).first()
            if user:
                # Update password hash
                user.hashed_password = get_password_hash(password)
                print(f"✅ Updated password for {username}")
            else:
                print(f"❌ User {username} not found")
        
        session.commit()
        print("\n✅ All passwords updated successfully!")

if __name__ == "__main__":
    fix_passwords()