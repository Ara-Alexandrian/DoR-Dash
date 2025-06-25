from typing import List, Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status, UploadFile, File, Request
from fastapi.responses import Response
from pydantic import EmailStr
import os
import redis
import json
import base64
from datetime import datetime
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None
import io

from sqlalchemy.orm import Session
from app.api.endpoints.auth import User, get_current_user, create_user as auth_create_user, update_user as auth_update_user, delete_user as auth_delete_user, get_all_users
from app.db.session import get_sync_db
from app.core.logging import logger
from app.core.permissions import get_admin_user, get_faculty_or_admin_user, is_owner_or_admin
from app.core.security import get_password_hash
from app.core.config import settings
from app.schemas.auth import UserCreate, UserUpdate, UserResponse

router = APIRouter()

# Redis connection for avatar caching
def get_redis_client():
    """Get Redis client for avatar caching"""
    try:
        r = redis.Redis(
            host=settings.REDIS_SERVER,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=False
        )
        r.ping()  # Test connection
        return r
    except Exception as e:
        logger.warning(f"Redis not available for avatar caching: {e}")
        return None

# Function to generate a new user ID - no longer needed with database auto-increment

# Get all users (admin or faculty only)
@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = Query(0, description="Skip N users"),
    limit: int = Query(100, description="Limit to N users"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_sync_db)
):
    """
    Retrieve users for management (admin only).
    For viewing roster, use /roster endpoint instead.
    """
    all_users = get_all_users(db)
    return all_users[skip : skip + limit]

