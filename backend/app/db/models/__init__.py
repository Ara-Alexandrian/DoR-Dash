# Import all models to make them discoverable by Alembic
from .user import User, UserRole
from .file_upload import FileUpload
from .meeting import Meeting, MeetingType
from .registration_request import RegistrationRequest, RegistrationStatus
from .agenda_item import AgendaItem, AgendaItemType
from .student_update import StudentUpdate
from .faculty_update import FacultyUpdate, AnnouncementType
from .presentation import AssignedPresentation
from .presentation_assignment import PresentationAssignment, PresentationType