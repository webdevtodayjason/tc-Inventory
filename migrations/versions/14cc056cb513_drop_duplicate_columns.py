"""drop_duplicate_columns

Revision ID: 14cc056cb513
Revises: 8ec20402fb59
Create Date: 2025-02-06 13:48:16.784123

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '14cc056cb513'
down_revision = '8ec20402fb59'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the duplicate columns from computer_systems table
    op.drop_column('computer_systems', 'serial_number')
    op.drop_column('computer_systems', 'location')


def downgrade():
    # Add back the columns if needed to rollback
    op.add_column('computer_systems', sa.Column('serial_number', sa.String(length=100), nullable=True))
    op.add_column('computer_systems', sa.Column('location', sa.String(length=100), nullable=True))
