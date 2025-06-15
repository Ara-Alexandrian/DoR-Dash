from datetime import datetime
from typing import List, Optional, Annotated
from fastapi import APIRouter, HTTPException, Depends, Path, Query, status, UploadFile, File, Form
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
import os
import tempfile

from app.api.endpoints.auth import User, get_current_user
from app.schemas.agenda_item import (
    AgendaItem, 
    AgendaItemCreate,
    AgendaItemUpdate,
    AgendaItemList,
    StudentUpdateCreate,
    StudentUpdateUpdate,
    StudentUpdate,
    FacultyUpdateCreate,
    FacultyUpdateUpdate,
    FacultyUpdate
)
from app.db.models.agenda_item import AgendaItem as DBAgendaItem, AgendaItemType
from app.db.models.user import User as DBUser
from app.db.models.meeting import Meeting as DBMeeting
from app.db.models.file_upload import FileUpload as DBFileUpload
from app.db.session import get_sync_db

router = APIRouter()


# Helper function to convert DB agenda item to response format
def agenda_item_to_response(db_item: DBAgendaItem) -> AgendaItem:
    """Convert database agenda item to response format"""
    # Convert files to expected format
    files = []
    for file_upload in db_item.file_uploads:
        files.append({
            "id": file_upload.id,
            "filename": file_upload.filename,
            "file_size": file_upload.file_size or 0,
            "file_type": file_upload.file_type or "other",
            "upload_date": file_upload.upload_date
        })
    
    return AgendaItem(
        id=db_item.id,
        meeting_id=db_item.meeting_id,
        user_id=db_item.user_id,
        user_name=db_item.user.full_name or db_item.user.username,
        item_type=db_item.item_type,
        order_index=db_item.order_index,
        title=db_item.title,
        content=db_item.content,
        is_presenting=db_item.is_presenting,
        files=files,
        created_at=db_item.created_at,
        updated_at=db_item.updated_at
    )


@router.post("/", response_model=AgendaItem, status_code=status.HTTP_201_CREATED)
async def create_agenda_item(
    current_user: Annotated[User, Depends(get_current_user)],
    item_in: AgendaItemCreate,
    db: Session = Depends(get_sync_db)
):
    """
    Create a new agenda item
    """
    # Enhanced user validation
    if current_user.role not in ["admin", "faculty"] and item_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: User {current_user.id} cannot create agenda items for user {item_in.user_id}"
        )
    
    # Validate user exists
    user = db.query(DBUser).filter(DBUser.id == item_in.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate meeting exists
    if item_in.meeting_id:
        meeting = db.query(DBMeeting).filter(DBMeeting.id == item_in.meeting_id).first()
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meeting with ID {item_in.meeting_id} not found"
            )
    
    # Auto-generate title if not provided
    title = item_in.title
    if not title:
        type_name = item_in.item_type.value.replace('_', ' ').title()
        title = f"{type_name} - {user.full_name or user.username}"
    
    # Create new database record
    db_item = DBAgendaItem(
        meeting_id=item_in.meeting_id,
        user_id=item_in.user_id,
        item_type=item_in.item_type,
        order_index=item_in.order_index,
        title=title,
        content=item_in.content,
        is_presenting=item_in.is_presenting
    )
    
    # Save to database
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return agenda_item_to_response(db_item)


@router.get("/{item_id}", response_model=AgendaItem)
async def get_agenda_item(
    current_user: Annotated[User, Depends(get_current_user)],
    item_id: int = Path(..., description="The ID of the agenda item to retrieve"),
    db: Session = Depends(get_sync_db)
):
    """
    Get a specific agenda item by ID
    """
    # Find the item in database
    item = db.query(DBAgendaItem).options(
        joinedload(DBAgendaItem.user),
        joinedload(DBAgendaItem.file_uploads)
    ).filter(DBAgendaItem.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agenda item with ID {item_id} not found"
        )
    
    # Check permissions - admins and faculty can see all items, students can only see their own
    if current_user.role not in ["admin", "faculty"] and item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own agenda items"
        )
    
    return agenda_item_to_response(item)


