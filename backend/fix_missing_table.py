#!/usr/bin/env python3
"""
Fix missing presentation_assignment_files table
This script creates the missing table that should have been created by the migration.
"""

import os
import sys
import traceback
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def get_database_url():
    """Get database URL from environment variables"""
    return os.getenv('DATABASE_URL', 'postgresql://DoRadmin:1232@172.30.98.213:5432/DoR')

def create_missing_table():
    """Create the missing presentation_assignment_files table"""
    
    # SQL to create the table (from the migration)
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS presentation_assignment_files (
        id SERIAL PRIMARY KEY,
        presentation_assignment_id INTEGER NOT NULL,
        uploaded_by_id INTEGER NOT NULL,
        filename VARCHAR(255) NOT NULL,
        original_filename VARCHAR(255) NOT NULL,
        filepath VARCHAR(500) NOT NULL,
        file_type VARCHAR(100) NOT NULL,
        file_size INTEGER NOT NULL,
        mime_type VARCHAR(200),
        file_category VARCHAR(50),
        description VARCHAR(500),
        upload_date TIMESTAMP DEFAULT NOW() NOT NULL,
        created_at TIMESTAMP DEFAULT NOW() NOT NULL,
        updated_at TIMESTAMP DEFAULT NOW() NOT NULL,
        FOREIGN KEY (presentation_assignment_id) REFERENCES presentation_assignments(id) ON DELETE CASCADE,
        FOREIGN KEY (uploaded_by_id) REFERENCES "user"(id) ON DELETE CASCADE
    );
    """
    
    # Create index
    create_index_sql = """
    CREATE INDEX IF NOT EXISTS ix_presentation_assignment_files_id 
    ON presentation_assignment_files (id);
    """
    
    try:
        # Connect to database
        engine = create_engine(get_database_url())
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Check if table exists
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'presentation_assignment_files'
                    );
                """))
                
                table_exists = result.scalar()
                
                if table_exists:
                    print("✅ Table presentation_assignment_files already exists")
                    return True
                
                print("🔧 Creating presentation_assignment_files table...")
                
                # Create the table
                conn.execute(text(create_table_sql))
                print("✅ Table created successfully")
                
                # Create the index
                conn.execute(text(create_index_sql))
                print("✅ Index created successfully")
                
                # Commit transaction
                trans.commit()
                
                print("🎉 presentation_assignment_files table created successfully!")
                return True
                
            except Exception as e:
                # Rollback on error
                trans.rollback()
                print(f"❌ Error creating table: {e}")
                traceback.print_exc()
                return False
                
    except SQLAlchemyError as e:
        print(f"❌ Database connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return False

def verify_table():
    """Verify the table was created correctly"""
    try:
        engine = create_engine(get_database_url())
        
        with engine.connect() as conn:
            # Check table structure
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'presentation_assignment_files'
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            
            if columns:
                print("📋 Table structure:")
                for col in columns:
                    nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                    print(f"  - {col[0]}: {col[1]} ({nullable})")
                
                # Check foreign keys
                result = conn.execute(text("""
                    SELECT constraint_name, table_name, column_name, 
                           foreign_table_name, foreign_column_name
                    FROM information_schema.key_column_usage kcu
                    JOIN information_schema.referential_constraints rc
                        ON kcu.constraint_name = rc.constraint_name
                    JOIN information_schema.key_column_usage kcu2
                        ON rc.unique_constraint_name = kcu2.constraint_name
                    WHERE kcu.table_name = 'presentation_assignment_files';
                """))
                
                fkeys = result.fetchall()
                if fkeys:
                    print("🔗 Foreign keys:")
                    for fk in fkeys:
                        print(f"  - {fk[2]} → {fk[3]}.{fk[4]}")
                
                return True
            else:
                print("❌ Table not found after creation")
                return False
                
    except Exception as e:
        print(f"❌ Error verifying table: {e}")
        return False

if __name__ == "__main__":
    print("🔧 DoR-Dash Database Fix: Creating missing presentation_assignment_files table")
    print("=" * 70)
    
    # Create the table
    if create_missing_table():
        # Verify it was created
        if verify_table():
            print("\n🎉 SUCCESS: Database fix completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ FAILURE: Table creation verification failed")
            sys.exit(1)
    else:
        print("\n❌ FAILURE: Could not create table")
        sys.exit(1)