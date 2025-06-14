# Database Architecture & SQLAlchemy Reference

## Overview
DoR-Dash uses PostgreSQL with SQLAlchemy ORM. The system has evolved from individual models to a unified `AgendaItem` approach while maintaining backward compatibility with legacy models.

## Core Architecture Principles

### 1. Unified vs Legacy Models
- **NEW APPROACH**: All content (student updates, faculty updates) stored in `AgendaItem` table
- **LEGACY SUPPORT**: Original models (`StudentUpdate`, `FacultyUpdate`, `AssignedPresentation`) maintained for API compatibility
- **DUAL SYSTEM**: Both approaches work simultaneously during transition

### 2. SQLAlchemy Base Class
All models MUST inherit from `app.db.base_class.Base`:
```python
from app.db.base_class import Base

class YourModel(Base):
    # Your model definition
```

**NEVER** create separate `declarative_base()` instances - this breaks relationship mapping.

## Table Relationships Map

### Core Tables
```
user (Primary)
├── agenda_items (1:many)
├── created_meetings (1:many) 
├── file_uploads (1:many)
├── student_updates (1:many) [LEGACY]
├── faculty_updates (1:many) [LEGACY]
└── presentations (1:many) [LEGACY]

meeting (Primary)
├── agenda_items (1:many)
├── student_updates (1:many) [LEGACY]
└── faculty_updates (1:many) [LEGACY]

agendaitem (Primary)
├── file_uploads (1:many)
└── user (many:1)
└── meeting (many:1)

fileupload (Junction Table)
├── user (many:1)
├── agenda_item (many:1)
├── student_update (many:1) [LEGACY]
└── faculty_update (many:1) [LEGACY]
```

## Required Foreign Keys

### FileUpload Model
```python
class FileUpload(Base):
    # Core FKs
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    agenda_item_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agendaitem.id", ondelete="CASCADE"))
    
    # Legacy FKs (REQUIRED for backward compatibility)
    student_update_id: Mapped[Optional[int]] = mapped_column(ForeignKey("student_updates.id", ondelete="CASCADE"))
    faculty_update_id: Mapped[Optional[int]] = mapped_column(ForeignKey("faculty_updates.id", ondelete="CASCADE"))
```

### User Model Relationships
```python
class User(Base):
    # Core relationships
    agenda_items = relationship("AgendaItem", back_populates="user")
    created_meetings = relationship("Meeting", back_populates="creator", foreign_keys="Meeting.created_by")
    file_uploads = relationship("FileUpload", back_populates="user")
    
    # Legacy relationships (REQUIRED)
    student_updates = relationship("StudentUpdate", back_populates="student")
    faculty_updates = relationship("FacultyUpdate", back_populates="faculty")
    presentations = relationship("AssignedPresentation", back_populates="user")
```

### Meeting Model Relationships
```python
class Meeting(Base):
    # Core relationships
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_meetings")
    agenda_items = relationship("AgendaItem", back_populates="meeting")
    
    # Legacy relationships (REQUIRED)
    student_updates = relationship("StudentUpdate", back_populates="meeting")
    faculty_updates = relationship("FacultyUpdate", back_populates="meeting")
```

## Legacy Model Requirements

### StudentUpdate (Legacy)
```python
class StudentUpdate(Base):
    __tablename__ = "student_updates"
    
    student_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    meeting_id = Column(Integer, ForeignKey("meeting.id"), nullable=True)
    
    # Relationships
    student = relationship("User", back_populates="student_updates")
    meeting = relationship("Meeting", back_populates="student_updates")
    files = relationship("FileUpload", back_populates="student_update")
```

### FacultyUpdate (Legacy)
```python
class FacultyUpdate(Base):
    __tablename__ = "faculty_updates"
    
    faculty_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    meeting_id = Column(Integer, ForeignKey("meeting.id"), nullable=True)
    
    # Relationships
    faculty = relationship("User", back_populates="faculty_updates")
    meeting = relationship("Meeting", back_populates="faculty_updates")
    files = relationship("FileUpload", back_populates="faculty_update")
```

### AssignedPresentation (Legacy)
```python
class AssignedPresentation(Base):
    __tablename__ = "assigned_presentations"
    
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="presentations")
```

