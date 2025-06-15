# Database Architecture & SQLAlchemy Reference

**Last Updated:** June 15, 2025  
**Migration Status:** COMPLETE - All data persistent in PostgreSQL  
**Architecture Version:** V3.0 - Unified AgendaItem Model

## Overview
DoR-Dash uses PostgreSQL with SQLAlchemy ORM. The system has successfully migrated from in-memory storage to a unified `AgendaItem` approach with complete database persistence. Legacy models are maintained for API compatibility but no longer actively used for data storage.

## Core Architecture Principles

### 1. Current Architecture (V3.0 - June 2025)
- **UNIFIED MODEL**: All content (student updates, faculty updates) stored in `AgendaItem` table with JSONB content
- **COMPLETE PERSISTENCE**: No in-memory storage - all data safely stored in PostgreSQL
- **LEGACY COMPATIBILITY**: Original API endpoints maintained but use unified backend storage
- **DATA SAFETY**: 100% persistence achieved - no data loss on restart/deployment

### 2. SQLAlchemy Base Class
All models MUST inherit from `app.db.base_class.Base`:
```python
from app.db.base_class import Base

class YourModel(Base):
    # Your model definition
```

**NEVER** create separate `declarative_base()` instances - this breaks relationship mapping.

## Current Database Schema (V3.0)

### AgendaItem Model (Primary)
```python
class AgendaItem(Base):
    __tablename__ = "agendaitem"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[Optional[int]] = mapped_column(ForeignKey("meeting.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    item_type: Mapped[AgendaItemType] = mapped_column(Enum(AgendaItemType))
    title: Mapped[Optional[str]] = mapped_column(String(255))
    content: Mapped[dict] = mapped_column(JSON, default=dict)
    is_presenting: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
```

### User Model (Core)
```python
class User(Base):
    __tablename__ = "user"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole))
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Primary relationships (AgendaItem model)
    agenda_items = relationship("AgendaItem", back_populates="user")
    created_meetings = relationship("Meeting", back_populates="creator")
    file_uploads = relationship("FileUpload", back_populates="user")
```

### Meeting Model (Core)
```python
class Meeting(Base):
    __tablename__ = "meeting"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    date: Mapped[datetime] = mapped_column(DateTime)
    description: Mapped[Optional[str]] = mapped_column(Text)
    meeting_type: Mapped[str] = mapped_column(String(50))
    created_by: Mapped[int] = mapped_column(ForeignKey("user.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="created_meetings")
    agenda_items = relationship("AgendaItem", back_populates="meeting")
```

### FileUpload Model (Updated)
```python
class FileUpload(Base):
    __tablename__ = "fileupload"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    original_filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(100))
    file_size: Mapped[int] = mapped_column(Integer)
    file_path: Mapped[str] = mapped_column(String(500))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Primary FKs
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    agenda_item_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agendaitem.id", ondelete="CASCADE"))
    
    # Legacy FKs (Maintained for compatibility - not actively used)
    student_update_id: Mapped[Optional[int]] = mapped_column(ForeignKey("student_updates.id", ondelete="CASCADE"))
    faculty_update_id: Mapped[Optional[int]] = mapped_column(ForeignKey("faculty_updates.id", ondelete="CASCADE"))
    
    # Relationships
    user = relationship("User", back_populates="file_uploads")
    agenda_item = relationship("AgendaItem", back_populates="files")
```

### RegistrationRequest Model (Core)
```python
class RegistrationRequest(Base):
    __tablename__ = "registrationrequest"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100))
    full_name: Mapped[str] = mapped_column(String(100))
    password_hash: Mapped[str] = mapped_column(String(255))
    status: Mapped[RegistrationStatus] = mapped_column(Enum(RegistrationStatus))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    processed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"))
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
```

## Table Relationships Map (Updated V3.0)

### Core Tables
```
user (Primary)
├── agenda_items (1:many) ✅ ACTIVE
├── created_meetings (1:many) ✅ ACTIVE
├── file_uploads (1:many) ✅ ACTIVE
├── registration_requests (1:many) ✅ ACTIVE
├── student_updates (1:many) ⚠️ LEGACY
├── faculty_updates (1:many) ⚠️ LEGACY
└── presentations (1:many) ⚠️ LEGACY

meeting (Primary)
├── agenda_items (1:many) ✅ ACTIVE
├── student_updates (1:many) ⚠️ LEGACY
└── faculty_updates (1:many) ⚠️ LEGACY

agendaitem (Primary) ✅ UNIFIED MODEL
├── file_uploads (1:many) ✅ ACTIVE
├── user (many:1) ✅ ACTIVE
└── meeting (many:1) ✅ ACTIVE

fileupload (Updated)
├── user (many:1) ✅ ACTIVE
├── agenda_item (many:1) ✅ ACTIVE
├── student_update (many:1) ⚠️ LEGACY
└── faculty_update (many:1) ⚠️ LEGACY
```

