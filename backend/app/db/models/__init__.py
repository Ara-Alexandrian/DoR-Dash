# Import all models to make them discoverable by Alembic
from .user import User, UserRole
from .student_update import StudentUpdate
from .faculty_update import FacultyUpdate, AnnouncementType
from .file_upload import FileUpload
from .meeting import Meeting, MeetingType