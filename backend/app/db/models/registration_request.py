from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, func, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM as PostgresEnum
from app.db.base_class import Base
from app.db.models.user import UserRole
import enum


class RegistrationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RegistrationRequest(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # User information from registration
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    preferred_email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    role: Mapped[str] = mapped_column(
        String(20), default=UserRole.STUDENT.value, nullable=False
    )
    
    # Password (will be hashed when user is created)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Request status and tracking
    status: Mapped[str] = mapped_column(
        String(20), default=RegistrationStatus.PENDING.value, nullable=False
    )
    admin_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    requested_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )