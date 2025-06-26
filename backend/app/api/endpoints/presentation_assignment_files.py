from datetime import datetime
from typing import List, Optional
import os
import uuid
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.api.endpoints.auth import User, get_current_user
from app.core.logging import logger
from app.db.models.presentation_assignment import PresentationAssignment
from app.db.models.presentation_assignment_file import PresentationAssignmentFile
from app.db.models.user import User as DBUser, UserRole
from app.db.session import get_sync_db
from app.core.config import settings

router = APIRouter()

# Configuration
UPLOAD_DIR = "uploads/presentation_assignments"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx',
    '.txt', '.rtf', '.jpg', '.jpeg', '.png', '.gif', '.svg',
    '.zip', '.rar', '.7z', '.tar', '.gz', '.csv', '.json',
    '.py', '.r', '.m', '.ipynb', '.md', '.tex'
}

# Pydantic models
class PresentationAssignmentFileResponse(BaseModel):
    id: int
    presentation_assignment_id: int
    uploaded_by_id: int
    uploaded_by_name: str
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    mime_type: Optional[str]
    file_category: Optional[str]
    description: Optional[str]
    upload_date: datetime
    download_url: str
    
    class Config:
        from_attributes = True

class FileUploadRequest(BaseModel):
    file_category: Optional[str] = None
    description: Optional[str] = None

def validate_file(upload_file: UploadFile) -> None:
    """Validate uploaded file"""
    if not upload_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    # Check file extension
    file_ext = os.path.splitext(upload_file.filename.lower())[1]
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size (if available)
    if hasattr(upload_file, 'size') and upload_file.size and upload_file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )

def ensure_upload_dir():
    """Ensure upload directory exists"""
    os.makedirs(UPLOAD_DIR, exist_ok=True)

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename to prevent conflicts"""
    file_ext = os.path.splitext(original_filename)[1]
    unique_name = f"{uuid.uuid4()}{file_ext}"
    return unique_name

@router.post("/{assignment_id}/files/", response_model=PresentationAssignmentFileResponse)
async def upload_file(
    assignment_id: int,
    file: UploadFile = File(...),
    file_category: Optional[str] = None,
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Upload a file for a presentation assignment
    """
    # Validate file
    validate_file(file)
    
    # Get the assignment and check permissions
    assignment = db.query(PresentationAssignment).filter(
        PresentationAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation assignment not found"
        )
    
    # Check if user can upload files for this assignment
    # Only the assigned student/presenter can upload files (not the faculty who created the assignment)
    if assignment.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned presenter can upload files for this presentation"
        )
    
    try:
        # Ensure upload directory exists
        ensure_upload_dir()
        
        # Generate unique filename
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file to disk
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Get file size
        file_size = len(content)
        
        # Create database record
        db_file = PresentationAssignmentFile(
            presentation_assignment_id=assignment_id,
            uploaded_by_id=current_user.id,
            filename=unique_filename,
            original_filename=file.filename,
            filepath=file_path,
            file_type=os.path.splitext(file.filename)[1].lower(),
            file_size=file_size,
            mime_type=file.content_type,
            file_category=file_category,
            description=description
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        # Load the uploader information for response
        db_file_with_user = db.query(PresentationAssignmentFile).options(
            joinedload(PresentationAssignmentFile.uploaded_by)
        ).filter(PresentationAssignmentFile.id == db_file.id).first()
        
        return PresentationAssignmentFileResponse(
            id=db_file_with_user.id,
            presentation_assignment_id=db_file_with_user.presentation_assignment_id,
            uploaded_by_id=db_file_with_user.uploaded_by_id,
            uploaded_by_name=db_file_with_user.uploaded_by.full_name or db_file_with_user.uploaded_by.username,
            filename=db_file_with_user.filename,
            original_filename=db_file_with_user.original_filename,
            file_type=db_file_with_user.file_type,
            file_size=db_file_with_user.file_size,
            mime_type=db_file_with_user.mime_type,
            file_category=db_file_with_user.file_category,
            description=db_file_with_user.description,
            upload_date=db_file_with_user.upload_date,
            download_url=f"/api/v1/presentation-assignments/{assignment_id}/files/{db_file_with_user.id}/download"
        )
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        # Clean up file if database operation failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file"
        )

