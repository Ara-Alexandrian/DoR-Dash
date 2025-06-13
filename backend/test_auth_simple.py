#!/usr/bin/env python3
"""
Simple test of authentication system to debug issues
"""

import sys
from pathlib import Path
import traceback

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("Testing imports...")
    from app.core.config import settings
    print(f"✓ Config imported, DB: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
    
    from app.core.security import get_password_hash, verify_password
    print("✓ Security module imported")
    
    # Test password hashing
    test_password = "test123"
    hashed = get_password_hash(test_password)
    print(f"✓ Password hashing works: {len(hashed)} chars")
    
    # Test password verification
    is_valid = verify_password(test_password, hashed)
    print(f"✓ Password verification works: {is_valid}")
    
    print("\nTesting database connection...")
    from sqlalchemy import create_engine, text
    
    # Create engine
    DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    print(f"Database URL: {DATABASE_URL}")
    
    engine = create_engine(DATABASE_URL)
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"✓ Database connected: {version[:50]}...")
        
        # Check if user table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'user'
            );
        """))
        user_table_exists = result.scalar()
        print(f"✓ User table exists: {user_table_exists}")
        
        if user_table_exists:
            result = conn.execute(text("SELECT COUNT(*) FROM \"user\""))
            user_count = result.scalar()
            print(f"✓ Users in database: {user_count}")
            
            if user_count > 0:
                result = conn.execute(text("SELECT username, role FROM \"user\" LIMIT 3"))
                users = result.fetchall()
                print(f"✓ Sample users: {users}")
        else:
            print("⚠ User table does not exist")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    traceback.print_exc()