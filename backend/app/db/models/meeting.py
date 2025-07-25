from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM as PostgresEnum
from app.db.base_class import Base
import enum


class MeetingType(str, enum.Enum):
    GENERAL_UPDATE = "general_update"
    PRESENTATIONS_AND_UPDATES = "presentations_and_updates"
    OTHER = "other"


class EventType(str, enum.Enum):
    MEETING = "meeting"
    CONFERENCE = "conference"
    HOLIDAY = "holiday"
    BLOCK_TIME = "block_time"
    OTHER_EVENT = "other_event"


class Meeting(Base):
    """Meeting model for scheduled appointments and events"""
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meeting_type: Mapped[str] = mapped_column(
        String(50), default=MeetingType.GENERAL_UPDATE.value, nullable=False
    )
    event_type: Mapped[str] = mapped_column(
        String(50), default=EventType.MEETING.value, nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    
    # Track changes
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    
    # Relationships (core only to avoid circular imports)
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_meetings")
    agenda_items = relationship("AgendaItem", back_populates="meeting", cascade="all, delete-orphan", order_by="AgendaItem.order_index")
    presentation_assignments = relationship("PresentationAssignment", back_populates="meeting", cascade="all, delete-orphan")
    
    @property
    def meeting_type_enum(self) -> MeetingType:
        """Get meeting_type as enum"""
        return MeetingType(self.meeting_type)
    
    @meeting_type_enum.setter
    def meeting_type_enum(self, value: MeetingType):
        """Set meeting_type from enum"""
        self.meeting_type = value.value
    
    @property
    def event_type_enum(self) -> EventType:
        """Get event_type as enum"""
        return EventType(self.event_type)
    
    @event_type_enum.setter
    def event_type_enum(self, value: EventType):
        """Set event_type from enum"""
        self.event_type = value.value