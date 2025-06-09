from datetime import timedelta, datetime
from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import create_access_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# In-memory user database (replace with real database in production)
USERS_DB = []
user_id_counter = 1

# Initialize with minimal admin user only
# Additional users can be created through the admin interface
def initialize_admin():
    global user_id_counter
    if not USERS_DB:
        # Only create the initial admin user
        admin_user = {
            "id": 1,
            "username": "cerebro",
            "email": "cerebro@admin.com",
            "full_name": "Cerebro Admin",
            "preferred_email": None,
            "phone": None,
            "role": "admin",
            "is_active": True,
            "password": "123"
        }
        USERS_DB.append(admin_user)
        user_id_counter = 2

# Initialize admin on module load
initialize_admin()

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    preferred_email: Optional[str] = None
    phone: Optional[str] = None
    role: str
    is_active: bool

def get_user_by_username(username: str):
    """Get user by username from database"""
    return next((user for user in USERS_DB if user["username"] == username), None)

def get_user_by_id(user_id: int):
    """Get user by ID from database"""
    return next((user for user in USERS_DB if user["id"] == user_id), None)

def create_user(user_data: dict):
    """Create a new user in the database"""
    global user_id_counter
    user_data["id"] = user_id_counter
    USERS_DB.append(user_data)
    user_id_counter += 1
    return user_data

def update_user(user_id: int, update_data: dict):
    """Update user in database"""
    user_idx = next((i for i, u in enumerate(USERS_DB) if u["id"] == user_id), None)
    if user_idx is not None:
        for field, value in update_data.items():
            if value is not None:
                USERS_DB[user_idx][field] = value
        return USERS_DB[user_idx]
    return None

def delete_user(user_id: int):
    """Delete user from database"""
    user_idx = next((i for i, u in enumerate(USERS_DB) if u["id"] == user_id), None)
    if user_idx is not None:
        return USERS_DB.pop(user_idx)
    return None

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    User login endpoint
    """
    print(f"DEBUG: Login attempt for username: {form_data.username}")
    print(f"DEBUG: Available users: {[u['username'] for u in USERS_DB]}")
    
    # Find user with matching username
    user = get_user_by_username(form_data.username)
    
    if not user:
        print(f"DEBUG: User {form_data.username} not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User {form_data.username} not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"DEBUG: Found user: {user['username']}")
    print(f"DEBUG: Stored password: '{user['password']}'")
    print(f"DEBUG: Provided password: '{form_data.password}'")
    
    # Check password
    if form_data.password != user["password"]:
        print(f"DEBUG: Password mismatch for user {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"DEBUG: Login successful for {form_data.username}")
    
    # Create simple token (just base64 encoded username for simplicity)
    import base64
    simple_token = base64.b64encode(f"{user['username']}:{user['id']}".encode()).decode()
    
    # Return token
    return {"access_token": simple_token, "token_type": "bearer"}

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Get current user from token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode simple base64 token
        import base64
        decoded = base64.b64decode(token.encode()).decode()
        username, user_id = decoded.split(":")
        
        print(f"DEBUG: Token validation for username: {username}")
        
    except Exception as e:
        print(f"DEBUG: Token validation failed: {e}")
        raise credentials_exception
    
    # Find user by username (get fresh data from database)
    user_data = get_user_by_username(username)
    
    if user_data:
        user = User(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            preferred_email=user_data["preferred_email"],
            phone=user_data["phone"],
            role=user_data["role"],
            is_active=user_data["is_active"]
        )
        return user
    
    raise credentials_exception

@router.get("/profile", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get current user profile
    """
    return current_user