from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from app.api.endpoints.auth import User, get_current_user
from app.core.logging import logger
from app.db.models.presentation_assignment import PresentationAssignment, PresentationType
from app.db.models.user import User as DBUser, UserRole
from app.db.models.meeting import Meeting
from app.db.session import get_sync_db

router = APIRouter()

# Pydantic models for request/response
class PresentationAssignmentCreate(BaseModel):
    student_id: int
    meeting_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    presentation_type: PresentationType
    duration_minutes: Optional[int] = Field(None, ge=1, le=300)  # 1-300 minutes
    requirements: Optional[str] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None
    
    # Grillometer settings (1-3 scale)
    grillometer_novelty: Optional[int] = Field(None, ge=1, le=3)
    grillometer_methodology: Optional[int] = Field(None, ge=1, le=3)
    grillometer_delivery: Optional[int] = Field(None, ge=1, le=3)

class PresentationAssignmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    presentation_type: Optional[PresentationType] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=300)
    requirements: Optional[str] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None
    is_completed: Optional[bool] = None
    
    # Grillometer settings
    grillometer_novelty: Optional[int] = Field(None, ge=1, le=3)
    grillometer_methodology: Optional[int] = Field(None, ge=1, le=3)
    grillometer_delivery: Optional[int] = Field(None, ge=1, le=3)

class PresentationAssignmentResponse(BaseModel):
    id: int
    student_id: int
    student_name: str
    assigned_by_id: int
    assigned_by_name: str
    meeting_id: Optional[int]
    meeting_title: Optional[str]
    title: str
    description: Optional[str]
    presentation_type: PresentationType
    duration_minutes: Optional[int]
    requirements: Optional[str]
    due_date: Optional[datetime]
    assigned_date: datetime
    is_completed: bool
    completion_date: Optional[datetime]
    notes: Optional[str]
    
    # Grillometer settings
    grillometer_novelty: Optional[int]
    grillometer_methodology: Optional[int]
    grillometer_delivery: Optional[int]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=PresentationAssignmentResponse)
