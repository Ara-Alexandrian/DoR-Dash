from datetime import datetime, timedelta
from typing import List, Optional, Annotated
from fastapi import APIRouter, HTTPException, Depends, Path, Query, status
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.core.security import get_password_hash
from app.db.models.user import User, UserRole
from app.db.models.student_update import StudentUpdate
from app.db.models.meeting import Meeting, MeetingType
from app.db.session import get_sync_db as get_db
from app.services.auth import get_current_user, get_current_active_user

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
        orm_mode = True

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
        orm_mode = True

class MeetingResponse(MeetingBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

# Routes
@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    meeting_in: MeetingCreate
):
    """
    Create a new meeting (admin only)
    """
    # Mock implementation
    return {
        "id": 1,
        "title": meeting_in.title,
        "description": meeting_in.description,
        "date": meeting_in.date,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "created_by": 1,
    }

@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: int = Path(..., description="The ID of the meeting to retrieve")
):
    """
    Get a meeting by ID
    """
    # Mock implementation
    return {
        "id": meeting_id,
        "title": "Sample Meeting",
        "description": "Sample description",
        "date": datetime.now().date(),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "created_by": 1,
    }

@router.get("/", response_model=List[MeetingResponse])
async def list_meetings(
    skip: int = Query(0, description="Number of meetings to skip for pagination"),
    limit: int = Query(100, description="Maximum number of meetings to return")
):
    """
    List all meetings with optional filtering
    """
    # Mock implementation
    meetings = [
        {
            "id": 1,
            "title": "Weekly Team Meeting",
            "description": "Regular weekly sync",
            "date": datetime.now().date(),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "created_by": 1,
        },
        {
            "id": 2,
            "title": "Project Planning Session",
            "description": "Planning for Q3",
            "date": (datetime.now() + timedelta(days=7)).date(),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "created_by": 1,
        }
    ]
    
    return meetings[skip:skip+limit]

@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_in: MeetingUpdate,
    meeting_id: int = Path(..., description="The ID of the meeting to update")
):
    """
    Update a meeting (admin only)
    """
    # Mock implementation
    return {
        "id": meeting_id,
        "title": meeting_in.title or "Updated Meeting",
        "description": meeting_in.description or "Updated description",
        "date": meeting_in.date or datetime.now().date(),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "created_by": 1,
    }
    

@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(
    meeting_id: int = Path(..., description="The ID of the meeting to delete")
):
    """
    Delete a meeting (admin only)
    """
    # Mock implementation
    return None