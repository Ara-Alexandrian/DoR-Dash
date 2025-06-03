from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Path, Query, status
from pydantic import BaseModel, validator

from app.db.models.user import User, UserRole
from app.db.models.meeting import MeetingType
from app.services.auth import get_current_active_user

router = APIRouter()

# Schemas
class MeetingBase(BaseModel):
    title: str
    description: Optional[str] = None
    meeting_type: MeetingType
    start_time: datetime
    end_time: datetime
    
    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and v < values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v
    
    class Config:
        from_attributes = True

class MeetingCreate(MeetingBase):
    pass

class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    meeting_type: Optional[MeetingType] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if v and 'start_time' in values and values['start_time'] and v < values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v
    
    class Config:
        from_attributes = True

class MeetingResponse(MeetingBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

# Routes
@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    meeting_in: MeetingCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new meeting (admin only)
    """
    # Check if user is admin
    if current_user.role not in [UserRole.admin, UserRole.faculty]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and faculty can create meetings"
        )
    
    # Mock implementation - in production this would save to database
    return {
        "id": 1,
        "title": meeting_in.title,
        "description": meeting_in.description,
        "meeting_type": meeting_in.meeting_type,
        "start_time": meeting_in.start_time,
        "end_time": meeting_in.end_time,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "created_by": current_user.id,
    }

@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: int = Path(..., description="The ID of the meeting to retrieve"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a meeting by ID
    """
    # Mock implementation
    return {
        "id": meeting_id,
        "title": "Sample Meeting",
        "description": "Sample description",
        "meeting_type": MeetingType.general_update,
        "start_time": datetime.now(),
        "end_time": datetime.now() + timedelta(hours=1),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "created_by": 1,
    }

@router.get("/", response_model=List[MeetingResponse])
async def list_meetings(
    skip: int = Query(0, description="Number of meetings to skip for pagination"),
    limit: int = Query(100, description="Maximum number of meetings to return"),
    start_date: Optional[datetime] = Query(None, description="Filter meetings from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter meetings until this date"),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all meetings with optional filtering
    """
    # Return empty list - no mock data, but structure is correct
    meetings = []
    
    return meetings[skip:skip+limit]

@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_in: MeetingUpdate,
    meeting_id: int = Path(..., description="The ID of the meeting to update"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a meeting (admin only)
    """
    # Check if user is admin
    if current_user.role not in [UserRole.admin, UserRole.faculty]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and faculty can update meetings"
        )
    
    # Mock implementation
    return {
        "id": meeting_id,
        "title": meeting_in.title or "Updated Meeting",
        "description": meeting_in.description or "Updated description",
        "meeting_type": meeting_in.meeting_type or MeetingType.general_update,
        "start_time": meeting_in.start_time or datetime.now(),
        "end_time": meeting_in.end_time or datetime.now() + timedelta(hours=1),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "created_by": 1,
    }
    

@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(
    meeting_id: int = Path(..., description="The ID of the meeting to delete"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a meeting (admin only)
    """
    # Check if user is admin
    if current_user.role not in [UserRole.admin, UserRole.faculty]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and faculty can delete meetings"
        )
    
    # Mock implementation
    return None