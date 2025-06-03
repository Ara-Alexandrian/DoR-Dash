from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


class StudentUpdate(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    meeting_id: Mapped[Optional[int]] = mapped_column(ForeignKey("meeting.id", ondelete="SET NULL"), nullable=True)
    progress_text: Mapped[str] = mapped_column(Text, nullable=False)
    challenges_text: Mapped[str] = mapped_column(Text, nullable=False)
    next_steps_text: Mapped[str] = mapped_column(Text, nullable=False)
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
    user = relationship("User", back_populates="student_updates")
    meeting = relationship("Meeting", back_populates="student_updates")
    file_uploads = relationship("FileUpload", back_populates="student_update", cascade="all, delete-orphan")