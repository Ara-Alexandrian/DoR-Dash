from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Path, Query, status
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session

from app.api.endpoints.auth import User, get_current_user
from app.db.models.meeting import Meeting, MeetingType
from app.db.session import get_sync_db
from app.api.endpoints.updates import STUDENT_UPDATES_DB
from app.api.endpoints.faculty_updates import FACULTY_UPDATES_DB

router = APIRouter()

# DATABASE STORAGE - NO MORE IN-MEMORY LOSS!

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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Create a new meeting (admin only) - SAVED TO POSTGRESQL
    """
    # Check if user is admin
    if current_user.role not in ["admin", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and faculty can create meetings"
        )
    
    # Create new meeting in database
    db_meeting = Meeting(
        title=meeting_in.title,
        description=meeting_in.description,
        meeting_type=meeting_in.meeting_type,
        start_time=meeting_in.start_time,
        end_time=meeting_in.end_time,
        created_by=current_user.id,
    )
    
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    
    return db_meeting

@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: int = Path(..., description="The ID of the meeting to retrieve"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get a meeting by ID - FROM POSTGRESQL
    """
    # Find the meeting in the database
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting with ID {meeting_id} not found"
        )
    
    return meeting

@router.get("/", response_model=List[MeetingResponse])
async def list_meetings(
    skip: int = Query(0, description="Number of meetings to skip for pagination"),
    limit: int = Query(100, description="Maximum number of meetings to return"),
    start_date: Optional[datetime] = Query(None, description="Filter meetings from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter meetings until this date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    List all meetings with optional filtering - FROM POSTGRESQL
    """
    # Build query with optional filters
    query = db.query(Meeting)
    
    if start_date:
        query = query.filter(Meeting.start_time >= start_date)
    
    if end_date:
        query = query.filter(Meeting.start_time <= end_date)
    
    # Sort by start time and apply pagination
    meetings = query.order_by(Meeting.start_time).offset(skip).limit(limit).all()
    
    return meetings

@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_in: MeetingUpdate,
    meeting_id: int = Path(..., description="The ID of the meeting to update"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Update a meeting (admin only) - SAVED TO POSTGRESQL
    """
    # Check if user is admin
    if current_user.role not in ["admin", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and faculty can update meetings"
        )
    
    # Find the meeting in the database
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting with ID {meeting_id} not found"
        )
    
    # Update only fields that were provided
    if meeting_in.title is not None:
        meeting.title = meeting_in.title
    if meeting_in.description is not None:
        meeting.description = meeting_in.description
    if meeting_in.meeting_type is not None:
        meeting.meeting_type = meeting_in.meeting_type
    if meeting_in.start_time is not None:
        meeting.start_time = meeting_in.start_time
    if meeting_in.end_time is not None:
        meeting.end_time = meeting_in.end_time
    
    # Save changes to database
    db.commit()
    db.refresh(meeting)
    
    return meeting
    

@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(
    meeting_id: int = Path(..., description="The ID of the meeting to delete"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Delete a meeting (admin only) - FROM POSTGRESQL
    """
    # Check if user is admin
    if current_user.role not in ["admin", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and faculty can delete meetings"
        )
    
    # Find the meeting in the database
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting with ID {meeting_id} not found"
        )
    
    # Delete from database
    db.delete(meeting)
    db.commit()
    
    return None


@router.get("/{meeting_id}/agenda")
async def get_meeting_agenda(
    meeting_id: int = Path(..., description="The ID of the meeting"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get complete agenda for a meeting including all updates - FROM POSTGRESQL
    """
    # Find the meeting in the database
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting with ID {meeting_id} not found"
        )
    
    # Get student updates for this meeting (still using in-memory for now)
    student_updates = [u for u in STUDENT_UPDATES_DB if u.get("meeting_id") == meeting_id]
    
    # Get faculty updates for this meeting (still using in-memory for now)
    faculty_updates = [u for u in FACULTY_UPDATES_DB if u.get("meeting_id") == meeting_id]
    
    print(f"DEBUG: Getting agenda for meeting {meeting_id}")
    print(f"DEBUG: Found {len(student_updates)} student updates")
    print(f"DEBUG: Found {len(faculty_updates)} faculty updates")
    print(f"DEBUG: Total updates in STUDENT_UPDATES_DB: {len(STUDENT_UPDATES_DB)}")
    print(f"DEBUG: Total updates in FACULTY_UPDATES_DB: {len(FACULTY_UPDATES_DB)}")
    
    # Compile agenda
    agenda = {
        "meeting": meeting,
        "student_updates": student_updates,
        "faculty_updates": faculty_updates,
        "total_updates": len(student_updates) + len(faculty_updates)
    }
    
    return agenda