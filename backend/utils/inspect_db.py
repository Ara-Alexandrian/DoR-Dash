#!/usr/bin/env python3
"""
Database inspection script for DoR-Dash
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

# Database connection URL
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

def inspect_database():
    """Inspect the current database structure"""
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        print("\n=== DATABASE INSPECTION ===")
        
        # Check existing tables
        print("\n1. EXISTING TABLES:")
        tables = inspector.get_table_names()
        for table in sorted(tables):
            print(f"  - {table}")
        
        # Check enum types
        print("\n2. ENUM TYPES:")
        result = conn.execute(text("""
            SELECT typname FROM pg_type 
            WHERE typtype = 'e' 
            ORDER BY typname;
        """))
        for row in result:
            print(f"  - {row[0]}")
        
        # Check user table structure if it exists
        if 'user' in tables:
            print("\n3. USER TABLE STRUCTURE:")
            columns = inspector.get_columns('user')
            for col in columns:
                print(f"  - {col['name']}: {col['type']} (nullable: {col['nullable']})")
        
        # Check constraints and foreign keys
        print("\n4. FOREIGN KEY CONSTRAINTS:")
        for table in tables:
            fks = inspector.get_foreign_keys(table)
            if fks:
                print(f"  Table: {table}")
                for fk in fks:
                    print(f"    - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        
        # Check alembic version
        print("\n5. ALEMBIC VERSION:")
        try:
            result = conn.execute(text("SELECT version_num FROM alembic_version;"))
            version = result.scalar()
            print(f"  Current version: {version}")
        except Exception as e:
            print(f"  Error getting version: {e}")
        
        # Check for any data in user table
        if 'user' in tables:
            print("\n6. USER TABLE DATA:")
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM \"user\";"))
                count = result.scalar()
                print(f"  Total users: {count}")
                
                if count > 0:
                    result = conn.execute(text('SELECT username FROM "user" LIMIT 5;'))
                    print("  Sample users:")
                    for row in result:
                        print(f"    - {row[0]}")
            except Exception as e:
                print(f"  Error querying user table: {e}")

if __name__ == "__main__":
    inspect_database()