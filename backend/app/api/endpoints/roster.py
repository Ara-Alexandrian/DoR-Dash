from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session
from app.api.endpoints.auth import User, get_current_user, get_all_users
from app.db.session import get_sync_db
from app.core.permissions import get_faculty_or_admin_user
from app.schemas.auth import UserResponse

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_roster(
    current_user: User = Depends(get_faculty_or_admin_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get all users in the roster.
    Only faculty, secretary, and admins can access the roster.
    """
    # Return all users from database
    all_users = get_all_users(db)
    
    # Sort by role hierarchy then by name
    role_order = {"admin": 1, "faculty": 2, "secretary": 3, "student": 4}
    all_users.sort(key=lambda x: (role_order.get(x["role"], 5), x.get("full_name", x["username"])))
    
    return all_users