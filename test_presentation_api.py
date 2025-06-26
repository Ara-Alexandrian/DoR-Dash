#!/usr/bin/env python3
"""
Test the presentation assignment API endpoints
"""
import requests
import json
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "http://172.30.98.21:8001/api/v1"

def test_auth():
    """Test authentication and get token"""
    login_data = {
        "username": "amcguffey",  # Faculty user
        "password": "testpassword123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Login successful for {data.get('username')}")
            return data.get('access_token')
        else:
            print(f"✗ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"✗ Login error: {e}")
        return None

def test_presentation_types(headers):
    """Test getting presentation types"""
    try:
        response = requests.get(f"{BASE_URL}/presentation-assignments/types/", headers=headers, timeout=10)
        if response.status_code == 200:
            types = response.json()
            print(f"✓ Presentation types: {types}")
            return True
        else:
            print(f"✗ Failed to get types: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Types error: {e}")
        return False

def test_get_assignments(headers):
    """Test getting presentation assignments"""
    try:
        response = requests.get(f"{BASE_URL}/presentation-assignments/", headers=headers, timeout=10)
        if response.status_code == 200:
            assignments = response.json()
            print(f"✓ Got {len(assignments)} assignments")
            return assignments
        else:
            print(f"✗ Failed to get assignments: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"✗ Get assignments error: {e}")
        return None

def test_create_assignment(headers):
    """Test creating a presentation assignment"""
    assignment_data = {
        "student_id": 17,  # Student user ID (mheat11)
        "title": "API Test Presentation",
        "description": "Testing presentation assignment creation via API",
        "presentation_type": "casual",
        "duration_minutes": 20,
        "due_date": (datetime.utcnow() + timedelta(days=14)).isoformat(),
        "requirements": "Present your recent research findings"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/presentation-assignments/", 
                               json=assignment_data, headers=headers, timeout=10)
        if response.status_code == 200:
            assignment = response.json()
            print(f"✓ Created assignment: {assignment['title']} (ID: {assignment['id']})")
            return assignment
        else:
            print(f"✗ Failed to create assignment: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"✗ Create assignment error: {e}")
        return None

def main():
    print("=== Testing Presentation Assignment API ===")
    
    print("\n1. Testing authentication...")
    token = test_auth()
    if not token:
        print("Cannot proceed without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n2. Testing presentation types endpoint...")
    test_presentation_types(headers)
    
    print("\n3. Testing get assignments endpoint...")
    assignments = test_get_assignments(headers)
    
    print("\n4. Testing create assignment endpoint...")
    new_assignment = test_create_assignment(headers)
    
    print("\n5. Testing get assignments again...")
    assignments_after = test_get_assignments(headers)
    
    if assignments is not None and assignments_after is not None:
        if len(assignments_after) > len(assignments):
            print("✓ Assignment was successfully created and can be retrieved")
        else:
            print("✗ Assignment creation may have failed")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()