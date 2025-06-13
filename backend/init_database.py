#!/usr/bin/env python3
"""
Database initialization script for DoR-Dash
Creates all necessary tables, enum types, and initial data
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.base import Base
from app.db.models import (
    User, UserRole, 
    Meeting, MeetingType,
    AgendaItem, AgendaItemType,
    FileUpload,
    RegistrationRequest, RegistrationStatus
)
from app.core.security import get_password_hash

# Database connection URL
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

def create_enum_types(engine):
    """Create PostgreSQL enum types if they don't exist"""
    with engine.connect() as conn:
        # Check and create UserRole enum
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM pg_type 
                WHERE typname = 'userrole'
            );
        """))
        if not result.scalar():
            conn.execute(text("""
                CREATE TYPE userrole AS ENUM ('STUDENT', 'FACULTY', 'SECRETARY', 'ADMIN');
            """))
            print("Created userrole enum type")
        
        # Check and create MeetingType enum
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM pg_type 
                WHERE typname = 'meetingtype'
            );
        """))
        if not result.scalar():
            conn.execute(text("""
                CREATE TYPE meetingtype AS ENUM ('general_update', 'presentations_and_updates', 'other');
            """))
            print("Created meetingtype enum type")
        
        # Check and create AgendaItemType enum
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM pg_type 
                WHERE typname = 'agendaitemtype'
            );
        """))
        if not result.scalar():
            conn.execute(text("""
                CREATE TYPE agendaitemtype AS ENUM ('student_update', 'faculty_update', 'announcement', 'presentation');
            """))
            print("Created agendaitemtype enum type")
        
        # Check and create RegistrationStatus enum
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM pg_type 
                WHERE typname = 'registrationstatus'
            );
        """))
        if not result.scalar():
            conn.execute(text("""
                CREATE TYPE registrationstatus AS ENUM ('pending', 'approved', 'rejected');
            """))
            print("Created registrationstatus enum type")
        
        conn.commit()

