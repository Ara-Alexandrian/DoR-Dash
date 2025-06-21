#!/usr/bin/env python3
"""
Test raw SQL insertion to verify database works
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.core.config import settings

# Database connection URL
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

def test_raw_insert():
    """Test raw SQL insertion"""
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Insert meeting using raw SQL
            start_time = datetime.now() + timedelta(hours=1)
            end_time = datetime.now() + timedelta(hours=2)
            
            result = conn.execute(text("""
                INSERT INTO meeting (title, description, meeting_type, start_time, end_time, created_by)
                VALUES (:title, :description, :meeting_type, :start_time, :end_time, :created_by)
                RETURNING id, meeting_type;
            """), {
                'title': 'Test Raw Meeting',
                'description': 'Test meeting with raw SQL',
                'meeting_type': 'general_update',  # Use the actual enum value
                'start_time': start_time,
                'end_time': end_time,
                'created_by': 2  # cerebro's ID
            })
            
            row = result.fetchone()
            print(f"Meeting inserted successfully! ID: {row[0]}, Type: {row[1]}")
            
            conn.commit()
            
            # Query it back
            result = conn.execute(text("""
                SELECT id, title, meeting_type FROM meeting WHERE title = 'Test Raw Meeting';
            """))
            
            for row in result:
                print(f"Retrieved: ID={row[0]}, Title={row[1]}, Type={row[2]}")
                
        except Exception as e:
            print(f"Error with raw SQL: {e}")
            conn.rollback()

if __name__ == "__main__":
    test_raw_insert()