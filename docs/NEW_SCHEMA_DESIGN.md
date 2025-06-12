# DoR-Dash Schema Refactor: Unified Agenda Items

## Current Problems
- Fragmented schema: `studentupdate` + `facultyupdate` tables
- Complex UNION queries needed for agenda assembly
- No agenda ordering or formal structure
- Inconsistent table naming conventions
- Data integrity issues (admin users with student updates)

## New Unified Schema

### Core Design Principles
1. **Single Source of Truth**: One `agenda_item` table for all agenda entries
2. **Polymorphic Content**: JSONB field for type-specific data
3. **Proper Ordering**: Built-in ordering within meetings  
4. **Extensible**: Easy to add new agenda item types
5. **Data Integrity**: Proper foreign key relationships

### Schema Tables

#### 1. agenda_item (NEW - Core Table)
```sql
CREATE TABLE agenda_item (
    id SERIAL PRIMARY KEY,
    meeting_id INTEGER NOT NULL REFERENCES meeting(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    item_type VARCHAR(50) NOT NULL CHECK (item_type IN ('student_update', 'faculty_update', 'announcement', 'presentation')),
    order_index INTEGER DEFAULT 0,
    title VARCHAR(255),
    content JSONB NOT NULL DEFAULT '{}',
    is_presenting BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure ordering within meetings
    UNIQUE(meeting_id, order_index)
);

-- Indexes for performance
CREATE INDEX idx_agenda_item_meeting_order ON agenda_item(meeting_id, order_index);
CREATE INDEX idx_agenda_item_user ON agenda_item(user_id);
CREATE INDEX idx_agenda_item_type ON agenda_item(item_type);
CREATE INDEX idx_agenda_item_content ON agenda_item USING GIN(content);
```

#### 2. Content Structure by Type

**Student Update Content:**
```json
{
  "progress_text": "string",
  "challenges_text": "string", 
  "next_steps_text": "string",
  "meeting_notes": "string"
}
```

**Faculty Update Content:**
```json
{
  "announcements_text": "string",
  "announcement_type": "general|urgent|deadline",
  "projects_text": "string", 
  "project_status_text": "string",
  "faculty_questions": "string"
}
```

#### 3. file_upload (UPDATE - Reference agenda_item)
```sql
-- Update existing table to reference agenda_item instead of separate tables
ALTER TABLE file_upload DROP CONSTRAINT IF EXISTS file_upload_student_update_id_fkey;
ALTER TABLE file_upload DROP CONSTRAINT IF EXISTS file_upload_faculty_update_id_fkey;
ALTER TABLE file_upload DROP COLUMN IF EXISTS student_update_id;
ALTER TABLE file_upload DROP COLUMN IF EXISTS faculty_update_id;
ALTER TABLE file_upload ADD COLUMN agenda_item_id INTEGER REFERENCES agenda_item(id) ON DELETE CASCADE;
```

### Migration Strategy

#### Phase 1: Create New Schema
1. Create `agenda_item` table
2. Migrate data from `studentupdate` and `facultyupdate`
3. Update `file_upload` references

#### Phase 2: Data Migration
1. Copy student updates to agenda_item with type='student_update'
2. Copy faculty updates to agenda_item with type='faculty_update'  
3. Migrate file upload references
4. Assign proper ordering within meetings

#### Phase 3: Drop Old Tables
1. Drop `studentupdate` table
2. Drop `facultyupdate` table

## Benefits

### 1. Simplified Queries
**Before:**
```sql
-- Complex UNION needed for agenda
SELECT * FROM studentupdate WHERE meeting_id = ?
UNION ALL  
SELECT * FROM facultyupdate WHERE meeting_id = ?
```

**After:**
```sql  
-- Single query for complete agenda
SELECT * FROM agenda_item 
WHERE meeting_id = ? 
ORDER BY order_index;
```

### 2. Proper Agenda Ordering
```sql
-- Reorder agenda items
UPDATE agenda_item SET order_index = ? WHERE id = ?;
```

### 3. Extensible Design
```sql
-- Add new agenda item types easily
INSERT INTO agenda_item (meeting_id, user_id, item_type, content) 
VALUES (?, ?, 'presentation', '{"title": "Research Findings", "duration": 30}');
```

### 4. Single File Upload Model
```sql
-- All files reference agenda_item
SELECT * FROM file_upload WHERE agenda_item_id = ?;
```

## API Simplification

### Before (Complex)
- `/api/v1/updates/` (student updates)
- `/api/v1/faculty-updates/` (faculty updates)  
- Manual agenda assembly in meetings endpoint

### After (Unified)
- `/api/v1/agenda-items/` (all agenda items)
- `/api/v1/meetings/{id}/agenda` (automatically ordered)
- Single CRUD interface for all agenda content

## Timeline
- Phase 1: Schema creation - 1 day
- Phase 2: Data migration - 1 day  
- Phase 3: API refactor - 2 days
- Phase 4: Frontend updates - 1 day
- Phase 5: Testing & cleanup - 1 day

**Total: ~1 week for complete refactor**