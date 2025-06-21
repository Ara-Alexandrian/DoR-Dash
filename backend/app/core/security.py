"""
Security configuration and utilities for DoR-Dash application.
Centralized security settings and validation functions.
"""
import os
import secrets
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityConfig:
    """Centralized security configuration."""
    
    def __init__(self):
        self.secret_key = self._get_secret_key()
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    def _get_secret_key(self) -> str:
        """Get JWT secret key from environment or generate a secure one."""
        secret_key = os.getenv("SECRET_KEY")
        
        if not secret_key:
            raise ValueError(
                "SECRET_KEY environment variable is required. "
                "Generate one using: python -c 'import secrets; print(secrets.token_urlsafe(64))'"
            )
        
        # Validate secret key strength
        if len(secret_key) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters long for security. "
                "Generate a stronger one using: python -c 'import secrets; print(secrets.token_urlsafe(64))'"
            )
        
        return secret_key
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None

# Global security configuration instance
security_config = SecurityConfig()

# Convenience functions for backward compatibility
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token (convenience function)."""
    return security_config.create_access_token(data, expires_delta)

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token (convenience function)."""
    return security_config.verify_token(token)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)

def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength.
    Returns (is_valid, list_of_errors)
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")
    
    # Optional: special character requirement
    # if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
    #     errors.append("Password must contain at least one special character")
    
    return len(errors) == 0, errors