#!/usr/bin/env python3
"""
Test script to verify the unified agenda item schema migration
"""
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from app.db.session import engine
from app.db.models.agenda_item import AgendaItem, AgendaItemType
from app.db.models.user import User
from app.db.models.meeting import Meeting

def test_schema():
    """Test the new unified schema"""
    print("Testing unified agenda item schema...")
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Test 1: Check if agenda_item table exists and is accessible
        print("\n1. Testing agenda_item table access...")
        agenda_items = db.query(AgendaItem).all()
        print(f"   Found {len(agenda_items)} agenda items")
        
        # Test 2: Check relationships
        print("\n2. Testing relationships...")
        for item in agenda_items[:3]:  # Test first 3 items
            print(f"   Agenda Item {item.id}: {item.item_type} by {item.user.username if item.user else 'Unknown'}")
            print(f"   Content: {list(item.content.keys()) if item.content else 'No content'}")
            print(f"   Files: {len(item.file_uploads)} files attached")
        
        # Test 3: Test content access methods
        print("\n3. Testing content accessors...")
        student_items = db.query(AgendaItem).filter(AgendaItem.item_type == AgendaItemType.STUDENT_UPDATE).first()
        if student_items:
            print(f"   Student update content: {student_items.student_content}")
        
        faculty_items = db.query(AgendaItem).filter(AgendaItem.item_type == AgendaItemType.FACULTY_UPDATE).first()
        if faculty_items:
            print(f"   Faculty update content: {faculty_items.faculty_content}")
        
        # Test 4: Test ordering within meetings
        print("\n4. Testing agenda ordering...")
        meetings = db.query(Meeting).limit(2).all()
        for meeting in meetings:
            items = db.query(AgendaItem).filter(
                AgendaItem.meeting_id == meeting.id
            ).order_by(AgendaItem.order_index).all()
            print(f"   Meeting {meeting.id}: {len(items)} agenda items")
            for item in items:
                print(f"     Order {item.order_index}: {item.item_type} by {item.user.username}")
        
        # Test 5: Test factory methods
        print("\n5. Testing factory methods...")
        # Don't actually create, just test the method exists
        test_student = AgendaItem.create_student_update(
            meeting_id=1, user_id=1, progress_text="Test progress"
        )
        print(f"   Student update factory: {test_student.item_type} with content keys: {list(test_student.content.keys())}")
        
        print("\n✅ Schema test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Schema test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_schema()