## Model Registration

### Required Imports in `/app/db/base.py`
```python
from app.db.base_class import Base  # noqa
from app.db.models.user import User  # noqa
from app.db.models.meeting import Meeting  # noqa
from app.db.models.agenda_item import AgendaItem  # noqa
from app.db.models.file_upload import FileUpload  # noqa
from app.db.models.registration_request import RegistrationRequest  # noqa

# Legacy models (REQUIRED for API compatibility)
from app.db.models.student_update import StudentUpdate  # noqa
from app.db.models.faculty_update import FacultyUpdate  # noqa
from app.db.models.presentation import AssignedPresentation  # noqa
```

### Required Imports in `/app/db/models/__init__.py`
```python
from .user import User, UserRole
from .file_upload import FileUpload
from .meeting import Meeting, MeetingType
from .registration_request import RegistrationRequest, RegistrationStatus
from .agenda_item import AgendaItem, AgendaItemType

# Legacy models
from .student_update import StudentUpdate
from .faculty_update import FacultyUpdate, AnnouncementType
from .presentation import AssignedPresentation
```

## Common SQLAlchemy Errors & Solutions

### 1. "No module named 'app.db.models.X'"
**Cause**: Missing model file or import
**Solution**: 
- Create the model file
- Add import to `__init__.py` and `base.py`

### 2. "Could not determine join condition between parent/child tables"
**Cause**: Missing ForeignKey constraint
**Solution**: Add `ForeignKey("table.column")` to the mapped_column

### 3. "Expression 'User' failed to locate a name"
**Cause**: Different declarative_base() instances
**Solution**: All models must use `app.db.base_class.Base`

### 4. "One or more mappers failed to initialize"
**Cause**: Circular relationship or missing back_populates
**Solution**: Ensure all relationships have matching `back_populates`

## Database Migration Strategy

### Current State (Transition Period)
1. **AgendaItem** table stores new content
2. **Legacy tables** still exist for API compatibility
3. **FileUpload** links to both systems

### Future State (Post-Migration)
1. Legacy tables can be dropped
2. Legacy foreign keys in FileUpload removed
3. Legacy relationships in core models removed

## Debugging SQLAlchemy Issues

### 1. Check Model Registration
```bash
# In backend directory
python3 -c "from app.db.base import Base; print([m.__name__ for m in Base.registry.mappers])"
```

### 2. Validate Relationships
```bash
# Check specific model
python3 -c "from app.db.models.user import User; print(User.__mapper__.relationships.keys())"
```

### 3. Database Schema Verification
```sql
-- Check foreign key constraints
SELECT constraint_name, table_name, column_name, foreign_table_name, foreign_column_name 
FROM information_schema.key_column_usage 
WHERE constraint_name IN (
    SELECT constraint_name FROM information_schema.table_constraints 
    WHERE constraint_type = 'FOREIGN KEY'
);
```

## Emergency Fixes

### If Backend Won't Start Due to Model Issues:
1. Check latest error in `/app/logs/backend.log`
2. Identify missing foreign key or relationship
3. Add missing constraint:
   ```python
   column_name = mapped_column(ForeignKey("target_table.id"))
   ```
4. Add matching relationship:
   ```python
   related_model = relationship("ModelName", back_populates="this_model")
   ```
5. Restart backend

### Model Creation Checklist:
- [ ] Inherits from `app.db.base_class.Base`
- [ ] Added to `base.py` imports
- [ ] Added to `__init__.py` imports  
- [ ] All foreign keys have `ForeignKey()` constraint
- [ ] All relationships have matching `back_populates`
- [ ] Table name follows convention (lowercase, pluralized)

## Performance Considerations

### Eager Loading
```python
# Load related data efficiently
db.query(User).options(joinedload(User.agenda_items)).all()
```

### Relationship Loading
```python
# Use selectinload for one-to-many
db.query(Meeting).options(selectinload(Meeting.agenda_items)).all()
```

---

**Remember**: SQLAlchemy relationship errors are always about missing foreign keys or mismatched relationship definitions. This reference should prevent 99% of common issues.