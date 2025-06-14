from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

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
    faculty_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    announcement_type = Column(Enum(AnnouncementType), default=AnnouncementType.GENERAL)
    is_urgent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    faculty = relationship("User", back_populates="faculty_updates")
    meeting = relationship("Meeting", back_populates="faculty_updates")
    files = relationship("FileUpload", back_populates="faculty_update")