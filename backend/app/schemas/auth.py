from typing import Optional
from pydantic import BaseModel, RootModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    
class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    is_active: bool = True
    preferred_email: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: str = "student"  # Default to student role

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    preferred_email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    id: int
    role: str
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    preferred_email: Optional[str] = None
    phone: Optional[str] = None
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str
    
class User(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    
class UserList(RootModel):
    root: list[UserResponse]