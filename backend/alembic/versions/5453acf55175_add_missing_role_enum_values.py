"""Add missing role enum values

Revision ID: 5453acf55175
Revises: 65c2b80029f3
Create Date: 2025-06-05 18:06:06.755239

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5453acf55175'
down_revision = '65c2b80029f3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing enum values to userrole enum type
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'faculty'")
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'secretary'")


def downgrade() -> None:
    pass