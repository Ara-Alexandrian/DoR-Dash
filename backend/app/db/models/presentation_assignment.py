from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSON
import enum

from app.db.base_class import Base


class PresentationType(enum.Enum):
    CASUAL = "casual"
    MOCK_DEFENSE = "mock_defense"
    PRE_CONFERENCE = "pre_conference"
    THESIS_PROPOSAL = "thesis_proposal"
    DISSERTATION_DEFENSE = "dissertation_defense"
    JOURNAL_CLUB = "journal_club"
    RESEARCH_UPDATE = "research_update"


class PresentationAssignment(Base):
    __tablename__ = "presentation_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Relationships
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    assigned_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    meeting_id: Mapped[int] = mapped_column(Integer, ForeignKey("meeting.id"), nullable=False)
    
    # Assignment details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    presentation_type: Mapped[PresentationType] = mapped_column(Enum(PresentationType), nullable=False)
    
    # Expectations and requirements
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Special requirements or expectations
    
    # Dates
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    assigned_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    
    # Status tracking
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completion_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Grillometer settings - intensity scoring for feedback focus areas
    grillometer_novelty: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-3 scale (ice cube to flame)
    grillometer_methodology: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-3 scale
    grillometer_delivery: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-3 scale
    
    # Additional metadata
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Faculty notes or feedback
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Additional structured data
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationships
    student = relationship("User", foreign_keys=[student_id], back_populates="assigned_presentations")
    assigned_by = relationship("User", foreign_keys=[assigned_by_id], back_populates="presentation_assignments_made")
    meeting = relationship("Meeting", back_populates="presentation_assignments")
    files = relationship("PresentationAssignmentFile", back_populates="presentation_assignment", cascade="all, delete-orphan")