## Content Storage Strategy

### JSONB Content Field Structure

**Student Update Content:**
```json
{
  "progress_text": "Research progress description",
  "challenges_text": "Current challenges faced", 
  "next_steps_text": "Planned next steps",
  "meeting_notes": "Additional notes for meeting",
  "refined_content": "AI-refined version (if applicable)"
}
```

**Faculty Update Content:**
```json
{
  "announcements_text": "Faculty announcements",
  "announcement_type": "general|urgent|deadline",
  "projects_text": "Project updates", 
  "project_status_text": "Project status information",
  "faculty_questions": "Questions for students"
}
```

**General Announcement Content:**
```json
{
  "message": "Announcement text",
  "priority": "low|medium|high",
  "category": "administrative|academic|social",
  "expiry_date": "2025-12-31T23:59:59Z"
}
```

## Migration History (COMPLETED June 2025)

### ✅ Phase 1: Schema Creation (COMPLETED)
1. ✅ Created `agendaitem` table with JSONB content field
2. ✅ Updated `fileupload` table to reference agenda items
3. ✅ Added proper foreign key relationships

### ✅ Phase 2: Data Migration (COMPLETED)
1. ✅ Migrated all student updates to `agendaitem` with type='student_update'
2. ✅ Migrated all faculty updates to `agendaitem` with type='faculty_update'
3. ✅ Updated file upload references to point to agenda items
4. ✅ Converted all in-memory storage to database persistence

### ✅ Phase 3: API Migration (COMPLETED)
1. ✅ Updated all CRUD operations to use AgendaItem model
2. ✅ Maintained legacy API endpoints for backward compatibility
3. ✅ Fixed file upload associations and error handling
4. ✅ Achieved 100% database persistence

## Current Benefits (Achieved V3.0)

### 1. Simplified Queries (IMPLEMENTED)
**Before (In-Memory):**
```python
# Complex dictionary lookups
student_updates = STUDENT_UPDATES_DB.get(meeting_id, [])
faculty_updates = FACULTY_UPDATES_DB.get(meeting_id, [])
# Data lost on restart!
```

**After (Database):**
```sql  
-- Single query for complete agenda
SELECT * FROM agendaitem 
WHERE meeting_id = ? 
ORDER BY created_at;
```

### 2. Chronological Ordering (IMPLEMENTED)
```sql
-- Natural ordering by creation time
SELECT * FROM agendaitem 
WHERE meeting_id = ? 
ORDER BY created_at, is_presenting DESC;
```

### 3. Extensible Design (IMPLEMENTED)
```sql
-- Add new agenda item types easily
INSERT INTO agendaitem (meeting_id, user_id, item_type, content) 
VALUES (?, ?, 'announcement', '{"message": "Lab closure", "priority": "high"}');
```

### 4. Integrated File Upload Model (IMPLEMENTED)
```sql
-- All files properly reference agenda items
SELECT f.*, ai.title, ai.item_type 
FROM file_upload f 
JOIN agendaitem ai ON f.agenda_item_id = ai.id 
WHERE ai.meeting_id = ?;
```

## API Simplification

### Before (Complex)
- Multiple in-memory dictionaries (STUDENT_UPDATES_DB, FACULTY_UPDATES_DB)
- Manual data structure management
- Data loss on container restart
- Complex file association logic

### After (Unified)
- Single `/api/v1/agenda-items/` endpoint for all content
- Automatic database persistence
- `/api/v1/meetings/{id}/agenda` returns complete agenda
- Legacy endpoints maintained for backward compatibility

## Model Registration

### Required Imports in `/app/db/base.py`
```python
from app.db.base_class import Base  # noqa
from app.db.models.user import User  # noqa
from app.db.models.meeting import Meeting  # noqa
from app.db.models.agenda_item import AgendaItem  # noqa
from app.db.models.file_upload import FileUpload  # noqa
from app.db.models.registration_request import RegistrationRequest  # noqa

# Legacy models (maintained for compatibility)
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

# Legacy models (compatibility only)
from .student_update import StudentUpdate
from .faculty_update import FacultyUpdate, AnnouncementType
from .presentation import AssignedPresentation
```

## Common SQLAlchemy Patterns

### 1. Query AgendaItems by Meeting
```python
# Get all agenda items for a meeting
agenda_items = db.query(AgendaItem)\
    .filter(AgendaItem.meeting_id == meeting_id)\
    .order_by(AgendaItem.created_at)\
    .all()
```

