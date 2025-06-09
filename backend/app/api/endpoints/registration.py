from datetime import datetime
from typing import List, Annotated, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr

from app.api.endpoints.auth import User, get_current_user, create_user, USERS_DB
from app.core.permissions import get_admin_user

router = APIRouter()

# In-memory storage for registration requests
REGISTRATION_REQUESTS = []
request_id_counter = 1

class RegistrationRequest(BaseModel):
    full_name: str
    email: EmailStr
    username: str
    password: str
    phone: Optional[str] = None
    preferred_email: Optional[str] = None

class RegistrationRequestResponse(BaseModel):
    id: int
    full_name: str
    email: str
    username: str
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
async def submit_registration_request(request: RegistrationRequest):
    """
    Submit a registration request (no authentication required)
    This is for students to self-register
    """
    global request_id_counter
    
    # Check if username or email already exists in users or pending requests
    if any(u["username"] == request.username for u in USERS_DB):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    if any(u["email"] == request.email for u in USERS_DB):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
        
    if any(r["username"] == request.username for r in REGISTRATION_REQUESTS if r["status"] == "pending"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration request with this username is already pending"
        )
    
    if any(r["email"] == request.email for r in REGISTRATION_REQUESTS if r["status"] == "pending"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration request with this email is already pending"
        )
    
    # Create registration request
    new_request = {
        "id": request_id_counter,
        "full_name": request.full_name,
        "email": request.email,
        "username": request.username,
        "password": request.password,  # In production, hash this
        "phone": request.phone,
        "preferred_email": request.preferred_email,
        "status": "pending",
        "requested_at": datetime.now(),
        "reviewed_at": None,
        "reviewed_by": None,
        "admin_notes": None
    }
    
    REGISTRATION_REQUESTS.append(new_request)
    request_id_counter += 1
    
    return {
        "message": "Registration request submitted successfully. You will be notified when an administrator reviews your request.",
        "request_id": new_request["id"]
    }

@router.get("/requests", response_model=List[RegistrationRequestResponse])
async def list_registration_requests(
    current_user: User = Depends(get_admin_user),
    status_filter: Optional[str] = None
):
    """
    List all registration requests (admin only)
    """
    requests = REGISTRATION_REQUESTS
    
    if status_filter:
        requests = [r for r in requests if r["status"] == status_filter]
    
    # Sort by requested date (newest first)
    requests.sort(key=lambda x: x["requested_at"], reverse=True)
    
    return requests

@router.put("/requests/{request_id}", response_model=dict)
async def review_registration_request(
    request_id: int,
    review: RegistrationRequestUpdate,
    current_user: User = Depends(get_admin_user)
):
    """
    Approve or reject a registration request (admin only)
    """
    # Find the request
    request_idx = next((i for i, r in enumerate(REGISTRATION_REQUESTS) if r["id"] == request_id), None)
    
    if request_idx is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registration request with ID {request_id} not found"
        )
    
    request_data = REGISTRATION_REQUESTS[request_idx]
    
    if request_data["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request has already been {request_data['status']}"
        )
    
    if review.status not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'approved' or 'rejected'"
        )
    
    # Update request status
    request_data["status"] = review.status
    request_data["reviewed_at"] = datetime.now()
    request_data["reviewed_by"] = current_user.username
    if hasattr(review, 'admin_notes') and review.admin_notes:
        request_data["admin_notes"] = review.admin_notes
    
    REGISTRATION_REQUESTS[request_idx] = request_data
    
    # If approved, create the user account
    if review.status == "approved":
        user_data = {
            "username": request_data["username"],
            "email": request_data["email"],
            "full_name": request_data["full_name"],
            "phone": request_data["phone"],
            "preferred_email": request_data["preferred_email"],
            "password": request_data["password"],
            "role": "student",  # All self-registrations are students
            "is_active": True
        }
        
        # Create the user account
        create_user(user_data)
        
        return {
            "message": f"Registration request approved. User account created for {request_data['username']}.",
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
    current_user: User = Depends(get_admin_user)
):
    """
    Delete a registration request (admin only)
    """
    request_idx = next((i for i, r in enumerate(REGISTRATION_REQUESTS) if r["id"] == request_id), None)
    
    if request_idx is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registration request with ID {request_id} not found"
        )
    
    REGISTRATION_REQUESTS.pop(request_idx)
    return None