def create_tables(engine):
    """Create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")

def create_initial_users(db: Session):
    """Create initial admin and test users"""
    users_data = [
        {
            "username": "cerebro",
            "email": "cerebro@dor.edu",
            "full_name": "Charles Xavier",
            "role": UserRole.ADMIN,
            "password": "123"
        },
        {
            "username": "aalexandrian",
            "email": "aalexandrian@dor.edu",
            "full_name": "Alex Alexandrian",
            "role": UserRole.STUDENT,
            "password": "12345678"
        },
        {
            "username": "jdoe",
            "email": "jdoe@dor.edu",
            "full_name": "John Doe",
            "role": UserRole.STUDENT,
            "password": "12345678"
        },
        {
            "username": "ssmith",
            "email": "ssmith@dor.edu",
            "full_name": "Sarah Smith",
            "role": UserRole.FACULTY,
            "password": "12345678"
        }
    ]
    
    for user_data in users_data:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing_user:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                role=user_data["role"].value,  # Use .value to get the string
                hashed_password=get_password_hash(user_data["password"]),
                is_active=True
            )
            db.add(user)
            print(f"Created user: {user.username} (role: {user.role})")
        else:
            print(f"User already exists: {user_data['username']}")
    
    db.commit()

def create_sample_meetings(db: Session):
    """Create sample meetings"""
    # Get admin user
    admin = db.query(User).filter(User.username == "cerebro").first()
    if not admin:
        print("Admin user not found, skipping meeting creation")
        return
    
    meetings_data = [
        {
            "title": "Weekly Research Update",
            "description": "Regular weekly meeting for research progress updates",
            "meeting_type": MeetingType.GENERAL_UPDATE,
            "start_time": datetime.now() + timedelta(days=1, hours=15, minutes=30),
            "end_time": datetime.now() + timedelta(days=1, hours=17)
        },
        {
            "title": "End of Month Presentations",
            "description": "Monthly presentations and comprehensive updates",
            "meeting_type": MeetingType.PRESENTATIONS_AND_UPDATES,
            "start_time": datetime.now() + timedelta(days=7, hours=14),
            "end_time": datetime.now() + timedelta(days=7, hours=17)
        },
        {
            "title": "Special Topics Discussion",
            "description": "Discussion on emerging research topics",
            "meeting_type": MeetingType.OTHER,
            "start_time": datetime.now() + timedelta(days=14, hours=10),
            "end_time": datetime.now() + timedelta(days=14, hours=12)
        }
    ]
    
    for meeting_data in meetings_data:
        # Check if meeting already exists (by title and start time)
        existing = db.query(Meeting).filter(
            Meeting.title == meeting_data["title"],
            Meeting.start_time == meeting_data["start_time"]
        ).first()
        
        if not existing:
            meeting = Meeting(
                title=meeting_data["title"],
                description=meeting_data["description"],
                meeting_type=meeting_data["meeting_type"].value,  # Use .value to get the string
                start_time=meeting_data["start_time"],
                end_time=meeting_data["end_time"],
                created_by=admin.id
            )
            db.add(meeting)
            print(f"Created meeting: {meeting.title}")
        else:
            print(f"Meeting already exists: {meeting_data['title']}")
    
    db.commit()

def create_sample_agenda_items(db: Session):
    """Create sample agenda items"""
    # Get users and meetings
    student1 = db.query(User).filter(User.username == "aalexandrian").first()
    student2 = db.query(User).filter(User.username == "jdoe").first()
    faculty = db.query(User).filter(User.username == "ssmith").first()
    
    meeting = db.query(Meeting).filter(Meeting.title == "Weekly Research Update").first()
    
    if not all([student1, student2, faculty, meeting]):
        print("Required users or meeting not found, skipping agenda items")
        return
    
    # Create student updates
    student_update1 = AgendaItem.create_student_update(
        meeting_id=meeting.id,
        user_id=student1.id,
        progress_text="Completed data collection for the first phase of my research project.",
        challenges_text="Having difficulty with statistical analysis of the collected data.",
        next_steps_text="Will consult with statistics department and begin writing methodology section.",
        meeting_notes="Need to schedule meeting with stats consultant",
        will_present=True,
        order_index=1
    )
    
    student_update2 = AgendaItem.create_student_update(
        meeting_id=meeting.id,
        user_id=student2.id,
        progress_text="Finished literature review and started experimental design.",
        challenges_text="Equipment availability is limited, may need to adjust timeline.",
        next_steps_text="Submit equipment request and begin pilot testing.",
        meeting_notes="",
        will_present=False,
        order_index=2
    )
    
    # Create faculty update
    faculty_update = AgendaItem.create_faculty_update(
        meeting_id=meeting.id,
        user_id=faculty.id,
        announcements_text="New grant opportunities available for research projects. Deadline is next month.",
        announcement_type="funding",
        projects_text="Department is launching new collaborative research initiative.",
        project_status_text="Initial planning phase, looking for student participants.",
        faculty_questions="Who would be interested in participating in the new initiative?",
        is_presenting=True,
        order_index=0
    )
    
    # Check if items already exist
    existing = db.query(AgendaItem).filter(
        AgendaItem.meeting_id == meeting.id
    ).first()
    
    if not existing:
        db.add(student_update1)
        db.add(student_update2)
        db.add(faculty_update)
        db.commit()
        print("Created sample agenda items")
    else:
        print("Agenda items already exist for this meeting")

def create_sample_registration_request(db: Session):
    """Create a sample registration request"""
    # Check if any pending requests exist
    existing = db.query(RegistrationRequest).filter(
        RegistrationRequest.status == RegistrationStatus.PENDING
    ).first()
    
    if not existing:
        request = RegistrationRequest(
            username="newstudent",
            email="newstudent@dor.edu",
            full_name="New Student",
            preferred_email="personal@email.com",
            phone="555-0123",
            role=UserRole.STUDENT,
            password="password123",  # This should be hashed when creating actual user
            status=RegistrationStatus.PENDING
        )
        db.add(request)
        db.commit()
        print("Created sample registration request")
    else:
        print("Pending registration request already exists")

def main():
    """Main initialization function"""
    print(f"Initializing database at: {DATABASE_URL}")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    try:
        # Create enum types first
        create_enum_types(engine)
        
        # Create tables
        create_tables(engine)
        
        # Create initial data
        with Session(engine) as db:
            create_initial_users(db)
            create_sample_meetings(db)
            create_sample_agenda_items(db)
            create_sample_registration_request(db)
        
        print("\nDatabase initialization completed successfully!")
        print("\nCreated users:")
        print("  - cerebro (admin) - password: 123")
        print("  - aalexandrian (student) - password: 12345678")
        print("  - jdoe (student) - password: 12345678")
        print("  - ssmith (faculty) - password: 12345678")
        
    except Exception as e:
        print(f"Error during initialization: {e}")
        raise

if __name__ == "__main__":
    main()