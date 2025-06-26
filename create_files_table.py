#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.db.session import SessionLocal
from sqlalchemy import text

# SQL to create the presentation_assignment_files table
create_table_sql = """
CREATE TABLE IF NOT EXISTS presentation_assignment_files (
    id SERIAL PRIMARY KEY,
    presentation_assignment_id INTEGER NOT NULL REFERENCES presentation_assignments(id) ON DELETE CASCADE,
    uploaded_by_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    filepath VARCHAR(500) NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(200),
    file_category VARCHAR(50),
    description VARCHAR(500),
    upload_date TIMESTAMP DEFAULT NOW() NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_presentation_assignment_files_id ON presentation_assignment_files(id);
CREATE INDEX IF NOT EXISTS ix_presentation_assignment_files_assignment_id ON presentation_assignment_files(presentation_assignment_id);
"""

db = SessionLocal()
try:
    db.execute(text(create_table_sql))
    db.commit()
    print("Successfully created presentation_assignment_files table")
except Exception as e:
    print(f"Error creating table: {e}")
    db.rollback()
finally:
    db.close()