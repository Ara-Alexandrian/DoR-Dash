from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


class FileUpload(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    # New unified reference
    agenda_item_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("agenda_item.id", ondelete="CASCADE"), nullable=True
    )
    
    # Legacy references (to be removed after migration)
    student_update_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("studentupdate.id", ondelete="CASCADE"), nullable=True
    )
    faculty_update_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("facultyupdate.id", ondelete="CASCADE"), nullable=True
    )
    
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    filepath: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(nullable=False)  # Size in bytes
    upload_date: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="file_uploads")
    agenda_item = relationship("AgendaItem", back_populates="file_uploads")
    
    # Legacy relationships (to be removed after migration)
    student_update = relationship("StudentUpdate", back_populates="file_uploads")
    faculty_update = relationship("FacultyUpdate", back_populates="file_uploads")

    @property
    def file_path(self) -> str:
        """Alias for compatibility"""
        return self.filepath