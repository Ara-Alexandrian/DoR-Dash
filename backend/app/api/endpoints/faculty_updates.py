from datetime import datetime
from typing import List, Optional, Annotated
from fastapi import APIRouter, HTTPException, Depends, Path, Query, status, UploadFile, File, Form
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
import os
import tempfile

from app.api.endpoints.auth import User, get_current_user
from app.core.logging import logger
from app.schemas.faculty_update import (
    FacultyUpdateCreate,
    FacultyUpdateUpdate,
    FacultyUpdateList,
    AnnouncementType
)
from app.schemas.agenda_item import (
    FacultyUpdate,
    AgendaItem as AgendaItemSchema
)
from app.db.models.agenda_item import AgendaItem, AgendaItemType
from app.db.models.user import User as DBUser
from app.db.models.meeting import Meeting as DBMeeting
from app.db.models.file_upload import FileUpload as DBFileUpload
from app.db.session import get_sync_db

router = APIRouter()

# DATABASE STORAGE - NO MORE IN-MEMORY LOSS!
# Note: Keep FACULTY_UPDATES_DB for backward compatibility during transition
FACULTY_UPDATES_DB = []
update_id_counter = 1  # Simple ID counter


@router.post("/", response_model=FacultyUpdate, status_code=status.HTTP_201_CREATED)
async def create_faculty_update(
    current_user: Annotated[User, Depends(get_current_user)],
    update_in: FacultyUpdateCreate,
    db: Session = Depends(get_sync_db)
):
    """
    Create a new faculty update - NOW PERSISTENT IN DATABASE!
    """
    # Check if user is a faculty member or admin
    if current_user.role not in ["faculty", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only faculty members and admins can create faculty updates"
        )
    
    # Check if user is submitting for themselves or admin submitting for a faculty
    if current_user.role != "admin" and update_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit updates for yourself"
        )
    
    # Validate that at least one field has content
    if not any([
        update_in.announcements_text, 
        update_in.projects_text, 
        update_in.project_status_text, 
        update_in.faculty_questions
    ]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one update field must have content"
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
        meeting = db.query(DBMeeting).filter(DBMeeting.id == update_in.meeting_id).first()
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found"
            )
    else:
        # Use the most recent meeting as default for general faculty updates
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
    
    
    # Convert to response format - use content JSON field
    content = db_update.content or {}
    
    # Validate announcement_type and default to 'general' if invalid
    announcement_type = content.get("announcement_type", "general")
    valid_types = ["general", "urgent", "deadline", "funding"]
    if announcement_type not in valid_types:
        logger.warning(f"Invalid announcement_type '{announcement_type}' for update {db_update.id}, defaulting to 'general'")
        announcement_type = "general"
    
    return FacultyUpdate(
        id=db_update.id,
        user_id=db_update.user_id,
        user_name=user.full_name or user.username,
        meeting_id=db_update.meeting_id,
        announcements_text=content.get("announcements_text", ""),
        announcement_type=announcement_type,
        projects_text=content.get("projects_text", ""),
        project_status_text=content.get("project_status_text", ""),
        faculty_questions=content.get("faculty_questions", ""),
        is_presenting=db_update.is_presenting,
        files=[],  # Will be loaded separately
        submission_date=db_update.created_at,
        submitted_at=db_update.created_at,  # For frontend compatibility
        created_at=db_update.created_at,
        updated_at=db_update.updated_at
    )


@router.get("/{update_id}", response_model=FacultyUpdate)
async def read_faculty_update(
    current_user: Annotated[User, Depends(get_current_user)],
    update_id: int = Path(..., description="The ID of the faculty update to retrieve"),
    db: Session = Depends(get_sync_db)
):
    """
    Get a specific faculty update by ID - FROM DATABASE
    """
    # Find the update in database
    agenda_item = db.query(AgendaItem).options(
        joinedload(AgendaItem.user),
        joinedload(AgendaItem.file_uploads)
    ).filter(AgendaItem.id == update_id, AgendaItem.item_type == AgendaItemType.FACULTY_UPDATE.value).first()
    
    if not agenda_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Faculty update with ID {update_id} not found"
        )
    
    # Check permissions - faculty can see all faculty updates, students can see all faculty updates
    if current_user.role == "faculty" and agenda_item.user_id != current_user.id:
        logger.info(f"Faculty {current_user.id} accessed update from faculty {agenda_item.user_id}")
    
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
    
    # Use content JSON field
    content = agenda_item.content or {}
    
    # Validate announcement_type and default to 'general' if invalid
    announcement_type = content.get("announcement_type", "general")
    valid_types = ["general", "urgent", "deadline", "funding"]
    if announcement_type not in valid_types:
        logger.warning(f"Invalid announcement_type '{announcement_type}' for update {agenda_item.id}, defaulting to 'general'")
        announcement_type = "general"
    
    return FacultyUpdate(
        id=agenda_item.id,
        user_id=agenda_item.user_id,
        user_name=agenda_item.user.full_name or agenda_item.user.username,
        meeting_id=agenda_item.meeting_id,
        announcements_text=content.get("announcements_text", ""),
        announcement_type=announcement_type,
        projects_text=content.get("projects_text", ""),
        project_status_text=content.get("project_status_text", ""),
        faculty_questions=content.get("faculty_questions", ""),
        is_presenting=agenda_item.is_presenting,
        files=files,
        submission_date=agenda_item.created_at,
        submitted_at=agenda_item.created_at,
        created_at=agenda_item.created_at,
        updated_at=agenda_item.updated_at
    )


