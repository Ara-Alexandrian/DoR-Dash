from typing import Annotated
from fastapi import Depends, HTTPException, status
from app.api.endpoints.auth import get_current_user
from pydantic import BaseModel

# Mock equivalent model to the User from mock_auth
class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    preferred_email: str = None
    phone: str = None
    role: str
    is_active: bool

# Role hierarchy and permissions
ROLE_HIERARCHY = {
    "student": 1,  # Basic access
    "faculty": 2,  # Intermediate access
    "admin": 3     # Full access
}

def check_user_role(required_role: str, user_role: str) -> bool:
    """
    Check if user's role has sufficient permissions
    based on the role hierarchy.
    """
    if user_role not in ROLE_HIERARCHY or required_role not in ROLE_HIERARCHY:
        return False
        
    return ROLE_HIERARCHY[user_role] >= ROLE_HIERARCHY[required_role]

def has_role(required_role: str):
    """
    Dependency to check if a user has the required role or higher.
    """
    async def role_checker(current_user: Annotated[User, Depends(get_current_user)]):
        if not check_user_role(required_role, current_user.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. {required_role.capitalize()} role or higher required."
            )
        return current_user
    return role_checker

# Pre-defined permission dependencies
get_faculty_or_admin_user = has_role("faculty")
get_admin_user = has_role("admin")

# For APIs that only check if the user is the owner or an admin
def is_owner_or_admin(user_id: int, current_user: User) -> bool:
    """Check if current user is the resource owner or an admin"""
    if current_user.id == user_id:
        return True
    return current_user.role == "admin"