#!/usr/bin/env python3
"""
Test meeting insertion using direct enum values
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models.meeting import Meeting, MeetingType
from app.db.models.user import User

# Database connection URL
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

def test_meeting_direct():
    """Test meeting insertion using direct enum values"""
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    with Session(engine) as session:
        # Get admin user
        admin = session.query(User).filter(User.username == "cerebro").first()
        if not admin:
            print("Admin user not found!")
            return
        
        print(f"Found admin user: {admin.username} (id: {admin.id})")
        
        # Create a simple meeting using enum value directly
        meeting = Meeting(
            title="Test Meeting Direct",
            description="Test meeting with direct enum value",
            meeting_type=MeetingType.GENERAL_UPDATE.value,  # Use .value to get the string
            start_time=datetime.now() + timedelta(hours=1),
            end_time=datetime.now() + timedelta(hours=2),
            created_by=admin.id
        )
        
        print(f"Meeting object created:")
        print(f"  - title: {meeting.title}")
        print(f"  - meeting_type: {meeting.meeting_type}")
        print(f"  - meeting_type type: {type(meeting.meeting_type)}")
        
        try:
            session.add(meeting)
            session.commit()
            print("Meeting inserted successfully!")
            
            # Query it back to verify
            saved_meeting = session.query(Meeting).filter(Meeting.title == "Test Meeting Direct").first()
            if saved_meeting:
                print(f"Retrieved meeting: {saved_meeting.title}, type: {saved_meeting.meeting_type}")
            
        except Exception as e:
            print(f"Error inserting meeting: {e}")
            session.rollback()

if __name__ == "__main__":
    test_meeting_direct()