from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
import enum


class MeetingType(str, enum.Enum):
    GENERAL_UPDATE = "general_update"
    PRESENTATIONS_AND_UPDATES = "presentations_and_updates"
    OTHER = "other"


class Meeting(Base):
    """Meeting model for scheduled appointments"""
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meeting_type: Mapped[MeetingType] = mapped_column(
        Enum(MeetingType), default=MeetingType.GENERAL_UPDATE, nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    
    # Track changes
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_meetings")
    agenda_items = relationship("AgendaItem", back_populates="meeting", cascade="all, delete-orphan", order_by="AgendaItem.order_index")
    
    # Legacy relationships (to be removed after migration)
    student_updates = relationship("StudentUpdate", back_populates="meeting", cascade="all, delete-orphan")
    faculty_updates = relationship("FacultyUpdate", back_populates="meeting", cascade="all, delete-orphan")