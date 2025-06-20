from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM as PostgresEnum
from app.db.base_class import Base
import enum


class UserRole(str, enum.Enum):
    STUDENT = "STUDENT"
    FACULTY = "FACULTY"
    SECRETARY = "SECRETARY"
    ADMIN = "ADMIN"


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # User information
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    preferred_email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Temporarily disabled until migration runs
    
    # Role and status
    role: Mapped[str] = mapped_column(
        String(20), default=UserRole.STUDENT.value, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships (core only to avoid circular imports)
    agenda_items = relationship("AgendaItem", back_populates="user", cascade="all, delete-orphan")
    created_meetings = relationship("Meeting", back_populates="creator", foreign_keys="Meeting.created_by", cascade="all, delete-orphan")
    file_uploads = relationship("FileUpload", back_populates="user", cascade="all, delete-orphan")
    
    # Presentation assignment relationships
    assigned_presentations = relationship("PresentationAssignment", foreign_keys="PresentationAssignment.student_id", back_populates="student", cascade="all, delete-orphan")
    presentation_assignments_made = relationship("PresentationAssignment", foreign_keys="PresentationAssignment.assigned_by_id", back_populates="assigned_by", cascade="all, delete-orphan")
    
    @property
    def role_enum(self) -> UserRole:
        """Get role as enum"""
        return UserRole(self.role)
    
    @role_enum.setter
    def role_enum(self, value: UserRole):
        """Set role from enum"""
        self.role = value.value