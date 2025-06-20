from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Path, Query, status
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session

from app.api.endpoints.auth import User, get_current_user
from app.db.models.meeting import Meeting, MeetingType
from app.db.models.agenda_item import AgendaItem as DBAgendaItem, AgendaItemType
from app.db.session import get_sync_db
from sqlalchemy.orm import joinedload
# Legacy in-memory storage no longer needed - all data is in PostgreSQL

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
    Delete a meeting and all associated agenda items (admin only) - FROM POSTGRESQL
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
    
    # Delete the meeting (agenda items will be deleted via CASCADE)
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
    Get complete agenda for a meeting - UNIFIED AGENDA ITEMS (SIMPLIFIED!)
    """
    # Import here to avoid circular imports
    from app.db.models.agenda_item import AgendaItem as DBAgendaItem, AgendaItemType
    from app.schemas.agenda_item import StudentUpdate, FacultyUpdate
    
    # Find the meeting in the database
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meeting with ID {meeting_id} not found"
        )
    
    # Get ALL agenda items for this meeting in proper order - SINGLE QUERY!
    agenda_items = db.query(DBAgendaItem).options(
        joinedload(DBAgendaItem.user),
        joinedload(DBAgendaItem.file_uploads)
    ).filter(
        DBAgendaItem.meeting_id == meeting_id
    ).order_by(DBAgendaItem.order_index, DBAgendaItem.created_at).all()
    
    # Separate into legacy format for backward compatibility
    student_updates = []
    faculty_updates = []
    
    for item in agenda_items:
        # Convert files to expected format
        files = []
        for file_upload in item.file_uploads:
            files.append({
                "id": file_upload.id,
                "name": file_upload.filename,
                "size": file_upload.file_size or 0,
                "file_path": file_upload.file_path,
                "type": file_upload.file_type or "other",
                "upload_date": file_upload.upload_date.isoformat() if file_upload.upload_date else None
            })
        
        if item.item_type == AgendaItemType.STUDENT_UPDATE.value:
            content = item.content
            student_updates.append({
                "id": item.id,
                "user_id": item.user_id,
                "user_name": item.user.full_name or item.user.username,
                "progress_text": content.get("progress_text", ""),
                "challenges_text": content.get("challenges_text", ""),
                "next_steps_text": content.get("next_steps_text", ""),
                "meeting_notes": content.get("meeting_notes", ""),
                "will_present": item.is_presenting,
                "meeting_id": item.meeting_id,
                "files": files,
                "submission_date": item.created_at.isoformat(),
                "submitted_at": item.created_at.isoformat(),  # For frontend compatibility
                "created_at": item.created_at.isoformat(),
                "updated_at": item.updated_at.isoformat()
            })
        
        elif item.item_type == AgendaItemType.FACULTY_UPDATE.value:
            content = item.content
            faculty_updates.append({
                "id": item.id,
                "user_id": item.user_id,
                "user_name": item.user.full_name or item.user.username,
                "announcements_text": content.get("announcements_text", ""),
                "announcement_type": content.get("announcement_type", "general"),
                "projects_text": content.get("projects_text", ""),
                "project_status_text": content.get("project_status_text", ""),
                "faculty_questions": content.get("faculty_questions", ""),
                "is_presenting": item.is_presenting,
                "meeting_id": item.meeting_id,
                "files": files,
                "submission_date": item.created_at.isoformat(),
                "submitted_at": item.created_at.isoformat(),  # For frontend compatibility
                "created_at": item.created_at.isoformat(),
                "updated_at": item.updated_at.isoformat()
            })
    
    # Compile agenda - MUCH SIMPLER!
    agenda = {
        "meeting": meeting,
        "student_updates": student_updates,
        "faculty_updates": faculty_updates,
        "total_updates": len(student_updates) + len(faculty_updates)
    }
    
    return agenda


@router.get("/integrity-check")
async def check_meeting_data_integrity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Check data integrity across meetings and updates (admin only)
    """
    # Check if user is admin
    if current_user.role not in ["admin", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and faculty can access integrity checks"
        )
    
    # Find orphaned agenda items (meeting_id points to non-existent meeting)
    orphaned_agenda_items = db.query(DBAgendaItem).outerjoin(
        Meeting, DBAgendaItem.meeting_id == Meeting.id
    ).filter(
        DBAgendaItem.meeting_id.isnot(None),
        Meeting.id.is_(None)
    ).all()
    
    # Find agenda items without meeting assignment
    unassigned_agenda_items = db.query(DBAgendaItem).filter(
        DBAgendaItem.meeting_id.is_(None)
    ).all()
    
    # Find meetings without any agenda items
    meetings_without_updates = db.query(Meeting).outerjoin(
        DBAgendaItem, Meeting.id == DBAgendaItem.meeting_id
    ).filter(
        DBAgendaItem.id.is_(None)
    ).all()
    
    integrity_report = {
        "orphaned_data": {
            "agenda_items": [
                {"id": u.id, "user_id": u.user_id, "meeting_id": u.meeting_id, "item_type": u.item_type, "created_at": u.created_at.isoformat()}
                for u in orphaned_agenda_items
            ]
        },
        "unassigned_updates": {
            "agenda_items": [
                {"id": u.id, "user_id": u.user_id, "item_type": u.item_type, "created_at": u.created_at.isoformat()}
                for u in unassigned_agenda_items
            ]
        },
        "empty_meetings": [
            {"id": m.id, "title": m.title, "start_time": m.start_time.isoformat()}
            for m in meetings_without_updates
        ],
        "summary": {
            "orphaned_agenda_items": len(orphaned_agenda_items),
            "unassigned_agenda_items": len(unassigned_agenda_items),
            "empty_meetings": len(meetings_without_updates),
            "total_issues": len(orphaned_agenda_items) + len(unassigned_agenda_items)
        }
    }
    
    return integrity_report


@router.post("/cleanup-orphaned")
async def cleanup_orphaned_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Clean up orphaned agenda items (admin only)
    """
    # Check if user is admin
    if current_user.role not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform data cleanup"
        )
    
    # Delete orphaned agenda items
    orphaned_count = db.query(DBAgendaItem).outerjoin(
        Meeting, DBAgendaItem.meeting_id == Meeting.id
    ).filter(
        DBAgendaItem.meeting_id.isnot(None),
        Meeting.id.is_(None)
    ).count()
    
    db.query(DBAgendaItem).outerjoin(
        Meeting, DBAgendaItem.meeting_id == Meeting.id
    ).filter(
        DBAgendaItem.meeting_id.isnot(None),
        Meeting.id.is_(None)
    ).delete()
    
    db.commit()
    
    return {
        "message": "Cleanup completed successfully",
        "deleted": {
            "agenda_items": orphaned_count,
            "total": orphaned_count
        }
    }