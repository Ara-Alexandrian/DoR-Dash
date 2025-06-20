from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_

from app.api.endpoints.auth import User, get_current_user
from app.db.models.meeting import Meeting
from app.db.models.agenda_item import AgendaItem, AgendaItemType
from app.db.models.user import User as DBUser
from app.db.session import get_sync_db

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get dashboard statistics for the current user
    - All users see only their own updates for consistency with the updates page
    - This ensures dashboard counts match what users see when they click "Your Updates"
    """
    # Calculate date 30 days ago
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    # Base query for agenda items
    base_query = db.query(AgendaItem).filter(
        AgendaItem.item_type.in_([AgendaItemType.STUDENT_UPDATE, AgendaItemType.FACULTY_UPDATE])
    )
    
    # Filter to show only user's own updates for consistency with the updates page
    # This ensures the dashboard count matches what users see when they click "Your Updates"
    query = base_query.filter(AgendaItem.user_id == current_user.id)
    
    # Get total updates count
    total_updates = query.count()
    
    # Get recent updates count (last 30 days)
    recent_updates = query.filter(
        AgendaItem.created_at >= thirty_days_ago
    ).count()
    
    # Get upcoming presentations count - always filter by user for consistency
    presentations_query = db.query(AgendaItem).filter(
        AgendaItem.is_presenting == True,
        AgendaItem.item_type == AgendaItemType.STUDENT_UPDATE,
        AgendaItem.user_id == current_user.id
    ).join(Meeting).filter(
        Meeting.start_time >= datetime.now()
    )
    
    upcoming_presentations = presentations_query.count()
    
    # Get completed presentations count - always filter by user for consistency
    completed_presentations_query = db.query(AgendaItem).filter(
        AgendaItem.is_presenting == True,
        AgendaItem.item_type == AgendaItemType.STUDENT_UPDATE,
        AgendaItem.user_id == current_user.id
    ).join(Meeting).filter(
        Meeting.start_time < datetime.now()
    )
    
    completed_presentations = completed_presentations_query.count()
    
    return {
        "totalUpdates": total_updates,
        "recentUpdates": recent_updates,
        "upcomingPresentations": upcoming_presentations,
        "completedPresentations": completed_presentations,
        "userRole": current_user.role
    }

@router.get("/recent-updates")
async def get_recent_updates(
    limit: int = Query(5, description="Number of recent updates to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get recent updates for dashboard display
    - All users see only their own recent updates for consistency with the updates page
    """
    # Base query with user info
    query = db.query(AgendaItem).options(
        joinedload(AgendaItem.user),
        joinedload(AgendaItem.file_uploads)
    ).filter(
        AgendaItem.item_type.in_([AgendaItemType.STUDENT_UPDATE, AgendaItemType.FACULTY_UPDATE])
    )
    
    # Filter to show only user's own updates for consistency with the updates page
    query = query.filter(AgendaItem.user_id == current_user.id)
    
    # Get recent updates, ordered by creation date
    recent_items = query.order_by(AgendaItem.created_at.desc()).limit(limit).all()
    
    # Convert to response format
    updates = []
    for item in recent_items:
        update_data = {
            "id": item.id,
            "user_id": item.user_id,
            "user_name": item.user.full_name or item.user.username if item.user else "Unknown",
            "submission_date": item.created_at.isoformat(),
            "meeting_id": item.meeting_id,
            "is_faculty": item.item_type == AgendaItemType.FACULTY_UPDATE.value,
            "type": item.item_type
        }
        
        # Add type-specific fields from content
        if item.content:
            if item.item_type == AgendaItemType.STUDENT_UPDATE.value:
                update_data.update({
                    "progress_text": item.content.get("progress_text", ""),
                    "challenges_text": item.content.get("challenges_text", ""),
                    "will_present": item.is_presenting
                })
            elif item.item_type == AgendaItemType.FACULTY_UPDATE.value:
                update_data.update({
                    "announcements_text": item.content.get("announcements_text", ""),
                    "announcement_type": item.content.get("announcement_type", "general")
                })
        
        updates.append(update_data)
    
    return {
        "items": updates,
        "total": len(updates)
    }

@router.get("/activity-summary")
async def get_activity_summary(
    days: int = Query(7, description="Number of days to look back"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db)
):
    """
    Get activity summary for the past N days
    Shows update counts per day
    """
    start_date = datetime.now() - timedelta(days=days)
    
    # Base query
    query = db.query(
        func.date(AgendaItem.created_at).label('date'),
        func.count(AgendaItem.id).label('count')
    ).filter(
        AgendaItem.item_type.in_([AgendaItemType.STUDENT_UPDATE, AgendaItemType.FACULTY_UPDATE]),
        AgendaItem.created_at >= start_date
    )
    
    # Filter to show only user's own updates for consistency with the updates page
    query = query.filter(AgendaItem.user_id == current_user.id)
    
    # Group by date
    daily_counts = query.group_by(func.date(AgendaItem.created_at)).all()
    
    # Convert to response format
    activity = []
    for date, count in daily_counts:
        activity.append({
            "date": date.isoformat() if date else None,
            "count": count
        })
    
    return {
        "days": days,
        "activity": activity,
        "total": sum(item["count"] for item in activity)
    }