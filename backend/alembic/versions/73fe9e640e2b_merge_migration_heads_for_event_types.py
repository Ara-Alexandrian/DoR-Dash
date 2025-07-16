"""merge migration heads for event types

Revision ID: 73fe9e640e2b
Revises: add_event_type_to_meetings, f1e2d3c4b5a6
Create Date: 2025-07-16 12:08:01.674501

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73fe9e640e2b'
down_revision = ('add_event_type_to_meetings', 'f1e2d3c4b5a6')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass