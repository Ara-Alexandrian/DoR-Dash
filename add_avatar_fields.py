#!/usr/bin/env python3
"""
Script to add avatar storage fields to the user table in PostgreSQL
Using database credentials from config.py
"""

import psycopg2
import psycopg2.extras
from psycopg2 import sql

# Database connection details from config.py
DB_CONFIG = {
    'host': '172.30.98.213',
    'port': 5432,
    'database': 'DoR',
    'user': 'DoRadmin',
    'password': '1232'
}

def connect_to_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def check_user_table_structure(cursor):
    """Check current user table structure"""
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'user'
        ORDER BY ordinal_position;
    """)
    columns = cursor.fetchall()
    
    print("Current user table structure:")
    for col in columns:
        print(f"  {col[0]}: {col[1]} (nullable: {col[2]})")
    
    return [col[0] for col in columns]

def add_avatar_fields(cursor):
    """Add avatar_data and avatar_content_type fields to user table"""
    
    # Check if avatar_data field exists
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'user' AND column_name = 'avatar_data';
    """)
    
    if not cursor.fetchone():
        print("Adding avatar_data field...")
        cursor.execute("""
            ALTER TABLE "user" 
            ADD COLUMN avatar_data BYTEA NULL;
        """)
        print("✅ avatar_data field added")
    else:
        print("✅ avatar_data field already exists")
    
    # Check if avatar_content_type field exists
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'user' AND column_name = 'avatar_content_type';
    """)
    
    if not cursor.fetchone():
        print("Adding avatar_content_type field...")
        cursor.execute("""
            ALTER TABLE "user" 
            ADD COLUMN avatar_content_type VARCHAR(50) NULL;
        """)
        print("✅ avatar_content_type field added")
    else:
        print("✅ avatar_content_type field already exists")

def check_existing_avatars(cursor):
    """Check for existing avatar_url entries"""
    cursor.execute("""
        SELECT id, username, avatar_url 
        FROM "user" 
        WHERE avatar_url IS NOT NULL;
    """)
    
    avatars = cursor.fetchall()
    print(f"\nFound {len(avatars)} users with existing avatar_url:")
    for user in avatars:
        print(f"  User {user[0]} ({user[1]}): {user[2]}")
    
    return avatars

def create_test_user_if_needed(cursor):
    """Create a test user for avatar testing if needed"""
    cursor.execute("""
        SELECT id, username FROM "user" WHERE username = 'testuser' LIMIT 1;
    """)
    
    test_user = cursor.fetchone()
    if not test_user:
        print("\nCreating test user for avatar testing...")
        cursor.execute("""
            INSERT INTO "user" (username, email, hashed_password, full_name, role, is_active)
            VALUES ('testuser', 'test@example.com', 'hashed_password', 'Test User', 'STUDENT', true)
            RETURNING id, username;
        """)
        test_user = cursor.fetchone()
        print(f"✅ Test user created: {test_user[1]} (ID: {test_user[0]})")
    else:
        print(f"✅ Test user exists: {test_user[1]} (ID: {test_user[0]})")
    
    return test_user

def main():
    """Main function to add avatar fields to PostgreSQL"""
    print("🔧 Adding avatar storage fields to PostgreSQL user table...")
    print(f"Connecting to PostgreSQL at {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    
    conn = connect_to_db()
    if not conn:
        print("❌ Failed to connect to database")
        return
    
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Check current table structure
        print("\n1. Checking current user table structure...")
        columns = check_user_table_structure(cursor)
        
        # Add avatar fields
        print("\n2. Adding avatar storage fields...")
        add_avatar_fields(cursor)
        
        # Check for existing avatars
        print("\n3. Checking existing avatar URLs...")
        existing_avatars = check_existing_avatars(cursor)
        
        # Create test user if needed
        print("\n4. Setting up test user...")
        test_user = create_test_user_if_needed(cursor)
        
        # Commit changes
        conn.commit()
        
        print("\n✅ Avatar fields successfully added to PostgreSQL!")
        print("\nNext steps:")
        print("- Update backend code to use database storage for avatars")
        print("- Implement Redis caching for avatar serving")
        print("- Create avatar serving endpoint")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()