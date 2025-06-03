from typing import List, Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from pydantic import EmailStr

from app.api.endpoints.mock_auth import DEMO_USERS, User, get_current_user
from app.core.permissions import get_admin_user, get_faculty_or_admin_user, is_owner_or_admin
from app.core.security import get_password_hash
from app.schemas.auth import UserCreate, UserUpdate, UserResponse

router = APIRouter()

# Ensure DEMO_USERS has some data
if not DEMO_USERS:
    DEMO_USERS.extend([
        {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "full_name": "Admin User",
            "preferred_email": None,
            "phone": None,
            "role": "admin",
            "is_active": True,
            "password": "password"
        },
        {
            "id": 2,
            "username": "faculty1",
            "email": "faculty1@example.com",
            "full_name": "Faculty Member",
            "preferred_email": "faculty1@personal.com",
            "phone": "555-123-4567",
            "role": "faculty",
            "is_active": True,
            "password": "password"
        },
        {
            "id": 3,
            "username": "student1",
            "email": "student1@example.com",
            "full_name": "Student One",
            "preferred_email": None,
            "phone": None,
            "role": "student",
            "is_active": True,
            "password": "password"
        }
    ])

# Function to generate a new user ID (for mock data)
def generate_user_id():
    if not DEMO_USERS:
        return 1
    return max(user["id"] for user in DEMO_USERS) + 1

# Get all users (admin or faculty only)
@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = Query(0, description="Skip N users"),
    limit: int = Query(100, description="Limit to N users"),
    current_user: User = Depends(get_faculty_or_admin_user)
):
    """
    Retrieve users.
    - Admin can see all users
    - Faculty can see all users
    - Students can't access this endpoint
    """
    return DEMO_USERS[skip : skip + limit]

# Get user by ID
@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int = Path(..., description="The ID of the user to get"),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific user by ID.
    - Admin can see any user
    - Faculty can see any user
    - Students can only see themselves
    """
    # Check if user is trying to access someone else's profile without permission
    if current_user.role == "student" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this user's information"
        )
    
    user = next((user for user in DEMO_USERS if user["id"] == user_id), None)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return user

# Create new user (admin only)
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    current_user: User = Depends(get_admin_user)
):
    """
    Create new user (admin only).
    """
    # Check if username or email already exists
    if any(u["username"] == user_in.username for u in DEMO_USERS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    if any(u["email"] == user_in.email for u in DEMO_USERS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Create new user
    new_user = user_in.dict()
    new_user["id"] = generate_user_id()
    new_user["password"] = get_password_hash(user_in.password)  # In real app, password would be hashed
    
    # Add to demo users
    DEMO_USERS.append(new_user)
    
    return new_user

# Update user (admin can update anyone, users can update themselves)
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    user_id: int = Path(..., description="The ID of the user to update"),
    current_user: User = Depends(get_current_user)
):
    """
    Update a user.
    - Admin can update any user
    - Users can only update themselves
    - Password changes are allowed
    """
    # Check if user exists
    user_idx = next((i for i, u in enumerate(DEMO_USERS) if u["id"] == user_id), None)
    
    if user_idx is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Check permissions - only admins or the user themselves can update
    if not is_owner_or_admin(user_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this user"
        )
    
    # Get user to update
    user = DEMO_USERS[user_idx]
    
    # If not admin, restrict what can be changed
    if current_user.role != "admin":
        # Regular users cannot change their role or active status
        if user_update.role is not None or user_update.is_active is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update role or active status"
            )
    
    # Update fields that were provided
    update_data = user_update.dict(exclude_unset=True)
    
    # Hash password if provided
    if "password" in update_data and update_data["password"]:
        update_data["password"] = get_password_hash(update_data["password"])  # In real app, hash the password
    
    for field, value in update_data.items():
        if value is not None:
            user[field] = value
    
    # Update in "database"
    DEMO_USERS[user_idx] = user
    
    return user

# Delete user (admin only)
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int = Path(..., description="The ID of the user to delete"),
    current_user: User = Depends(get_admin_user)
):
    """
    Delete a user (admin only).
    """
    # Check if user exists
    user_idx = next((i for i, u in enumerate(DEMO_USERS) if u["id"] == user_id), None)
    
    if user_idx is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Don't allow admin to delete themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account"
        )
    
    # Delete from "database"
    DEMO_USERS.pop(user_idx)
    
    return None

# Change password (admin can change anyone's, users can change their own)
@router.post("/{user_id}/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    user_id: int = Path(..., description="The ID of the user"),
    old_password: str = None,
    new_password: str = None,
    current_user: User = Depends(get_current_user)
):
    """
    Change a user's password.
    - Admin can change any user's password without knowing old password
    - Users can change their own password if they provide the correct old password
    """
    # Check if user exists
    user_idx = next((i for i, u in enumerate(DEMO_USERS) if u["id"] == user_id), None)
    
    if user_idx is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Check permissions
    if not is_owner_or_admin(user_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to change this user's password"
        )
    
    # Get user
    user = DEMO_USERS[user_idx]
    
    # Non-admins must provide the old password
    if current_user.role != "admin" and current_user.id == user_id:
        if not old_password or old_password != user["password"]:  # In real app, verify hash
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password"
            )
    
    # Update password
    user["password"] = get_password_hash(new_password)  # In real app, hash the password
    
    # Update in "database"
    DEMO_USERS[user_idx] = user
    
    return {"message": "Password changed successfully"}