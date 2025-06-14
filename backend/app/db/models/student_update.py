from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class StudentUpdate(Base):
    """
    Legacy student update model for backward compatibility
    This is now superseded by AgendaItem model
    """
    __tablename__ = "student_updates"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    original_content = Column(Text, nullable=True)
    refined_content = Column(Text, nullable=True)
    reflection = Column(Text, nullable=True)
    goals = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_submitted = Column(Boolean, default=False)
    
    # Relationships
    student = relationship("User", back_populates="student_updates")
    meeting = relationship("Meeting", back_populates="student_updates")
    files = relationship("FileUpload", back_populates="student_update")