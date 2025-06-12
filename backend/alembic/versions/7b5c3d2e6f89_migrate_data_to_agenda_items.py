"""Migrate data to agenda items

Revision ID: 7b5c3d2e6f89
Revises: 6a4b2c1d5e78
Create Date: 2025-06-12 14:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '7b5c3d2e6f89'
down_revision = '6a4b2c1d5e78'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create a session to execute raw SQL
    bind = op.get_bind()
    
    print("Starting data migration to agenda_item table...")
    
    # Migrate student updates to agenda_item
    print("Migrating student updates...")
    student_migration = text("""
        INSERT INTO agenda_item (
            meeting_id, user_id, item_type, order_index, title, content, 
            is_presenting, created_at, updated_at
        )
        SELECT 
            meeting_id,
            user_id,
            'student_update'::agendaitemtype,
            ROW_NUMBER() OVER (PARTITION BY meeting_id ORDER BY created_at) - 1 as order_index,
            CONCAT('Student Update - ', u.full_name, ' (', u.username, ')') as title,
            jsonb_build_object(
                'progress_text', COALESCE(progress_text, ''),
                'challenges_text', COALESCE(challenges_text, ''),
                'next_steps_text', COALESCE(next_steps_text, ''),
                'meeting_notes', COALESCE(meeting_notes, '')
            ) as content,
            will_present,
            created_at,
            updated_at
        FROM studentupdate su
        JOIN "user" u ON su.user_id = u.id
        ORDER BY meeting_id, created_at;
    """)
    
    result = bind.execute(student_migration)
    print(f"Migrated {result.rowcount} student updates")
    
    # Migrate faculty updates to agenda_item
    print("Migrating faculty updates...")
    faculty_migration = text("""
        INSERT INTO agenda_item (
            meeting_id, user_id, item_type, order_index, title, content, 
            is_presenting, created_at, updated_at
        )
        SELECT 
            meeting_id,
            user_id,
            'faculty_update'::agendaitemtype,
            (SELECT COUNT(*) FROM agenda_item ai WHERE ai.meeting_id = fu.meeting_id) as order_index,
            CONCAT('Faculty Update - ', u.full_name, ' (', u.username, ')') as title,
            jsonb_build_object(
                'announcements_text', COALESCE(announcements_text, ''),
                'announcement_type', COALESCE(announcement_type::text, 'general'),
                'projects_text', COALESCE(projects_text, ''),
                'project_status_text', COALESCE(project_status_text, ''),
                'faculty_questions', COALESCE(faculty_questions, '')
            ) as content,
            is_presenting,
            created_at,
            updated_at
        FROM facultyupdate fu
        JOIN "user" u ON fu.user_id = u.id
        ORDER BY meeting_id, created_at;
    """)
    
    result = bind.execute(faculty_migration)
    print(f"Migrated {result.rowcount} faculty updates")
    
    # Migrate file upload references for student updates
    print("Migrating file upload references...")
    
    # First, migrate student update file references
    student_file_migration = text("""
        UPDATE fileupload 
        SET agenda_item_id = (
            SELECT ai.id 
            FROM agenda_item ai
            JOIN studentupdate su ON (
                ai.meeting_id = su.meeting_id 
                AND ai.user_id = su.user_id 
                AND ai.item_type = 'student_update'
                AND ai.created_at = su.created_at
            )
            WHERE su.id = fileupload.student_update_id
        )
        WHERE student_update_id IS NOT NULL;
    """)
    
    result = bind.execute(student_file_migration)
    print(f"Migrated {result.rowcount} student update file references")
    
    # Migrate faculty update file references (if any exist)
    faculty_file_migration = text("""
        UPDATE fileupload 
        SET agenda_item_id = (
            SELECT ai.id 
            FROM agenda_item ai
            JOIN facultyupdate fu ON (
                ai.meeting_id = fu.meeting_id 
                AND ai.user_id = fu.user_id 
                AND ai.item_type = 'faculty_update'
                AND ai.created_at = fu.created_at
            )
            WHERE fu.id = fileupload.faculty_update_id
        )
        WHERE faculty_update_id IS NOT NULL;
    """)
    
    result = bind.execute(faculty_file_migration)
    print(f"Migrated {result.rowcount} faculty update file references")
    
    # Verify migration
    verification = text("SELECT COUNT(*) as total FROM agenda_item")
    result = bind.execute(verification)
    total_items = result.fetchone()[0]
    print(f"Migration complete. Total agenda items: {total_items}")
    
    # Drop old foreign key constraints and columns from fileupload
    print("Cleaning up old file upload references...")
    
    # Check if constraints exist before dropping them
    try:
        op.drop_constraint('fileupload_student_update_id_fkey', 'fileupload', type_='foreignkey')
    except:
        pass  # Constraint might not exist
        
    try:
        op.drop_constraint('fileupload_faculty_update_id_fkey', 'fileupload', type_='foreignkey')
    except:
        pass  # Constraint might not exist
    
    # Drop old columns
    try:
        op.drop_column('fileupload', 'student_update_id')
    except:
        pass  # Column might not exist
        
    try:
        op.drop_column('fileupload', 'faculty_update_id')
    except:
        pass  # Column might not exist


def downgrade() -> None:
    print("WARNING: This downgrade will lose data! Proceeding anyway...")
    
    # Recreate old columns in fileupload table
    op.add_column('fileupload', sa.Column('student_update_id', sa.Integer(), nullable=True))
    op.add_column('fileupload', sa.Column('faculty_update_id', sa.Integer(), nullable=True))
    
    # Note: We cannot restore the exact same data because the old tables still exist
    # This is a destructive migration - the old tables will be dropped in a later migration
    
    # Clear the agenda_item table
    bind = op.get_bind()
    bind.execute(text("DELETE FROM agenda_item"))
    
    print("Downgrade complete - agenda_item table cleared")