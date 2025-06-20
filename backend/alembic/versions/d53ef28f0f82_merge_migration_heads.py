"""Merge migration heads

Revision ID: d53ef28f0f82
Revises: 1234567890ab, a1b2c3d4e5f6
Create Date: 2025-06-20 11:23:50.226820

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd53ef28f0f82'
down_revision = ('1234567890ab', 'a1b2c3d4e5f6')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass