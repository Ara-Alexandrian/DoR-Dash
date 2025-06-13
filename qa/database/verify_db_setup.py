#!/usr/bin/env python3
"""
Verify database setup and fix any issues.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.parent.parent / 'backend'
if backend_path.exists():
    sys.path.insert(0, str(backend_path))
else:
    sys.path.insert(0, '/app/backend')

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import Session
    from app.core.config import settings
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def check_and_setup_database():
    """Check database state and setup if needed."""
    DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    
    print(f"Connecting to database: {settings.POSTGRES_DB}@{settings.POSTGRES_SERVER}")
    print("-" * 60)
    
    engine = create_engine(DATABASE_URL)
    
    with Session(engine) as session:
        # Check what tables exist
        tables = session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public' 
            ORDER BY table_name
        """)).fetchall()
        
        table_names = [t[0] for t in tables]
        print(f"Existing tables: {table_names}")
        
        # Check enum types
        enums = session.execute(text("""
            SELECT typname 
            FROM pg_type 
            WHERE typtype = 'e'
            ORDER BY typname
        """)).fetchall()
        
        enum_names = [e[0] for e in enums]
        print(f"Existing enum types: {enum_names}")
        
        # Expected tables
        expected_tables = ['user', 'meeting', 'agenda_item', 'fileupload', 'registration_request']
        missing_tables = [t for t in expected_tables if t not in table_names]
        
        if missing_tables:
            print(f"\nMissing tables: {missing_tables}")
            
            # Try to create the missing user table first as others depend on it
            if 'user' in missing_tables:
                print("Creating user table...")
                try:
                    session.execute(text("""
                        CREATE TABLE "user" (
                            id SERIAL PRIMARY KEY,
                            username VARCHAR(50) UNIQUE NOT NULL,
                            email VARCHAR(100) UNIQUE NOT NULL,
                            full_name VARCHAR(100) NOT NULL,
                            hashed_password VARCHAR(255) NOT NULL,
                            role userrole NOT NULL DEFAULT 'STUDENT',
                            is_active BOOLEAN NOT NULL DEFAULT true,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    session.commit()
                    print("✅ User table created")
                except Exception as e:
                    print(f"❌ Failed to create user table: {e}")
                    session.rollback()
        
        # Check if we have any data
        if 'user' in table_names:
            user_count = session.execute(text("SELECT COUNT(*) FROM \"user\"")).scalar()
            print(f"\nUser count: {user_count}")
            
            if user_count == 0:
                print("No users found. Database needs initial data.")
                return False
        
        return len(missing_tables) == 0

if __name__ == "__main__":
    try:
        success = check_and_setup_database()
        if success:
            print("\n✅ Database setup verified!")
        else:
            print("\n❌ Database needs setup")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)