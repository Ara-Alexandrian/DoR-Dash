"""add user avatar_url field

Revision ID: a1b2c3d4e5f6
Revises: 9d7e8f6a5b4c
Create Date: 2025-06-19 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '9d7e8f6a5b4c'
branch_labels = None
depends_on = None


def upgrade():
    """Add avatar_url column to user table"""
    op.add_column('user', sa.Column('avatar_url', sa.String(500), nullable=True))


def downgrade():
    """Remove avatar_url column from user table"""
    op.drop_column('user', 'avatar_url')