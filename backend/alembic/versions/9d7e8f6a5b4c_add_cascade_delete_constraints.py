"""add cascade delete constraints - fixed version

Revision ID: 9d7e8f6a5b4c
Revises: 8c6d4e3f7a90
Create Date: 2025-06-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '9d7e8f6a5b4c'
down_revision = '8c6d4e3f7a90'
branch_labels = None
depends_on = None


def upgrade():
    """Add CASCADE constraints to foreign keys for user deletion - checks if tables exist first"""
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()
    
    # Only operate on tables that actually exist
    # Most of these tables have been migrated to agenda_items already
    
    # Update meetings table if it exists
    if 'meetings' in existing_tables:
        constraints = [c['name'] for c in inspector.get_foreign_keys('meetings')]
        if 'meetings_created_by_fkey' in constraints:
            op.drop_constraint('meetings_created_by_fkey', 'meetings', type_='foreignkey')
            op.create_foreign_key(
                'meetings_created_by_fkey', 
                'meetings', 
                'users', 
                ['created_by'], 
                ['id'], 
                ondelete='SET NULL'
            )
    
    # Update agenda_items if it exists
    if 'agenda_items' in existing_tables:
        constraints = [c['name'] for c in inspector.get_foreign_keys('agenda_items')]
        if 'agenda_items_user_id_fkey' in constraints:
            op.drop_constraint('agenda_items_user_id_fkey', 'agenda_items', type_='foreignkey')
            op.create_foreign_key(
                'agenda_items_user_id_fkey', 
                'agenda_items', 
                'users', 
                ['user_id'], 
                ['id'], 
                ondelete='CASCADE'
            )
        if 'agenda_items_meeting_id_fkey' in constraints:
            op.drop_constraint('agenda_items_meeting_id_fkey', 'agenda_items', type_='foreignkey')
            op.create_foreign_key(
                'agenda_items_meeting_id_fkey', 
                'agenda_items', 
                'meetings', 
                ['meeting_id'], 
                ['id'], 
                ondelete='CASCADE'
            )
    
    # Update file_uploads if it exists
    if 'file_uploads' in existing_tables:
        constraints = [c['name'] for c in inspector.get_foreign_keys('file_uploads')]
        if 'file_uploads_user_id_fkey' in constraints:
            op.drop_constraint('file_uploads_user_id_fkey', 'file_uploads', type_='foreignkey')
            op.create_foreign_key(
                'file_uploads_user_id_fkey', 
                'file_uploads', 
                'users', 
                ['user_id'], 
                ['id'], 
                ondelete='CASCADE'
            )


def downgrade():
    """Remove CASCADE constraints - only if tables exist"""
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()
    
    if 'meetings' in existing_tables:
        constraints = [c['name'] for c in inspector.get_foreign_keys('meetings')]
        if 'meetings_created_by_fkey' in constraints:
            op.drop_constraint('meetings_created_by_fkey', 'meetings', type_='foreignkey')
            op.create_foreign_key(
                'meetings_created_by_fkey', 
                'meetings', 
                'users', 
                ['created_by'], 
                ['id']
            )
    
    if 'agenda_items' in existing_tables:
        constraints = [c['name'] for c in inspector.get_foreign_keys('agenda_items')]
        if 'agenda_items_user_id_fkey' in constraints:
            op.drop_constraint('agenda_items_user_id_fkey', 'agenda_items', type_='foreignkey')
            op.create_foreign_key(
                'agenda_items_user_id_fkey', 
                'agenda_items', 
                'users', 
                ['user_id'], 
                ['id']
            )
        if 'agenda_items_meeting_id_fkey' in constraints:
            op.drop_constraint('agenda_items_meeting_id_fkey', 'agenda_items', type_='foreignkey')
            op.create_foreign_key(
                'agenda_items_meeting_id_fkey', 
                'agenda_items', 
                'meetings', 
                ['meeting_id'], 
                ['id']
            )
    
    if 'file_uploads' in existing_tables:
        constraints = [c['name'] for c in inspector.get_foreign_keys('file_uploads')]
        if 'file_uploads_user_id_fkey' in constraints:
            op.drop_constraint('file_uploads_user_id_fkey', 'file_uploads', type_='foreignkey')
            op.create_foreign_key(
                'file_uploads_user_id_fkey', 
                'file_uploads', 
                'users', 
                ['user_id'], 
                ['id']
            )