async def create_presentation_assignment(
    assignment_data: PresentationAssignmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Create a new presentation assignment (faculty/admin only)
    """
    # Check if user has permission to assign presentations
    if current_user.role.upper() not in [UserRole.FACULTY.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only faculty and admin users can assign presentations"
        )
    
    # Verify the student exists and is actually a student
    student = db.query(DBUser).filter(DBUser.id == assignment_data.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    if student.role != UserRole.STUDENT.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only assign presentations to students"
        )
    
    # Verify meeting exists if provided
    meeting = None
    if assignment_data.meeting_id:
        meeting = db.query(Meeting).filter(Meeting.id == assignment_data.meeting_id).first()
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found"
            )
    
    # Create the assignment
    assignment = PresentationAssignment(
        student_id=assignment_data.student_id,
        assigned_by_id=current_user.id,
        meeting_id=assignment_data.meeting_id,
        title=assignment_data.title,
        description=assignment_data.description,
        presentation_type=assignment_data.presentation_type,
        duration_minutes=assignment_data.duration_minutes,
        requirements=assignment_data.requirements,
        due_date=assignment_data.due_date,
        notes=assignment_data.notes,
        grillometer_novelty=assignment_data.grillometer_novelty,
        grillometer_methodology=assignment_data.grillometer_methodology,
        grillometer_delivery=assignment_data.grillometer_delivery
    )
    
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    # Load relationships for response
    assignment_with_relations = db.query(PresentationAssignment).options(
        joinedload(PresentationAssignment.student),
        joinedload(PresentationAssignment.assigned_by),
        joinedload(PresentationAssignment.meeting)
    ).filter(PresentationAssignment.id == assignment.id).first()
    
    return PresentationAssignmentResponse(
        id=assignment_with_relations.id,
        student_id=assignment_with_relations.student_id,
        student_name=assignment_with_relations.student.full_name or assignment_with_relations.student.username,
        assigned_by_id=assignment_with_relations.assigned_by_id,
        assigned_by_name=assignment_with_relations.assigned_by.full_name or assignment_with_relations.assigned_by.username,
        meeting_id=assignment_with_relations.meeting_id,
        meeting_title=assignment_with_relations.meeting.title if assignment_with_relations.meeting else None,
        title=assignment_with_relations.title,
        description=assignment_with_relations.description,
        presentation_type=assignment_with_relations.presentation_type,
        duration_minutes=assignment_with_relations.duration_minutes,
        requirements=assignment_with_relations.requirements,
        due_date=assignment_with_relations.due_date,
        assigned_date=assignment_with_relations.assigned_date,
        is_completed=assignment_with_relations.is_completed,
        completion_date=assignment_with_relations.completion_date,
        notes=assignment_with_relations.notes,
        grillometer_novelty=assignment_with_relations.grillometer_novelty,
        grillometer_methodology=assignment_with_relations.grillometer_methodology,
        grillometer_delivery=assignment_with_relations.grillometer_delivery,
        created_at=assignment_with_relations.created_at,
        updated_at=assignment_with_relations.updated_at
    )

@router.get("/", response_model=List[PresentationAssignmentResponse])
async def get_presentation_assignments(
    student_id: Optional[int] = None,
    assigned_by_id: Optional[int] = None,
    meeting_id: Optional[int] = None,
    is_completed: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get presentation assignments with filtering options
    - Students can only see their own assignments
    - Faculty/admin can see all assignments or filter by parameters
    """
    try:
        query = db.query(PresentationAssignment).options(
            joinedload(PresentationAssignment.student),
            joinedload(PresentationAssignment.assigned_by),
            joinedload(PresentationAssignment.meeting)
        )
        
        # Apply role-based filtering
        if current_user.role.upper() == UserRole.STUDENT.value:
            # Students can only see their own assignments
            query = query.filter(PresentationAssignment.student_id == current_user.id)
        else:
            # Faculty/admin can filter by parameters
            if student_id:
                query = query.filter(PresentationAssignment.student_id == student_id)
            if assigned_by_id:
                query = query.filter(PresentationAssignment.assigned_by_id == assigned_by_id)
        
        # Apply common filters
        if meeting_id:
            query = query.filter(PresentationAssignment.meeting_id == meeting_id)
        if is_completed is not None:
            query = query.filter(PresentationAssignment.is_completed == is_completed)
        
        assignments = query.order_by(PresentationAssignment.due_date.desc().nullslast(), PresentationAssignment.created_at.desc()).all()
        
        return [
            PresentationAssignmentResponse(
                id=assignment.id,
                student_id=assignment.student_id,
                student_name=assignment.student.full_name or assignment.student.username,
                assigned_by_id=assignment.assigned_by_id,
                assigned_by_name=assignment.assigned_by.full_name or assignment.assigned_by.username,
                meeting_id=assignment.meeting_id,
                meeting_title=assignment.meeting.title if assignment.meeting else None,
            title=assignment.title,
            description=assignment.description,
            presentation_type=assignment.presentation_type,
            duration_minutes=assignment.duration_minutes,
            requirements=assignment.requirements,
            due_date=assignment.due_date,
            assigned_date=assignment.assigned_date,
            is_completed=assignment.is_completed,
            completion_date=assignment.completion_date,
            notes=assignment.notes,
            grillometer_novelty=assignment.grillometer_novelty,
            grillometer_methodology=assignment.grillometer_methodology,
            grillometer_delivery=assignment.grillometer_delivery,
            created_at=assignment.created_at,
            updated_at=assignment.updated_at
        )
        for assignment in assignments
    ]
    except Exception as e:
        # If table doesn't exist or there's a relationship issue, return empty list
        logger.error(f"Presentation assignments query error: {e}")
        return []

@router.get("/{assignment_id}", response_model=PresentationAssignmentResponse)
async def get_presentation_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get a specific presentation assignment
    """
    assignment = db.query(PresentationAssignment).options(
        joinedload(PresentationAssignment.student),
        joinedload(PresentationAssignment.assigned_by),
        joinedload(PresentationAssignment.meeting)
    ).filter(PresentationAssignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation assignment not found"
        )
    
    # Check access permissions
    if current_user.role.upper() == UserRole.STUDENT.value and assignment.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own presentation assignments"
        )
    
    return PresentationAssignmentResponse(
        id=assignment.id,
        student_id=assignment.student_id,
        student_name=assignment.student.full_name or assignment.student.username,
        assigned_by_id=assignment.assigned_by_id,
        assigned_by_name=assignment.assigned_by.full_name or assignment.assigned_by.username,
        meeting_id=assignment.meeting_id,
        meeting_title=assignment.meeting.title if assignment.meeting else None,
        title=assignment.title,
        description=assignment.description,
        presentation_type=assignment.presentation_type,
        duration_minutes=assignment.duration_minutes,
        requirements=assignment.requirements,
        due_date=assignment.due_date,
        assigned_date=assignment.assigned_date,
        is_completed=assignment.is_completed,
        completion_date=assignment.completion_date,
        notes=assignment.notes,
        grillometer_novelty=assignment.grillometer_novelty,
        grillometer_methodology=assignment.grillometer_methodology,
        grillometer_delivery=assignment.grillometer_delivery,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at
    )

@router.put("/{assignment_id}", response_model=PresentationAssignmentResponse)
async def update_presentation_assignment(
    assignment_id: int,
    assignment_data: PresentationAssignmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Update a presentation assignment (faculty/admin only, or student can mark as completed)
    """
    assignment = db.query(PresentationAssignment).filter(PresentationAssignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation assignment not found"
        )
    
    # Check permissions
    if current_user.role.upper() == UserRole.STUDENT.value:
        # Students can only mark their own assignments as completed
        if assignment.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own presentation assignments"
            )
        # Students can only update completion status
        if assignment_data.dict(exclude_unset=True).keys() - {"is_completed"}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students can only mark assignments as completed"
            )
    elif current_user.role.upper() not in [UserRole.FACULTY.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only faculty, admin, or the assigned student can update assignments"
        )
    
    # Update fields
    update_data = assignment_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assignment, field, value)
    
    # Set completion date if marking as completed
    if assignment_data.is_completed is True and not assignment.completion_date:
        assignment.completion_date = datetime.utcnow()
    elif assignment_data.is_completed is False:
        assignment.completion_date = None
    
    assignment.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(assignment)
    
    # Load relationships for response
    assignment_with_relations = db.query(PresentationAssignment).options(
        joinedload(PresentationAssignment.student),
        joinedload(PresentationAssignment.assigned_by),
        joinedload(PresentationAssignment.meeting)
    ).filter(PresentationAssignment.id == assignment.id).first()
    
    return PresentationAssignmentResponse(
        id=assignment_with_relations.id,
        student_id=assignment_with_relations.student_id,
        student_name=assignment_with_relations.student.full_name or assignment_with_relations.student.username,
        assigned_by_id=assignment_with_relations.assigned_by_id,
        assigned_by_name=assignment_with_relations.assigned_by.full_name or assignment_with_relations.assigned_by.username,
        meeting_id=assignment_with_relations.meeting_id,
        meeting_title=assignment_with_relations.meeting.title if assignment_with_relations.meeting else None,
        title=assignment_with_relations.title,
        description=assignment_with_relations.description,
        presentation_type=assignment_with_relations.presentation_type,
        duration_minutes=assignment_with_relations.duration_minutes,
        requirements=assignment_with_relations.requirements,
        due_date=assignment_with_relations.due_date,
        assigned_date=assignment_with_relations.assigned_date,
        is_completed=assignment_with_relations.is_completed,
        completion_date=assignment_with_relations.completion_date,
        notes=assignment_with_relations.notes,
        grillometer_novelty=assignment_with_relations.grillometer_novelty,
        grillometer_methodology=assignment_with_relations.grillometer_methodology,
        grillometer_delivery=assignment_with_relations.grillometer_delivery,
        created_at=assignment_with_relations.created_at,
        updated_at=assignment_with_relations.updated_at
    )

@router.delete("/{assignment_id}")
async def delete_presentation_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Delete a presentation assignment (faculty/admin only)
    """
    if current_user.role.upper() not in [UserRole.FACULTY.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only faculty and admin users can delete presentation assignments"
        )
    
    assignment = db.query(PresentationAssignment).filter(PresentationAssignment.id == assignment_id).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation assignment not found"
        )
    
    db.delete(assignment)
    db.commit()
    
    return {"message": "Presentation assignment deleted successfully"}

@router.get("/types/", response_model=List[str])
async def get_presentation_types():
    """
    Get all available presentation types
    """
    return [ptype.value for ptype in PresentationType]