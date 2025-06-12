from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Path, Query, status
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session

from app.api.endpoints.auth import User, get_current_user
from app.db.models.meeting import Meeting, MeetingType
from app.db.models.student_update import StudentUpdate as DBStudentUpdate
from app.db.models.faculty_update import FacultyUpdate as DBFacultyUpdate
from app.db.session import get_sync_db
from sqlalchemy.orm import joinedload
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
    
    # Count associated agenda items for logging
    student_updates_count = db.query(DBStudentUpdate).filter(DBStudentUpdate.meeting_id == meeting_id).count()
    faculty_updates_count = db.query(DBFacultyUpdate).filter(DBFacultyUpdate.meeting_id == meeting_id).count()
    
    print(f"DEBUG: Deleting meeting {meeting_id} with {student_updates_count} student updates and {faculty_updates_count} faculty updates")
    
    # Delete all associated student updates first (with their file uploads via cascade)
    db.query(DBStudentUpdate).filter(DBStudentUpdate.meeting_id == meeting_id).delete()
    
    # Delete all associated faculty updates first (with their file uploads via cascade)  
    db.query(DBFacultyUpdate).filter(DBFacultyUpdate.meeting_id == meeting_id).delete()
    
    # Now delete the meeting itself
    db.delete(meeting)
    db.commit()
    
    print(f"DEBUG: Successfully deleted meeting {meeting_id} and all associated agenda items")
    
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
    
    # Get student updates for this meeting from DATABASE
    student_updates_query = db.query(DBStudentUpdate).options(
        joinedload(DBStudentUpdate.user),
        joinedload(DBStudentUpdate.file_uploads)
    ).filter(DBStudentUpdate.meeting_id == meeting_id)

    student_updates = []
    for update in student_updates_query.all():
        # Convert to same format as frontend expects
        files = []
        for file_upload in update.file_uploads:
            files.append({
                "id": file_upload.id,
                "name": file_upload.filename,
                "size": file_upload.file_size or 0,
                "file_path": file_upload.file_path,
                "type": file_upload.file_type or "other",
                "upload_date": file_upload.upload_date.isoformat() if file_upload.upload_date else None
            })
        
        student_updates.append({
            "id": update.id,
            "user_id": update.user_id,
            "user_name": update.user.full_name or update.user.username,
            "progress_text": update.progress_text,
            "challenges_text": update.challenges_text,
            "next_steps_text": update.next_steps_text,
            "meeting_notes": update.meeting_notes,
            "will_present": update.will_present,
            "meeting_id": update.meeting_id,
            "files": files,
            "submission_date": update.submission_date.isoformat(),
            "created_at": update.created_at.isoformat(),
            "updated_at": update.updated_at.isoformat()
        })
    
    # Get faculty updates for this meeting from DATABASE
    faculty_updates_query = db.query(DBFacultyUpdate).options(
        joinedload(DBFacultyUpdate.user)
    ).filter(DBFacultyUpdate.meeting_id == meeting_id)

    faculty_updates = []
    for update in faculty_updates_query.all():
        faculty_updates.append({
            "id": update.id,
            "user_id": update.user_id,
            "user_name": update.user.full_name or update.user.username,
            "announcements_text": update.announcements_text,
            "announcement_type": update.announcement_type.value if update.announcement_type else "general",
            "projects_text": update.projects_text,
            "project_status_text": update.project_status_text,
            "faculty_questions": update.faculty_questions,
            "is_presenting": update.is_presenting,
            "meeting_id": update.meeting_id,
            "submission_date": update.submission_date.isoformat(),
            "created_at": update.created_at.isoformat(),
            "updated_at": update.updated_at.isoformat()
        })
    
    print(f"DEBUG: Getting agenda for meeting {meeting_id} from DATABASE")
    print(f"DEBUG: Found {len(student_updates)} student updates in PostgreSQL")
    print(f"DEBUG: Found {len(faculty_updates)} faculty updates in PostgreSQL")
    
    # Compile agenda
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
    
    # Find orphaned student updates (meeting_id points to non-existent meeting)
    orphaned_student_updates = db.query(DBStudentUpdate).outerjoin(
        Meeting, DBStudentUpdate.meeting_id == Meeting.id
    ).filter(
        DBStudentUpdate.meeting_id.isnot(None),
        Meeting.id.is_(None)
    ).all()
    
    # Find orphaned faculty updates
    orphaned_faculty_updates = db.query(DBFacultyUpdate).outerjoin(
        Meeting, DBFacultyUpdate.meeting_id == Meeting.id
    ).filter(
        DBFacultyUpdate.meeting_id.isnot(None),
        Meeting.id.is_(None)
    ).all()
    
    # Find updates without meeting assignment
    unassigned_student_updates = db.query(DBStudentUpdate).filter(
        DBStudentUpdate.meeting_id.is_(None)
    ).all()
    
    unassigned_faculty_updates = db.query(DBFacultyUpdate).filter(
        DBFacultyUpdate.meeting_id.is_(None)
    ).all()
    
    # Find meetings without any updates
    meetings_without_updates = db.query(Meeting).outerjoin(
        DBStudentUpdate, Meeting.id == DBStudentUpdate.meeting_id
    ).outerjoin(
        DBFacultyUpdate, Meeting.id == DBFacultyUpdate.meeting_id
    ).filter(
        DBStudentUpdate.id.is_(None),
        DBFacultyUpdate.id.is_(None)
    ).all()
    
    integrity_report = {
        "orphaned_data": {
            "student_updates": [
                {"id": u.id, "user_id": u.user_id, "meeting_id": u.meeting_id, "created_at": u.created_at.isoformat()}
                for u in orphaned_student_updates
            ],
            "faculty_updates": [
                {"id": u.id, "user_id": u.user_id, "meeting_id": u.meeting_id, "created_at": u.created_at.isoformat()}
                for u in orphaned_faculty_updates
            ]
        },
        "unassigned_updates": {
            "student_updates": [
                {"id": u.id, "user_id": u.user_id, "created_at": u.created_at.isoformat()}
                for u in unassigned_student_updates
            ],
            "faculty_updates": [
                {"id": u.id, "user_id": u.user_id, "created_at": u.created_at.isoformat()}
                for u in unassigned_faculty_updates
            ]
        },
        "empty_meetings": [
            {"id": m.id, "title": m.title, "start_time": m.start_time.isoformat()}
            for m in meetings_without_updates
        ],
        "summary": {
            "orphaned_student_updates": len(orphaned_student_updates),
            "orphaned_faculty_updates": len(orphaned_faculty_updates),
            "unassigned_student_updates": len(unassigned_student_updates),
            "unassigned_faculty_updates": len(unassigned_faculty_updates),
            "empty_meetings": len(meetings_without_updates),
            "total_issues": len(orphaned_student_updates) + len(orphaned_faculty_updates)
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
    
    # Delete orphaned student updates
    orphaned_student_count = db.query(DBStudentUpdate).outerjoin(
        Meeting, DBStudentUpdate.meeting_id == Meeting.id
    ).filter(
        DBStudentUpdate.meeting_id.isnot(None),
        Meeting.id.is_(None)
    ).count()
    
    db.query(DBStudentUpdate).outerjoin(
        Meeting, DBStudentUpdate.meeting_id == Meeting.id
    ).filter(
        DBStudentUpdate.meeting_id.isnot(None),
        Meeting.id.is_(None)
    ).delete()
    
    # Delete orphaned faculty updates
    orphaned_faculty_count = db.query(DBFacultyUpdate).outerjoin(
        Meeting, DBFacultyUpdate.meeting_id == Meeting.id
    ).filter(
        DBFacultyUpdate.meeting_id.isnot(None),
        Meeting.id.is_(None)
    ).count()
    
    db.query(DBFacultyUpdate).outerjoin(
        Meeting, DBFacultyUpdate.meeting_id == Meeting.id
    ).filter(
        DBFacultyUpdate.meeting_id.isnot(None),
        Meeting.id.is_(None)
    ).delete()
    
    db.commit()
    
    return {
        "message": "Cleanup completed successfully",
        "deleted": {
            "student_updates": orphaned_student_count,
            "faculty_updates": orphaned_faculty_count,
            "total": orphaned_student_count + orphaned_faculty_count
        }
    }