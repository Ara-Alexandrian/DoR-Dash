"""add event_type to meetings and make end_time optional

Revision ID: add_event_type_to_meetings
Revises: d53ef28f0f82
Create Date: 2025-01-16 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_event_type_to_meetings'
down_revision = 'd53ef28f0f82'
branch_labels = None
depends_on = None


def upgrade():
    # Add event_type column with default value
    op.add_column('meeting', sa.Column('event_type', sa.String(50), nullable=False, server_default='meeting'))
    
    # Make end_time nullable
    op.alter_column('meeting', 'end_time',
                    existing_type=sa.DateTime(),
                    nullable=True)


def downgrade():
    # Remove event_type column
    op.drop_column('meeting', 'event_type')
    
    # Make end_time required again
    op.alter_column('meeting', 'end_time',
                    existing_type=sa.DateTime(),
                    nullable=False)