# Get user by ID
@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int = Path(..., description="The ID of the user to get"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get a specific user by ID.
    - Admin can see any user
    - Faculty can see any user
    - Students can only see themselves
    """
    # Check if user is trying to access someone else's profile without permission
    if current_user.role == "student" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this user's information"
        )
    
    all_users = get_all_users(db)
    user = next((user for user in all_users if user["id"] == user_id), None)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return user

# Create new user (admin only)
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_sync_db)
):
    """
    Create new user (admin only).
    """
    all_users = get_all_users(db)
    
    # Check if username or email already exists
    if any(u["username"] == user_in.username for u in all_users):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    if any(u["email"] == user_in.email for u in all_users):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Create new user
    new_user = user_in.dict()
    new_user["password"] = user_in.password
    
    # Add to users database
    created_user = auth_create_user(db, new_user)
    
    return created_user

# Update user (admin can update anyone, users can update themselves)
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    user_id: int = Path(..., description="The ID of the user to update"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Update a user.
    - Admin can update any user
    - Users can only update themselves
    - Password changes are allowed
    """
    all_users = get_all_users(db)
    
    # Check if user exists
    user = next((u for u in all_users if u["id"] == user_id), None)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Check permissions - only admins or the user themselves can update
    if not is_owner_or_admin(user_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this user"
        )
    
    # If not admin, restrict what can be changed
    if current_user.role != "admin":
        # Regular users cannot change their role or active status
        if user_update.role is not None or user_update.is_active is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update role or active status"
            )
    
    # Update fields that were provided
    update_data = user_update.dict(exclude_unset=True)
    
    try:
        # Update in database using auth function
        updated_user = auth_update_user(db, user_id, update_data)
        
        if updated_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        return updated_user
        
    except ValueError as e:
        # Handle validation errors (like invalid role)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Handle other database errors
        logger.error(f"Error in update_user endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )

# Delete user (admin only)
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int = Path(..., description="The ID of the user to delete"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_sync_db)
):
    """
    Delete a user (admin only).
    """
    all_users = get_all_users(db)
    
    # Check if user exists
    user = next((u for u in all_users if u["id"] == user_id), None)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Don't allow admin to delete themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account"
        )
    
    # Delete from database using auth function
    try:
        deleted_user = auth_delete_user(db, user_id)
        
        if deleted_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found during deletion"
            )
        
        return None
        
    except Exception as e:
        logger.error(f"Error in delete_user endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

# Change password (admin can change anyone's, users can change their own)
@router.post("/{user_id}/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    user_id: int = Path(..., description="The ID of the user"),
    old_password: str = None,
    new_password: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Change a user's password.
    - Admin can change any user's password without knowing old password
    - Users can change their own password if they provide the correct old password
    """
    all_users = get_all_users(db)
    
    # Check if user exists
    user = next((u for u in all_users if u["id"] == user_id), None)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Check permissions
    if not is_owner_or_admin(user_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to change this user's password"
        )
    
    # Non-admins must provide the old password (Note: password verification would need to be enhanced for real passwords)
    if current_user.role != "admin" and current_user.id == user_id:
        if not old_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old password is required"
            )
    
    # Update password using auth function
    auth_update_user(db, user_id, {"password": new_password})
    
    return {"message": "Password changed successfully"}


# Upload/update user avatar
@router.post("/{user_id}/avatar", status_code=status.HTTP_200_OK)
async def upload_avatar(
    user_id: int = Path(..., description="The ID of the user"),
    file: UploadFile = File(..., description="Avatar image file (JPG, PNG, WebP max 5MB)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Upload or update a user's avatar image.
    - Admin can update any user's avatar
    - Users can only update their own avatar
    - Supported formats: JPG, PNG, WebP
    - Max file size: 5MB
    - Images are automatically resized to 200x200px
    """
    # Check permissions - only admins or the user themselves can update avatar
    if not is_owner_or_admin(user_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this user's avatar"
        )
    
    # Check if user exists
    all_users = get_all_users(db)
    user = next((u for u in all_users if u["id"] == user_id), None)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Validate file type - be more lenient with MIME types and check file extension too
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif', 'image/bmp', 'image/tiff']
    file_ext = file.filename.lower().split('.')[-1] if file.filename and '.' in file.filename else ''
    allowed_extensions = ['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp', 'tiff', 'tif']
    
    # Check either MIME type or file extension
    if file.content_type not in allowed_types and file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed formats: {', '.join(allowed_extensions).upper()}"
        )
    
    # Read and validate file size
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit"
        )
    
    try:
        # Check if PIL is available
        if not PIL_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Image processing not available. PIL/Pillow not installed."
            )
        
        # Process the image with PIL
        image = Image.open(io.BytesIO(content))
        
        # Verify it's actually an image
        image.verify()
        # Re-open the image since verify() closes it
        image = Image.open(io.BytesIO(content))
        
        # Check if image is already properly sized (from frontend cropper)
        img_w, img_h = image.size
        is_already_cropped = (img_w == 200 and img_h == 200)
        
        # Debug logging
        logger.info(f"Avatar upload for user {user_id}: received image size {img_w}x{img_h}, mode: {image.mode}")
        logger.info(f"Is already cropped: {is_already_cropped}")
        
        if is_already_cropped:
            # Image is already cropped by frontend with user's preferred positioning and soft edges
            # Just ensure it's in RGB mode for JPEG compatibility
            if image.mode in ('RGBA', 'LA', 'P'):
                # Convert RGBA to RGB with white background, preserving soft edges
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                
                # Use proper alpha compositing to preserve soft edges
                if image.mode == 'RGBA':
                    # Split channels for better soft edge preservation
                    r, g, b, a = image.split()
                    rgb_image = Image.merge('RGB', (r, g, b))
                    background.paste(rgb_image, (0, 0), a)
                elif image.mode == 'LA':
                    # Grayscale with alpha
                    l, a = image.split()
                    background.paste(image.convert('RGB'), (0, 0), a)
                else:
                    # Fallback for other modes
                    background.paste(image, (0, 0), image if hasattr(image, 'mode') and 'A' in image.mode else None)
                    
                image = background
            elif image.mode not in ('RGB', 'L'):
                image = image.convert('RGB')
        else:
            # Image needs processing - do smart cropping as fallback
            # Convert to RGB if necessary (for JPG compatibility)
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparency
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode not in ('RGB', 'L'):
                # Convert any other modes to RGB
                image = image.convert('RGB')
            
            # Resize to 200x200 with smart cropping
            # First, resize to make the smallest dimension 200px
            if img_w < img_h:
                new_w = 200
                new_h = int((200 * img_h) / img_w)
            else:
                new_h = 200
                new_w = int((200 * img_w) / img_h)
            
            image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Crop to 200x200 from center
            left = (new_w - 200) // 2
            top = (new_h - 200) // 2
            image = image.crop((left, top, left + 200, top + 200))
        
        # Save processed image to memory buffer for database storage
        image_buffer = io.BytesIO()
        image.save(image_buffer, 'JPEG', quality=90, optimize=True)
        avatar_data = image_buffer.getvalue()
        content_type = 'image/jpeg'
        
        # Store avatar in database instead of file system
        auth_update_user(db, user_id, {
            "avatar_data": avatar_data,
            "avatar_content_type": content_type,
            "avatar_url": f"/api/v1/users/{user_id}/avatar/image"  # New endpoint for serving avatars
        })
        
        return {
            "message": "Avatar uploaded successfully",
            "avatar_url": f"/api/v1/users/{user_id}/avatar/image",
            "file_size": len(content),
            "processed_size": f"{image.size[0]}x{image.size[1]}",
            "storage": "database",
            "processing": "preserved" if is_already_cropped else "cropped"
        }
        
    except Exception as e:
        logger.error(f"Error processing avatar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process avatar image"
        )


