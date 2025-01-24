"""add mobile tables

Revision ID: add_mobile_tables
Revises: b2e0961e8a45
Create Date: 2025-01-23 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_mobile_tables'
down_revision = 'b2e0961e8a45'
branch_labels = None
depends_on = None

def upgrade():
    # Create mobile_checkout_reasons table
    op.create_table('mobile_checkout_reasons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create mobile_device_tokens table
    op.create_table('mobile_device_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('device_token', sa.String(length=255), nullable=False),
        sa.Column('device_type', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add is_mobile column to transactions table
    op.add_column('transactions',
        sa.Column('is_mobile', sa.Boolean(), nullable=True, server_default='false')
    )

def downgrade():
    # Remove is_mobile column from transactions
    op.drop_column('transactions', 'is_mobile')
    
    # Drop the tables
    op.drop_table('mobile_device_tokens')
    op.drop_table('mobile_checkout_reasons') 