# This file is used to set up relationships between models after all models have been defined
# to avoid circular import issues

def setup_relationships():
    # Import the models here to avoid circular imports
    from app.db.models.user import User
    from app.db.models.student_update import StudentUpdate
    from app.db.models.support_request import SupportRequest
    from app.db.models.mock_exam_request import MockExamRequest
    from app.db.models.file_upload import FileUpload
    from app.db.models.presentation import AssignedPresentation
    from sqlalchemy.orm import relationship
    
    # Set up relationships for User model
    if not hasattr(User, 'student_updates'):
        User.student_updates = relationship("StudentUpdate", back_populates="user", cascade="all, delete-orphan")
        User.support_requests = relationship("SupportRequest", back_populates="user", cascade="all, delete-orphan")
        User.mock_exam_requests = relationship("MockExamRequest", back_populates="user", cascade="all, delete-orphan")
        User.file_uploads = relationship("FileUpload", back_populates="user", cascade="all, delete-orphan")
        User.presentations = relationship("AssignedPresentation", back_populates="user", cascade="all, delete-orphan")