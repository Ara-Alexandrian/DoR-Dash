from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
import enum


class AnnouncementType(str, enum.Enum):
    GENERAL = "general"
    URGENT = "urgent"
    DEADLINE = "deadline"


class FacultyUpdate(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    meeting_id: Mapped[Optional[int]] = mapped_column(ForeignKey("meeting.id", ondelete="SET NULL"), nullable=True)
    
    # Faculty-specific fields
    announcements_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    announcement_type: Mapped[AnnouncementType] = mapped_column(
        Enum(AnnouncementType), default=AnnouncementType.GENERAL, nullable=False
    )
    projects_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    project_status_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    faculty_questions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_presenting: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    submission_date: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="faculty_updates")
    meeting = relationship("Meeting", back_populates="faculty_updates")
    file_uploads = relationship("FileUpload", back_populates="faculty_update", cascade="all, delete-orphan")