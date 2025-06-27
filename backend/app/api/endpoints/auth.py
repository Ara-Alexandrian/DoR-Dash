from datetime import timedelta, datetime
from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
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
    avatar_url: Optional[str] = None
    role: str
    is_active: bool

def get_user_by_username(db: Session, username: str):
    """Get user by username from database"""
    try:
        logger.debug(f"Querying user by username: {username}")
        user = db.query(UserModel).filter(UserModel.username == username).first()
        logger.debug(f"Query result: {user.username if user else 'None'}")
        return user
    except Exception as e:
        logger.error(f"Error in get_user_by_username: {e}")
        logger.error(f"Error details: {type(e).__name__}: {str(e)}")
        # Try again with a fresh session if the first query fails
        try:
            db.rollback()
            logger.debug(f"Retrying query for username: {username}")
            user = db.query(UserModel).filter(UserModel.username == username).first()
            logger.debug(f"Retry result: {user.username if user else 'None'}")
            return user
        except Exception as e2:
            logger.error(f"Error in get_user_by_username retry: {e2}")
            logger.error(f"Error retry details: {type(e2).__name__}: {str(e2)}")
            return None

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
        
        logger.debug(f"Updating user {user_id} with data: {update_data}")
        
        for field, value in update_data.items():
            if value is not None:
                logger.debug(f"Setting {field} = {value}")
                if field == "password":
                    db_user.hashed_password = get_password_hash(value)
                elif field == "role":
                    # The database enum uses uppercase values, but our Python enum uses lowercase
                    # Convert to uppercase to match database enum
                    role_value = value.upper() if isinstance(value, str) else value
                    logger.debug(f"Setting role to {role_value} (converted from {value})")
                    
                    # Validate role before setting
                    valid_roles = ["STUDENT", "FACULTY", "SECRETARY", "ADMIN"]  # Database enum values
                    if role_value not in valid_roles:
                        logger.error(f"Invalid role '{role_value}'. Valid roles: {valid_roles}")
                        raise ValueError(f"Invalid role '{role_value}'. Valid roles: {valid_roles}")
                    
                    # Set role directly as string - database expects uppercase
                    logger.debug(f"Setting role directly as uppercase string: '{role_value}'")
                    db_user.role = role_value
                    logger.debug(f"Successfully set role to: {db_user.role}")
                    logger.debug(f"Type of role after setting: {type(db_user.role)}")
                elif hasattr(db_user, field):
                    setattr(db_user, field, value)
                else:
                    logger.debug(f"Field {field} not found on user model")
        
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
            "avatar_url": getattr(db_user, 'avatar_url', None),  # Safe access for backward compatibility
            "avatar_data": getattr(db_user, 'avatar_data', None),  # Avatar binary data
            "avatar_content_type": getattr(db_user, 'avatar_content_type', None)  # Avatar MIME type
        }
        
        logger.debug(f"Successfully updated user: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in update_user: {e}")
        logger.error(f"Full exception details: {type(e).__name__}: {str(e)}")
        logger.error(f"Update data was: {update_data}")
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
        
        logger.info(f"Deleting user {user_data['username']} and all associated data...")
        
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
            logger.warning(f"Could not collect file paths: {e}")
            deleted_agenda_count = 0
        
        # 2. Count related records for reporting
        try:
            meetings = fresh_db.query(Meeting).filter(Meeting.created_by == user_id).all()
            deleted_meetings_count = len(meetings)
        except Exception as e:
            logger.warning(f"Could not count meetings: {e}")
            deleted_meetings_count = 0
        
        # 3. Delete legacy records that might not have CASCADE constraints
        try:
            deleted_student_updates = fresh_db.query(StudentUpdate).filter(StudentUpdate.student_id == user_id).delete()
            logger.info(f"Deleted {deleted_student_updates} legacy student updates")
        except Exception as e:
            logger.warning(f"Could not delete student updates: {e}")
            fresh_db.rollback()
            
        try:
            deleted_faculty_updates = fresh_db.query(FacultyUpdate).filter(FacultyUpdate.faculty_id == user_id).delete()
            logger.info(f"Deleted {deleted_faculty_updates} legacy faculty updates")
        except Exception as e:
            logger.warning(f"Could not delete faculty updates: {e}")
            fresh_db.rollback()
            
        try:
            deleted_presentations = fresh_db.query(AssignedPresentation).filter(AssignedPresentation.user_id == user_id).delete()
            logger.info(f"Deleted {deleted_presentations} presentations")
        except Exception as e:
            logger.warning(f"Could not delete presentations: {e}")
            fresh_db.rollback()
        
        # 4. Finally, delete the user (CASCADE will handle related records)
        try:
            fresh_db.delete(db_user)
            fresh_db.commit()
            logger.info(f"Successfully deleted user {user_data['username']} from database")
        except Exception as e:
            logger.error(f"Error deleting user from database: {e}")
            fresh_db.rollback()
            raise e
        
        # 5. Delete physical files after successful database transaction
        for file_path, filename in file_paths_to_delete:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Deleted file: {filename}")
                except Exception as e:
                    logger.warning(f"Could not delete file {filename}: {e}")
        
        logger.info(f"Successfully completed deletion of user {user_data['username']}:")
        logger.info(f"  - {deleted_agenda_count} agenda items (cascade deleted)")
        logger.info(f"  - {deleted_meetings_count} meetings (set to null created_by)")
        logger.info(f"  - {len(file_paths_to_delete)} physical files removed")
        
        return user_data
        
    except Exception as e:
        logger.error(f"Error in delete_user: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
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
        logger.info("Admin user 'cerebro' created")

@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_sync_db)
):
    """
    User login endpoint
    """
    logger.debug(f"Login attempt for username: {form_data.username}")
    
    # Ensure admin user exists
    initialize_admin(db)
    
    # Get user from database
    user = get_user_by_username(db, form_data.username)
    
    if not user:
        logger.debug(f"User {form_data.username} not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        logger.debug(f"Invalid password for user {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        logger.debug(f"User {form_data.username} is inactive")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.now()
    db.commit()
    
    # Create access token using AuthService for consistency
    from app.services.auth_service import AuthService
    logger.info(f"[AUTH_DEBUG] Creating token using AuthService for user: {user.username}")
    logger.info(f"[AUTH_DEBUG] Token expiry minutes: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
    
    access_token = AuthService.create_access_token(user)
    
    logger.info(f"[AUTH_DEBUG] Generated token: {access_token[:20]}...{access_token[-10:] if len(access_token) > 30 else access_token}")
    logger.info(f"Login successful for user {form_data.username}")
    
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], 
    db: Session = Depends(get_sync_db)
) -> User:
    """
    Get current authenticated user from token
    """
    logger.info(f"[AUTH_DEBUG] get_current_user called with token: {token[:20]}..." if token else "[AUTH_DEBUG] get_current_user called with NO token")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        logger.error("[AUTH_DEBUG] No token provided")
        raise credentials_exception
    
    try:
        # Use AuthService to verify token
        from app.services.auth_service import AuthService
        
        logger.info(f"[AUTH_DEBUG] Attempting to verify token with AuthService")
        payload = AuthService.verify_token(token)
        logger.info(f"[AUTH_DEBUG] Token verification result: {payload}")
        
        if payload is None:
            logger.error("[AUTH_DEBUG] Token verification returned None")
            raise credentials_exception
            
        sub_value = payload.get("sub")
        logger.info(f"[AUTH_DEBUG] Extracted 'sub' from token: {sub_value}")
        
        if sub_value is None:
            logger.error("[AUTH_DEBUG] No 'sub' field in token payload")
            raise credentials_exception
        
        # Check if payload has a 'username' field (AuthService format)
        if "username" in payload:
            username = payload["username"]
            logger.info(f"[AUTH_DEBUG] Using username from payload: {username}")
        else:
            # Try to use 'sub' as username (legacy format)
            # If 'sub' is numeric, it's probably a user ID, look up by ID
            try:
                user_id = int(sub_value)
                logger.info(f"[AUTH_DEBUG] 'sub' appears to be user ID: {user_id}")
                user = get_user_by_id(db, user_id)
                if user is None:
                    logger.error(f"[AUTH_DEBUG] User not found for ID: {user_id}")
                    raise credentials_exception
                username = user.username
                logger.info(f"[AUTH_DEBUG] Found user by ID, username: {username}")
            except ValueError:
                # 'sub' is not numeric, treat as username
                username = sub_value
                logger.info(f"[AUTH_DEBUG] Using 'sub' as username: {username}")
        
        if username is None:
            logger.error("[AUTH_DEBUG] Could not determine username from token")
            raise credentials_exception
            
    except Exception as jwt_error:
        logger.error(f"[AUTH_DEBUG] JWT verification failed: {jwt_error}")
        logger.error(f"[AUTH_DEBUG] JWT error type: {type(jwt_error).__name__}")
        try:
            # Fallback to simple base64 format for compatibility: username:id
            logger.info("[AUTH_DEBUG] Trying fallback base64 decoding")
            if ":" in token:
                import base64
                decoded = base64.b64decode(token).decode()
                username = decoded.split(":")[0]
                logger.info(f"[AUTH_DEBUG] Fallback decoded username: {username}")
            else:
                logger.error("[AUTH_DEBUG] No ':' in token for fallback decoding")
                raise credentials_exception
        except Exception as fallback_error:
            logger.error(f"[AUTH_DEBUG] Fallback decoding failed: {fallback_error}")
            raise credentials_exception
    except Exception as general_error:
        logger.error(f"[AUTH_DEBUG] General error in token processing: {general_error}")
        raise credentials_exception
    
    logger.info(f"[AUTH_DEBUG] Looking up user by username: {username}")
    user = get_user_by_username(db, username)
    if user is None:
        logger.error(f"[AUTH_DEBUG] User not found for username: {username}")
        raise credentials_exception
    
    logger.info(f"[AUTH_DEBUG] Found user: {user.username}, ID: {user.id}, role: {user.role}, active: {user.is_active}")
    
    if not user.is_active:
        logger.error(f"[AUTH_DEBUG] User {user.username} is inactive")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return User(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        preferred_email=user.preferred_email,
        phone=user.phone,
        avatar_url=user.avatar_url,
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

@router.post("/debug-token")
async def debug_token(
    token_data: dict,
    db: Session = Depends(get_sync_db)
):
    """
    Debug endpoint to analyze token issues
    Accepts: {"token": "your_token_here"}
    """
    token = token_data.get("token")
    if not token:
        return {"error": "No token provided", "status": "missing_token"}
    
    debug_info = {
        "token_received": True,
        "token_length": len(token),
        "token_preview": f"{token[:20]}...{token[-10:] if len(token) > 30 else token}",
        "token_format": "unknown"
    }
    
    # Check if it's a JWT token
    if token.count('.') == 2:
        debug_info["token_format"] = "jwt"
        try:
            from app.services.auth_service import AuthService
            payload = AuthService.verify_token(token)
            if payload:
                debug_info["jwt_valid"] = True
                debug_info["jwt_payload"] = payload
                debug_info["username"] = payload.get("sub")
                
                # Check if user exists
                if debug_info["username"]:
                    user = get_user_by_username(db, debug_info["username"])
                    if user:
                        debug_info["user_exists"] = True
                        debug_info["user_active"] = user.is_active
                        debug_info["user_info"] = {
                            "id": user.id,
                            "username": user.username,
                            "role": user.role,
                            "last_login": str(user.last_login) if user.last_login else None
                        }
                    else:
                        debug_info["user_exists"] = False
                        debug_info["error"] = f"User '{debug_info['username']}' not found in database"
                else:
                    debug_info["error"] = "No 'sub' field in JWT payload"
            else:
                debug_info["jwt_valid"] = False
                debug_info["error"] = "JWT token verification failed"
        except Exception as e:
            debug_info["jwt_valid"] = False
            debug_info["jwt_error"] = str(e)
            debug_info["jwt_error_type"] = type(e).__name__
    elif ":" in token:
        debug_info["token_format"] = "base64_legacy"
        try:
            import base64
            decoded = base64.b64decode(token).decode()
            username = decoded.split(":")[0]
            debug_info["legacy_username"] = username
            debug_info["legacy_valid"] = True
            
            # Check if user exists
            user = get_user_by_username(db, username)
            if user:
                debug_info["user_exists"] = True
                debug_info["user_active"] = user.is_active
            else:
                debug_info["user_exists"] = False
                debug_info["error"] = f"User '{username}' not found in database"
        except Exception as e:
            debug_info["legacy_valid"] = False
            debug_info["legacy_error"] = str(e)
    
    return debug_info

@router.get("/test-auth")
async def test_auth(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_sync_db)
):
    """
    Test authentication flow - returns detailed success/failure info
    """
    try:
        user = get_current_user(token, db)
        return {
            "status": "success",
            "message": "Authentication successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "is_active": user.is_active
            },
            "token_info": {
                "token_length": len(token),
                "token_preview": f"{token[:20]}...{token[-10:] if len(token) > 30 else token}"
            }
        }
    except HTTPException as e:
        return {
            "status": "failed",
            "error": e.detail,
            "status_code": e.status_code,
            "token_info": {
                "token_length": len(token) if token else 0,
                "token_preview": f"{token[:20]}...{token[-10:] if len(token) > 30 else token}" if token else "NO_TOKEN"
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "token_info": {
                "token_length": len(token) if token else 0,
                "token_preview": f"{token[:20]}...{token[-10:] if len(token) > 30 else token}" if token else "NO_TOKEN"
            }
        }

def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current user and verify admin privileges
    """
    if current_user.role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
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
            "avatar_data": getattr(user, 'avatar_data', None),  # Avatar binary data
            "avatar_content_type": getattr(user, 'avatar_content_type', None),  # Avatar MIME type
            "password": "***"  # Don't expose passwords
        }
        for user in users
    ]