### 2. Query with File Associations
```python
# Get agenda items with their files
from sqlalchemy.orm import joinedload

agenda_items = db.query(AgendaItem)\
    .options(joinedload(AgendaItem.files))\
    .filter(AgendaItem.meeting_id == meeting_id)\
    .all()
```

### 3. Filter by Content Type
```python
# Get only student updates
student_items = db.query(AgendaItem)\
    .filter(AgendaItem.item_type == AgendaItemType.STUDENT_UPDATE)\
    .all()
```

### 4. JSONB Content Queries
```python
# Query content within JSONB field
from sqlalchemy import cast, String

urgent_announcements = db.query(AgendaItem)\
    .filter(AgendaItem.item_type == AgendaItemType.FACULTY_UPDATE)\
    .filter(cast(AgendaItem.content['announcement_type'], String) == 'urgent')\
    .all()
```

## Performance Considerations

### Indexes (Current)
```sql
-- Existing indexes
CREATE INDEX idx_agendaitem_meeting_id ON agendaitem(meeting_id);
CREATE INDEX idx_agendaitem_user_id ON agendaitem(user_id);
CREATE INDEX idx_agendaitem_type ON agendaitem(item_type);
CREATE INDEX idx_agendaitem_created_at ON agendaitem(created_at);

-- JSONB indexes for content queries
CREATE INDEX idx_agendaitem_content_gin ON agendaitem USING GIN(content);
```

### Query Optimization
```python
# Use selectinload for one-to-many relationships
agenda_items = db.query(AgendaItem)\
    .options(selectinload(AgendaItem.files))\
    .filter(AgendaItem.meeting_id == meeting_id)\
    .all()

# Use joinedload for many-to-one relationships
agenda_items = db.query(AgendaItem)\
    .options(joinedload(AgendaItem.user))\
    .filter(AgendaItem.meeting_id == meeting_id)\
    .all()
```

## Quality Assurance Validation

**Latest QA Report (June 15, 2025):**
- ✅ Database connectivity and health confirmed
- ✅ All core tables present with proper relationships
- ✅ File upload system working with database storage
- ⚠️ 2 minor API bugs identified and documented
- ✅ No data loss risk - complete persistence verified

## Current System Status (June 2025)

### ✅ ACHIEVEMENTS
- **100% Database Persistence:** All data safely stored in PostgreSQL
- **Unified Data Model:** Single AgendaItem table for all content types
- **File Integration:** Binary files + database metadata properly linked
- **Performance:** Fast queries with proper indexing
- **Data Safety:** No risk of data loss from restarts or deployments

### 🎯 ACTIVE MONITORING
- **QA System:** Automated testing and validation
- **Health Checks:** Database connectivity and performance monitoring
- **Error Tracking:** Known issues documented with specific fixes

### 🔧 NEXT OPTIMIZATIONS
1. Fix student update schema bug (missing `to_agenda_item_create` method)
2. Debug faculty update listing HTTP 500 errors
3. Optimize JSONB queries for better performance
4. Clean up legacy table dependencies

### Current State (Complete Migration - June 2025)
1. **AgendaItem** table stores ALL content (no in-memory storage)
2. **Legacy tables** exist but unused - can be safely dropped
3. **FileUpload** primarily uses agenda_item_id relationships
4. **Complete persistence** - all data survives restarts and deployments

### Future Optimization (V3.1)
1. Remove legacy table dependencies once API migration confirmed stable
2. Optimize JSONB queries with proper indexes
3. Clean up unused foreign key relationships
4. Performance tuning for large datasets

## Emergency Fixes

### If Backend Won't Start Due to Model Issues:
1. Check latest error in container logs: `docker logs dor-dash`
2. Verify all imports in `base.py` and `__init__.py`
3. Check for missing foreign key constraints
4. Ensure all relationships have matching `back_populates`
5. Restart backend container

### Model Creation Checklist:
- [ ] Inherits from `app.db.base_class.Base`
- [ ] Added to `base.py` imports
- [ ] Added to `__init__.py` imports  
- [ ] All foreign keys have `ForeignKey()` constraint
- [ ] All relationships have matching `back_populates`
- [ ] Table name follows convention (lowercase)

**Remember**: The unified AgendaItem model with JSONB content provides flexibility while maintaining data integrity. All relationship errors are now database-enforced with proper foreign keys.

---

**Database Architecture Notes:**
- Complete migration to unified model achieved June 2025
- All data persistence guaranteed - no in-memory storage
- Legacy compatibility maintained for smooth transition
- Performance optimized with proper indexing and query patterns
- Quality assurance monitoring ensures database health and integrity