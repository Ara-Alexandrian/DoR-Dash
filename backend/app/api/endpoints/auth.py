from datetime import timedelta, datetime
from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.db.session import get_sync_db
from app.db.models.user import User as UserModel, UserRole

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

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

def get_user_by_username(db: Session, username: str):
    """Get user by username from database"""
    return db.query(UserModel).filter(UserModel.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    """Get user by ID from database"""
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def create_user(db: Session, user_data: dict):
    """Create a new user in the database"""
    # Hash the password
    hashed_password = get_password_hash(user_data["password"])
    
    # Ensure role is uppercase to match database enum
    role_value = user_data.get("role", "student").upper()
    
    db_user = UserModel(
        username=user_data["username"],
        email=user_data["email"],
        full_name=user_data["full_name"],
        preferred_email=user_data.get("preferred_email"),
        phone=user_data.get("phone"),
        role=role_value,  # Pass as string - database uses uppercase enum values
        is_active=user_data.get("is_active", True),
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Convert to dict for compatibility
    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "full_name": db_user.full_name,
        "preferred_email": db_user.preferred_email,
        "phone": db_user.phone,
        "role": db_user.role.lower() if isinstance(db_user.role, str) else db_user.role,
        "is_active": db_user.is_active,
        "password": user_data["password"]  # For compatibility with existing code
    }

def update_user(db: Session, user_id: int, update_data: dict):
    """Update user in database"""
    try:
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return None
        
        print(f"DEBUG: Updating user {user_id} with data: {update_data}")
        
        for field, value in update_data.items():
            if value is not None:
                print(f"DEBUG: Setting {field} = {value}")
                if field == "password":
                    db_user.hashed_password = get_password_hash(value)
                elif field == "role":
                    # The database enum uses uppercase values, but our Python enum uses lowercase
                    # Convert to uppercase to match database enum
                    role_value = value.upper() if isinstance(value, str) else value
                    print(f"DEBUG: Setting role to {role_value} (converted from {value})")
                    
                    # Validate role before setting
                    valid_roles = ["STUDENT", "FACULTY", "SECRETARY", "ADMIN"]  # Database enum values
                    if role_value not in valid_roles:
                        print(f"ERROR: Invalid role '{role_value}'. Valid roles: {valid_roles}")
                        raise ValueError(f"Invalid role '{role_value}'. Valid roles: {valid_roles}")
                    
                    # Set role directly as string - database expects uppercase
                    print(f"DEBUG: Setting role directly as uppercase string: '{role_value}'")
                    db_user.role = role_value
                    print(f"DEBUG: Successfully set role to: {db_user.role}")
                    print(f"DEBUG: Type of role after setting: {type(db_user.role)}")
                elif hasattr(db_user, field):
                    setattr(db_user, field, value)
                else:
                    print(f"DEBUG: Field {field} not found on user model")
        
        db.commit()
        db.refresh(db_user)
        
        result = {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "preferred_email": db_user.preferred_email,
            "phone": db_user.phone,
            "role": db_user.role.lower() if isinstance(db_user.role, str) else db_user.role,
            "is_active": db_user.is_active,
            "avatar_url": getattr(db_user, 'avatar_url', None)  # Safe access for backward compatibility
        }
        
        print(f"DEBUG: Successfully updated user: {result}")
        return result
        
    except Exception as e:
        print(f"ERROR in update_user: {e}")
        print(f"ERROR: Full exception details: {type(e).__name__}: {str(e)}")
        print(f"ERROR: Update data was: {update_data}")
        db.rollback()
        raise e

def delete_user(db: Session, user_id: int):
    """Delete user and all associated data from database"""
    # Create a completely fresh session to avoid any transaction state issues
    from app.db.session import SessionLocal
    
    # Close the existing session if it's in a bad state
    try:
        db.rollback()
    except:
        pass
    
    # Get a fresh session
    fresh_db = SessionLocal()
    
    try:
        
        db_user = fresh_db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            fresh_db.close()
            return None
        
        # Store user data before deletion
        user_data = {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "role": db_user.role
        }
        
        print(f"Deleting user {user_data['username']} and all associated data...")
        
        # Import models for cleanup
        from app.db.models.agenda_item import AgendaItem
        from app.db.models.file_upload import FileUpload
        from app.db.models.meeting import Meeting
        from app.db.models.registration_request import RegistrationRequest
        from app.db.models.student_update import StudentUpdate
        from app.db.models.faculty_update import FacultyUpdate
        from app.db.models.presentation import AssignedPresentation
        import os
        
        # 1. Handle file deletion first (outside transaction)
        file_paths_to_delete = []
        
        try:
            # Collect file paths to delete
            agenda_items = fresh_db.query(AgendaItem).filter(AgendaItem.user_id == user_id).all()
            deleted_agenda_count = len(agenda_items)
            
            for item in agenda_items:
                file_uploads = fresh_db.query(FileUpload).filter(FileUpload.agenda_item_id == item.id).all()
                for file_upload in file_uploads:
                    if file_upload.file_path:
                        file_paths_to_delete.append((file_upload.file_path, file_upload.filename))
            
            # Also get orphaned files
            orphaned_files = fresh_db.query(FileUpload).filter(FileUpload.user_id == user_id).all()
            for file_upload in orphaned_files:
                if file_upload.file_path:
                    file_paths_to_delete.append((file_upload.file_path, file_upload.filename))
                    
        except Exception as e:
            print(f"Warning: Could not collect file paths: {e}")
            deleted_agenda_count = 0
        
        # 2. Count related records for reporting
        try:
            meetings = fresh_db.query(Meeting).filter(Meeting.created_by == user_id).all()
            deleted_meetings_count = len(meetings)
        except Exception as e:
            print(f"Warning: Could not count meetings: {e}")
            deleted_meetings_count = 0
        
        # 3. Delete legacy records that might not have CASCADE constraints
        try:
            deleted_student_updates = fresh_db.query(StudentUpdate).filter(StudentUpdate.student_id == user_id).delete()
            print(f"  Deleted {deleted_student_updates} legacy student updates")
        except Exception as e:
            print(f"  Warning: Could not delete student updates: {e}")
            fresh_db.rollback()
            
        try:
            deleted_faculty_updates = fresh_db.query(FacultyUpdate).filter(FacultyUpdate.faculty_id == user_id).delete()
            print(f"  Deleted {deleted_faculty_updates} legacy faculty updates")
        except Exception as e:
            print(f"  Warning: Could not delete faculty updates: {e}")
            fresh_db.rollback()
            
        try:
            deleted_presentations = fresh_db.query(AssignedPresentation).filter(AssignedPresentation.user_id == user_id).delete()
            print(f"  Deleted {deleted_presentations} presentations")
        except Exception as e:
            print(f"  Warning: Could not delete presentations: {e}")
            fresh_db.rollback()
        
        # 4. Finally, delete the user (CASCADE will handle related records)
        try:
            fresh_db.delete(db_user)
            fresh_db.commit()
            print(f"Successfully deleted user {user_data['username']} from database")
        except Exception as e:
            print(f"Error deleting user from database: {e}")
            fresh_db.rollback()
            raise e
        
        # 5. Delete physical files after successful database transaction
        for file_path, filename in file_paths_to_delete:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"  Deleted file: {filename}")
                except Exception as e:
                    print(f"  Warning: Could not delete file {filename}: {e}")
        
        print(f"Successfully completed deletion of user {user_data['username']}:")
        print(f"  - {deleted_agenda_count} agenda items (cascade deleted)")
        print(f"  - {deleted_meetings_count} meetings (set to null created_by)")
        print(f"  - {len(file_paths_to_delete)} physical files removed")
        
        return user_data
        
    except Exception as e:
        print(f"ERROR in delete_user: {e}")
        print(f"Exception type: {type(e).__name__}")
        try:
            fresh_db.rollback()
            fresh_db.close()
        except:
            pass  # Ignore rollback/close errors
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete user: {str(e)}"
        )
    finally:
        # Always close the fresh session
        try:
            fresh_db.close()
        except:
            pass

