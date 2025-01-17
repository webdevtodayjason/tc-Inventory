"""add tags to computer systems

Revision ID: add_system_tags
Revises: 9415b4889fc3
Create Date: 2024-01-10 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_system_tags'
down_revision = '9415b4889fc3'
branch_labels = None
depends_on = None


def upgrade():
    # Create system_tags association table
    op.create_table('system_tags',
        sa.Column('system_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['system_id'], ['computer_systems.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('system_id', 'tag_id')
    )


def downgrade():
    op.drop_table('system_tags') 