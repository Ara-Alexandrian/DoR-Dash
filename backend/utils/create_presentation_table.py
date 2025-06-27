#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.db.session import SessionLocal
from sqlalchemy import text

# SQL to create the enum type and presentation_assignments table
create_table_sql = """
CREATE TYPE presentationtype AS ENUM (
    'casual', 'mock_defense', 'pre_conference', 'thesis_proposal', 
    'dissertation_defense', 'journal_club', 'research_update'
);

CREATE TABLE IF NOT EXISTS presentation_assignments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    assigned_by_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    meeting_id INTEGER REFERENCES meeting(id) ON DELETE SET NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    presentation_type presentationtype NOT NULL,
    duration_minutes INTEGER,
    requirements TEXT,
    due_date TIMESTAMP,
    assigned_date TIMESTAMP DEFAULT NOW() NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE NOT NULL,
    completion_date TIMESTAMP,
    grillometer_novelty INTEGER CHECK (grillometer_novelty >= 1 AND grillometer_novelty <= 3),
    grillometer_methodology INTEGER CHECK (grillometer_methodology >= 1 AND grillometer_methodology <= 3),
    grillometer_delivery INTEGER CHECK (grillometer_delivery >= 1 AND grillometer_delivery <= 3),
    notes TEXT,
    extra_data JSON,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_presentation_assignments_id ON presentation_assignments(id);
CREATE INDEX IF NOT EXISTS ix_presentation_assignments_student_id ON presentation_assignments(student_id);
CREATE INDEX IF NOT EXISTS ix_presentation_assignments_meeting_id ON presentation_assignments(meeting_id);
"""

db = SessionLocal()
try:
    db.execute(text(create_table_sql))
    db.commit()
    print("Successfully created presentation_assignments table")
except Exception as e:
    print(f"Error creating table: {e}")
    db.rollback()
finally:
    db.close()