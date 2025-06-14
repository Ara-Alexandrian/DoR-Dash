from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from datetime import datetime
import enum
from app.db.base_class import Base

class AnnouncementType(enum.Enum):
    GENERAL = "general"
    ACADEMIC = "academic"
    ADMINISTRATIVE = "administrative"
    RESEARCH = "research"
    EVENT = "event"
    URGENT = "urgent"

class FacultyUpdate(Base):
    """
    Legacy faculty update model for backward compatibility
    This is now superseded by AgendaItem model
    """
    __tablename__ = "faculty_updates"
    
    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    meeting_id = Column(Integer, ForeignKey("meeting.id"), nullable=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    announcement_type = Column(Enum(AnnouncementType), default=AnnouncementType.GENERAL)
    is_urgent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # NO RELATIONSHIPS - avoid circular imports