from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.endpoints.auth import User, get_current_user, get_all_users
from app.core.permissions import get_admin_user
from app.db.session import get_sync_db

router = APIRouter()

# Mock data storage for presentations
PRESENTATIONS = []

class PresentationBase(BaseModel):
    user_id: int
    meeting_date: datetime
    status: str = "scheduled"
    is_confirmed: bool = False

class PresentationCreate(BaseModel):
    meeting_date: datetime

class PresentationUpdate(BaseModel):
    user_id: Optional[int] = None
    meeting_date: Optional[datetime] = None
    status: Optional[str] = None
    is_confirmed: Optional[bool] = None

class PresentationResponse(PresentationBase):
    id: int
    user_name: Optional[str] = None
    user_email: Optional[str] = None

# Generate ID for new presentation
def generate_presentation_id():
    if not PRESENTATIONS:
        return 1
    return max(p["id"] for p in PRESENTATIONS) + 1

@router.get("/", response_model=List[PresentationResponse])
async def get_presentations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get all presentations.
    - Students can only see their own presentations
    - Faculty and admins can see all presentations
    """
    # Get all users from database
    all_users = get_all_users(db)
    
    # Filter presentations based on user role
    if current_user.role == "student":
        filtered_presentations = [p for p in PRESENTATIONS if p["user_id"] == current_user.id]
    else:
        filtered_presentations = PRESENTATIONS
    
    # Add user information to each presentation
    result = []
    for presentation in filtered_presentations:
        # Find user info
        user = next((u for u in all_users if u["id"] == presentation["user_id"]), None)
        
        presentation_dict = presentation.copy()
        if user:
            presentation_dict["user_name"] = user.get("full_name", user["username"])
            presentation_dict["user_email"] = user["email"]
        
        result.append(presentation_dict)
    
    # Sort by meeting date
    result.sort(key=lambda x: x["meeting_date"])
    
    return result

@router.post("/assign", response_model=List[PresentationResponse])
async def assign_presentations(
    assignment_data: PresentationCreate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_sync_db)
):
    """
    Automatically assign presentations for a given meeting date.
    Admin only endpoint.
    """
    # Get all users from database
    all_users = get_all_users(db)
    
    # Get all students
    students = [u for u in all_users if u["role"] == "student"]
    
    if not students:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No students available to assign presentations"
        )
    
    # Create presentations for each student
    new_presentations = []
    meeting_date = assignment_data.meeting_date
    
    for i, student in enumerate(students):
        # Check if student already has a presentation on this date
        existing = any(
            p["user_id"] == student["id"] and 
            p["meeting_date"].date() == meeting_date.date() 
            for p in PRESENTATIONS
        )
        
        if not existing:
            presentation = {
                "id": generate_presentation_id(),
                "user_id": student["id"],
                "meeting_date": meeting_date + timedelta(minutes=15 * i),  # 15 min slots
                "status": "scheduled",
                "is_confirmed": False,
                "user_name": student.get("full_name", student["username"]),
                "user_email": student["email"]
            }
            PRESENTATIONS.append(presentation)
            new_presentations.append(presentation)
    
    return new_presentations

@router.put("/{presentation_id}", response_model=PresentationResponse)
async def update_presentation(
    presentation_id: int,
    update_data: PresentationUpdate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_sync_db)
):
    """
    Update a presentation assignment.
    Admin only endpoint.
    """
    # Get all users from database
    all_users = get_all_users(db)
    
    # Find presentation
    presentation_idx = next(
        (i for i, p in enumerate(PRESENTATIONS) if p["id"] == presentation_id), 
        None
    )
    
    if presentation_idx is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Presentation with ID {presentation_id} not found"
        )
    
    # Update fields
    presentation = PRESENTATIONS[presentation_idx]
    update_dict = update_data.dict(exclude_unset=True)
    
    for field, value in update_dict.items():
        if value is not None:
            presentation[field] = value
    
    # Update user info if user_id changed
    if "user_id" in update_dict:
        user = next((u for u in all_users if u["id"] == presentation["user_id"]), None)
        if user:
            presentation["user_name"] = user.get("full_name", user["username"])
            presentation["user_email"] = user["email"]
    
    PRESENTATIONS[presentation_idx] = presentation
    
    return presentation

@router.delete("/{presentation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_presentation(
    presentation_id: int,
    current_user: User = Depends(get_admin_user)
):
    """
    Delete a presentation.
    Admin only endpoint.
    """
    # Find presentation
    presentation_idx = next(
        (i for i, p in enumerate(PRESENTATIONS) if p["id"] == presentation_id), 
        None
    )
    
    if presentation_idx is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Presentation with ID {presentation_id} not found"
        )
    
    # Delete from list
    PRESENTATIONS.pop(presentation_idx)
    
    return None