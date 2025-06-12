#!/usr/bin/env python3
"""
Manual script to create the initial database migration since autogenerate is failing
"""

import asyncio
import sys
sys.path.append('/app/backend')

from app.db.session import engine
from sqlalchemy import text

async def create_database_schema():
    """Create the database schema manually"""
    
    async with engine.begin() as conn:
        print("Creating enum types...")
        
        # Create enum types
        await conn.execute(text("""
            CREATE TYPE userrole AS ENUM ('STUDENT', 'FACULTY', 'SECRETARY', 'ADMIN');
        """))
        
        await conn.execute(text("""
            CREATE TYPE meetingtype AS ENUM ('general_update', 'presentations_and_updates', 'other');
        """))
        
        await conn.execute(text("""
            CREATE TYPE registrationstatus AS ENUM ('pending', 'approved', 'rejected');
        """))
        
        await conn.execute(text("""
            CREATE TYPE agendaitemtype AS ENUM ('student_update', 'faculty_update', 'announcement', 'presentation');
        """))
        
        print("Creating tables...")
        
        # Create meeting table first
        await conn.execute(text("""
            CREATE TABLE meeting (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                meeting_type meetingtype NOT NULL DEFAULT 'general_update',
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP NOT NULL,
                created_by INTEGER NOT NULL REFERENCES "user"(id),
                created_at TIMESTAMP NOT NULL DEFAULT now(),
                updated_at TIMESTAMP NOT NULL DEFAULT now()
            );
        """))
        
        # Create agenda_item table
        await conn.execute(text("""
            CREATE TABLE agenda_item (
                id SERIAL PRIMARY KEY,
                meeting_id INTEGER NOT NULL REFERENCES meeting(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                item_type agendaitemtype NOT NULL,
                order_index INTEGER NOT NULL DEFAULT 0,
                title VARCHAR(255),
                content JSONB NOT NULL DEFAULT '{}',
                is_presenting BOOLEAN NOT NULL DEFAULT false,
                created_at TIMESTAMP NOT NULL DEFAULT now(),
                updated_at TIMESTAMP NOT NULL DEFAULT now()
            );
        """))
        
        # Create indexes
        await conn.execute(text("""
            CREATE INDEX ix_meeting_created_by ON meeting(created_by);
            CREATE INDEX ix_agenda_item_meeting_id ON agenda_item(meeting_id);
            CREATE INDEX ix_agenda_item_user_id ON agenda_item(user_id);
            CREATE INDEX ix_agenda_item_item_type ON agenda_item(item_type);
        """))
        
        # Create fileupload table (without agenda_item_id for now)
        await conn.execute(text("""
            CREATE TABLE fileupload (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                agenda_item_id INTEGER,
                filename VARCHAR(255) NOT NULL,
                filepath VARCHAR(500) NOT NULL,
                file_type VARCHAR(100) NOT NULL,
                file_size INTEGER NOT NULL,
                upload_date TIMESTAMP NOT NULL DEFAULT now(),
                created_at TIMESTAMP NOT NULL DEFAULT now(),
                updated_at TIMESTAMP NOT NULL DEFAULT now()
            );
        """))
        
        # Add foreign key for agenda_item_id after agenda_item table exists
        await conn.execute(text("""
            ALTER TABLE fileupload 
            ADD CONSTRAINT fileupload_agenda_item_id_fkey 
            FOREIGN KEY (agenda_item_id) REFERENCES agenda_item(id) ON DELETE CASCADE;
        """))
        
        # Create registration_request table
        await conn.execute(text("""
            CREATE TABLE registration_request (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                preferred_email VARCHAR(100),
                phone VARCHAR(20),
                research_interests TEXT,
                additional_info TEXT,
                status registrationstatus NOT NULL DEFAULT 'pending',
                admin_notes TEXT,
                requested_at TIMESTAMP NOT NULL DEFAULT now(),
                reviewed_at TIMESTAMP,
                created_at TIMESTAMP NOT NULL DEFAULT now(),
                updated_at TIMESTAMP NOT NULL DEFAULT now()
            );
        """))
        
        print("Database schema created successfully!")

if __name__ == "__main__":
    asyncio.run(create_database_schema())