def initialize_admin(db: Session):
    """Initialize admin user if it doesn't exist"""
    admin_user = get_user_by_username(db, "cerebro")
    if not admin_user:
        admin_data = {
            "username": "cerebro",
            "email": "cerebro@admin.com",
            "full_name": "Cerebro Admin",
            "role": "admin",
            "is_active": True,
            "password": "123"
        }
        create_user(db, admin_data)
        print("Admin user 'cerebro' created")

@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_sync_db)
):
    """
    User login endpoint
    """
    print(f"DEBUG: Login attempt for username: {form_data.username}")
    
    # Ensure admin user exists
    initialize_admin(db)
    
    # Get user from database
    user = get_user_by_username(db, form_data.username)
    
    if not user:
        print(f"DEBUG: User {form_data.username} not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        print(f"DEBUG: Invalid password for user {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        print(f"DEBUG: User {form_data.username} is inactive")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    print(f"DEBUG: Login successful for user {form_data.username}")
    
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], 
    db: Session = Depends(get_sync_db)
) -> User:
    """
    Get current authenticated user from token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Try JWT token first
        from jose import JWTError, jwt
        from app.core.config import settings
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    except JWTError:
        try:
            # Fallback to simple base64 format for compatibility: username:id
            if ":" in token:
                import base64
                decoded = base64.b64decode(token).decode()
                username = decoded.split(":")[0]
            else:
                raise credentials_exception
        except Exception:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    
    return User(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        preferred_email=user.preferred_email,
        phone=user.phone,
        role=user.role.lower() if isinstance(user.role, str) else user.role,
        is_active=user.is_active
    )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout user (placeholder for token blacklisting in future)
    """
    return {"message": "Successfully logged out"}

@router.get("/profile", response_model=User)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile
    """
    return current_user

# Function to get all users (for compatibility with existing code)
def get_all_users(db: Session):
    """Get all users from database as list of dicts for compatibility"""
    users = db.query(UserModel).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "preferred_email": user.preferred_email,
            "phone": user.phone,
            "role": user.role.lower() if isinstance(user.role, str) else user.role,
            "is_active": user.is_active,
            "avatar_url": getattr(user, 'avatar_url', None),  # Safe access for backward compatibility
            "password": "***"  # Don't expose passwords
        }
        for user in users
    ]