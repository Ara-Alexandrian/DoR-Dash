#!/usr/bin/env python3
"""
Test script to verify presentation assignment creation works after fixing the enum type issue.
This script tests the creation of a presentation assignment to identify any remaining issues.
"""
import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from app.db.session import get_sync_db
from app.db.models.presentation_assignment import PresentationAssignment, PresentationType
from app.db.models.user import User, UserRole
from app.core.logging import logger

def test_presentation_assignment_creation():
    """
    Test creating a presentation assignment to verify the enum type fix.
    """
    logger.info("Starting presentation assignment creation test...")
    
    # Get database session
    db = next(get_sync_db())
    
    try:
        # Find a faculty user and a student user for testing
        faculty_user = db.query(User).filter(User.role == UserRole.FACULTY.value).first()
        student_user = db.query(User).filter(User.role == UserRole.STUDENT.value).first()
        
        if not faculty_user:
            logger.error("No faculty user found in database. Cannot test assignment creation.")
            return False
            
        if not student_user:
            logger.error("No student user found in database. Cannot test assignment creation.")
            return False
            
        logger.info(f"Using faculty user: {faculty_user.username} (ID: {faculty_user.id})")
        logger.info(f"Using student user: {student_user.username} (ID: {student_user.id})")
        
        # Create a test presentation assignment
        test_assignment = PresentationAssignment(
            student_id=student_user.id,
            assigned_by_id=faculty_user.id,
            meeting_id=None,  # No meeting required for this test
            title="Test Presentation Assignment",
            description="This is a test assignment to verify enum handling",
            presentation_type=PresentationType.CASUAL,  # Using enum directly
            duration_minutes=30,
            requirements="Test requirements",
            due_date=datetime.utcnow() + timedelta(days=7),  # Due in 1 week
            notes="Test notes",
            grillometer_novelty=2,
            grillometer_methodology=2,
            grillometer_delivery=2
        )
        
        logger.info("Attempting to add assignment to database...")
        db.add(test_assignment)
        db.commit()
        db.refresh(test_assignment)
        
        logger.info(f"SUCCESS: Created presentation assignment with ID: {test_assignment.id}")
        logger.info(f"Assignment type: {test_assignment.presentation_type}")
        logger.info(f"Assignment type value: {test_assignment.presentation_type.value}")
        
        # Clean up the test assignment
        db.delete(test_assignment)
        db.commit()
        logger.info("Test assignment cleaned up successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"ERROR creating presentation assignment: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        db.rollback()
        return False
        
    finally:
        db.close()

def test_enum_values():
    """
    Test that all enum values are properly defined and accessible.
    """
    logger.info("Testing PresentationType enum values...")
    
    try:
        for ptype in PresentationType:
            logger.info(f"Enum value: {ptype.name} = {ptype.value}")
        
        logger.info("All enum values are accessible")
        return True
        
    except Exception as e:
        logger.error(f"ERROR testing enum values: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing presentation assignment creation after enum fix...")
    
    # Test enum values first
    enum_test_passed = test_enum_values()
    
    # Test assignment creation
    creation_test_passed = test_presentation_assignment_creation()
    
    if enum_test_passed and creation_test_passed:
        print("✓ All tests passed! Presentation assignment creation should work now.")
        sys.exit(0)
    else:
        print("✗ Some tests failed. Check the logs for details.")
        sys.exit(1)