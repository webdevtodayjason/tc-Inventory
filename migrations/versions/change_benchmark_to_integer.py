"""change benchmark to integer

Revision ID: change_benchmark_to_integer
Revises: 6392c17321d3
Create Date: 2025-01-23 12:53:44.794622

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'change_benchmark_to_integer'
down_revision = '6392c17321d3'
branch_labels = None
depends_on = None


def upgrade():
    # Convert existing float values to integers before changing type
    op.execute('UPDATE cpu SET benchmark = ROUND(benchmark::numeric)::integer WHERE benchmark IS NOT NULL')
    
    # Change column type to integer
    with op.batch_alter_table('cpu', schema=None) as batch_op:
        batch_op.alter_column('benchmark',
                            existing_type=sa.Float(),
                            type_=sa.Integer(),
                            existing_nullable=True)


def downgrade():
    # Change column type back to float
    with op.batch_alter_table('cpu', schema=None) as batch_op:
        batch_op.alter_column('benchmark',
                            existing_type=sa.Integer(),
                            type_=sa.Float(),
                            existing_nullable=True) 