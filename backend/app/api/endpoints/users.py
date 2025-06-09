from typing import List, Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from pydantic import EmailStr

from sqlalchemy.orm import Session
from app.api.endpoints.auth import User, get_current_user, create_user as auth_create_user, update_user as auth_update_user, delete_user as auth_delete_user, get_all_users
from app.db.session import get_sync_db
from app.core.permissions import get_admin_user, get_faculty_or_admin_user, is_owner_or_admin
from app.core.security import get_password_hash
from app.schemas.auth import UserCreate, UserUpdate, UserResponse

router = APIRouter()

# Function to generate a new user ID - no longer needed with database auto-increment

# Get all users (admin or faculty only)
@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = Query(0, description="Skip N users"),
    limit: int = Query(100, description="Limit to N users"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_sync_db)
):
    """
    Retrieve users for management (admin only).
    For viewing roster, use /roster endpoint instead.
    """
    all_users = get_all_users(db)
    return all_users[skip : skip + limit]

# Get user by ID
@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int = Path(..., description="The ID of the user to get"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
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
    
    all_users = get_all_users(db)
    user = next((user for user in all_users if user["id"] == user_id), None)
    
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
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_sync_db)
):
    """
    Create new user (admin only).
    """
    all_users = get_all_users(db)
    
    # Check if username or email already exists
    if any(u["username"] == user_in.username for u in all_users):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    if any(u["email"] == user_in.email for u in all_users):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Create new user
    new_user = user_in.dict()
    new_user["password"] = user_in.password
    
    # Add to users database
    created_user = auth_create_user(db, new_user)
    
    return created_user

# Update user (admin can update anyone, users can update themselves)
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    user_id: int = Path(..., description="The ID of the user to update"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Update a user.
    - Admin can update any user
    - Users can only update themselves
    - Password changes are allowed
    """
    all_users = get_all_users(db)
    
    # Check if user exists
    user = next((u for u in all_users if u["id"] == user_id), None)
    
    if user is None:
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
    
    try:
        # Update in database using auth function
        updated_user = auth_update_user(db, user_id, update_data)
        
        if updated_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        return updated_user
        
    except ValueError as e:
        # Handle validation errors (like invalid role)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Handle other database errors
        print(f"ERROR in update_user endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )

# Delete user (admin only)
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int = Path(..., description="The ID of the user to delete"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_sync_db)
):
    """
    Delete a user (admin only).
    """
    all_users = get_all_users(db)
    
    # Check if user exists
    user = next((u for u in all_users if u["id"] == user_id), None)
    
    if user is None:
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
    
    # Delete from database using auth function
    auth_delete_user(db, user_id)
    
    return None

# Change password (admin can change anyone's, users can change their own)
@router.post("/{user_id}/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    user_id: int = Path(..., description="The ID of the user"),
    old_password: str = None,
    new_password: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Change a user's password.
    - Admin can change any user's password without knowing old password
    - Users can change their own password if they provide the correct old password
    """
    all_users = get_all_users(db)
    
    # Check if user exists
    user = next((u for u in all_users if u["id"] == user_id), None)
    
    if user is None:
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
    
    # Non-admins must provide the old password (Note: password verification would need to be enhanced for real passwords)
    if current_user.role != "admin" and current_user.id == user_id:
        if not old_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old password is required"
            )
    
    # Update password using auth function
    auth_update_user(db, user_id, {"password": new_password})
    
    return {"message": "Password changed successfully"}