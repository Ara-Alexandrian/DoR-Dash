from datetime import datetime
from typing import List, Optional, Annotated
from fastapi import APIRouter, HTTPException, Depends, Path, Query, status, UploadFile, File, Form
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
import os
import tempfile

from app.api.endpoints.auth import User, get_current_user
from app.schemas.student_update import (
    StudentUpdate, 
    StudentUpdateCreate,
    StudentUpdateUpdate,
    StudentUpdateList
)

router = APIRouter()

# In-memory storage for student updates (mimicking a database)
STUDENT_UPDATES_DB = []
update_id_counter = 1  # Simple ID counter


@router.post("/", response_model=StudentUpdate, status_code=status.HTTP_201_CREATED)
async def create_student_update(
    current_user: Annotated[User, Depends(get_current_user)],
    update_in: StudentUpdateCreate
):
    """
    Create a new student update
    """
    global update_id_counter
    
    # Check if user is submitting for themselves or admin submitting for a student
    if current_user.role != "admin" and update_in.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit updates for yourself"
        )
    
    # Create new update with current timestamp
    now = datetime.now()
    new_update = {
        "id": update_id_counter,
        "user_id": update_in.user_id,
        "user_name": current_user.full_name or current_user.username,
        "progress_text": update_in.progress_text,
        "challenges_text": update_in.challenges_text,
        "next_steps_text": update_in.next_steps_text,
        "meeting_notes": getattr(update_in, 'meeting_notes', None),
        "will_present": getattr(update_in, 'will_present', False),
        "meeting_id": update_in.meeting_id,
        "files": [],  # Initialize empty files array
        "submission_date": now,
        "created_at": now,
        "updated_at": now
    }
    
    # Add to "database"
    STUDENT_UPDATES_DB.append(new_update)
    update_id_counter += 1
    
    print(f"DEBUG: Created student update with ID {new_update['id']}, meeting_id: {new_update['meeting_id']}")
    print(f"DEBUG: Total updates in DB: {len(STUDENT_UPDATES_DB)}")
    
    return new_update


@router.get("/{update_id}", response_model=StudentUpdate)
async def read_student_update(
    current_user: Annotated[User, Depends(get_current_user)],
    update_id: int = Path(..., description="The ID of the student update to retrieve")
):
    """
    Get a specific student update by ID
    """
    # Find the update in our "database"
    update = next((u for u in STUDENT_UPDATES_DB if u["id"] == update_id), None)
    
    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student update with ID {update_id} not found"
        )
    
    # Check permissions - only admins can see all updates, students can only see their own
    if current_user.role != "admin" and update["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own updates"
        )
    
    return update


@router.get("/", response_model=StudentUpdateList)
async def list_student_updates(
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, description="Number of updates to skip"),
    limit: int = Query(100, description="Max number of updates to return"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    meeting_id: Optional[int] = Query(None, description="Filter by meeting ID")
):
    """
    List student updates with pagination and optional filtering by user_id
    """
    # Filter updates based on permissions and query parameters
    if current_user.role not in ["admin", "faculty"]:
        # Students can only see their own updates
        filtered_updates = [u for u in STUDENT_UPDATES_DB if u["user_id"] == current_user.id]
    else:
        # Admins and faculty can see all updates
        filtered_updates = STUDENT_UPDATES_DB[:]
    
    # Apply additional filters
    if user_id:
        filtered_updates = [u for u in filtered_updates if u["user_id"] == user_id]
    
    if meeting_id:
        filtered_updates = [u for u in filtered_updates if u.get("meeting_id") == meeting_id]
    
    # Sort by submission date (newest first)
    filtered_updates.sort(key=lambda x: x["submission_date"], reverse=True)
    
    # Apply pagination
    paginated_updates = filtered_updates[skip:skip + limit]
    
    return {
        "items": paginated_updates,
        "total": len(filtered_updates)
    }


@router.put("/{update_id}", response_model=StudentUpdate)
async def update_student_update(
    current_user: Annotated[User, Depends(get_current_user)],
    update_in: StudentUpdateUpdate,
    update_id: int = Path(..., description="The ID of the student update to update")
):
    """
    Update an existing student update
    """
    # Find the update in our "database"
    update_idx = next((i for i, u in enumerate(STUDENT_UPDATES_DB) if u["id"] == update_id), None)
    
    if update_idx is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student update with ID {update_id} not found"
        )
    
    update = STUDENT_UPDATES_DB[update_idx]
    
    # Check permissions - only admins can update all updates, students can only update their own
    if current_user.role != "admin" and update["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own updates"
        )
    
    # Update only fields that were provided
    if update_in.progress_text is not None:
        update["progress_text"] = update_in.progress_text
    if update_in.challenges_text is not None:
        update["challenges_text"] = update_in.challenges_text
    if update_in.next_steps_text is not None:
        update["next_steps_text"] = update_in.next_steps_text
    if hasattr(update_in, 'meeting_notes') and update_in.meeting_notes is not None:
        update["meeting_notes"] = update_in.meeting_notes
    if hasattr(update_in, 'will_present') and update_in.will_present is not None:
        update["will_present"] = update_in.will_present
    if update_in.meeting_id is not None:
        update["meeting_id"] = update_in.meeting_id
    
    # Update the timestamp
    update["updated_at"] = datetime.now()
    
    # Update in our "database"
    STUDENT_UPDATES_DB[update_idx] = update
    
    return update


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
    update_id: int = Path(..., description="The ID of the student update to delete")
):
    """
    Delete a student update
    """
    # Find the update in our "database"
    update_idx = next((i for i, u in enumerate(STUDENT_UPDATES_DB) if u["id"] == update_id), None)
    
    if update_idx is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student update with ID {update_id} not found"
        )
    
    update = STUDENT_UPDATES_DB[update_idx]
    
    # Check permissions - only admins can delete all updates, students can only delete their own
    if current_user.role != "admin" and update["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own updates"
        )
    
    # Delete from our "database"
    STUDENT_UPDATES_DB.pop(update_idx)
    
    return None