"""
Test suite for user service.
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.db.models.user import User, UserRole

class TestUserService:
    """Test cases for UserService."""
    
    def test_get_all_users(self):
        """Test getting all users."""
        mock_db = Mock(spec=Session)
        mock_users = [Mock(spec=User), Mock(spec=User)]
        mock_db.query.return_value.all.return_value = mock_users
        
        result = UserService.get_all_users(mock_db)
        
        assert result == mock_users
        mock_db.query.assert_called_once_with(User)
    
    def test_get_user_by_id_success(self):
        """Test successful user retrieval by ID."""
        mock_db = Mock(spec=Session)
        mock_user = Mock(spec=User)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = UserService.get_user_by_id(mock_db, 1)
        
        assert result == mock_user
    
    def test_get_user_by_id_not_found(self):
        """Test user retrieval when user doesn't exist."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = UserService.get_user_by_id(mock_db, 999)
        
        assert result is None
    
    def test_create_user_success(self):
        """Test successful user creation."""
        mock_db = Mock(spec=Session)
        
        # Mock that username/email don't exist
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Mock the created user
        mock_user = Mock(spec=User)
        mock_db.refresh = Mock()
        
        with patch('app.services.user_service.get_password_hash', return_value="hashed_password"):
            with patch('app.db.models.user.User', return_value=mock_user):
                result = UserService.create_user(
                    mock_db, "testuser", "test@example.com", "password", "Test User"
                )
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_user)
    
    def test_create_user_username_exists(self):
        """Test user creation when username already exists."""
        mock_db = Mock(spec=Session)
        
        # Mock existing user
        mock_existing_user = Mock(spec=User)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_existing_user
        
        with pytest.raises(HTTPException) as exc_info:
            UserService.create_user(
                mock_db, "existinguser", "test@example.com", "password", "Test User"
            )
        
        assert exc_info.value.status_code == 400
        assert "Username already exists" in str(exc_info.value.detail)
    
    def test_validate_user_exists_success(self):
        """Test successful user existence validation."""
        mock_db = Mock(spec=Session)
        mock_user = Mock(spec=User)
        
        with patch.object(UserService, 'get_user_by_id', return_value=mock_user):
            result = UserService.validate_user_exists(mock_db, 1)
        
        assert result == mock_user
    
    def test_validate_user_exists_not_found(self):
        """Test user existence validation when user doesn't exist."""
        mock_db = Mock(spec=Session)
        
        with patch.object(UserService, 'get_user_by_id', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                UserService.validate_user_exists(mock_db, 999)
        
        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)
    
    def test_is_admin_true(self):
        """Test admin role check - positive case."""
        mock_user = Mock(spec=User)
        mock_user.role = UserRole.ADMIN.value
        
        result = UserService.is_admin(mock_user)
        
        assert result is True
    
    def test_is_admin_false(self):
        """Test admin role check - negative case."""
        mock_user = Mock(spec=User)
        mock_user.role = UserRole.STUDENT.value
        
        result = UserService.is_admin(mock_user)
        
        assert result is False
    
    def test_is_faculty_or_admin_faculty(self):
        """Test faculty/admin check with faculty role."""
        mock_user = Mock(spec=User)
        mock_user.role = UserRole.FACULTY.value
        
        result = UserService.is_faculty_or_admin(mock_user)
        
        assert result is True
    
    def test_is_faculty_or_admin_admin(self):
        """Test faculty/admin check with admin role."""
        mock_user = Mock(spec=User)
        mock_user.role = UserRole.ADMIN.value
        
        result = UserService.is_faculty_or_admin(mock_user)
        
        assert result is True
    
    def test_is_faculty_or_admin_student(self):
        """Test faculty/admin check with student role."""
        mock_user = Mock(spec=User)
        mock_user.role = UserRole.STUDENT.value
        
        result = UserService.is_faculty_or_admin(mock_user)
        
        assert result is False

if __name__ == "__main__":
    pytest.main([__file__])