@router.get("/", response_model=AgendaItemList)
async def list_agenda_items(
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(100, description="Max number of items to return"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    meeting_id: Optional[int] = Query(None, description="Filter by meeting ID"),
    item_type: Optional[AgendaItemType] = Query(None, description="Filter by item type"),
    db: Session = Depends(get_sync_db)
):
    """
    List agenda items with pagination and optional filtering
    """
    # Start with base query
    query = db.query(DBAgendaItem).options(
        joinedload(DBAgendaItem.user),
        joinedload(DBAgendaItem.file_uploads)
    )
    
    # Filter items based on permissions and query parameters
    if current_user.role not in ["admin", "faculty"]:
        # Students can only see their own items
        query = query.filter(DBAgendaItem.user_id == current_user.id)
    
    # Apply additional filters
    if user_id:
        query = query.filter(DBAgendaItem.user_id == user_id)
    
    if meeting_id:
        query = query.filter(DBAgendaItem.meeting_id == meeting_id)
    
    if item_type:
        query = query.filter(DBAgendaItem.item_type == item_type)
    
    # Get total count before pagination
    total = query.count()
    
    # Sort by meeting and order_index, then by creation date
    items = query.order_by(
        DBAgendaItem.meeting_id.desc(),
        DBAgendaItem.order_index,
        DBAgendaItem.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    # Convert to response format
    result_items = [agenda_item_to_response(item) for item in items]
    
    return AgendaItemList(items=result_items, total=total)


@router.put("/{item_id}", response_model=AgendaItem)
async def update_agenda_item(
    current_user: Annotated[User, Depends(get_current_user)],
    item_update: AgendaItemUpdate,
    item_id: int = Path(..., description="The ID of the agenda item to update"),
    db: Session = Depends(get_sync_db)
):
    """
    Update an existing agenda item
    """
    # Find the item in database
    item = db.query(DBAgendaItem).options(
        joinedload(DBAgendaItem.user),
        joinedload(DBAgendaItem.file_uploads)
    ).filter(DBAgendaItem.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agenda item with ID {item_id} not found"
        )
    
    # Check permissions - admins and faculty can update all items, students can only update their own
    if current_user.role not in ["admin", "faculty"] and item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own agenda items"
        )
    
    # Update only fields that were provided
    if item_update.meeting_id is not None:
        # Validate meeting exists
        meeting = db.query(DBMeeting).filter(DBMeeting.id == item_update.meeting_id).first()
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meeting with ID {item_update.meeting_id} not found"
            )
        item.meeting_id = item_update.meeting_id
    
    if item_update.order_index is not None:
        item.order_index = item_update.order_index
    
    if item_update.title is not None:
        item.title = item_update.title
    
    if item_update.content is not None:
        # Merge content updates with existing content
        if item.content:
            item.content.update(item_update.content)
        else:
            item.content = item_update.content
    
    if item_update.is_presenting is not None:
        item.is_presenting = item_update.is_presenting
    
    # Save to database
    db.commit()
    db.refresh(item)
    
    return agenda_item_to_response(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agenda_item(
    current_user: Annotated[User, Depends(get_current_user)],
    item_id: int = Path(..., description="The ID of the agenda item to delete"),
    db: Session = Depends(get_sync_db)
):
    """
    Delete an agenda item
    """
    # Find the item in database
    item = db.query(DBAgendaItem).filter(DBAgendaItem.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agenda item with ID {item_id} not found"
        )
    
    # Check permissions - admins and faculty can delete all items, students can only delete their own
    if current_user.role not in ["admin", "faculty"] and item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own agenda items"
        )
    
    # Delete from database (cascades to file_uploads automatically)
    db.delete(item)
    db.commit()
    
    return None