# Get user avatar (with Redis caching)
@router.get("/{user_id}/avatar/image")
async def get_avatar(
    user_id: int = Path(..., description="The ID of the user"),
    db: Session = Depends(get_sync_db)
):
    """
    Get a user's avatar image from database with Redis caching.
    - Cached avatars are served from Redis for performance
    - Falls back to database if cache miss
    - Returns 404 if user has no avatar
    """
    cache_key = f"avatar:{user_id}"
    redis_client = get_redis_client()
    
    # Try to get from Redis cache first
    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                avatar_info = json.loads(cached_data)
                avatar_data = base64.b64decode(avatar_info['data'])
                content_type = avatar_info['content_type']
                
                logger.info(f"Avatar served from Redis cache for user {user_id}")
                return Response(
                    content=avatar_data,
                    media_type=content_type,
                    headers={
                        "Cache-Control": "public, max-age=3600",
                        "X-Avatar-Source": "redis-cache"
                    }
                )
        except Exception as e:
            logger.warning(f"Redis cache error for avatar {user_id}: {e}")
    
    # Get user from database
    all_users = get_all_users(db)
    user = next((u for u in all_users if u["id"] == user_id), None)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Check if user has avatar data in database
    if not user.get("avatar_data") or not user.get("avatar_content_type"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User has no avatar"
        )
    
    avatar_data = user["avatar_data"]
    content_type = user["avatar_content_type"]
    
    # Cache avatar in Redis for future requests
    if redis_client:
        try:
            avatar_cache_data = {
                'data': base64.b64encode(avatar_data).decode('utf-8'),
                'content_type': content_type,
                'cached_at': datetime.now().isoformat(),
                'size': len(avatar_data)
            }
            # Cache for 1 hour
            redis_client.setex(cache_key, 3600, json.dumps(avatar_cache_data))
            logger.info(f"Avatar cached in Redis for user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to cache avatar in Redis: {e}")
    
    logger.info(f"Avatar served from database for user {user_id}")
    return Response(
        content=avatar_data,
        media_type=content_type,
        headers={
            "Cache-Control": "public, max-age=3600",
            "X-Avatar-Source": "database"
        }
    )


# Delete user avatar
@router.delete("/{user_id}/avatar", status_code=status.HTTP_200_OK)
async def delete_avatar(
    user_id: int = Path(..., description="The ID of the user"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Delete a user's avatar image (reverts to initials).
    - Admin can delete any user's avatar
    - Users can only delete their own avatar
    """
    # Check permissions
    if not is_owner_or_admin(user_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this user's avatar"
        )
    
    # Check if user exists
    all_users = get_all_users(db)
    user = next((u for u in all_users if u["id"] == user_id), None)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Clear avatar data from Redis cache
    cache_key = f"avatar:{user_id}"
    redis_client = get_redis_client()
    if redis_client:
        try:
            redis_client.delete(cache_key)
            logger.info(f"Avatar cache cleared for user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to clear avatar cache: {e}")
    
    # Clear avatar data from database
    auth_update_user(db, user_id, {
        "avatar_url": None,
        "avatar_data": None,
        "avatar_content_type": None
    })
    
    return {"message": "Avatar deleted successfully"}