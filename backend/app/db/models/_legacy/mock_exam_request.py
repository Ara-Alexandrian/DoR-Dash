from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


class MockExamRequest(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    preferred_session: Mapped[str] = mapped_column(String(100), nullable=False)
    focus_topics: Mapped[str] = mapped_column(Text, nullable=False)
    presentation_length: Mapped[int] = mapped_column(Integer, default=30, nullable=False)  # Length in minutes
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
    user = relationship("User", back_populates="mock_exam_requests")