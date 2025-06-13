#!/usr/bin/env python3
"""
Test authentication functionality
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models.user import User, UserRole
from app.core.security import verify_password, get_password_hash

# Database connection URL
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

def test_authentication():
    """Test user authentication"""
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    with Session(engine) as session:
        print("\n=== AUTHENTICATION TEST ===")
        
        # Test admin user
        print("\n1. Testing admin user (cerebro):")
        admin = session.query(User).filter(User.username == "cerebro").first()
        if admin:
            print(f"   Found user: {admin.username}")
            print(f"   Email: {admin.email}")
            print(f"   Full name: {admin.full_name}")
            print(f"   Role: {admin.role}")
            print(f"   Role enum: {admin.role_enum}")
            print(f"   Is active: {admin.is_active}")
            
            # Test password
            password_check = verify_password("123", admin.hashed_password)
            print(f"   Password '123' verification: {'✅ SUCCESS' if password_check else '❌ FAILED'}")
        else:
            print("   ❌ Admin user not found!")
        
        # Test student user
        print("\n2. Testing student user (aalexandrian):")
        student = session.query(User).filter(User.username == "aalexandrian").first()
        if student:
            print(f"   Found user: {student.username}")
            print(f"   Email: {student.email}")
            print(f"   Full name: {student.full_name}")
            print(f"   Role: {student.role}")
            print(f"   Role enum: {student.role_enum}")
            print(f"   Is active: {student.is_active}")
            
            # Test password
            password_check = verify_password("12345678", student.hashed_password)
            print(f"   Password '12345678' verification: {'✅ SUCCESS' if password_check else '❌ FAILED'}")
        else:
            print("   ❌ Student user not found!")
        
        # Test meetings
        print("\n3. Testing meetings:")
        from app.db.models.meeting import Meeting
        meetings = session.query(Meeting).all()
        print(f"   Total meetings: {len(meetings)}")
        for meeting in meetings:
            print(f"   - {meeting.title} (type: {meeting.meeting_type}, type_enum: {meeting.meeting_type_enum})")
        
        # Test agenda items
        print("\n4. Testing agenda items:")
        from app.db.models.agenda_item import AgendaItem
        agenda_items = session.query(AgendaItem).all()
        print(f"   Total agenda items: {len(agenda_items)}")
        for item in agenda_items:
            print(f"   - {item.item_type} by {item.user.username} for meeting {item.meeting.title}")

if __name__ == "__main__":
    test_authentication()