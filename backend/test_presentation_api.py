#!/usr/bin/env python3
"""Test script to verify presentation assignment API endpoint works correctly"""

import requests
import json
from datetime import datetime, timedelta

# Test configuration
BASE_URL = "http://localhost:8000/api/v1"
FACULTY_USERNAME = "amcguffey"
FACULTY_PASSWORD = "password123"  # Assuming default password
STUDENT_USERNAME = "maire"

def get_auth_token(username, password):
    """Get authentication token for a user"""
    try:
        login_data = {"username": username, "password": password}
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            return token
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_user_search():
    """Test user search endpoint"""
    print("Testing user search endpoint...")
    
    # Get faculty token
    faculty_token = get_auth_token(FACULTY_USERNAME, FACULTY_PASSWORD)
    if not faculty_token:
        print("Failed to get faculty token")
        return False
    
    headers = {"Authorization": f"Bearer {faculty_token}"}
    
    # Search for marie
    response = requests.get(f"{BASE_URL}/users/search?username=maire", headers=headers)
    print(f"Search response status: {response.status_code}")
    
    if response.status_code == 200:
        users = response.json()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  - ID: {user['id']}, Username: {user['username']}, Role: {user['role']}")
        return len(users) > 0
    else:
        print(f"Search failed: {response.text}")
        return False

def test_presentation_assignment():
    """Test presentation assignment creation"""
    print("\nTesting presentation assignment creation...")
    
    # Get faculty token
    faculty_token = get_auth_token(FACULTY_USERNAME, FACULTY_PASSWORD)
    if not faculty_token:
        print("Failed to get faculty token")
        return False
    
    headers = {"Authorization": f"Bearer {faculty_token}"}
    
    # First, get the student ID
    search_response = requests.get(f"{BASE_URL}/users/search?username={STUDENT_USERNAME}", headers=headers)
    if search_response.status_code != 200:
        print(f"Failed to find student: {search_response.text}")
        return False
    
    students = search_response.json()
    if not students:
        print("No students found")
        return False
    
    student_id = students[0]['id']
    print(f"Found student ID: {student_id}")
    
    # Get meetings
    meetings_response = requests.get(f"{BASE_URL}/meetings", headers=headers)
    if meetings_response.status_code != 200:
        print(f"Failed to get meetings: {meetings_response.text}")
        return False
    
    meetings = meetings_response.json()
    print(f"Found {len(meetings)} meetings")
    
    # Find an upcoming meeting
    upcoming_meeting = None
    for meeting in meetings:
        meeting_start = datetime.fromisoformat(meeting['start_time'].replace('Z', '+00:00'))
        if meeting_start > datetime.now():
            upcoming_meeting = meeting
            break
    
    if not upcoming_meeting:
        print("No upcoming meetings found")
        return False
    
    print(f"Using meeting: {upcoming_meeting['title']} (ID: {upcoming_meeting['id']})")
    
    # Create presentation assignment
    assignment_data = {
        "student_id": student_id,
        "meeting_id": upcoming_meeting['id'],
        "title": "Test Presentation Assignment",
        "description": "This is a test assignment created via API",
        "presentation_type": "casual",
        "duration_minutes": 30,
        "requirements": "Test requirements",
        "due_date": upcoming_meeting['start_time'],
        "notes": "Test notes",
        "grillometer_novelty": 2,
        "grillometer_methodology": 2,
        "grillometer_delivery": 2
    }
    
    print(f"Creating assignment with data: {json.dumps(assignment_data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/presentation-assignments/", 
                           json=assignment_data, 
                           headers=headers)
    
    print(f"Assignment creation response status: {response.status_code}")
    
    if response.status_code == 200:
        assignment = response.json()
        print(f"Successfully created assignment with ID: {assignment['id']}")
        print(f"Student: {assignment['student_name']}")
        print(f"Meeting: {assignment['meeting_title']}")
        return True
    else:
        print(f"Assignment creation failed: {response.text}")
        return False

def main():
    """Main test function"""
    print("Starting presentation assignment API tests...")
    
    # Test user search
    search_success = test_user_search()
    
    # Test presentation assignment creation
    assignment_success = test_presentation_assignment()
    
    print(f"\nTest Results:")
    print(f"User search: {'PASS' if search_success else 'FAIL'}")
    print(f"Presentation assignment: {'PASS' if assignment_success else 'FAIL'}")
    
    if search_success and assignment_success:
        print("\nAll tests passed!")
        return True
    else:
        print("\nSome tests failed!")
        return False

if __name__ == "__main__":
    main()