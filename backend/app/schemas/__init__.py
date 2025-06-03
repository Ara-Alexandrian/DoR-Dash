# Import all schemas to make them discoverable
from .auth import Token, TokenData, TokenPayload, UserCreate, UserUpdate, UserInDB, UserResponse, User, UserList
from .student_update import StudentUpdate, StudentUpdateCreate, StudentUpdateUpdate, StudentUpdateList
from .faculty_update import FacultyUpdate, FacultyUpdateCreate, FacultyUpdateUpdate, FacultyUpdateList, AnnouncementType
