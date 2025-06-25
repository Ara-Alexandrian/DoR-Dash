"""create presentation assignments table

Revision ID: 7b0ef1220e47
Revises: d53ef28f0f82
Create Date: 2025-06-21 00:52:26.551468

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7b0ef1220e47'
down_revision = 'd53ef28f0f82'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum type for presentation types
    presentation_type_enum = postgresql.ENUM(
        'casual', 'mock_defense', 'pre_conference', 'thesis_proposal',
        'dissertation_defense', 'journal_club', 'research_update',
        name='presentationtype'
    )
    presentation_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Create presentation_assignments table
    op.create_table('presentation_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('assigned_by_id', sa.Integer(), nullable=False),
        sa.Column('meeting_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('presentation_type', sa.Enum('casual', 'mock_defense', 'pre_conference', 'thesis_proposal', 'dissertation_defense', 'journal_club', 'research_update', name='presentationtype'), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('assigned_date', sa.DateTime(), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('completion_date', sa.DateTime(), nullable=True),
        sa.Column('grillometer_novelty', sa.Integer(), nullable=True),
        sa.Column('grillometer_methodology', sa.Integer(), nullable=True),
        sa.Column('grillometer_delivery', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['assigned_by_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['meeting_id'], ['meeting.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_presentation_assignments_id'), 'presentation_assignments', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_presentation_assignments_id'), table_name='presentation_assignments')
    op.drop_table('presentation_assignments')
    
    # Drop enum type
    presentation_type_enum = postgresql.ENUM(
        'casual', 'mock_defense', 'pre_conference', 'thesis_proposal',
        'dissertation_defense', 'journal_club', 'research_update',
        name='presentationtype'
    )
    presentation_type_enum.drop(op.get_bind(), checkfirst=True)