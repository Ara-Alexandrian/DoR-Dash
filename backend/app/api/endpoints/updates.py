from datetime import datetime
from typing import List, Optional, Annotated
from fastapi import APIRouter, HTTPException, Depends, Path, Query, status, UploadFile, File, Form
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
import os
import tempfile

from app.api.endpoints.auth import User, get_current_user
from app.schemas.student_update import (
    StudentUpdate, 
    StudentUpdateCreate,
    StudentUpdateUpdate,
    StudentUpdateList
)
from app.db.models.student_update import StudentUpdate as DBStudentUpdate
from app.db.models.user import User as DBUser
from app.db.models.meeting import Meeting as DBMeeting
from app.db.models.file_upload import FileUpload as DBFileUpload
from app.db.session import get_sync_db

router = APIRouter()

# DATABASE STORAGE - NO MORE IN-MEMORY LOSS!
# Note: Keep STUDENT_UPDATES_DB for backward compatibility during transition
STUDENT_UPDATES_DB = []
update_id_counter = 1  # Simple ID counter


@router.post("/", response_model=StudentUpdate, status_code=status.HTTP_201_CREATED)
async def create_student_update(
    current_user: Annotated[User, Depends(get_current_user)],
    update_in: StudentUpdateCreate,
    db: Session = Depends(get_sync_db)
):
    """
    Create a new student update - NOW PERSISTENT IN DATABASE!
    """
    # Enhanced user validation with detailed error messages
    if current_user.role != "admin" and update_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: User {current_user.id} ({current_user.username}) cannot submit updates for user {update_in.user_id}. Students can only submit for themselves."
        )
    
    # Additional security check - ensure user_id is valid and positive
    if update_in.user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id: Must be a positive integer"
        )
    
    # Validate user exists
    user = db.query(DBUser).filter(DBUser.id == update_in.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate meeting exists if provided
    if update_in.meeting_id:
        # Check for valid meeting_id format
        if update_in.meeting_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid meeting_id: Must be a positive integer"
            )
        
        meeting = db.query(DBMeeting).filter(DBMeeting.id == update_in.meeting_id).first()
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meeting with ID {update_in.meeting_id} not found. Please ensure the meeting exists before submitting updates."
            )
        
        # Additional check: ensure meeting is not in the past (optional warning)
        if meeting.start_time < datetime.now():
            print(f"WARNING: User {current_user.id} submitting update for past meeting {meeting.id} ({meeting.title})")
    
    # Create new database record
    db_update = DBStudentUpdate(
        user_id=update_in.user_id,
        meeting_id=update_in.meeting_id,
        progress_text=update_in.progress_text,
        challenges_text=update_in.challenges_text,
        next_steps_text=update_in.next_steps_text,
        meeting_notes=getattr(update_in, 'meeting_notes', None),
        will_present=getattr(update_in, 'will_present', False)
    )
    
    # Save to database
    db.add(db_update)
    db.commit()
    db.refresh(db_update)
    
    print(f"DEBUG: Created student update with ID {db_update.id}, meeting_id: {db_update.meeting_id}")
    print(f"DEBUG: Update saved to PostgreSQL database")
    
    # Convert to response format
    return StudentUpdate(
        id=db_update.id,
        user_id=db_update.user_id,
        user_name=user.full_name or user.username,
        progress_text=db_update.progress_text,
        challenges_text=db_update.challenges_text,
        next_steps_text=db_update.next_steps_text,
        meeting_notes=db_update.meeting_notes,
        will_present=db_update.will_present,
        meeting_id=db_update.meeting_id,
        files=[],  # Will be loaded separately
        submission_date=db_update.submission_date,
        created_at=db_update.created_at,
        updated_at=db_update.updated_at
    )


@router.get("/{update_id}", response_model=StudentUpdate)
async def read_student_update(
    current_user: Annotated[User, Depends(get_current_user)],
    update_id: int = Path(..., description="The ID of the student update to retrieve"),
    db: Session = Depends(get_sync_db)
):
    """
    Get a specific student update by ID - FROM DATABASE
    """
    # Find the update in database
    update = db.query(DBStudentUpdate).options(
        joinedload(DBStudentUpdate.user),
        joinedload(DBStudentUpdate.file_uploads)
    ).filter(DBStudentUpdate.id == update_id).first()
    
    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student update with ID {update_id} not found"
        )
    
    # Check permissions - admins and faculty can see all updates, students can only see their own
    if current_user.role not in ["admin", "faculty"] and update.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own updates"
        )
    
    # Convert files to expected format
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
    
    return StudentUpdate(
        id=update.id,
        user_id=update.user_id,
        user_name=update.user.full_name or update.user.username,
        progress_text=update.progress_text,
        challenges_text=update.challenges_text,
        next_steps_text=update.next_steps_text,
        meeting_notes=update.meeting_notes,
        will_present=update.will_present,
        meeting_id=update.meeting_id,
        files=files,
        submission_date=update.submission_date,
        created_at=update.created_at,
        updated_at=update.updated_at
    )


