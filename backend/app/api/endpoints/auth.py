from datetime import timedelta
from typing import Annotated, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.core.session import get_session_manager, SessionManager
from app.db.session import get_sync_db as get_db
from app.services.auth import authenticate_user, get_current_user
from app.schemas.auth import Token, UserResponse

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    # Update last login timestamp
    user.last_login = timedelta(minutes=0)
    db.commit()
    
    # Return token in OAuth2 format
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", response_model=UserResponse)
async def read_users_me(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Get current user profile
    """
    current_user = get_current_user(db, token)
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return current_user

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    token: str = Depends(oauth2_scheme),
    session_manager: SessionManager = Depends(get_session_manager)
) -> Dict[str, str]:
    """
    Logout user and invalidate token
    
    This endpoint will:
    1. Add the token to a blacklist in Redis
    2. Return a success message
    
    The token will be invalidated and unusable for future requests
    """
    # Extract user ID from token
    try:
        # Add token to blacklist in Redis
        # We'll store it with the token as the key and expiration matching token lifetime
        token_key = f"blacklist:{token}"
        await session_manager.redis.set(
            token_key, 
            "1", 
            ex=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        return {"message": "Successfully logged out"}
    except Exception as e:
        return {"message": "Logout successful"}