@router.get("/{assignment_id}/files/", response_model=List[PresentationAssignmentFileResponse])
async def list_files(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    List all files for a presentation assignment
    """
    # Get the assignment and check permissions
    assignment = db.query(PresentationAssignment).filter(
        PresentationAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation assignment not found"
        )
    
    # Check permissions - assigned presenter or faculty/admin can view files
    if current_user.role.upper() == UserRole.STUDENT.value:
        # Students can only see files for their own assignments
        if assignment.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view files for your own assignments"
            )
    elif current_user.role.upper() not in [UserRole.FACULTY.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view files"
        )
    
    # Get files with uploader information
    files = db.query(PresentationAssignmentFile).options(
        joinedload(PresentationAssignmentFile.uploaded_by)
    ).filter(
        PresentationAssignmentFile.presentation_assignment_id == assignment_id
    ).order_by(PresentationAssignmentFile.upload_date.desc()).all()
    
    return [
        PresentationAssignmentFileResponse(
            id=file.id,
            presentation_assignment_id=file.presentation_assignment_id,
            uploaded_by_id=file.uploaded_by_id,
            uploaded_by_name=file.uploaded_by.full_name or file.uploaded_by.username,
            filename=file.filename,
            original_filename=file.original_filename,
            file_type=file.file_type,
            file_size=file.file_size,
            mime_type=file.mime_type,
            file_category=file.file_category,
            description=file.description,
            upload_date=file.upload_date,
            download_url=f"/api/v1/presentation-assignments/{assignment_id}/files/{file.id}/download"
        )
        for file in files
    ]

@router.get("/{assignment_id}/files/{file_id}/download")
async def download_file(
    assignment_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Download a file from a presentation assignment
    """
    # Get the file record
    file_record = db.query(PresentationAssignmentFile).options(
        joinedload(PresentationAssignmentFile.presentation_assignment)
    ).filter(
        and_(
            PresentationAssignmentFile.id == file_id,
            PresentationAssignmentFile.presentation_assignment_id == assignment_id
        )
    ).first()
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check permissions - assigned presenter or faculty/admin can download files
    assignment = file_record.presentation_assignment
    if current_user.role.upper() == UserRole.STUDENT.value:
        # Students can only download files for their own assignments
        if assignment.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only download files for your own assignments"
            )
    elif current_user.role.upper() not in [UserRole.FACULTY.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to download files"
        )
    
    # Check if file exists on disk
    if not os.path.exists(file_record.filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    return FileResponse(
        path=file_record.filepath,
        filename=file_record.original_filename,
        media_type=file_record.mime_type or 'application/octet-stream'
    )

@router.delete("/{assignment_id}/files/{file_id}")
async def delete_file(
    assignment_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Delete a file from a presentation assignment
    """
    # Get the file record
    file_record = db.query(PresentationAssignmentFile).options(
        joinedload(PresentationAssignmentFile.presentation_assignment)
    ).filter(
        and_(
            PresentationAssignmentFile.id == file_id,
            PresentationAssignmentFile.presentation_assignment_id == assignment_id
        )
    ).first()
    
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check permissions - only the assigned presenter can delete files (and only their own uploaded files)
    assignment = file_record.presentation_assignment
    if assignment.student_id != current_user.id or file_record.uploaded_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own uploaded presentation files"
        )
    
    # Delete file from disk
    if os.path.exists(file_record.filepath):
        try:
            os.remove(file_record.filepath)
        except Exception as e:
            logger.error(f"Failed to delete file from disk: {e}")
    
    # Delete from database
    db.delete(file_record)
    db.commit()
    
    return {"message": "File deleted successfully"}