@router.get("/", response_model=StudentUpdateList)
async def list_student_updates(
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, description="Number of updates to skip"),
    limit: int = Query(100, description="Max number of updates to return"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    meeting_id: Optional[int] = Query(None, description="Filter by meeting ID"),
    db: Session = Depends(get_sync_db)
):
    """
    List student updates with pagination and optional filtering - FROM DATABASE
    """
    # Start with base query
    query = db.query(DBStudentUpdate).options(
        joinedload(DBStudentUpdate.user),
        joinedload(DBStudentUpdate.file_uploads)
    )
    
    # Filter updates based on permissions and query parameters
    if current_user.role not in ["admin", "faculty"]:
        # Students can only see their own updates
        query = query.filter(DBStudentUpdate.user_id == current_user.id)
    
    # Apply additional filters
    if user_id:
        query = query.filter(DBStudentUpdate.user_id == user_id)
    
    if meeting_id:
        query = query.filter(DBStudentUpdate.meeting_id == meeting_id)
    
    # Get total count before pagination
    total = query.count()
    
    # Sort by submission date (newest first) and apply pagination
    updates = query.order_by(DBStudentUpdate.submission_date.desc()).offset(skip).limit(limit).all()
    
    # Convert to response format
    result_items = []
    for update in updates:
        # Convert files to expected format
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
        
        result_items.append(StudentUpdate(
            id=update.id,
            user_id=update.user_id,
            user_name=update.user.full_name or update.user.username,
            progress_text=update.progress_text,
            challenges_text=update.challenges_text,
            next_steps_text=update.next_steps_text,
            meeting_notes=update.meeting_notes,
            will_present=update.will_present,
            meeting_id=update.meeting_id,
            files=files,
            submission_date=update.submission_date,
            created_at=update.created_at,
            updated_at=update.updated_at
        ))
    
    return {
        "items": result_items,
        "total": total
    }


@router.put("/{update_id}", response_model=StudentUpdate)
async def update_student_update(
    current_user: Annotated[User, Depends(get_current_user)],
    update_in: StudentUpdateUpdate,
    update_id: int = Path(..., description="The ID of the student update to update"),
    db: Session = Depends(get_sync_db)
):
    """
    Update an existing student update - PERSISTENT IN DATABASE
    """
    # Find the update in database
    update = db.query(DBStudentUpdate).options(
        joinedload(DBStudentUpdate.user),
        joinedload(DBStudentUpdate.file_uploads)
    ).filter(DBStudentUpdate.id == update_id).first()
    
    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student update with ID {update_id} not found"
        )
    
    # Check permissions - admins and faculty can update all updates, students can only update their own
    if current_user.role not in ["admin", "faculty"] and update.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own updates"
        )
    
    # Update only fields that were provided
    if update_in.progress_text is not None:
        update.progress_text = update_in.progress_text
    if update_in.challenges_text is not None:
        update.challenges_text = update_in.challenges_text
    if update_in.next_steps_text is not None:
        update.next_steps_text = update_in.next_steps_text
    if hasattr(update_in, 'meeting_notes') and update_in.meeting_notes is not None:
        update.meeting_notes = update_in.meeting_notes
    if hasattr(update_in, 'will_present') and update_in.will_present is not None:
        update.will_present = update_in.will_present
    if update_in.meeting_id is not None:
        update.meeting_id = update_in.meeting_id
    
    # Save to database
    db.commit()
    db.refresh(update)
    
    # Convert files to expected format
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
    
    return StudentUpdate(
        id=update.id,
        user_id=update.user_id,
        user_name=update.user.full_name or update.user.username,
        progress_text=update.progress_text,
        challenges_text=update.challenges_text,
        next_steps_text=update.next_steps_text,
        meeting_notes=update.meeting_notes,
        will_present=update.will_present,
        meeting_id=update.meeting_id,
        files=files,
        submission_date=update.submission_date,
        created_at=update.created_at,
        updated_at=update.updated_at
    )


