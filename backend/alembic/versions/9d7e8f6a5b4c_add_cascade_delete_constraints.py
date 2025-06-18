"""add cascade delete constraints

Revision ID: 9d7e8f6a5b4c
Revises: 8c6d4e3f7a90
Create Date: 2025-06-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d7e8f6a5b4c'
down_revision = '8c6d4e3f7a90'
branch_labels = None
depends_on = None


def upgrade():
    """Add CASCADE constraints to foreign keys for user deletion"""
    # Drop and recreate foreign key constraints with CASCADE
    
    # 1. Update student_updates table
    op.drop_constraint('student_updates_student_id_fkey', 'student_updates', type_='foreignkey')
    op.create_foreign_key(
        'student_updates_student_id_fkey', 
        'student_updates', 
        'user', 
        ['student_id'], 
        ['id'], 
        ondelete='CASCADE'
    )
    
    # 2. Update faculty_updates table
    op.drop_constraint('faculty_updates_faculty_id_fkey', 'faculty_updates', type_='foreignkey')
    op.create_foreign_key(
        'faculty_updates_faculty_id_fkey', 
        'faculty_updates', 
        'user', 
        ['faculty_id'], 
        ['id'], 
        ondelete='CASCADE'
    )
    
    # 3. Update assigned_presentations table
    op.drop_constraint('assigned_presentations_user_id_fkey', 'assigned_presentations', type_='foreignkey')
    op.create_foreign_key(
        'assigned_presentations_user_id_fkey', 
        'assigned_presentations', 
        'user', 
        ['user_id'], 
        ['id'], 
        ondelete='CASCADE'
    )
    
    # 4. Update meeting table to SET NULL instead of blocking deletion
    op.drop_constraint('meeting_created_by_fkey', 'meeting', type_='foreignkey')
    op.alter_column('meeting', 'created_by', nullable=True)
    op.create_foreign_key(
        'meeting_created_by_fkey', 
        'meeting', 
        'user', 
        ['created_by'], 
        ['id'], 
        ondelete='SET NULL'
    )


def downgrade():
    """Remove CASCADE constraints"""
    # Revert foreign key constraints
    
    # 1. Revert student_updates table
    op.drop_constraint('student_updates_student_id_fkey', 'student_updates', type_='foreignkey')
    op.create_foreign_key(
        'student_updates_student_id_fkey', 
        'student_updates', 
        'user', 
        ['student_id'], 
        ['id']
    )
    
    # 2. Revert faculty_updates table
    op.drop_constraint('faculty_updates_faculty_id_fkey', 'faculty_updates', type_='foreignkey')
    op.create_foreign_key(
        'faculty_updates_faculty_id_fkey', 
        'faculty_updates', 
        'user', 
        ['faculty_id'], 
        ['id']
    )
    
    # 3. Revert assigned_presentations table
    op.drop_constraint('assigned_presentations_user_id_fkey', 'assigned_presentations', type_='foreignkey')
    op.create_foreign_key(
        'assigned_presentations_user_id_fkey', 
        'assigned_presentations', 
        'user', 
        ['user_id'], 
        ['id']
    )
    
    # 4. Revert meeting table
    op.drop_constraint('meeting_created_by_fkey', 'meeting', type_='foreignkey')
    op.alter_column('meeting', 'created_by', nullable=False)
    op.create_foreign_key(
        'meeting_created_by_fkey', 
        'meeting', 
        'user', 
        ['created_by'], 
        ['id']
    )