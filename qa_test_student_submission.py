#!/usr/bin/env python3
"""
QA Test: Student submission workflow
Test student1 creating a new agenda item, then test permissions
"""
import requests
import json
import sys

# API base URL
BASE_URL = "https://dd.kronisto.net/api/v1"

def get_auth_token(username, password):
    """Login and get authentication token"""
    response = requests.post(f"{BASE_URL}/auth/login", data={
        "username": username,
        "password": password,
        "grant_type": "password"
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Login failed for {username}: {response.status_code} - {response.text}")
        return None

def test_student_submission():
    """Test student1 creating a new submission"""
    print("=== QA TEST: Student Submission Workflow ===\n")
    
    # Test 1: Login as student1
    print("1. Testing login as student1...")
    token = get_auth_token("student1", "12345678")  # Using known test password
    if not token:
        print("❌ FAILED: Could not login as student1")
        return False
    print("✅ SUCCESS: student1 logged in")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 2: Create a new student update
    print("\n2. Creating new student update...")
    update_data = {
        "user_id": 9,  # student1's ID
        "meeting_id": 2,  # Use meeting 2
        "progress_text": "QA TEST: Completed database schema refactor and testing new unified agenda system. Successfully migrated from fragmented tables to unified approach.",
        "challenges_text": "QA TEST: Minor challenges with backwards compatibility, but resolved with adapter pattern.",
        "next_steps_text": "QA TEST: Complete frontend migration and remove legacy endpoints.",
        "meeting_notes": "QA TEST: Discussed new schema benefits with team.",
        "will_present": True
    }
    
    response = requests.post(f"{BASE_URL}/updates/", 
                           headers=headers, 
                           json=update_data)
    
    if response.status_code == 201:
        update = response.json()
        update_id = update.get("id")
        print(f"✅ SUCCESS: Created student update with ID {update_id}")
        print(f"   Content preview: {update.get('progress_text', '')[:50]}...")
        return update_id, token
    else:
        print(f"❌ FAILED: Could not create student update: {response.status_code} - {response.text}")
        return None, token

def test_edit_permissions(update_id, student1_token):
    """Test edit permissions for different users"""
    print(f"\n=== Testing Edit Permissions for Update ID {update_id} ===")
    
    # Test 3: student1 can edit their own submission
    print("\n3. Testing student1 editing their own submission...")
    edit_data = {
        "progress_text": "QA TEST EDIT: Updated progress text by original student",
        "challenges_text": "QA TEST EDIT: Updated challenges by original student"
    }
    
    response = requests.put(f"{BASE_URL}/updates/{update_id}",
                          headers={"Authorization": f"Bearer {student1_token}"},
                          json=edit_data)
    
    if response.status_code == 200:
        updated = response.json()
        print("✅ SUCCESS: student1 can edit their own submission")
        print(f"   Updated content: {updated.get('progress_text', '')[:50]}...")
    else:
        print(f"❌ FAILED: student1 cannot edit their own submission: {response.status_code}")
    
    # Test 4: testuser (different student) cannot edit
    print("\n4. Testing testuser (different student) cannot edit...")
    testuser_token = get_auth_token("testuser", "password123")
    if testuser_token:
        response = requests.put(f"{BASE_URL}/updates/{update_id}",
                              headers={"Authorization": f"Bearer {testuser_token}"},
                              json={"progress_text": "UNAUTHORIZED EDIT ATTEMPT"})
        
        if response.status_code == 403:
            print("✅ SUCCESS: testuser correctly denied permission")
        else:
            print(f"❌ FAILED: testuser should be denied, got {response.status_code}")
    else:
        print("❌ FAILED: Could not login as testuser")
    
    # Test 5: cerebro (admin) can edit
    print("\n5. Testing cerebro (admin) can edit...")
    admin_token = get_auth_token("cerebro", "123")
    if admin_token:
        response = requests.put(f"{BASE_URL}/updates/{update_id}",
                              headers={"Authorization": f"Bearer {admin_token}"},
                              json={"meeting_notes": "QA TEST: Admin edit - verified admin permissions"})
        
        if response.status_code == 200:
            print("✅ SUCCESS: cerebro (admin) can edit any submission")
        else:
            print(f"❌ FAILED: admin edit failed: {response.status_code}")
    else:
        print("❌ FAILED: Could not login as cerebro")
    
    # Test 6: aalexandrian (faculty) can edit
    print("\n6. Testing aalexandrian (faculty) can edit...")
    faculty_token = get_auth_token("aalexandrian", "12345678")
    if faculty_token:
        response = requests.put(f"{BASE_URL}/updates/{update_id}",
                              headers={"Authorization": f"Bearer {faculty_token}"},
                              json={"meeting_notes": "QA TEST: Faculty edit - verified faculty permissions"})
        
        if response.status_code == 200:
            print("✅ SUCCESS: aalexandrian (faculty) can edit student submissions")
        else:
            print(f"❌ FAILED: faculty edit failed: {response.status_code}")
    else:
        print("❌ FAILED: Could not login as aalexandrian")

def test_agenda_view():
    """Test viewing the agenda"""
    print(f"\n=== Testing Meeting Agenda View ===")
    
    # Test with different user roles
    for username, password, role in [
        ("student1", "12345678", "STUDENT"),
        ("cerebro", "123", "ADMIN"),
        ("aalexandrian", "12345678", "FACULTY")
    ]:
        token = get_auth_token(username, password)
        if token:
            response = requests.get(f"{BASE_URL}/meetings/2/agenda",
                                  headers={"Authorization": f"Bearer {token}"})
            if response.status_code == 200:
                agenda = response.json()
                student_updates = agenda.get('student_updates', [])
                print(f"✅ SUCCESS: {role} can view agenda ({len(student_updates)} student updates)")
            else:
                print(f"❌ FAILED: {role} cannot view agenda: {response.status_code}")

if __name__ == "__main__":
    try:
        update_id, token = test_student_submission()
        if update_id:
            test_edit_permissions(update_id, token)
            test_agenda_view()
        else:
            print("❌ CRITICAL: Could not create test submission")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()