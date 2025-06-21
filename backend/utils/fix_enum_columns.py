#!/usr/bin/env python3
"""
Fix database columns to use string instead of enum types
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.core.config import settings

# Database connection URL
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

def fix_enum_columns():
    """Convert enum columns to string columns"""
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("\n=== FIXING ENUM COLUMNS ===")
        
        try:
            # Fix agendaitem.item_type column
            print("1. Converting agendaitem.item_type from enum to string...")
            conn.execute(text("""
                ALTER TABLE agendaitem 
                ALTER COLUMN item_type TYPE VARCHAR(30) 
                USING item_type::text;
            """))
            print("   ✅ agendaitem.item_type converted to VARCHAR(30)")
            
            # Note: meeting.meeting_type and user.role should already be handled 
            # by our string fix, but let's check and convert if needed
            
            # Check meeting table
            result = conn.execute(text("""
                SELECT data_type FROM information_schema.columns 
                WHERE table_name = 'meeting' AND column_name = 'meeting_type';
            """))
            meeting_type_data_type = result.scalar()
            
            if meeting_type_data_type == 'USER-DEFINED':  # This means it's still an enum
                print("2. Converting meeting.meeting_type from enum to string...")
                conn.execute(text("""
                    ALTER TABLE meeting 
                    ALTER COLUMN meeting_type TYPE VARCHAR(50) 
                    USING meeting_type::text;
                """))
                print("   ✅ meeting.meeting_type converted to VARCHAR(50)")
            else:
                print(f"2. meeting.meeting_type already converted (type: {meeting_type_data_type})")
            
            # Check user table
            result = conn.execute(text("""
                SELECT data_type FROM information_schema.columns 
                WHERE table_name = 'user' AND column_name = 'role';
            """))
            user_role_data_type = result.scalar()
            
            if user_role_data_type == 'USER-DEFINED':  # This means it's still an enum
                print("3. Converting user.role from enum to string...")
                conn.execute(text("""
                    ALTER TABLE "user" 
                    ALTER COLUMN role TYPE VARCHAR(20) 
                    USING role::text;
                """))
                print("   ✅ user.role converted to VARCHAR(20)")
            else:
                print(f"3. user.role already converted (type: {user_role_data_type})")
            
            # Check registrationrequest table
            result = conn.execute(text("""
                SELECT data_type FROM information_schema.columns 
                WHERE table_name = 'registrationrequest' AND column_name = 'role';
            """))
            reg_role_data_type = result.scalar()
            
            if reg_role_data_type == 'USER-DEFINED':
                print("4. Converting registrationrequest.role from enum to string...")
                conn.execute(text("""
                    ALTER TABLE registrationrequest 
                    ALTER COLUMN role TYPE VARCHAR(20) 
                    USING role::text;
                """))
                print("   ✅ registrationrequest.role converted to VARCHAR(20)")
            else:
                print(f"4. registrationrequest.role already converted (type: {reg_role_data_type})")
            
            result = conn.execute(text("""
                SELECT data_type FROM information_schema.columns 
                WHERE table_name = 'registrationrequest' AND column_name = 'status';
            """))
            reg_status_data_type = result.scalar()
            
            if reg_status_data_type == 'USER-DEFINED':
                print("5. Converting registrationrequest.status from enum to string...")
                conn.execute(text("""
                    ALTER TABLE registrationrequest 
                    ALTER COLUMN status TYPE VARCHAR(20) 
                    USING status::text;
                """))
                print("   ✅ registrationrequest.status converted to VARCHAR(20)")
            else:
                print(f"5. registrationrequest.status already converted (type: {reg_status_data_type})")
            
            conn.commit()
            print("\n✅ All enum columns successfully converted to strings!")
            
        except Exception as e:
            print(f"Error fixing enum columns: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    fix_enum_columns()