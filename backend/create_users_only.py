#!/usr/bin/env python3
"""
Simple script to create initial users for testing authentication
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import get_password_hash

# Database connection URL
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

def create_users_table_if_not_exists(engine):
    """Create users table and enum if they don't exist"""
    with engine.connect() as conn:
        # Create enum type
        conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE userrole AS ENUM ('STUDENT', 'FACULTY', 'SECRETARY', 'ADMIN');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        # Create users table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS "user" (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                preferred_email VARCHAR(100),
                phone VARCHAR(20),
                role userrole NOT NULL DEFAULT 'STUDENT',
                hashed_password VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        conn.commit()

def create_test_users(engine):
    """Create test users"""
    users_data = [
        {
            "username": "cerebro",
            "email": "cerebro@dor.edu",
            "full_name": "Charles Xavier",
            "role": "ADMIN",
            "password": "123"
        },
        {
            "username": "aalexandrian",
            "email": "aalexandrian@dor.edu",
            "full_name": "Alex Alexandrian",
            "role": "STUDENT",
            "password": "12345678"
        },
        {
            "username": "ssmith",
            "email": "ssmith@dor.edu",
            "full_name": "Sarah Smith",
            "role": "FACULTY",
            "password": "12345678"
        }
    ]
    
    with engine.connect() as conn:
        for user_data in users_data:
            # Check if user exists
            result = conn.execute(text("""
                SELECT COUNT(*) FROM "user" WHERE username = :username
            """), {"username": user_data["username"]})
            
            if result.scalar() == 0:
                # Create user
                hashed_password = get_password_hash(user_data["password"])
                conn.execute(text("""
                    INSERT INTO "user" (username, email, full_name, role, hashed_password, is_active)
                    VALUES (:username, :email, :full_name, :role, :hashed_password, :is_active)
                """), {
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "full_name": user_data["full_name"],
                    "role": user_data["role"],
                    "hashed_password": hashed_password,
                    "is_active": True
                })
                print(f"Created user: {user_data['username']} (role: {user_data['role']})")
            else:
                print(f"User already exists: {user_data['username']}")
        
        conn.commit()

def main():
    """Main function"""
    print(f"Creating users in database: {DATABASE_URL}")
    
    engine = create_engine(DATABASE_URL)
    
    try:
        create_users_table_if_not_exists(engine)
        create_test_users(engine)
        print("\nUsers created successfully!")
        print("Test users:")
        print("  - cerebro (admin) - password: 123")
        print("  - aalexandrian (student) - password: 12345678")
        print("  - ssmith (faculty) - password: 12345678")
        
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()