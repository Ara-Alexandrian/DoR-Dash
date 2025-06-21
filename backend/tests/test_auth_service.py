"""
Test suite for authentication service.
"""
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService
from app.db.models.user import User, UserRole

class TestAuthService:
    """Test cases for AuthService."""
    
    def test_authenticate_user_success(self):
        """Test successful user authentication."""
        # Mock database session
        mock_db = Mock(spec=Session)
        
        # Mock user object
        mock_user = Mock(spec=User)
        mock_user.username = "testuser"
        mock_user.hashed_password = "$2b$12$hash"
        mock_user.last_login = None
        
        # Mock database query
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Mock password verification
        with patch('app.services.auth_service.verify_password', return_value=True):
            result = AuthService.authenticate_user(mock_db, "testuser", "password")
        
        assert result == mock_user
        mock_db.commit.assert_called_once()
    
    def test_authenticate_user_not_found(self):
        """Test authentication with non-existent user."""
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = AuthService.authenticate_user(mock_db, "nonexistent", "password")
        
        assert result is None
    
    def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password."""
        mock_db = Mock(spec=Session)
        
        mock_user = Mock(spec=User)
        mock_user.username = "testuser"
        mock_user.hashed_password = "$2b$12$hash"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        with patch('app.services.auth_service.verify_password', return_value=False):
            result = AuthService.authenticate_user(mock_db, "testuser", "wrongpassword")
        
        assert result is None
    
    def test_create_access_token(self):
        """Test JWT token creation."""
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.role = UserRole.STUDENT.value
        
        with patch('app.services.auth_service.security_config.create_access_token', return_value="mock_token"):
            token = AuthService.create_access_token(mock_user)
        
        assert token == "mock_token"
    
    def test_validate_user_permissions_success(self):
        """Test successful permission validation."""
        mock_user = Mock(spec=User)
        mock_user.role = UserRole.ADMIN.value
        
        result = AuthService.validate_user_permissions(mock_user, [UserRole.ADMIN, UserRole.FACULTY])
        
        assert result is True
    
    def test_validate_user_permissions_failure(self):
        """Test failed permission validation."""
        mock_user = Mock(spec=User)
        mock_user.role = UserRole.STUDENT.value
        
        result = AuthService.validate_user_permissions(mock_user, [UserRole.ADMIN, UserRole.FACULTY])
        
        assert result is False

if __name__ == "__main__":
    pytest.main([__file__])