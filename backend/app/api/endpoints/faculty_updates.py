from datetime import datetime
from typing import List, Optional, Annotated
from fastapi import APIRouter, HTTPException, Depends, Path, Query, status
from pydantic import BaseModel

from app.api.endpoints.mock_auth import User, get_current_user
from app.schemas.faculty_update import (
    FacultyUpdate,
    FacultyUpdateCreate,
    FacultyUpdateUpdate,
    FacultyUpdateList,
    AnnouncementType
)

router = APIRouter()

# In-memory storage for faculty updates (mimicking a database)
FACULTY_UPDATES_DB = []
update_id_counter = 1  # Simple ID counter


@router.post("/", response_model=FacultyUpdate, status_code=status.HTTP_201_CREATED)
async def create_faculty_update(
    current_user: Annotated[User, Depends(get_current_user)],
    update_in: FacultyUpdateCreate
):
    """
    Create a new faculty update
    """
    global update_id_counter
    
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
    
    # Create new update with current timestamp
    now = datetime.now()
    new_update = {
        "id": update_id_counter,
        "user_id": update_in.user_id,
        "meeting_id": update_in.meeting_id,
        "announcements_text": update_in.announcements_text,
        "announcement_type": update_in.announcement_type,
        "projects_text": update_in.projects_text,
        "project_status_text": update_in.project_status_text,
        "faculty_questions": update_in.faculty_questions,
        "is_presenting": update_in.is_presenting,
        "submission_date": now,
        "created_at": now,
        "updated_at": now
    }
    
    # Add to "database"
    FACULTY_UPDATES_DB.append(new_update)
    update_id_counter += 1
    
    return new_update


@router.get("/{update_id}", response_model=FacultyUpdate)
async def read_faculty_update(
    current_user: Annotated[User, Depends(get_current_user)],
    update_id: int = Path(..., description="The ID of the faculty update to retrieve")
):
    """
    Get a specific faculty update by ID
    """
    # Find the update in our "database"
    update = next((u for u in FACULTY_UPDATES_DB if u["id"] == update_id), None)
    
    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Faculty update with ID {update_id} not found"
        )
    
    # Check permissions
    # Faculty can see their own updates and all other faculty updates
    # Students can see all faculty updates
    # Admins can see all updates
    if current_user.role == "faculty" and update["user_id"] != current_user.id:
        # Faculty can see other faculty updates but log the access
        print(f"Faculty {current_user.id} accessed update from faculty {update['user_id']}")
    
    return update


@router.get("/", response_model=FacultyUpdateList)
async def list_faculty_updates(
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, description="Number of updates to skip"),
    limit: int = Query(100, description="Max number of updates to return"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    meeting_id: Optional[int] = Query(None, description="Filter by meeting ID")
):
    """
    List faculty updates with pagination and optional filtering
    """
    # Apply filters
    filtered_updates = FACULTY_UPDATES_DB
    
    if user_id:
        filtered_updates = [u for u in filtered_updates if u["user_id"] == user_id]
        
    if meeting_id:
        filtered_updates = [u for u in filtered_updates if u["meeting_id"] == meeting_id]
    
    # Faculty members can see all faculty updates
    # Students can see all faculty updates
    # No additional permissions filtering needed
    
    # Sort by submission date (newest first)
    filtered_updates.sort(key=lambda x: x["submission_date"], reverse=True)
    
    # Apply pagination
    paginated_updates = filtered_updates[skip:skip + limit]
    
    return {
        "items": paginated_updates,
        "total": len(filtered_updates)
    }


@router.put("/{update_id}", response_model=FacultyUpdate)
async def update_faculty_update(
    current_user: Annotated[User, Depends(get_current_user)],
    update_in: FacultyUpdateUpdate,
    update_id: int = Path(..., description="The ID of the faculty update to update")
):
    """
    Update an existing faculty update
    """
    # Find the update in our "database"
    update_idx = next((i for i, u in enumerate(FACULTY_UPDATES_DB) if u["id"] == update_id), None)
    
    if update_idx is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Faculty update with ID {update_id} not found"
        )
    
    update = FACULTY_UPDATES_DB[update_idx]
    
    # Check permissions - only the faculty owner or admins can update
    if current_user.role != "admin" and update["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own updates"
        )
    
    # Update only fields that were provided
    if update_in.announcements_text is not None:
        update["announcements_text"] = update_in.announcements_text
    if update_in.announcement_type is not None:
        update["announcement_type"] = update_in.announcement_type
    if update_in.projects_text is not None:
        update["projects_text"] = update_in.projects_text
    if update_in.project_status_text is not None:
        update["project_status_text"] = update_in.project_status_text
    if update_in.faculty_questions is not None:
        update["faculty_questions"] = update_in.faculty_questions
    if update_in.is_presenting is not None:
        update["is_presenting"] = update_in.is_presenting
    if update_in.meeting_id is not None:
        update["meeting_id"] = update_in.meeting_id
    
    # Update the timestamp
    update["updated_at"] = datetime.now()
    
    # Update in our "database"
    FACULTY_UPDATES_DB[update_idx] = update
    
    return update


@router.delete("/{update_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faculty_update(
    current_user: Annotated[User, Depends(get_current_user)],
    update_id: int = Path(..., description="The ID of the faculty update to delete")
):
    """
    Delete a faculty update
    """
    # Find the update in our "database"
    update_idx = next((i for i, u in enumerate(FACULTY_UPDATES_DB) if u["id"] == update_id), None)
    
    if update_idx is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Faculty update with ID {update_id} not found"
        )
    
    update = FACULTY_UPDATES_DB[update_idx]
    
    # Check permissions - only the faculty owner or admins can delete
    if current_user.role != "admin" and update["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own updates"
        )
    
    # Delete from our "database"
    FACULTY_UPDATES_DB.pop(update_idx)
    
    return None