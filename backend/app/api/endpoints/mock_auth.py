from datetime import timedelta, datetime
from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import create_access_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Hardcoded users for demonstration
DEMO_USERS = [
    {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Admin User",
        "preferred_email": None,
        "phone": None,
        "role": "admin",
        "is_active": True,
        "password": "password"  # In a real app, this would be a hashed password
    },
    {
        "id": 2,
        "username": "faculty1",
        "email": "faculty1@example.com",
        "full_name": "Faculty Member",
        "preferred_email": "faculty1@personal.com",
        "phone": "555-123-4567",
        "role": "faculty",
        "is_active": True,
        "password": "password"
    },
    {
        "id": 3,
        "username": "student1",
        "email": "student1@example.com",
        "full_name": "Student One",
        "preferred_email": None,
        "phone": None,
        "role": "student",
        "is_active": True,
        "password": "password"
    }
]

# Default admin user
DEMO_ADMIN = DEMO_USERS[0]

# Simple pydantic models for authentication
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

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Find user with matching username
    user = next((user for user in DEMO_USERS if user["username"] == form_data.username), None)
    
    # Check if user exists and password matches
    if not user or form_data.password != user["password"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    # Return token
    return {"access_token": access_token, "token_type": "bearer"}

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
        # Decode JWT token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # Find user by username
    user_data = next((user for user in DEMO_USERS if user["username"] == token_data.username), None)
    
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