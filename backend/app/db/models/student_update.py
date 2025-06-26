from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from datetime import datetime
from app.db.base_class import Base

class StudentUpdate(Base):
    """
    Legacy student update model for backward compatibility
    This is now superseded by AgendaItem model
    """
    __tablename__ = "student_updates"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    meeting_id = Column(Integer, ForeignKey("meeting.id"), nullable=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    original_content = Column(Text, nullable=True)
    refined_content = Column(Text, nullable=True)
    reflection = Column(Text, nullable=True)
    goals = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_submitted = Column(Boolean, default=False)
    
    # NO RELATIONSHIPS - avoid circular imports