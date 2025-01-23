"""add benchmark field to cpu

Revision ID: 6392c17321d3
Revises: 7e2352cf0b03
Create Date: 2025-01-23 11:53:44.794622

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6392c17321d3'
down_revision = '7e2352cf0b03'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cpu', schema=None) as batch_op:
        batch_op.add_column(sa.Column('benchmark', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cpu', schema=None) as batch_op:
        batch_op.drop_column('benchmark')

    # ### end Alembic commands ###
