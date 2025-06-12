"""Drop old update tables

Revision ID: 8c6d4e3f7a90
Revises: 7b5c3d2e6f89
Create Date: 2025-06-12 14:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8c6d4e3f7a90'
down_revision = '7b5c3d2e6f89'
branch_labels = None
depends_on = None


def upgrade() -> None:
    print("Dropping old update tables...")
    
    # Drop old tables (data has been migrated to agenda_item)
    op.drop_table('studentupdate')
    op.drop_table('facultyupdate')
    
    # Drop old enum types that are no longer needed
    try:
        op.execute('DROP TYPE announcementtype')
    except:
        pass  # Type might not exist
    
    print("Old tables dropped successfully")


def downgrade() -> None:
    print("WARNING: Recreating old tables without data!")
    
    # Recreate the announcement type enum
    announcement_type = postgresql.ENUM(
        'general', 'urgent', 'deadline',
        name='announcementtype',
        create_type=False
    )
    announcement_type.create(op.get_bind())
    
    # Recreate studentupdate table
    op.create_table(
        'studentupdate',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('meeting_id', sa.Integer(), sa.ForeignKey('meeting.id', ondelete='SET NULL'), nullable=True),
        sa.Column('progress_text', sa.Text(), nullable=False),
        sa.Column('challenges_text', sa.Text(), nullable=False),
        sa.Column('next_steps_text', sa.Text(), nullable=False),
        sa.Column('meeting_notes', sa.Text(), nullable=True),
        sa.Column('will_present', sa.Boolean(), default=False, nullable=False),
        sa.Column('submission_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False)
    )
    
    # Recreate facultyupdate table
    op.create_table(
        'facultyupdate',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('meeting_id', sa.Integer(), sa.ForeignKey('meeting.id', ondelete='SET NULL'), nullable=True),
        sa.Column('announcements_text', sa.Text(), nullable=True),
        sa.Column('announcement_type', announcement_type, default='general', nullable=False),
        sa.Column('projects_text', sa.Text(), nullable=True),
        sa.Column('project_status_text', sa.Text(), nullable=True),
        sa.Column('faculty_questions', sa.Text(), nullable=True),
        sa.Column('is_presenting', sa.Boolean(), default=False, nullable=False),
        sa.Column('submission_date', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False)
    )
    
    print("Old tables recreated (without data)")