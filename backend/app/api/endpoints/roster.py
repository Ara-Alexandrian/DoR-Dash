from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.endpoints.auth import USERS_DB, User, get_current_user
from app.core.permissions import get_faculty_or_admin_user
from app.schemas.auth import UserResponse

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_roster(
    current_user: User = Depends(get_faculty_or_admin_user)
):
    """
    Get all students in the roster.
    Only faculty and admins can access the roster.
    """
    # Filter USERS_DB to only include students
    students = [user for user in USERS_DB if user["role"] == "student"]
    
    # Sort by name
    students.sort(key=lambda x: x.get("full_name", x["username"]))
    
    return students