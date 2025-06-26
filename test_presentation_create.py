#!/usr/bin/env python3
"""
Test script to create a presentation assignment and verify the API works
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.db.session import engine
from app.db.models.user import User as DBUser
from app.db.models.presentation_assignment import PresentationAssignment, PresentationType
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from datetime import datetime, timedelta

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_presentation_assignment_creation():
    """Test creating a presentation assignment directly in the database"""
    db = SessionLocal()
    try:
        # Get a faculty user to assign from
        faculty_user = db.query(DBUser).filter(DBUser.role == 'FACULTY').first()
        if not faculty_user:
            faculty_user = db.query(DBUser).filter(DBUser.role == 'ADMIN').first()
        
        # Get a student user to assign to
        student_user = db.query(DBUser).filter(DBUser.role == 'STUDENT').first()
        
        if not faculty_user:
            print("No faculty or admin user found")
            return False
        
        if not student_user:
            print("No student user found")
            return False
        
        print(f"Faculty user: {faculty_user.username} (ID: {faculty_user.id})")
        print(f"Student user: {student_user.username} (ID: {student_user.id})")
        
        # Create a test presentation assignment
        assignment = PresentationAssignment(
            student_id=student_user.id,
            assigned_by_id=faculty_user.id,
            title="Test Presentation Assignment",
            description="This is a test presentation assignment created to verify the system works",
            presentation_type=PresentationType.CASUAL.value,  # Use .value to get string
            duration_minutes=30,
            due_date=datetime.utcnow() + timedelta(days=7),
            requirements="Prepare a brief presentation on your recent work"
        )
        
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        
        print(f"Successfully created presentation assignment with ID: {assignment.id}")
        
        # Verify it exists
        check_assignment = db.query(PresentationAssignment).filter(
            PresentationAssignment.id == assignment.id
        ).first()
        
        if check_assignment:
            print("Assignment verification successful!")
            print(f"Title: {check_assignment.title}")
            print(f"Type: {check_assignment.presentation_type}")
            print(f"Due: {check_assignment.due_date}")
            return True
        else:
            print("Assignment verification failed!")
            return False
            
    except Exception as e:
        print(f"Error creating assignment: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def test_table_structure():
    """Test that the table structure is correct"""
    try:
        with engine.connect() as conn:
            # Check table exists
            result = conn.execute(text("SELECT COUNT(*) FROM presentation_assignments"))
            count = result.scalar()
            print(f"presentation_assignments table has {count} rows")
            
            # Check table structure
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'presentation_assignments' 
                ORDER BY ordinal_position
            """))
            
            print("Table structure:")
            for row in result:
                print(f"  {row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
            
            return True
    except Exception as e:
        print(f"Error checking table structure: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing Presentation Assignment System ===")
    
    print("\n1. Testing table structure...")
    if test_table_structure():
        print("✓ Table structure OK")
    else:
        print("✗ Table structure issues")
        sys.exit(1)
    
    print("\n2. Testing assignment creation...")
    if test_presentation_assignment_creation():
        print("✓ Assignment creation OK")
    else:
        print("✗ Assignment creation failed")
        sys.exit(1)
    
    print("\n✓ All tests passed!")