@router.get("/", response_model=FacultyUpdateList)
async def list_faculty_updates(
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, description="Number of updates to skip"),
    limit: int = Query(100, description="Max number of updates to return"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    meeting_id: Optional[int] = Query(None, description="Filter by meeting ID"),
    db: Session = Depends(get_sync_db)
):
    """
    List faculty updates with pagination and optional filtering - FROM DATABASE
    """
    try:
        logger.debug(f"Faculty updates - User: {current_user.id}, Role: {current_user.role}")
        
        # Start with base query using AgendaItem
        query = db.query(AgendaItem).options(
            joinedload(AgendaItem.user),
            joinedload(AgendaItem.file_uploads)
        ).filter(AgendaItem.item_type == AgendaItemType.FACULTY_UPDATE.value)
        
        # Filter updates based on permissions and query parameters
        if current_user.role not in ["admin"]:
            # Faculty can only see their own updates
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
        
        logger.debug(f"Found {total} faculty updates for user {current_user.id}")
        logger.debug(f"User {current_user.id} ({current_user.username}) is requesting faculty updates")
        logger.debug(f"User role: {current_user.role}")
        logger.debug(f"Query filters: user_id={current_user.id if current_user.role not in ['admin'] else 'ALL'}")
        logger.debug(f"Database result count: {total}")
        
        # Convert to response format
        result_items = []
        for agenda_item in agenda_items:
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
            
            # Create a response-compatible faculty update
            content = agenda_item.content
            
            # Validate announcement_type and default to 'general' if invalid
            announcement_type = content.get("announcement_type", "general")
            valid_types = ["general", "urgent", "deadline", "funding"]
            if announcement_type not in valid_types:
                logger.warning(f"Invalid announcement_type '{announcement_type}' for update {agenda_item.id}, defaulting to 'general'")
                announcement_type = "general"
            
            faculty_update = FacultyUpdate(
                id=agenda_item.id,
                user_id=agenda_item.user_id,
                user_name=agenda_item.user.full_name or agenda_item.user.username,
                meeting_id=agenda_item.meeting_id,
                announcements_text=content.get("announcements_text", ""),
                announcement_type=announcement_type,
                projects_text=content.get("projects_text", ""),
                project_status_text=content.get("project_status_text", ""),
                faculty_questions=content.get("faculty_questions", ""),
                is_presenting=agenda_item.is_presenting,
                files=files,
                submission_date=agenda_item.created_at,  # Required field!
                submitted_at=agenda_item.created_at,
                created_at=agenda_item.created_at,
                updated_at=agenda_item.updated_at
            )
            result_items.append(faculty_update)
        
        return FacultyUpdateList(
            items=result_items,
            total=total
        )
        
    except Exception as e:
        logger.error(f"Faculty updates endpoint failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve faculty updates: {str(e)}"
        )


@router.put("/{update_id}", response_model=FacultyUpdate)
async def update_faculty_update(
    current_user: Annotated[User, Depends(get_current_user)],
    update_in: FacultyUpdateUpdate,
    update_id: int = Path(..., description="The ID of the faculty update to update"),
    db: Session = Depends(get_sync_db)
):
    """
    Update an existing faculty update - PERSISTENT IN DATABASE
    """
    # Find the update in database
    agenda_item = db.query(AgendaItem).options(
        joinedload(AgendaItem.user),
        joinedload(AgendaItem.file_uploads)
    ).filter(AgendaItem.id == update_id, AgendaItem.item_type == AgendaItemType.FACULTY_UPDATE.value).first()
    
    if not agenda_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Faculty update with ID {update_id} not found"
        )
    
    # Check permissions - only the faculty owner or admins can update
    if current_user.role != "admin" and agenda_item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own updates"
        )
    
    # Update the content field with new values
    content = agenda_item.content.copy()  # Copy existing content
    
    if update_in.announcements_text is not None:
        content["announcements_text"] = update_in.announcements_text
    if update_in.announcement_type is not None:
        content["announcement_type"] = update_in.announcement_type
    if update_in.projects_text is not None:
        content["projects_text"] = update_in.projects_text
    if update_in.project_status_text is not None:
        content["project_status_text"] = update_in.project_status_text
    if update_in.faculty_questions is not None:
        content["faculty_questions"] = update_in.faculty_questions
    
    # Update the agenda item
    agenda_item.content = content
    if update_in.is_presenting is not None:
        agenda_item.is_presenting = update_in.is_presenting
    if update_in.meeting_id is not None:
        agenda_item.meeting_id = update_in.meeting_id
    
    # Save to database
    db.commit()
    db.refresh(agenda_item)
    
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
    
    # Use content JSON field
    content = agenda_item.content or {}
    
    # Validate announcement_type and default to 'general' if invalid
    announcement_type = content.get("announcement_type", "general")
    valid_types = ["general", "urgent", "deadline", "funding"]
    if announcement_type not in valid_types:
        logger.warning(f"Invalid announcement_type '{announcement_type}' for update {agenda_item.id}, defaulting to 'general'")
        announcement_type = "general"
    
    return FacultyUpdate(
        id=agenda_item.id,
        user_id=agenda_item.user_id,
        user_name=agenda_item.user.full_name or agenda_item.user.username,
        meeting_id=agenda_item.meeting_id,
        announcements_text=content.get("announcements_text", ""),
        announcement_type=announcement_type,
        projects_text=content.get("projects_text", ""),
        project_status_text=content.get("project_status_text", ""),
        faculty_questions=content.get("faculty_questions", ""),
        is_presenting=agenda_item.is_presenting,
        files=files,
        submission_date=agenda_item.created_at,
        submitted_at=agenda_item.created_at,
        created_at=agenda_item.created_at,
        updated_at=agenda_item.updated_at
    )


