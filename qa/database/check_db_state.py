#!/usr/bin/env python3
"""
Check the current state of the DoR-Dash database.
This script can be run locally or copied to the container.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.parent.parent / 'backend'
if backend_path.exists():
    sys.path.insert(0, str(backend_path))
else:
    # If running in container, use container path
    sys.path.insert(0, '/app/backend')

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import Session
    from app.core.config import settings
    from app.db.models import User, Meeting, AgendaItem, RegistrationRequest
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root or inside the container")
    sys.exit(1)

def check_database():
    """Check the current state of the database."""
    DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    
    print(f"Connecting to database: {settings.POSTGRES_DB}@{settings.POSTGRES_SERVER}")
    print("-" * 60)
    
    engine = create_engine(DATABASE_URL)
    
    with Session(engine) as session:
        # Check users
        user_count = session.execute(text("SELECT COUNT(*) FROM users")).scalar()
        print(f"Total users: {user_count}")
        
        # List users with roles
        users = session.execute(text("""
            SELECT username, full_name, role, is_active, created_at 
            FROM users 
            ORDER BY created_at DESC 
            LIMIT 10
        """)).fetchall()
        
        if users:
            print("\nRecent users:")
            for user in users:
                print(f"  - {user.username} ({user.full_name}) - Role: {user.role} - Active: {user.is_active}")
        
        # Check meetings
        meeting_count = session.execute(text("SELECT COUNT(*) FROM meetings")).scalar()
        print(f"\nTotal meetings: {meeting_count}")
        
        # List recent meetings
        meetings = session.execute(text("""
            SELECT title, meeting_type, start_time, created_at 
            FROM meetings 
            ORDER BY start_time DESC 
            LIMIT 5
        """)).fetchall()
        
        if meetings:
            print("\nRecent meetings:")
            for meeting in meetings:
                print(f"  - {meeting.title} ({meeting.meeting_type}) - {meeting.start_time}")
        
        # Check agenda items
        agenda_count = session.execute(text("SELECT COUNT(*) FROM agenda_items")).scalar()
        print(f"\nTotal agenda items: {agenda_count}")
        
        # Count by type
        type_counts = session.execute(text("""
            SELECT item_type, COUNT(*) as count 
            FROM agenda_items 
            GROUP BY item_type
        """)).fetchall()
        
        if type_counts:
            print("\nAgenda items by type:")
            for type_count in type_counts:
                print(f"  - {type_count.item_type}: {type_count.count}")
        
        # Check registration requests
        reg_count = session.execute(text("SELECT COUNT(*) FROM registration_requests")).scalar()
        print(f"\nTotal registration requests: {reg_count}")
        
        # Count by status
        status_counts = session.execute(text("""
            SELECT status, COUNT(*) as count 
            FROM registration_requests 
            GROUP BY status
        """)).fetchall()
        
        if status_counts:
            print("\nRegistration requests by status:")
            for status_count in status_counts:
                print(f"  - {status_count.status}: {status_count.count}")
        
        # Check file uploads
        file_count = session.execute(text("SELECT COUNT(*) FROM file_uploads")).scalar()
        print(f"\nTotal file uploads: {file_count}")
        
        print("-" * 60)
        print("Database check complete!")

if __name__ == "__main__":
    try:
        check_database()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)