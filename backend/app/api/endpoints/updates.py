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
    StudentUpdateCreate,
    StudentUpdateUpdate,
    StudentUpdateList
)
from app.schemas.agenda_item import (
    StudentUpdate, 
    AgendaItem as AgendaItemSchema
)
from app.db.models.agenda_item import AgendaItem, AgendaItemType
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
    
    # Handle meeting_id - use default if not provided
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
    else:
        # Use the most recent meeting as default for general student updates  
        default_meeting = db.query(DBMeeting).order_by(DBMeeting.id.desc()).first()
        if default_meeting:
            update_in.meeting_id = default_meeting.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No meetings available. Please create a meeting first or specify a meeting_id."
            )
    
    # Create new database record using unified AgendaItem model
    agenda_item_data = update_in.to_agenda_item_create()
    db_update = AgendaItem(
        meeting_id=agenda_item_data.meeting_id,
        user_id=agenda_item_data.user_id,
        item_type=agenda_item_data.item_type,
        order_index=agenda_item_data.order_index,
        title=agenda_item_data.title,
        content=agenda_item_data.content,
        is_presenting=agenda_item_data.is_presenting
    )
    
    # Save to database
    db.add(db_update)
    db.commit()
    db.refresh(db_update)
    
    print(f"DEBUG: Created student update with ID {db_update.id}, meeting_id: {db_update.meeting_id}")
    print(f"DEBUG: Update saved to PostgreSQL database")
    
    # Convert to response format - use content JSON field
    content = db_update.content or {}
    return StudentUpdate(
        id=db_update.id,
        user_id=db_update.user_id,
        user_name=user.full_name or user.username,
        progress_text=content.get("progress_text", ""),
        challenges_text=content.get("challenges_text", ""),
        next_steps_text=content.get("next_steps_text", ""),
        meeting_notes=content.get("meeting_notes", ""),
        will_present=db_update.is_presenting,
        meeting_id=db_update.meeting_id,
        files=[],  # Will be loaded separately
        submission_date=db_update.created_at,
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
    # Find the update in database using AgendaItem
    agenda_item = db.query(AgendaItem).options(
        joinedload(AgendaItem.user),
        joinedload(AgendaItem.file_uploads)
    ).filter(AgendaItem.id == update_id, AgendaItem.item_type == AgendaItemType.STUDENT_UPDATE.value).first()
    
    if not agenda_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student update with ID {update_id} not found"
        )
    
    # Check permissions - admins and faculty can see all updates, students can only see their own
    if current_user.role not in ["admin", "faculty"] and agenda_item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own updates"
        )
    
    # Convert files to expected format
    files = []
    for file_upload in agenda_item.file_uploads:
        files.append({
            "id": file_upload.id,
            "name": file_upload.filename,
            "size": file_upload.file_size or 0,
            "file_path": file_upload.file_path,
            "type": file_upload.file_type or "other",
            "upload_date": file_upload.upload_date.isoformat() if file_upload.upload_date else None
        })
    
    # Create a response-compatible agenda item with user information
    agenda_response = AgendaItemSchema(
        id=agenda_item.id,
        meeting_id=agenda_item.meeting_id,
        user_id=agenda_item.user_id,
        item_type=agenda_item.item_type,
        order_index=agenda_item.order_index,
        title=agenda_item.title,
        content=agenda_item.content,
        is_presenting=agenda_item.is_presenting,
        user_name=agenda_item.user.full_name or agenda_item.user.username,
        files=[],  # Will be populated by schema conversion
        created_at=agenda_item.created_at,
        updated_at=agenda_item.updated_at
    )
    
    # Convert to legacy format for API compatibility
    return StudentUpdate.from_agenda_item(agenda_response)


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
    # Start with base query using AgendaItem
    query = db.query(AgendaItem).options(
        joinedload(AgendaItem.user),
        joinedload(AgendaItem.file_uploads)
    ).filter(AgendaItem.item_type == AgendaItemType.STUDENT_UPDATE.value)
    
    # Filter updates based on permissions and query parameters
    if current_user.role not in ["admin", "faculty"]:
        # Students can only see their own updates
        query = query.filter(AgendaItem.user_id == current_user.id)
    
    # Apply additional filters
    if user_id:
        query = query.filter(AgendaItem.user_id == user_id)
    
    if meeting_id:
        query = query.filter(AgendaItem.meeting_id == meeting_id)
    
    # Get total count before pagination
    total = query.count()
    
    # Sort by creation date (newest first) and apply pagination
    agenda_items = query.order_by(AgendaItem.created_at.desc()).offset(skip).limit(limit).all()
    
    # Convert to response format
    result_items = []
    for agenda_item in agenda_items:
        # Create a response-compatible agenda item with user information
        agenda_response = AgendaItemSchema(
            id=agenda_item.id,
            meeting_id=agenda_item.meeting_id,
            user_id=agenda_item.user_id,
            item_type=agenda_item.item_type,
            order_index=agenda_item.order_index,
            title=agenda_item.title,
            content=agenda_item.content,
            is_presenting=agenda_item.is_presenting,
            user_name=agenda_item.user.full_name or agenda_item.user.username,
            files=[],  # Will be populated by schema conversion
            created_at=agenda_item.created_at,
            updated_at=agenda_item.updated_at
        )
        
        # Convert to legacy format and add to results
        result_items.append(StudentUpdate.from_agenda_item(agenda_response))
    
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
    # Find the update in database using AgendaItem
    agenda_item = db.query(AgendaItem).options(
        joinedload(AgendaItem.user),
        joinedload(AgendaItem.file_uploads)
    ).filter(AgendaItem.id == update_id, AgendaItem.item_type == AgendaItemType.STUDENT_UPDATE.value).first()
    
    if not agenda_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student update with ID {update_id} not found"
        )
    
    # Check permissions - admins and faculty can update all updates, students can only update their own
    if current_user.role not in ["admin", "faculty"] and agenda_item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own updates"
        )
    
    # Update the content field with new values
    content = agenda_item.content.copy()  # Copy existing content
    
    if update_in.progress_text is not None:
        content["progress_text"] = update_in.progress_text
    if update_in.challenges_text is not None:
        content["challenges_text"] = update_in.challenges_text
    if update_in.next_steps_text is not None:
        content["next_steps_text"] = update_in.next_steps_text
    if hasattr(update_in, 'meeting_notes') and update_in.meeting_notes is not None:
        content["meeting_notes"] = update_in.meeting_notes
    
    # Update the agenda item
    agenda_item.content = content
    if hasattr(update_in, 'will_present') and update_in.will_present is not None:
        agenda_item.is_presenting = update_in.will_present
    if update_in.meeting_id is not None:
        agenda_item.meeting_id = update_in.meeting_id
    
    # Save to database
    db.commit()
    db.refresh(agenda_item)
    
    # Create a response-compatible agenda item with user information
    agenda_response = AgendaItemSchema(
        id=agenda_item.id,
        meeting_id=agenda_item.meeting_id,
        user_id=agenda_item.user_id,
        item_type=agenda_item.item_type,
        order_index=agenda_item.order_index,
        title=agenda_item.title,
        content=agenda_item.content,
        is_presenting=agenda_item.is_presenting,
        user_name=agenda_item.user.full_name or agenda_item.user.username,
        files=[],  # Will be populated by schema conversion
        created_at=agenda_item.created_at,
        updated_at=agenda_item.updated_at
    )
    
    # Convert to legacy format for API compatibility
    return StudentUpdate.from_agenda_item(agenda_response)


