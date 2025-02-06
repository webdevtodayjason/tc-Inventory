"""add mobile tables

Revision ID: add_mobile_tables
Revises: previous_revision
Create Date: 2024-02-05 21:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_mobile_tables'
down_revision = None  # Update this with the previous migration's revision ID
branch_labels = None
depends_on = None

def upgrade():
    # Create mobile_device_tokens table
    op.create_table('mobile_device_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('device_token', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create mobile_checkout_reasons table
    op.create_table('mobile_checkout_reasons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Insert default checkout reasons
    op.execute("""
        INSERT INTO mobile_checkout_reasons (name, description, is_active, created_at)
        VALUES 
        ('CLIENT INSTALL', 'Installation at client site', true, NOW()),
        ('REPAIR', 'Item needs repair or maintenance', true, NOW()),
        ('TESTING', 'Testing or validation required', true, NOW()),
        ('DEMO', 'Client demonstration or presentation', true, NOW())
    """)

def downgrade():
    op.drop_table('mobile_checkout_reasons')
    op.drop_table('mobile_device_tokens') 