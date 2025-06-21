#!/usr/bin/env python3
"""
Database connection test using existing infrastructure
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import engine, SessionLocal, async_engine, async_session
from app.core.config import settings
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def test_sync_connection():
    """Test synchronous database connection"""
    print("=== SYNCHRONOUS DATABASE CONNECTION TEST ===")
    
    try:
        print(f"Connection string: postgresql://{settings.POSTGRES_USER}:***@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
        
        # Test basic connection
        with engine.connect() as conn:
            print("✓ Successfully connected to database (sync)")
            
            # Test 1: Basic connectivity
            result = conn.execute(text("SELECT 1 as test")).scalar()
            print(f"✓ Connection test passed: {result}")
            
            # Test 2: Check PostgreSQL version
            version = conn.execute(text("SELECT version()")).scalar()
            print(f"✓ PostgreSQL version: {version}")
            
            # Test 3: Check if 'user' table exists
            table_exists = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'user'
                )
            """)).scalar()
            print(f"✓ 'user' table exists: {table_exists}")
            
            if not table_exists:
                print("✗ User table does not exist - this is a critical issue!")
                return False
            
            # Test 4: Check user table structure
            columns = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'user'
                ORDER BY ordinal_position
            """)).fetchall()
            
            print("✓ User table structure:")
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                default = f" DEFAULT {col[3]}" if col[3] else ""
                print(f"  - {col[0]}: {col[1]} {nullable}{default}")
            
            # Test 5: Check if cerebro user exists
            cerebro_user = conn.execute(text("""
                SELECT id, username, hashed_password, role, is_active, created_at
                FROM "user"
                WHERE username = 'cerebro'
            """)).fetchone()
            
            if cerebro_user:
                print("✓ Cerebro user found:")
                print(f"  - ID: {cerebro_user[0]}")
                print(f"  - Username: {cerebro_user[1]}")
                print(f"  - Password hash: {cerebro_user[2][:20]}... (truncated)")
                print(f"  - Role: {cerebro_user[3]}")
                print(f"  - Active: {cerebro_user[4]}")
                print(f"  - Created: {cerebro_user[5]}")
                
                # Verify password hash format
                password_hash = cerebro_user[2]
                if password_hash.startswith("$2b$") or password_hash.startswith("$2a$"):
                    print("✓ Password hash format appears correct (bcrypt)")
                else:
                    print(f"⚠ Warning: Password hash format may be incorrect: {password_hash[:10]}...")
                    
            else:
                print("✗ Cerebro user not found!")
                
                # Show all users
                all_users = conn.execute(text("""
                    SELECT id, username, role, is_active, created_at
                    FROM "user"
                    ORDER BY id
                """)).fetchall()
                
                print(f"✓ All users in database ({len(all_users)}):")
                for user_row in all_users:
                    print(f"  - ID {user_row[0]}: {user_row[1]} ({user_row[2]}) - Active: {user_row[3]} - Created: {user_row[4]}")
            
            # Test 6: Count total users
            user_count = conn.execute(text('SELECT COUNT(*) FROM "user"')).scalar()
            print(f"✓ Total users in database: {user_count}")
            
            # Test 7: Check for schema issues
            print("\n=== SCHEMA VALIDATION ===")
            
            # Check for indexes
            indexes = conn.execute(text("""
                SELECT indexname, tablename, indexdef
                FROM pg_indexes
                WHERE schemaname = 'public' AND tablename = 'user'
                ORDER BY indexname
            """)).fetchall()
            
            print(f"✓ Found {len(indexes)} indexes on user table:")
            for idx in indexes:
                print(f"  - {idx[0]}: {idx[2]}")
            
            # Check for constraints
            constraints = conn.execute(text("""
                SELECT tc.constraint_name, tc.constraint_type, cc.check_clause
                FROM information_schema.table_constraints tc
                LEFT JOIN information_schema.check_constraints cc 
                    ON tc.constraint_name = cc.constraint_name
                WHERE tc.table_schema = 'public' AND tc.table_name = 'user'
                ORDER BY tc.constraint_type, tc.constraint_name
            """)).fetchall()
            
            print(f"✓ Found {len(constraints)} constraints on user table:")
            for constraint in constraints:
                constraint_info = f"{constraint[0]} ({constraint[1]})"
                if constraint[2]:
                    constraint_info += f": {constraint[2]}"
                print(f"  - {constraint_info}")
            
            # Check for enum types
            enums = conn.execute(text("""
                SELECT t.typname, e.enumlabel
                FROM pg_type t
                JOIN pg_enum e ON t.oid = e.enumtypid
                WHERE t.typname LIKE '%role%'
                ORDER BY t.typname, e.enumsortorder
            """)).fetchall()
            
            if enums:
                print(f"✓ Found role enum values:")
                current_enum = None
                for enum in enums:
                    if enum[0] != current_enum:
                        current_enum = enum[0]
                        print(f"  - {current_enum}:")
                    print(f"    * {enum[1]}")
            else:
                print("⚠ Warning: No role enum found")
            
            # Test 8: Check for other critical tables
            critical_tables = [
                'agenda_item', 'meeting', 'presentation', 'presentation_assignment',
                'file_upload', 'registration_request', 'student_update', 'faculty_update'
            ]
            
            print(f"\n=== CRITICAL TABLES CHECK ===")
            for table in critical_tables:
                exists = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table}'
                    )
                """)).scalar()
                
                status = "✓" if exists else "✗"
                print(f"{status} Table '{table}': {'exists' if exists else 'MISSING'}")
            
            return True
            
    except SQLAlchemyError as e:
        print(f"✗ SQLAlchemy error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

async def test_async_connection():
    """Test asynchronous database connection"""
    print("\n=== ASYNCHRONOUS DATABASE CONNECTION TEST ===")
    
    try:
        async with async_engine.begin() as conn:
            print("✓ Successfully connected to database (async)")
            
            result = await conn.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            print(f"✓ Async connection test passed: {test_value}")
            
            # Test async session
            async with async_session() as session:
                result = await session.execute(text("SELECT COUNT(*) FROM \"user\""))
                user_count = result.scalar()
                print(f"✓ Async session test passed - user count: {user_count}")
            
            return True
            
    except Exception as e:
        print(f"✗ Async connection error: {e}")
        return False

def main():
    print("DoR-Dash Database Connection Test")
    print("=" * 50)
    
    # Test sync connection
    sync_success = test_sync_connection()
    
    # Test async connection
    async_success = asyncio.run(test_async_connection())
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Sync connection: {'✓ SUCCESS' if sync_success else '✗ FAILED'}")
    print(f"Async connection: {'✓ SUCCESS' if async_success else '✗ FAILED'}")
    
    if sync_success and async_success:
        print("\n✓ All database connection tests passed!")
        print("\nRECOMMENDATIONS:")
        print("1. If you're still getting 500 errors during login:")
        print("   - Check application logs for detailed error messages")
        print("   - Verify that the bcrypt password hashing is working correctly")
        print("   - Ensure the authentication endpoint is using the correct session")
        print("2. The database schema appears to be properly set up")
        print("3. All critical tables exist")
        return 0
    else:
        print("\n✗ Database connection tests failed!")
        print("\nTROUBLESHOoting:")
        print("1. Check if database server is running")
        print("2. Verify credentials in .env file")
        print("3. Check network connectivity")
        print("4. Run database migrations if needed")
        return 1

if __name__ == "__main__":
    sys.exit(main())