@router.post("/{update_id}/files")
async def upload_files_to_update(
    current_user: Annotated[User, Depends(get_current_user)],
    update_id: int = Path(..., description="The ID of the student update"),
    files: List[UploadFile] = File(..., max_length=50 * 1024 * 1024),  # 50MB max per file
    db: Session = Depends(get_sync_db)
):
    """
    Upload files and attach them to an existing student update - DATABASE VERSION
    """
    # Find the update in database
    agenda_item = db.query(AgendaItem).filter(
        AgendaItem.id == update_id,
        AgendaItem.item_type == AgendaItemType.STUDENT_UPDATE.value
    ).first()
    
    if not agenda_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student update with ID {update_id} not found"
        )
    
    # Check permissions - only admins can upload to all updates, students can only upload to their own
    if current_user.role != "admin" and agenda_item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload files to your own updates"
        )
    
    # Process uploaded files - SAVE TO DATABASE AND DISK
    uploaded_files = []
    upload_dir = "/app/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    for file in files:
        # Generate unique filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"update_{update_id}_file_{timestamp}{file_extension}"
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
        
        # Create database record for file
        db_file = DBFileUpload(
            user_id=agenda_item.user_id,  # Required field that was missing!
            agenda_item_id=agenda_item.id,
            filename=file.filename,
            filepath=file_path,  # Note: model uses 'filepath' not 'file_path'
            file_size=len(content),
            file_type="document" if file.filename.endswith('.pdf') else 
                      "presentation" if file.filename.endswith(('.ppt', '.pptx')) else
                      "data" if file.filename.endswith(('.xlsx', '.csv')) else
                      "code" if file.filename.endswith('.zip') else
                      "other",
            upload_date=datetime.now()
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        # Store file metadata for response
        file_info = {
            "id": db_file.id,
            "name": file.filename,
            "size": len(content),
            "file_path": file_path,
            "type": db_file.file_type,
            "upload_date": db_file.upload_date.isoformat()
        }
        uploaded_files.append(file_info)
    
    return {"message": f"Successfully uploaded {len(uploaded_files)} files", "files": uploaded_files}


@router.get("/{update_id}/files/{file_id}/download")
async def download_file(
    update_id: int = Path(..., description="The ID of the student update"),
    file_id: int = Path(..., description="The ID of the file to download"),
    db: Session = Depends(get_sync_db)
):
    """
    Download a specific file from a student update - DATABASE VERSION
    """
    # Find the update in database
    agenda_item = db.query(AgendaItem).filter(
        AgendaItem.id == update_id,
        AgendaItem.item_type == AgendaItemType.STUDENT_UPDATE.value
    ).first()
    
    if not agenda_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student update with ID {update_id} not found"
        )
    
    # Find the file in database
    file_upload = db.query(DBFileUpload).filter(
        DBFileUpload.id == file_id,
        DBFileUpload.agenda_item_id == update_id
    ).first()
    
    if not file_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID {file_id} not found in this update"
        )
    
    # Check if the actual file exists on disk
    file_path = file_upload.file_path
    
    # Try multiple possible file locations
    possible_paths = [
        file_path,  # Original path from database
        os.path.basename(file_path),  # Just filename in current directory
        os.path.join("/app/uploads", os.path.basename(file_path)),  # Container upload directory
        os.path.join("/uploads", os.path.basename(file_path)),  # Root upload directory
    ]
    
    actual_file_path = None
    for path in possible_paths:
        if path and os.path.exists(path):
            actual_file_path = path
            break
    
    if not actual_file_path:
        # If no file found, show error with debugging info
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_upload.filename} not found. Tried paths: {possible_paths}"
        )
    
    # Determine the correct media type based on file extension
    file_extension = os.path.splitext(file_upload.filename)[1].lower()
    media_type_map = {
        '.pdf': 'application/pdf',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xls': 'application/vnd.ms-excel',
        '.csv': 'text/csv',
        '.txt': 'text/plain',
        '.md': 'text/markdown',
        '.zip': 'application/zip',
        '.rar': 'application/vnd.rar',
        '.7z': 'application/x-7z-compressed',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.svg': 'image/svg+xml',
        '.m': 'text/x-matlab',  # MATLAB files
        '.py': 'text/x-python',  # Python files
        '.js': 'application/javascript',  # JavaScript files
        '.html': 'text/html',
        '.css': 'text/css',
        '.json': 'application/json',
        '.xml': 'application/xml',
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav'
    }
    media_type = media_type_map.get(file_extension, 'application/octet-stream')
    
    # Return the actual file
    return FileResponse(
        path=actual_file_path,
        filename=file_upload.filename,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename=\"{file_upload.filename}\""
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
    # Find the update in database using AgendaItem
    agenda_item = db.query(AgendaItem).filter(
        AgendaItem.id == update_id, 
        AgendaItem.item_type == AgendaItemType.STUDENT_UPDATE.value
    ).first()
    
    if not agenda_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student update with ID {update_id} not found"
        )
    
    # Check permissions - only admins can delete all updates, students can only delete their own
    if current_user.role != "admin" and agenda_item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own updates"
        )
    
    # Delete from database (cascades to file_uploads automatically)
    db.delete(agenda_item)
    db.commit()
    
    print(f"DEBUG: Deleted student update with ID {update_id} from PostgreSQL database")
    
    return None