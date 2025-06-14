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
    ).filter(AgendaItem.item_type == AgendaItemType.STUDENT_UPDATE)
    
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