# File upload endpoint for agenda items
@router.post("/{item_id}/files", status_code=status.HTTP_201_CREATED)
async def upload_files_to_agenda_item(
    current_user: Annotated[User, Depends(get_current_user)],
    item_id: int = Path(..., description="The ID of the agenda item"),
    files: List[UploadFile] = File(..., description="Multiple files to upload (max 50MB each)"),
    db: Session = Depends(get_sync_db)
):
    """
    Upload multiple files to an agenda item
    Supports any file type with 50MB max size per file
    """
    # Find the agenda item
    item = db.query(DBAgendaItem).filter(DBAgendaItem.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agenda item with ID {item_id} not found"
        )
    
    # Check permissions
    if current_user.role not in ["admin", "faculty"] and item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload files to your own agenda items"
        )
    
    # Validate file count (reasonable limit)
    if len(files) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 20 files can be uploaded at once"
        )
    
    uploaded_files = []
    failed_files = []
    upload_dir = "/config/workspace/gitea/DoR-Dash/uploads"
    
    # Ensure upload directory exists
    os.makedirs(upload_dir, exist_ok=True)
    
    for file in files:
        try:
            # Validate file size
            content = await file.read()
            if len(content) > 50 * 1024 * 1024:  # 50MB limit
                failed_files.append({
                    "filename": file.filename,
                    "error": "File exceeds 50MB limit"
                })
                continue
            
            # Validate filename
            if not file.filename or file.filename.strip() == "":
                failed_files.append({
                    "filename": "unnamed_file",
                    "error": "Invalid filename"
                })
                continue
            
            # Generate unique filename to avoid conflicts
            timestamp = int(datetime.now().timestamp() * 1000)  # Include milliseconds
            safe_filename = "".join(c for c in file.filename if c.isalnum() or c in "._-").strip()
            if not safe_filename:
                safe_filename = f"file_{timestamp}"
            
            file_extension = os.path.splitext(file.filename)[1] if file.filename else ''
            unique_filename = f"agenda_{item_id}_{timestamp}_{safe_filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Save file to disk
            with open(file_path, "wb") as buffer:
                buffer.write(content)
            
            # Determine MIME type more accurately
            import mimetypes
            mime_type = file.content_type
            if not mime_type or mime_type == "application/octet-stream":
                mime_type, _ = mimetypes.guess_type(file.filename)
                if not mime_type:
                    mime_type = "application/octet-stream"
            
            # Save file metadata to database
            file_upload = DBFileUpload(
                user_id=current_user.id,
                agenda_item_id=item_id,
                filename=file.filename,  # Keep original filename
                filepath=file_path,      # Store full path
                file_type=mime_type,
                file_size=len(content)
            )
            
            db.add(file_upload)
            uploaded_files.append({
                "id": None,  # Will be set after commit
                "filename": file.filename,
                "size": len(content),
                "type": mime_type,
                "upload_date": datetime.now().isoformat()
            })
            
        except Exception as e:
            failed_files.append({
                "filename": file.filename or "unknown",
                "error": f"Upload failed: {str(e)}"
            })
    
    # Commit all successful uploads
    if uploaded_files:
        db.commit()
        # Refresh to get file IDs
        db.refresh(item)
        
        # Update uploaded_files with actual IDs
        recent_files = db.query(DBFileUpload).filter(
            DBFileUpload.agenda_item_id == item_id,
            DBFileUpload.user_id == current_user.id
        ).order_by(DBFileUpload.created_at.desc()).limit(len(uploaded_files)).all()
        
        for i, file_record in enumerate(recent_files):
            if i < len(uploaded_files):
                uploaded_files[-(i+1)]["id"] = file_record.id
    
    response = {
        "uploaded": len(uploaded_files),
        "failed": len(failed_files),
        "files": uploaded_files
    }
    
    if failed_files:
        response["failed_files"] = failed_files
    
    return response


