"""Unified agenda item schema

Revision ID: 6a4b2c1d5e78
Revises: 5453acf55175
Create Date: 2025-06-12 14:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6a4b2c1d5e78'
down_revision = '5453acf55175'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the agenda_item_type enum
    agenda_item_type = postgresql.ENUM(
        'student_update', 
        'faculty_update', 
        'announcement', 
        'presentation',
        name='agendaitemtype',
        create_type=False
    )
    agenda_item_type.create(op.get_bind())
    
    # Create the unified agenda_item table
    op.create_table(
        'agenda_item',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('meeting_id', sa.Integer(), sa.ForeignKey('meeting.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('item_type', agenda_item_type, nullable=False),
        sa.Column('order_index', sa.Integer(), default=0, nullable=False),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('content', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default='{}'),
        sa.Column('is_presenting', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        
        # Ensure unique ordering within meetings
        sa.UniqueConstraint('meeting_id', 'order_index', name='uq_meeting_order')
    )
    
    # Create indexes for performance
    op.create_index('idx_agenda_item_meeting_order', 'agenda_item', ['meeting_id', 'order_index'])
    op.create_index('idx_agenda_item_user', 'agenda_item', ['user_id'])
    op.create_index('idx_agenda_item_type', 'agenda_item', ['item_type'])
    op.create_index('idx_agenda_item_content', 'agenda_item', ['content'], postgresql_using='gin')
    
    # Update file_upload table to reference agenda_item
    # First, add the new column
    op.add_column('fileupload', sa.Column('agenda_item_id', sa.Integer(), sa.ForeignKey('agenda_item.id', ondelete='CASCADE'), nullable=True))
    
    # Create index for the new foreign key
    op.create_index('idx_fileupload_agenda_item', 'fileupload', ['agenda_item_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_fileupload_agenda_item', table_name='fileupload')
    op.drop_index('idx_agenda_item_content', table_name='agenda_item')
    op.drop_index('idx_agenda_item_type', table_name='agenda_item')
    op.drop_index('idx_agenda_item_user', table_name='agenda_item')
    op.drop_index('idx_agenda_item_meeting_order', table_name='agenda_item')
    
    # Remove agenda_item_id column from fileupload
    op.drop_column('fileupload', 'agenda_item_id')
    
    # Drop agenda_item table
    op.drop_table('agenda_item')
    
    # Drop the enum type
    op.execute('DROP TYPE agendaitemtype')