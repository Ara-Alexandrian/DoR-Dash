"""make meeting_id required in presentation_assignments

Revision ID: f1e2d3c4b5a6
Revises: a7e266bf84b2
Create Date: 2025-06-26 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1e2d3c4b5a6'
down_revision = 'a7e266bf84b2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # First, update any existing null meeting_id values
    # This is a data migration step to ensure no null values exist
    op.execute("""
        UPDATE presentation_assignments 
        SET meeting_id = (
            SELECT id FROM meeting 
            WHERE start_time >= NOW() 
            ORDER BY start_time ASC 
            LIMIT 1
        )
        WHERE meeting_id IS NULL
    """)
    
    # Now alter the column to be NOT NULL
    op.alter_column('presentation_assignments', 'meeting_id',
                    existing_type=sa.INTEGER(),
                    nullable=False)


def downgrade() -> None:
    # Make meeting_id nullable again
    op.alter_column('presentation_assignments', 'meeting_id',
                    existing_type=sa.INTEGER(),
                    nullable=True)