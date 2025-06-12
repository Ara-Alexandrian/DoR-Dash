# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.db.models.user import User  # noqa
from app.db.models.meeting import Meeting  # noqa
from app.db.models.agenda_item import AgendaItem  # noqa
from app.db.models.student_update import StudentUpdate  # noqa
from app.db.models.faculty_update import FacultyUpdate  # noqa
from app.db.models.support_request import SupportRequest  # noqa
from app.db.models.mock_exam_request import MockExamRequest  # noqa
from app.db.models.file_upload import FileUpload  # noqa
from app.db.models.presentation import AssignedPresentation  # noqa
