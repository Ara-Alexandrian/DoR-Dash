from datetime import datetime
from typing import List, Annotated, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr

from sqlalchemy.orm import Session
from app.api.endpoints.auth import User, get_current_user, create_user, get_all_users
from app.db.session import get_sync_db
from app.core.permissions import get_admin_user
from app.db.models.user import UserRole
from app.db.models.registration_request import RegistrationRequest as RegistrationRequestModel, RegistrationStatus

router = APIRouter()

# Database operations for registration requests

class RegistrationRequest(BaseModel):
    full_name: str
    email: EmailStr
    username: str
    password: str
    role: UserRole = UserRole.STUDENT  # Default to student, but user can select
    phone: Optional[str] = None
    preferred_email: Optional[str] = None

class RegistrationRequestResponse(BaseModel):
    id: int
    full_name: str
    email: str
    username: str
    role: UserRole
    phone: Optional[str] = None
    preferred_email: Optional[str] = None
    status: str  # pending, approved, rejected
    requested_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None

class RegistrationRequestUpdate(BaseModel):
    status: str  # approved, rejected
    admin_notes: Optional[str] = None

@router.post("/request", response_model=dict, status_code=status.HTTP_201_CREATED)
async def submit_registration_request(request: RegistrationRequest, db: Session = Depends(get_sync_db)):
    """
    Submit a registration request (no authentication required)
    This is for users to self-register
    """
    
    # Get all existing users from database
    existing_users = get_all_users(db)
    
    # Check if username or email already exists in users
    if any(u["username"] == request.username for u in existing_users):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    if any(u["email"] == request.email for u in existing_users):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
        
    # Check if username or email already exists in pending requests
    existing_request = db.query(RegistrationRequestModel).filter(
        (RegistrationRequestModel.username == request.username) |
        (RegistrationRequestModel.email == request.email)
    ).filter(RegistrationRequestModel.status == RegistrationStatus.PENDING).first()
    
    if existing_request:
        if existing_request.username == request.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration request with this username is already pending"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration request with this email is already pending"
            )
    
    # Create registration request in database
    try:
        db_request = RegistrationRequestModel(
            full_name=request.full_name,
            email=request.email,
            username=request.username,
            password=request.password,  # Store plain text for now
            role=request.role,
            phone=request.phone,
            preferred_email=request.preferred_email,
            status=RegistrationStatus.PENDING
        )
        
        db.add(db_request)
        db.commit()
        db.refresh(db_request)
        
        return {
            "message": "Registration request submitted successfully. You will be notified when an administrator reviews your request.",
            "request_id": db_request.id
        }
        
    except Exception as e:
        db.rollback()
        # If the table doesn't exist, create it
        if "relation" in str(e) and "does not exist" in str(e):
            # Create the table
            RegistrationRequestModel.__table__.create(db.bind, checkfirst=True)
            db.commit()
            
            # Try again
            db_request = RegistrationRequestModel(
                full_name=request.full_name,
                email=request.email,
                username=request.username,
                password=request.password,
                role=request.role,
                phone=request.phone,
                preferred_email=request.preferred_email,
                status=RegistrationStatus.PENDING
            )
            
            db.add(db_request)
            db.commit()
            db.refresh(db_request)
            
            return {
                "message": "Registration request submitted successfully. You will be notified when an administrator reviews your request.",
                "request_id": db_request.id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create registration request: {str(e)}"
            )

@router.get("/requests", response_model=List[RegistrationRequestResponse])
async def list_registration_requests(
    current_user: User = Depends(get_admin_user),
    status_filter: Optional[str] = None,
    db: Session = Depends(get_sync_db)
):
    """
    List all registration requests (admin only)
    """
    query = db.query(RegistrationRequestModel)
    
    if status_filter:
        query = query.filter(RegistrationRequestModel.status == RegistrationStatus(status_filter))
    
    # Sort by requested date (newest first)
    requests = query.order_by(RegistrationRequestModel.requested_at.desc()).all()
    
    # Convert to response format
    return [
        {
            "id": req.id,
            "full_name": req.full_name,
            "email": req.email,
            "username": req.username,
            "role": req.role,
            "phone": req.phone,
            "preferred_email": req.preferred_email,
            "status": req.status,
            "requested_at": req.requested_at,
            "reviewed_at": req.reviewed_at,
            "reviewed_by": req.reviewed_by
        }
        for req in requests
    ]

@router.put("/requests/{request_id}", response_model=dict)
async def review_registration_request(
    request_id: int,
    review: RegistrationRequestUpdate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_sync_db)
):
    """
    Approve or reject a registration request (admin only)
    """
    # Find the request in database
    db_request = db.query(RegistrationRequestModel).filter(RegistrationRequestModel.id == request_id).first()
    
    if not db_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registration request with ID {request_id} not found"
        )
    
    if db_request.status != RegistrationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request has already been {db_request.status}"
        )
    
    if review.status not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'approved' or 'rejected'"
        )
    
    # Update request status
    db_request.status = RegistrationStatus(review.status)
    db_request.reviewed_at = datetime.now()
    db_request.reviewed_by = current_user.username
    if hasattr(review, 'admin_notes') and review.admin_notes:
        db_request.admin_notes = review.admin_notes
    
    db.commit()
    
    # If approved, create the user account
    if review.status == "approved":
        user_data = {
            "username": db_request.username,
            "email": db_request.email,
            "full_name": db_request.full_name,
            "phone": db_request.phone,
            "preferred_email": db_request.preferred_email,
            "password": db_request.password,
            "role": db_request.role,  # Use the role they requested
            "is_active": True
        }
        
        # Create the user account in database
        create_user(db, user_data)
        
        return {
            "message": f"Registration request approved. User account created for {db_request.username}.",
            "user_created": True
        }
    else:
        return {
            "message": f"Registration request rejected.",
            "user_created": False
        }

@router.delete("/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_registration_request(
    request_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_sync_db)
):
    """
    Delete a registration request (admin only)
    """
    db_request = db.query(RegistrationRequestModel).filter(RegistrationRequestModel.id == request_id).first()
    
    if not db_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registration request with ID {request_id} not found"
        )
    
    db.delete(db_request)
    db.commit()
    return None