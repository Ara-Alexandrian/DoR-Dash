# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.db.models.user import User  # noqa
from app.db.models.meeting import Meeting  # noqa
from app.db.models.agenda_item import AgendaItem  # noqa
from app.db.models.file_upload import FileUpload  # noqa
from app.db.models.registration_request import RegistrationRequest  # noqa