# File download endpoint
@router.get("/{item_id}/files/{file_id}/download")
async def download_file_from_agenda_item(
    item_id: int = Path(..., description="The ID of the agenda item"),
    file_id: int = Path(..., description="The ID of the file to download"),
    db: Session = Depends(get_sync_db)
):
    """
    Download a file from an agenda item
    """
    # Find the agenda item
    item = db.query(DBAgendaItem).filter(DBAgendaItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agenda item with ID {item_id} not found"
        )
    
    # Find the file
    file_upload = db.query(DBFileUpload).filter(
        DBFileUpload.id == file_id,
        DBFileUpload.agenda_item_id == item_id
    ).first()
    
    if not file_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID {file_id} not found for this agenda item"
        )
    
    # Check permissions - anyone authenticated can download files from agenda items they can view
    if current_user.role not in ["admin", "faculty"] and item.user_id != current_user.id:
        # Allow viewing if user has general meeting access
        # This could be enhanced with more granular permissions
        pass
    
    # Check if file exists on disk
    if not os.path.exists(file_upload.filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk. It may have been moved or deleted."
        )
    
    # Return file for download
    return FileResponse(
        path=file_upload.filepath,
        filename=file_upload.filename,
        media_type=file_upload.file_type
    )


# List files for an agenda item
@router.get("/{item_id}/files")
async def list_files_for_agenda_item(
    current_user: Annotated[User, Depends(get_current_user)],
    item_id: int = Path(..., description="The ID of the agenda item"),
    db: Session = Depends(get_sync_db)
):
    """
    List all files attached to an agenda item
    """
    # Find the agenda item
    item = db.query(DBAgendaItem).filter(DBAgendaItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agenda item with ID {item_id} not found"
        )
    
    # Check permissions
    if current_user.role not in ["admin", "faculty"] and item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view files for agenda items you have access to"
        )
    
    # Get all files for this agenda item
    files = db.query(DBFileUpload).filter(
        DBFileUpload.agenda_item_id == item_id
    ).order_by(DBFileUpload.upload_date.desc()).all()
    
    file_list = []
    for file_upload in files:
        # Check if file exists on disk
        file_exists = os.path.exists(file_upload.filepath)
        
        file_list.append({
            "id": file_upload.id,
            "filename": file_upload.filename,
            "file_size": file_upload.file_size,
            "file_type": file_upload.file_type,
            "upload_date": file_upload.upload_date.isoformat(),
            "uploader": file_upload.user.username if file_upload.user else "Unknown",
            "file_exists": file_exists,
            "download_url": f"/api/v1/agenda-items/{item_id}/files/{file_upload.id}/download"
        })
    
    return {
        "agenda_item_id": item_id,
        "total_files": len(file_list),
        "files": file_list
    }


# Delete a file from an agenda item
@router.delete("/{item_id}/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file_from_agenda_item(
    current_user: Annotated[User, Depends(get_current_user)],
    item_id: int = Path(..., description="The ID of the agenda item"),
    file_id: int = Path(..., description="The ID of the file to delete"),
    db: Session = Depends(get_sync_db)
):
    """
    Delete a file from an agenda item
    """
    # Find the agenda item
    item = db.query(DBAgendaItem).filter(DBAgendaItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agenda item with ID {item_id} not found"
        )
    
    # Find the file
    file_upload = db.query(DBFileUpload).filter(
        DBFileUpload.id == file_id,
        DBFileUpload.agenda_item_id == item_id
    ).first()
    
    if not file_upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID {file_id} not found for this agenda item"
        )
    
    # Check permissions - only file uploader, item owner, or admin/faculty can delete
    if (current_user.role not in ["admin", "faculty"] and 
        file_upload.user_id != current_user.id and 
        item.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete files you uploaded or files from your own agenda items"
        )
    
    # Delete file from disk
    try:
        if os.path.exists(file_upload.filepath):
            os.remove(file_upload.filepath)
    except Exception as e:
        # Log error but continue with database deletion
        print(f"Warning: Could not delete file from disk: {e}")
    
    # Delete from database
    db.delete(file_upload)
    db.commit()
    
    return None


# Legacy compatibility endpoints for backward compatibility during transition