@router.post("/{update_id}/files")
async def upload_files_to_faculty_update(
    current_user: Annotated[User, Depends(get_current_user)],
    update_id: int = Path(..., description="The ID of the faculty update"),
    files: List[UploadFile] = File(..., max_length=50 * 1024 * 1024),  # 50MB max per file
    db: Session = Depends(get_sync_db)
):
    """
    Upload files and attach them to an existing faculty update - DATABASE VERSION
    """
    # Find the update in database (agenda items)
    agenda_item = db.query(AgendaItem).filter(
        AgendaItem.id == update_id,
        AgendaItem.item_type == AgendaItemType.FACULTY_UPDATE.value
    ).first()
    
    if agenda_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Faculty update with ID {update_id} not found"
        )
    
    # Check permissions - only the faculty owner or admins can upload files
    if current_user.role != "admin" and agenda_item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload files to your own updates"
        )
    
    # Process uploaded files - SAVE ACTUAL FILES
    uploaded_files = []
    upload_dir = "/app/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    for i, file in enumerate(files, 1):
        # Generate unique filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"faculty_{update_id}_file_{i}_{timestamp}{file_extension}"
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
        
        # Save file metadata to database using FileUpload model
        file_upload = DBFileUpload(
            user_id=current_user.id,
            agenda_item_id=agenda_item.id,
            filename=file.filename,
            filepath=file_path,
            file_type=file.content_type or "application/octet-stream",
            file_size=len(content),
            upload_date=datetime.now()
        )
        
        db.add(file_upload)
        
        # Store file info for response
        file_info = {
            "name": file.filename,
            "size": len(content),
            "file_path": file_path,
            "type": file.content_type or "application/octet-stream",
            "upload_date": datetime.now().isoformat()
        }
        uploaded_files.append(file_info)
    
    # Commit all file uploads to database
    db.commit()
    
    return {"message": f"Successfully uploaded {len(uploaded_files)} files", "files": uploaded_files}


@router.get("/{update_id}/files/{file_id}/download")
async def download_faculty_file(
    update_id: int = Path(..., description="The ID of the faculty update"),
    file_id: int = Path(..., description="The ID of the file to download"),
    db: Session = Depends(get_sync_db)
):
    """
    Download a specific file from a faculty update - DATABASE VERSION
    """
    # Find the update in database (agenda items)
    agenda_item = db.query(AgendaItem).filter(
        AgendaItem.id == update_id,
        AgendaItem.item_type == AgendaItemType.FACULTY_UPDATE.value
    ).first()
    
    if not agenda_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Faculty update with ID {update_id} not found"
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
    file_path = file_upload.filepath
    
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
async def delete_faculty_update(
    current_user: Annotated[User, Depends(get_current_user)],
    update_id: int = Path(..., description="The ID of the faculty update to delete"),
    db: Session = Depends(get_sync_db)
):
    """
    Delete a faculty update - PERSISTENT IN DATABASE
    """
    # Find the update in database
    agenda_item = db.query(AgendaItem).filter(
        AgendaItem.id == update_id, 
        AgendaItem.item_type == AgendaItemType.FACULTY_UPDATE.value
    ).first()
    
    if not agenda_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Faculty update with ID {update_id} not found"
        )
    
    # Check permissions - only the faculty owner or admins can delete
    if current_user.role != "admin" and agenda_item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own updates"
        )
    
    # Delete from database (cascades to file_uploads automatically)
    db.delete(agenda_item)
    db.commit()
    
    
    return None