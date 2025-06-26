from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


class PresentationAssignmentFile(Base):
    """
    File attachments for presentation assignments.
    Students can upload files for their assigned presentations.
    """
    __tablename__ = "presentation_assignment_files"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign key relationships
    presentation_assignment_id: Mapped[int] = mapped_column(
        ForeignKey("presentation_assignments.id", ondelete="CASCADE"), 
        nullable=False
    )
    uploaded_by_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    # File metadata
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    filepath: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(nullable=False)  # Size in bytes
    mime_type: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # File purpose/category (optional)
    file_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., 'slides', 'data', 'notes'
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timestamps
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
    presentation_assignment = relationship("PresentationAssignment", back_populates="files")
    uploaded_by = relationship("User", back_populates="presentation_files")

    @property
    def file_path(self) -> str:
        """Alias for compatibility"""
        return self.filepath
    
    @property
    def file_url(self) -> str:
        """Generate download URL for the file"""
        return f"/api/v1/presentation-assignments/{self.presentation_assignment_id}/files/{self.id}/download"