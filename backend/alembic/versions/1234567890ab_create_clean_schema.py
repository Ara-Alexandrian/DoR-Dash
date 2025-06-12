"""create clean schema

Revision ID: 1234567890ab
Revises: 8c6d4e3f7a90
Create Date: 2025-06-12 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1234567890ab'
down_revision = '8c6d4e3f7a90'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE userrole AS ENUM ('STUDENT', 'FACULTY', 'SECRETARY', 'ADMIN')")
    op.execute("CREATE TYPE meetingtype AS ENUM ('general_update', 'presentations_and_updates', 'other')")
    op.execute("CREATE TYPE registrationstatus AS ENUM ('pending', 'approved', 'rejected')")
    op.execute("CREATE TYPE agendaitemtype AS ENUM ('student_update', 'faculty_update', 'announcement', 'presentation')")
    
    # Create meeting table
    op.create_table('meeting',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('meeting_type', postgresql.ENUM('general_update', 'presentations_and_updates', 'other', name='meetingtype'), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meeting_created_by'), 'meeting', ['created_by'], unique=False)
    
    # Create agenda_item table
    op.create_table('agenda_item',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('meeting_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('item_type', postgresql.ENUM('student_update', 'faculty_update', 'announcement', 'presentation', name='agendaitemtype'), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('content', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('is_presenting', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['meeting_id'], ['meeting.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agenda_item_item_type'), 'agenda_item', ['item_type'], unique=False)
    op.create_index(op.f('ix_agenda_item_meeting_id'), 'agenda_item', ['meeting_id'], unique=False)
    op.create_index(op.f('ix_agenda_item_user_id'), 'agenda_item', ['user_id'], unique=False)
    
    # Create fileupload table
    op.create_table('fileupload',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('agenda_item_id', sa.Integer(), nullable=True),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('filepath', sa.String(length=500), nullable=False),
        sa.Column('file_type', sa.String(length=100), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('upload_date', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['agenda_item_id'], ['agenda_item.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create registration_request table
    op.create_table('registration_request',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('preferred_email', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('research_interests', sa.Text(), nullable=True),
        sa.Column('additional_info', sa.Text(), nullable=True),
        sa.Column('status', postgresql.ENUM('pending', 'approved', 'rejected', name='registrationstatus'), nullable=False),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('requested_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('registration_request')
    op.drop_table('fileupload')
    op.drop_table('agenda_item')
    op.drop_table('meeting')
    op.execute('DROP TYPE agendaitemtype')
    op.execute('DROP TYPE registrationstatus')
    op.execute('DROP TYPE meetingtype')
    op.execute('DROP TYPE userrole')