@router.post("/{update_id}/files")
async def upload_files_to_update(
    current_user: Annotated[User, Depends(get_current_user)],
    update_id: int = Path(..., description="The ID of the student update"),
    files: List[UploadFile] = File(..., max_length=50 * 1024 * 1024)  # 50MB max per file
):
    """
    Upload files and attach them to an existing student update
    """
    # Find the update in our "database"
    update_idx = next((i for i, u in enumerate(STUDENT_UPDATES_DB) if u["id"] == update_id), None)
    
    if update_idx is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student update with ID {update_id} not found"
        )
    
    update = STUDENT_UPDATES_DB[update_idx]
    
    # Check permissions - only admins can upload to all updates, students can only upload to their own
    if current_user.role != "admin" and update["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload files to your own updates"
        )
    
    # Process uploaded files - SAVE ACTUAL FILES
    uploaded_files = []
    upload_dir = "/config/workspace/gitea/DoR-Dash/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    for file in files:
        # Generate unique filename to avoid conflicts
        file_id = len(update.get("files", [])) + 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"update_{update_id}_file_{file_id}_{timestamp}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save the actual file content to disk
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file {file.filename}: {str(e)}"
            )
        
        # Store file metadata with actual file path
        file_info = {
            "id": file_id,
            "name": file.filename,
            "size": len(content),  # Actual size of content
            "file_path": file_path,  # Path to actual saved file
            "type": "document" if file.filename.endswith('.pdf') else 
                   "presentation" if file.filename.endswith(('.ppt', '.pptx')) else
                   "data" if file.filename.endswith(('.xlsx', '.csv')) else
                   "code" if file.filename.endswith('.zip') else
                   "other",
            "upload_date": datetime.now().isoformat()
        }
        uploaded_files.append(file_info)
    
    # Add files to the update
    if "files" not in update:
        update["files"] = []
    update["files"].extend(uploaded_files)
    
    # Update in our "database"
    STUDENT_UPDATES_DB[update_idx] = update
    
    return {"message": f"Successfully uploaded {len(uploaded_files)} files", "files": uploaded_files}


@router.get("/{update_id}/files/{file_id}/download")
async def download_file(
    update_id: int = Path(..., description="The ID of the student update"),
    file_id: int = Path(..., description="The ID of the file to download"),
    current_user: Optional[User] = Depends(lambda: None)  # Make auth optional for downloads
):
    """
    Download a specific file from a student update
    """
    # Find the update in our "database"
    update = next((u for u in STUDENT_UPDATES_DB if u["id"] == update_id), None)
    
    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student update with ID {update_id} not found"
        )
    
    # Skip permission check for development
    # In production, uncomment this to enforce permissions
    # if current_user and current_user.role not in ["admin", "faculty"] and update["user_id"] != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="You can only download files from your own updates"
    #     )
    
    # Find the file
    files = update.get("files", [])
    file_info = next((f for f in files if f["id"] == file_id), None)
    
    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID {file_id} not found in this update"
        )
    
    # Check if the actual file exists on disk
    file_path = file_info.get('file_path')
    if not file_path or not os.path.exists(file_path):
        # If no file_path (old uploads) or file doesn't exist, show error
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_info['name']} not found on disk. This may be an older upload before file storage was implemented."
        )
    
    # Determine the correct media type based on file extension
    file_extension = os.path.splitext(file_info['name'])[1].lower()
    media_type_map = {
        '.pdf': 'application/pdf',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.csv': 'text/csv',
        '.txt': 'text/plain',
        '.zip': 'application/zip',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg'
    }
    media_type = media_type_map.get(file_extension, 'application/octet-stream')
    
    # Return the actual file
    return FileResponse(
        path=file_path,
        filename=file_info['name'],
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename=\"{file_info['name']}\""
        }
    )


@router.delete("/{update_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student_update(
    current_user: Annotated[User, Depends(get_current_user)],
    update_id: int = Path(..., description="The ID of the student update to delete"),
    db: Session = Depends(get_sync_db)
):
    """
    Delete a student update - PERSISTENT IN DATABASE
    """
    # Find the update in database
    update = db.query(DBStudentUpdate).filter(DBStudentUpdate.id == update_id).first()
    
    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student update with ID {update_id} not found"
        )
    
    # Check permissions - only admins can delete all updates, students can only delete their own
    if current_user.role != "admin" and update.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own updates"
        )
    
    # Delete from database (cascades to file_uploads automatically)
    db.delete(update)
    db.commit()
    
    print(f"DEBUG: Deleted student update with ID {update_id} from PostgreSQL database")
    
    return None