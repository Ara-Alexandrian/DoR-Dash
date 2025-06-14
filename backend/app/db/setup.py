# This file is used to set up relationships between models after all models have been defined
# to avoid circular import issues

def setup_relationships():
    # Import the models here to avoid circular imports
    from app.db.models.user import User
    from app.db.models.agenda_item import AgendaItem
    from app.db.models.file_upload import FileUpload
    from app.db.models.meeting import Meeting
    from app.db.models.registration_request import RegistrationRequest
    from sqlalchemy.orm import relationship
    
    # Set up relationships for User model (using current unified AgendaItem system)
    if not hasattr(User, 'agenda_items'):
        User.agenda_items = relationship("AgendaItem", back_populates="user", cascade="all, delete-orphan")
        User.file_uploads = relationship("FileUpload", back_populates="user", cascade="all, delete-orphan")
        User.meetings = relationship("Meeting", back_populates="user", cascade="all, delete-orphan")
        User.registration_requests = relationship("RegistrationRequest", back_populates="user", cascade="all, delete-orphan")