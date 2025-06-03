import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.endpoints.mock_auth import create_test_token

client = TestClient(app)

@pytest.fixture
def faculty_token():
    """Create a token for a faculty user"""
    return create_test_token({"id": 1, "username": "faculty", "role": "faculty"})

@pytest.fixture
def admin_token():
    """Create a token for an admin user"""
    return create_test_token({"id": 2, "username": "admin", "role": "admin"})

@pytest.fixture
def student_token():
    """Create a token for a student user"""
    return create_test_token({"id": 3, "username": "student", "role": "student"})

def test_create_faculty_update(faculty_token):
    """Test creating a faculty update"""
    update_data = {
        "user_id": 1,
        "announcements_text": "Important announcement",
        "announcement_type": "general",
        "projects_text": "Project updates",
        "is_presenting": False
    }
    
    response = client.post(
        "/api/v1/faculty-updates",
        json=update_data,
        headers={"Authorization": f"Bearer {faculty_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["announcements_text"] == "Important announcement"
    assert data["announcement_type"] == "general"
    assert data["projects_text"] == "Project updates"
    assert data["is_presenting"] == False
    assert "id" in data

def test_get_faculty_updates(faculty_token):
    """Test getting all faculty updates"""
    response = client.get(
        "/api/v1/faculty-updates",
        headers={"Authorization": f"Bearer {faculty_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)

def test_student_cannot_create_faculty_update(student_token):
    """Test that students cannot create faculty updates"""
    update_data = {
        "user_id": 3,
        "announcements_text": "Important announcement",
        "announcement_type": "general",
        "projects_text": "Project updates"
    }
    
    response = client.post(
        "/api/v1/faculty-updates",
        json=update_data,
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    assert response.status_code == 403

def test_admin_can_create_faculty_update(admin_token):
    """Test that admins can create faculty updates"""
    update_data = {
        "user_id": 1,  # Creating for a faculty member
        "announcements_text": "Important announcement",
        "announcement_type": "general",
        "projects_text": "Project updates"
    }
    
    response = client.post(
        "/api/v1/faculty-updates",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 201