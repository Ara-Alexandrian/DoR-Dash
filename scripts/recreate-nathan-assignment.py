#!/usr/bin/env python3
"""
Script to recreate Nathan's lost presentation assignment.

This script can be run to recreate the presentation assignment for Nathan Dobranski
that was lost during the database migration.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the backend path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from app.db.database import SessionLocal
    from app.db.models.user import User
    from app.db.models.presentation_assignment import PresentationAssignment, PresentationType
    from app.db.models.meeting import Meeting
    from sqlalchemy.orm import Session
except ImportError as e:
    print(f"Error importing backend modules: {e}")
    print("Make sure to run this script from the DoR-Dash root directory with backend dependencies installed.")
    sys.exit(1)

def recreate_nathan_assignment():
    """Recreate Nathan's presentation assignment"""
    
    db: Session = SessionLocal()
    
    try:
        # Find Nathan by name or username
        nathan = db.query(User).filter(
            (User.full_name.ilike('%Nathan%Dobranski%')) |
            (User.username.ilike('%nathan%'))
        ).first()
        
        if not nathan:
            print("❌ Could not find Nathan Dobranski in the database.")
            print("Available users:")
            users = db.query(User).all()
            for user in users:
                print(f"  - ID: {user.id}, Name: {user.full_name}, Username: {user.username}, Role: {user.role}")
            return False
        
        print(f"✅ Found Nathan: {nathan.full_name} (ID: {nathan.id})")
        
        # Find Ara Alexandrian who assigned it
        ara = db.query(User).filter(
            (User.full_name.ilike('%Ara%Alexandrian%')) |
            (User.username.ilike('%ara%'))
        ).first()
        
        if not ara:
            print("❌ Could not find Ara Alexandrian in the database.")
            print("Available faculty/admin users:")
            faculty = db.query(User).filter(User.role.in_(['faculty', 'admin'])).all()
            for user in faculty:
                print(f"  - ID: {user.id}, Name: {user.full_name}, Username: {user.username}, Role: {user.role}")
            return False
        
        print(f"✅ Found Ara: {ara.full_name} (ID: {ara.id})")
        
        # Check if assignment already exists
        existing = db.query(PresentationAssignment).filter(
            PresentationAssignment.student_id == nathan.id,
            PresentationAssignment.title.ilike('%LLM Information Literacy%')
        ).first()
        
        if existing:
            print(f"⚠️  Assignment already exists: {existing.title} (ID: {existing.id})")
            return True
        
        # Find a recent meeting to associate with (optional)
        recent_meeting = db.query(Meeting).order_by(Meeting.created_at.desc()).first()
        meeting_id = recent_meeting.id if recent_meeting else None
        
        if meeting_id:
            print(f"✅ Will associate with meeting: {recent_meeting.title} (ID: {meeting_id})")
        else:
            print("⚠️  No meetings found - creating assignment without meeting association")
        
        # Create the presentation assignment based on documentation
        assignment = PresentationAssignment(
            student_id=nathan.id,
            assigned_by_id=ara.id,
            meeting_id=meeting_id,
            title="LLM Information Literacy System Update",
            description="Present progress on the AI-powered research assistance system",
            presentation_type=PresentationType.RESEARCH_UPDATE,
            duration_minutes=20,
            requirements="Slides, Data/Results, Time Management",
            grillometer_novelty=2,
            grillometer_methodology=3,
            grillometer_delivery=1,
            notes="Focus on methodology validation and statistical significance",
            due_date=datetime.now() + timedelta(days=7),  # Due next week
            assigned_date=datetime.now(),
            is_completed=False
        )
        
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        
        print(f"🎉 Successfully recreated Nathan's presentation assignment!")
        print(f"   ID: {assignment.id}")
        print(f"   Title: {assignment.title}")
        print(f"   Type: {assignment.presentation_type}")
        print(f"   Duration: {assignment.duration_minutes} minutes")
        print(f"   Due: {assignment.due_date}")
        print(f"   Grillometer: Novelty={assignment.grillometer_novelty}, Methodology={assignment.grillometer_methodology}, Delivery={assignment.grillometer_delivery}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating assignment: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()

def main():
    """Main script entry point"""
    print("🔧 Recreating Nathan's Presentation Assignment")
    print("=" * 50)
    
    success = recreate_nathan_assignment()
    
    if success:
        print("\n✅ Assignment recreation completed successfully!")
        print("Nathan can now view and upload files for his presentation assignment.")
    else:
        print("\n❌ Assignment recreation failed.")
        print("Please check the error messages above and ensure:")
        print("1. Both Nathan and Ara exist in the user database")
        print("2. Database connection is working")
        print("3. Required database tables exist")

if __name__ == "__main__":
    main()