#!/usr/bin/env python3
"""
Check enum values in database
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.core.config import settings

# Database connection URL
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

def check_enums():
    """Check enum values in database"""
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("\n=== ENUM VALUES CHECK ===")
        
        # Check meetingtype enum values
        print("\n1. MEETINGTYPE enum values:")
        result = conn.execute(text("""
            SELECT unnest(enum_range(NULL::meetingtype)) as enum_value;
        """))
        for row in result:
            print(f"  - '{row[0]}'")
        
        # Check userrole enum values
        print("\n2. USERROLE enum values:")
        result = conn.execute(text("""
            SELECT unnest(enum_range(NULL::userrole)) as enum_value;
        """))
        for row in result:
            print(f"  - '{row[0]}'")
        
        # Check agendaitemtype enum values
        print("\n3. AGENDAITEMTYPE enum values:")
        result = conn.execute(text("""
            SELECT unnest(enum_range(NULL::agendaitemtype)) as enum_value;
        """))
        for row in result:
            print(f"  - '{row[0]}'")
        
        # Check registrationstatus enum values
        print("\n4. REGISTRATIONSTATUS enum values:")
        result = conn.execute(text("""
            SELECT unnest(enum_range(NULL::registrationstatus)) as enum_value;
        """))
        for row in result:
            print(f"  - '{row[0]}'")

if __name__ == "__main__":
    check_enums()