#!/usr/bin/env python3
"""
Direct database connection test script
"""

import os
import sys
import socket
import json
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_socket_connection():
    """Test socket connection to database"""
    host = os.getenv("POSTGRES_SERVER", "172.30.98.213")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✓ Socket connection successful to {host}:{port}")
            return True
        else:
            print(f"✗ Socket connection failed to {host}:{port}")
            return False
    except Exception as e:
        print(f"✗ Socket connection error: {e}")
        return False

def test_with_asyncpg():
    """Try to use asyncpg if available"""
    try:
        import asyncpg
        import asyncio
        
        async def connect():
            host = os.getenv("POSTGRES_SERVER", "172.30.98.213")
            port = int(os.getenv("POSTGRES_PORT", "5432"))
            user = os.getenv("POSTGRES_USER", "DoRadmin")
            password = os.getenv("POSTGRES_PASSWORD", "1232")
            database = os.getenv("POSTGRES_DB", "DoR")
            
            print(f"Attempting connection to: {host}:{port}/{database} as {user}")
            
            try:
                conn = await asyncpg.connect(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=database
                )
                
                print("✓ Successfully connected to database with asyncpg")
                
                # Test 1: Check if we can connect
                result = await conn.fetchval("SELECT 1")
                print(f"✓ Connection test passed: {result}")
                
                # Test 2: Check if 'user' table exists
                table_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'user'
                    )
                """)
                print(f"✓ 'user' table exists: {table_exists}")
                
                # Test 3: Check table structure
                if table_exists:
                    columns = await conn.fetch("""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_schema = 'public' AND table_name = 'user'
                        ORDER BY ordinal_position
                    """)
                    print("✓ User table structure:")
                    for col in columns:
                        print(f"  - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
                
                # Test 4: Check if cerebro user exists
                cerebro_user = await conn.fetchrow("""
                    SELECT id, username, hashed_password, role, is_active
                    FROM "user"
                    WHERE username = 'cerebro'
                """)
                
                if cerebro_user:
                    print("✓ Cerebro user found:")
                    print(f"  - ID: {cerebro_user['id']}")
                    print(f"  - Username: {cerebro_user['username']}")
                    print(f"  - Password hash: {cerebro_user['hashed_password'][:20]}...")
                    print(f"  - Role: {cerebro_user['role']}")
                    print(f"  - Active: {cerebro_user['is_active']}")
                else:
                    print("✗ Cerebro user not found")
                
                # Test 5: Count total users
                user_count = await conn.fetchval('SELECT COUNT(*) FROM "user"')
                print(f"✓ Total users in database: {user_count}")
                
                # Test 6: Check for any schema issues
                print("\n=== SCHEMA VALIDATION ===")
                
                # Check for foreign key constraints
                fk_constraints = await conn.fetch("""
                    SELECT tc.constraint_name, tc.table_name, kcu.column_name, 
                           ccu.table_name AS foreign_table_name,
                           ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                    ORDER BY tc.table_name, tc.constraint_name
                """)
                
                print(f"✓ Found {len(fk_constraints)} foreign key constraints")
                for fk in fk_constraints:
                    print(f"  - {fk['table_name']}.{fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
                
                # Check for enum types
                enums = await conn.fetch("""
                    SELECT typname, enumlabel
                    FROM pg_type
                    JOIN pg_enum ON pg_type.oid = pg_enum.enumtypid
                    ORDER BY typname, enumsortorder
                """)
                
                if enums:
                    print(f"✓ Found {len(enums)} enum values")
                    current_enum = None
                    for enum in enums:
                        if enum['typname'] != current_enum:
                            current_enum = enum['typname']
                            print(f"  - {current_enum}:")
                        print(f"    * {enum['enumlabel']}")
                
                await conn.close()
                return True
                
            except Exception as e:
                print(f"✗ Database connection failed: {e}")
                return False
        
        return asyncio.run(connect())
        
    except ImportError:
        print("✗ asyncpg not available")
        return False

def test_with_sqlalchemy():
    """Try to use SQLAlchemy if available"""
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.exc import SQLAlchemyError
        
        host = os.getenv("POSTGRES_SERVER", "172.30.98.213")
        port = int(os.getenv("POSTGRES_PORT", "5432"))
        user = os.getenv("POSTGRES_USER", "DoRadmin")
        password = os.getenv("POSTGRES_PASSWORD", "1232")
        database = os.getenv("POSTGRES_DB", "DoR")
        
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        print(f"SQLAlchemy connection string: postgresql://{user}:***@{host}:{port}/{database}")
        
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            print("✓ Successfully connected to database with SQLAlchemy")
            
            # Test queries
            result = conn.execute(text("SELECT 1")).scalar()
            print(f"✓ Connection test passed: {result}")
            
            # Check if user table exists
            table_exists = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'user'
                )
            """)).scalar()
            print(f"✓ 'user' table exists: {table_exists}")
            
            if table_exists:
                # Check cerebro user
                cerebro_user = conn.execute(text("""
                    SELECT id, username, hashed_password, role, is_active
                    FROM "user"
                    WHERE username = 'cerebro'
                """)).fetchone()
                
                if cerebro_user:
                    print("✓ Cerebro user found:")
                    print(f"  - ID: {cerebro_user[0]}")
                    print(f"  - Username: {cerebro_user[1]}")
                    print(f"  - Password hash: {cerebro_user[2][:20]}...")
                    print(f"  - Role: {cerebro_user[3]}")
                    print(f"  - Active: {cerebro_user[4]}")
                else:
                    print("✗ Cerebro user not found")
                    
                    # Show all users
                    all_users = conn.execute(text("""
                        SELECT username, role, is_active
                        FROM "user"
                        ORDER BY id
                    """)).fetchall()
                    
                    print(f"✓ All users in database ({len(all_users)}):")
                    for user_row in all_users:
                        print(f"  - {user_row[0]} ({user_row[1]}) - Active: {user_row[2]}")
        
        return True
        
    except ImportError:
        print("✗ SQLAlchemy not available")
        return False
    except SQLAlchemyError as e:
        print(f"✗ SQLAlchemy error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error with SQLAlchemy: {e}")
        return False

def main():
    print("=== DATABASE CONNECTION TEST ===")
    print(f"Testing connection to PostgreSQL database")
    
    # Test socket connectivity first
    if not test_socket_connection():
        print("Cannot proceed - database server not reachable")
        sys.exit(1)
    
    # Try different connection methods
    success = False
    
    if test_with_asyncpg():
        success = True
    elif test_with_sqlalchemy():
        success = True
    else:
        print("✗ No suitable database drivers available")
        print("Try installing: pip install asyncpg or pip install sqlalchemy psycopg2-binary")
    
    if success:
        print("\n✓ Database connection test completed successfully")
    else:
        print("\n✗ Database connection test failed")
        sys.exit(1)

if __name__ == "__main__":
    main()