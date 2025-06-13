#!/usr/bin/env python3
"""
Fix user table by adding missing role column
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.core.config import settings

# Database connection URL
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

def fix_user_table():
    """Add missing role column to user table"""
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Check if role column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user' AND column_name = 'role';
            """))
            
            if result.rowcount == 0:
                print("Adding role column to user table...")
                
                # Add role column with default value
                conn.execute(text("""
                    ALTER TABLE "user" 
                    ADD COLUMN role userrole DEFAULT 'STUDENT' NOT NULL;
                """))
                
                print("Role column added successfully!")
                
                # Update existing users with appropriate roles
                print("Updating existing user roles...")
                
                # Set cerebro as admin
                conn.execute(text("""
                    UPDATE "user" SET role = 'ADMIN' WHERE username = 'cerebro';
                """))
                
                # Set other specific users
                conn.execute(text("""
                    UPDATE "user" SET role = 'STUDENT' 
                    WHERE username IN ('aalexandrian', 'testuser', 'student1');
                """))
                
                conn.commit()
                print("User roles updated successfully!")
                
                # Verify the changes
                result = conn.execute(text("""
                    SELECT username, role FROM "user" ORDER BY username;
                """))
                
                print("\nCurrent users and roles:")
                for row in result:
                    print(f"  - {row[0]}: {row[1]}")
                    
            else:
                print("Role column already exists!")
                
        except Exception as e:
            print(f"Error fixing user table: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    fix_user_table()