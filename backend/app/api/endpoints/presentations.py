from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from app.api.endpoints.auth import User, get_current_user, get_all_users
from app.core.permissions import get_admin_user
from app.db.session import get_sync_db
from app.db.models.agenda_item import AgendaItem as DBAgendaItem, AgendaItemType
from app.db.models.user import User as DBUser
from app.db.models.presentation import AssignedPresentation as DBPresentation

router = APIRouter()

# DATABASE STORAGE - NO MORE IN-MEMORY LOSS!
# Note: Keep PRESENTATIONS for backward compatibility during transition
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
    Get all presentations from DATABASE (no more data loss!).
    - Students can only see their own presentations
    - Faculty and admins can see all presentations
    """
    # Query presentations from database (no joinedload to avoid relationship issues)
    query = db.query(DBPresentation)
    
    # Filter presentations based on user role
    if current_user.role == "student":
        # Students can only see their own presentations
        query = query.filter(DBPresentation.user_id == current_user.id)
    
    # Get all presentations
    presentations = query.order_by(DBPresentation.meeting_date.desc()).all()
    
    # Convert to response format
    result = []
    for presentation in presentations:
        # Get user data separately since no relationship exists
        user = db.query(DBUser).filter(DBUser.id == presentation.user_id).first()
        user_name = user.full_name if user and user.full_name else (user.username if user else "Unknown")
        user_email = user.email if user else "unknown@example.com"
        
        result.append({
            "id": presentation.id,
            "user_id": presentation.user_id,
            "user_name": user_name,
            "user_email": user_email,
            "meeting_date": presentation.meeting_date,
            "status": presentation.status,
            "is_confirmed": presentation.is_confirmed
        })
    
    return result

@router.post("/", response_model=PresentationResponse, status_code=status.HTTP_201_CREATED)
async def create_presentation(
    presentation_data: PresentationBase,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_sync_db)
):
    """
    Create a new presentation assignment (admin only).
    """
    # Validate that the user exists
    user = db.query(DBUser).filter(DBUser.id == presentation_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {presentation_data.user_id} not found"
        )
    
    # Create new presentation in database
    new_presentation = DBPresentation(
        user_id=presentation_data.user_id,
        meeting_date=presentation_data.meeting_date,
        status=presentation_data.status,
        is_confirmed=presentation_data.is_confirmed
    )
    
    db.add(new_presentation)
    db.commit()
    db.refresh(new_presentation)
    
    # Return response with user info
    return {
        "id": new_presentation.id,
        "user_id": new_presentation.user_id,
        "user_name": user.full_name if user.full_name else user.username,
        "user_email": user.email,
        "meeting_date": new_presentation.meeting_date,
        "status": new_presentation.status,
        "is_confirmed": new_presentation.is_confirmed
    }

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