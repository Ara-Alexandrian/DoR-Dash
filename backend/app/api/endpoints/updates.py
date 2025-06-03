from datetime import datetime
from typing import List, Optional, Annotated
from fastapi import APIRouter, HTTPException, Depends, Path, Query, status
from pydantic import BaseModel

from app.api.endpoints.mock_auth import User, get_current_user
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
        "progress_text": update_in.progress_text,
        "challenges_text": update_in.challenges_text,
        "next_steps_text": update_in.next_steps_text,
        "submission_date": now,
        "created_at": now,
        "updated_at": now
    }
    
    # Add to "database"
    STUDENT_UPDATES_DB.append(new_update)
    update_id_counter += 1
    
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
    user_id: Optional[int] = Query(None, description="Filter by user ID")
):
    """
    List student updates with pagination and optional filtering by user_id
    """
    # Filter updates based on permissions and query parameters
    if current_user.role != "admin":
        # Students can only see their own updates
        filtered_updates = [u for u in STUDENT_UPDATES_DB if u["user_id"] == current_user.id]
    elif user_id:
        # Admins can filter by user_id
        filtered_updates = [u for u in STUDENT_UPDATES_DB if u["user_id"] == user_id]
    else:
        # Admins can see all updates
        filtered_updates = STUDENT_UPDATES_DB
    
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
    
    # Update the timestamp
    update["updated_at"] = datetime.now()
    
    # Update in our "database"
    STUDENT_UPDATES_DB[update_idx] = update
    
    return update


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