@router.post("/student-updates", response_model=StudentUpdate, status_code=status.HTTP_201_CREATED)
async def create_student_update_legacy(
    current_user: Annotated[User, Depends(get_current_user)],
    update_in: StudentUpdateCreate,
    db: Session = Depends(get_sync_db)
):
    """
    Legacy endpoint for creating student updates - converts to unified agenda item
    """
    # Convert to unified agenda item
    agenda_item_data = update_in.to_agenda_item_create()
    
    # Use the main create function
    agenda_item = await create_agenda_item(current_user, agenda_item_data, db)
    
    # Convert back to legacy format
    return StudentUpdate.from_agenda_item(agenda_item)


@router.get("/student-updates/{update_id}", response_model=StudentUpdate)
async def get_student_update_legacy(
    current_user: Annotated[User, Depends(get_current_user)],
    update_id: int = Path(..., description="The ID of the student update"),
    db: Session = Depends(get_sync_db)
):
    """
    Legacy endpoint for getting student updates
    """
    # Get the agenda item
    agenda_item = await get_agenda_item(current_user, update_id, db)
    
    # Ensure it's a student update
    if agenda_item.item_type != AgendaItemType.STUDENT_UPDATE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student update not found"
        )
    
    return StudentUpdate.from_agenda_item(agenda_item)


@router.put("/student-updates/{update_id}", response_model=StudentUpdate)
async def update_student_update_legacy(
    current_user: Annotated[User, Depends(get_current_user)],
    update_in: StudentUpdateUpdate,
    update_id: int = Path(..., description="The ID of the student update"),
    db: Session = Depends(get_sync_db)
):
    """
    Legacy endpoint for updating student updates
    """
    # Convert to unified update format
    agenda_item_update = update_in.to_agenda_item_update()
    
    # Use the main update function
    agenda_item = await update_agenda_item(current_user, agenda_item_update, update_id, db)
    
    return StudentUpdate.from_agenda_item(agenda_item)


@router.post("/faculty-updates", response_model=FacultyUpdate, status_code=status.HTTP_201_CREATED)
async def create_faculty_update_legacy(
    current_user: Annotated[User, Depends(get_current_user)],
    update_in: FacultyUpdateCreate,
    db: Session = Depends(get_sync_db)
):
    """
    Legacy endpoint for creating faculty updates - converts to unified agenda item
    """
    # Convert to unified agenda item
    agenda_item_data = update_in.to_agenda_item_create()
    
    # Use the main create function
    agenda_item = await create_agenda_item(current_user, agenda_item_data, db)
    
    # Convert back to legacy format
    return FacultyUpdate.from_agenda_item(agenda_item)


@router.get("/faculty-updates/{update_id}", response_model=FacultyUpdate)
async def get_faculty_update_legacy(
    current_user: Annotated[User, Depends(get_current_user)],
    update_id: int = Path(..., description="The ID of the faculty update"),
    db: Session = Depends(get_sync_db)
):
    """
    Legacy endpoint for getting faculty updates
    """
    # Get the agenda item
    agenda_item = await get_agenda_item(current_user, update_id, db)
    
    # Ensure it's a faculty update
    if agenda_item.item_type != AgendaItemType.FACULTY_UPDATE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faculty update not found"
        )
    
    return FacultyUpdate.from_agenda_item(agenda_item)


@router.put("/faculty-updates/{update_id}", response_model=FacultyUpdate)
async def update_faculty_update_legacy(
    current_user: Annotated[User, Depends(get_current_user)],
    update_in: FacultyUpdateUpdate,
    update_id: int = Path(..., description="The ID of the faculty update"),
    db: Session = Depends(get_sync_db)
):
    """
    Legacy endpoint for updating faculty updates
    """
    # Convert to unified update format
    agenda_item_update = update_in.to_agenda_item_update()
    
    # Use the main update function
    agenda_item = await update_agenda_item(current_user, agenda_item_update, update_id, db)
    
    return FacultyUpdate.from_agenda_item(agenda_item)