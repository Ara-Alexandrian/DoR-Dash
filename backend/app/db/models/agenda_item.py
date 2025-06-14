from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Text, DateTime, ForeignKey, func, Integer, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, ENUM as PostgresEnum
import enum

from app.db.base_class import Base


class AgendaItemType(str, enum.Enum):
    STUDENT_UPDATE = "student_update"
    FACULTY_UPDATE = "faculty_update"
    ANNOUNCEMENT = "announcement"
    PRESENTATION = "presentation"


class AgendaItem(Base):
    """
    Unified agenda item model - replaces separate StudentUpdate and FacultyUpdate tables
    """
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    meeting_id: Mapped[int] = mapped_column(
        ForeignKey("meeting.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    item_type: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False
    )
    is_presenting: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="agenda_items")
    meeting = relationship("Meeting", back_populates="agenda_items")
    file_uploads = relationship("FileUpload", back_populates="agenda_item", cascade="all, delete-orphan")
    
    @property
    def item_type_enum(self) -> AgendaItemType:
        """Get item_type as enum"""
        return AgendaItemType(self.item_type)
    
    @item_type_enum.setter
    def item_type_enum(self, value: AgendaItemType):
        """Set item_type from enum"""
        self.item_type = value.value

    def __repr__(self):
        return f"<AgendaItem(id={self.id}, type={self.item_type}, user_id={self.user_id}, meeting_id={self.meeting_id})>"

    @property
    def user_name(self) -> str:
        """Get user's display name"""
        if self.user:
            return self.user.full_name or self.user.username
        return "Unknown User"

    # Content accessors for different item types
    @property
    def student_content(self) -> Dict[str, str]:
        """Get student update specific content"""
        if self.item_type != AgendaItemType.STUDENT_UPDATE.value:
            raise ValueError("This agenda item is not a student update")
        return {
            "progress_text": self.content.get("progress_text", ""),
            "challenges_text": self.content.get("challenges_text", ""),
            "next_steps_text": self.content.get("next_steps_text", ""),
            "meeting_notes": self.content.get("meeting_notes", "")
        }

    @property
    def faculty_content(self) -> Dict[str, str]:
        """Get faculty update specific content"""
        if self.item_type != AgendaItemType.FACULTY_UPDATE.value:
            raise ValueError("This agenda item is not a faculty update")
        return {
            "announcements_text": self.content.get("announcements_text", ""),
            "announcement_type": self.content.get("announcement_type", "general"),
            "projects_text": self.content.get("projects_text", ""),
            "project_status_text": self.content.get("project_status_text", ""),
            "faculty_questions": self.content.get("faculty_questions", "")
        }

    def update_student_content(self, **kwargs) -> None:
        """Update student update content"""
        if self.item_type != AgendaItemType.STUDENT_UPDATE.value:
            raise ValueError("This agenda item is not a student update")
        
        valid_fields = {"progress_text", "challenges_text", "next_steps_text", "meeting_notes"}
        for key, value in kwargs.items():
            if key in valid_fields:
                self.content[key] = value

    def update_faculty_content(self, **kwargs) -> None:
        """Update faculty update content"""
        if self.item_type != AgendaItemType.FACULTY_UPDATE.value:
            raise ValueError("This agenda item is not a faculty update")
        
        valid_fields = {"announcements_text", "announcement_type", "projects_text", "project_status_text", "faculty_questions"}
        for key, value in kwargs.items():
            if key in valid_fields:
                self.content[key] = value

    @classmethod
    def create_student_update(
        cls, 
        meeting_id: int, 
        user_id: int, 
        progress_text: str = "",
        challenges_text: str = "",
        next_steps_text: str = "",
        meeting_notes: str = "",
        will_present: bool = False,
        order_index: int = 0
    ) -> "AgendaItem":
        """Factory method to create a student update agenda item"""
        return cls(
            meeting_id=meeting_id,
            user_id=user_id,
            item_type=AgendaItemType.STUDENT_UPDATE.value,
            order_index=order_index,
            content={
                "progress_text": progress_text,
                "challenges_text": challenges_text,
                "next_steps_text": next_steps_text,
                "meeting_notes": meeting_notes
            },
            is_presenting=will_present
        )

    @classmethod
    def create_faculty_update(
        cls,
        meeting_id: int,
        user_id: int,
        announcements_text: str = "",
        announcement_type: str = "general",
        projects_text: str = "",
        project_status_text: str = "",
        faculty_questions: str = "",
        is_presenting: bool = False,
        order_index: int = 0
    ) -> "AgendaItem":
        """Factory method to create a faculty update agenda item"""
        return cls(
            meeting_id=meeting_id,
            user_id=user_id,
            item_type=AgendaItemType.FACULTY_UPDATE.value,
            order_index=order_index,
            content={
                "announcements_text": announcements_text,
                "announcement_type": announcement_type,
                "projects_text": projects_text,
                "project_status_text": project_status_text,
                "faculty_questions": faculty_questions
            },
            is_presenting=is_presenting
        )