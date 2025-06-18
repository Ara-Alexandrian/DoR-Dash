from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from app.db.base_class import Base

class AssignedPresentation(Base):
    __tablename__ = "assigned_presentations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    meeting_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="scheduled", nullable=False)
    is_confirmed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # NO RELATIONSHIPS - avoid circular imports